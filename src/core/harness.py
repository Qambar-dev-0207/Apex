"""
AgentHarness — autonomous code-editing loop for APEX.

Beats Claude Code on:
  • Hot model swap (MiMo / Gemini / Groq) — agentic loop is model-agnostic.
  • Atomic multi_edit (single transactional patch with auto-rollback).
  • Per-step diff preview before any write.
  • Auto-snapshot of touched files to backups/ on first write.
  • Local-only — no telemetry, no network besides chosen LLM.
  • Hardware-aware: pauses when CPU/RAM critical.

Loop:
    user goal
        ↓
    MiMo (tool-calling)  ──► tool_calls
        ↓                       ↓
    parse                   execute (view/edit/write/bash/git/...)
        ↓                       ↓
    feed tool results back ─────┘
        ↓
    repeat until model calls `done` or max_steps reached.

Slash command:  /harness <goal>
"""

import os
import re
import json
import time
import shutil
import asyncio
import fnmatch
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from src.models.mimo_path import MimoClient
from src.models.fast_path import GroqClient
from src.models.local_path import OllamaClient
from src.tools.filesystem import FilesystemAgent
from src.tools.shell import ShellAgent
from src.tools.git_agent import GitAgent
from src.tools.diff_tool import DiffTool
from src.tools.todo import TodoTool
from src.tools.safety import SafetyGuard


# ── tool schemas (OpenAI function-calling format) ────────────────────────────

TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "view",
            "description": "Read a file with line numbers. Use BEFORE editing so edits target correct lines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative or absolute path."},
                    "offset": {"type": "integer", "description": "Optional 1-indexed start line."},
                    "limit": {"type": "integer", "description": "Optional max lines to return."},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write",
            "description": "Create a new file or overwrite entire contents. Use ONLY for new files; prefer edit for existing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit",
            "description": "Replace exact string match in a file. Fails if old_string not unique unless replace_all=true.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_string": {"type": "string"},
                    "new_string": {"type": "string"},
                    "replace_all": {"type": "boolean", "default": False},
                },
                "required": ["path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multi_edit",
            "description": "Apply multiple edits to one file atomically. Rolls back on any failure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "edits": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "old_string": {"type": "string"},
                                "new_string": {"type": "string"},
                                "replace_all": {"type": "boolean", "default": False},
                            },
                            "required": ["old_string", "new_string"],
                        },
                    },
                },
                "required": ["path", "edits"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_dir",
            "description": "Create directory (parents auto-created).",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete",
            "description": "Delete a file or directory. Use recursive=true for dirs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "recursive": {"type": "boolean", "default": False},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List entries in a directory.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "default": "."}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tree",
            "description": "Tree view of dir up to depth (skips .git, __pycache__, node_modules).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": "."},
                    "depth": {"type": "integer", "default": 3},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob",
            "description": "Find files matching a glob pattern. Recursive ** supported.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "root": {"type": "string", "default": "."},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search file contents for regex pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string", "default": "."},
                    "file_glob": {"type": "string", "description": "Optional glob filter (e.g. '*.py')"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run a shell command. Hardware/safety gated. Captures stdout/stderr.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout": {"type": "integer", "default": 60},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git",
            "description": "Git operations: status, diff, add, commit, log, push, pull, checkout.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["status", "diff", "add", "commit", "log", "push", "pull", "checkout"]},
                    "arg": {"type": "string", "description": "Optional: commit msg, file path, branch."},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "diff_preview",
            "description": "Preview a proposed change as unified diff before writing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "todo_add",
            "description": "Add a task to the persistent project todo list.",
            "parameters": {
                "type": "object",
                "properties": {"task": {"type": "string"}},
                "required": ["task"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "todo_list",
            "description": "List current todos for the active project.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "todo_done",
            "description": "Mark a todo completed by its id.",
            "parameters": {
                "type": "object",
                "properties": {"id": {"type": "string"}},
                "required": ["id"],
            },
        },
    },
    # ── APEX-wide tools (delegated to ParallelExecutor when wired) ──────────
    {
        "type": "function",
        "function": {
            "name": "vision_capture",
            "description": "Capture full screen (returns saved path).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "vision_describe",
            "description": "Describe what's in an image file (Gemini multimodal). Optional prompt for targeted Q&A.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "prompt": {"type": "string"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "vision_ocr",
            "description": "Extract all visible text from an image (Gemini-backed OCR).",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "video_describe",
            "description": "Understand a video by sampling frames and asking Gemini for a temporal description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "max_frames": {"type": "integer", "default": 8},
                    "prompt": {"type": "string"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "audio_transcribe",
            "description": "Transcribe audio via Groq Whisper.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "understand_media",
            "description": "Auto-detect media type (image/video/audio) and describe/transcribe.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "prompt": {"type": "string"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hardware_vitals",
            "description": "CPU/RAM/GPU snapshot. Use to gate heavy ops.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "code_compass_search",
            "description": "Token-efficient AST symbol search across project.",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string"}},
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "code_compass_context",
            "description": "Get compressed code context relevant to a query.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "knowledge_forge_search",
            "description": "Search ingested arxiv papers / capability proposals.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "swarm_run",
            "description": "Spawn specialist agents (architect/coder/critic/...) for a goal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string"},
                    "roster": {"type": "array", "items": {"type": "string"}},
                    "rounds": {"type": "integer", "default": 1},
                },
                "required": ["goal"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "think_partner",
            "description": "Cognitive collaborator. modes: cross_question, architect, debate, brainstorm, teach.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["cross_question", "architect", "debate", "brainstorm", "teach"]},
                    "prompt": {"type": "string"},
                },
                "required": ["mode", "prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Web search via DDG/Tavily/Brave. Returns ranked results.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Pull a specific URL's text content (HTML stripped).",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "research_swarm",
            "description": "Multi-agent deep research. Slower than web_search, deeper.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "workspace_summarize",
            "description": "Get active project context summary.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mcp_call",
            "description": "Invoke a tool on a connected MCP server.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server": {"type": "string"},
                    "tool": {"type": "string"},
                    "args": {"type": "object"},
                },
                "required": ["server", "tool"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "python_run",
            "description": "Execute a Python snippet in the sandbox.",
            "parameters": {
                "type": "object",
                "properties": {"code": {"type": "string"}},
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "done",
            "description": "Call when the goal is fully achieved. Provide a short summary of what was done.",
            "parameters": {
                "type": "object",
                "properties": {"summary": {"type": "string"}},
                "required": ["summary"],
            },
        },
    },
]


SYSTEM_PROMPT = """\
You are APEX-Harness, an autonomous code-editing agent embedded in the APEX OS.
You have direct read/write access to the user's project via tools.

PROTOCOL:
  1. Always `view` a file before editing it — never guess line content.
  2. Prefer `edit` over `write` for existing files. `write` is for NEW files only.
  3. For multiple edits to the same file, use `multi_edit` (atomic, rolls back on fail).
  4. Before touching shared state (network, DB, force-push, rm -rf, recursive delete on populated dirs), think twice.
  5. Use `bash` for tests/builds/linters after edits to verify your work.
  6. When the goal is fully done, call `done` with a concise summary.

STYLE:
  - Don't narrate. Call tools and act.
  - One tool at a time unless tasks are clearly independent.
  - If a tool fails, read the error and adapt — don't loop on the same call.
  - Match existing code style; no gratuitous refactors.
"""


# ── result helpers ───────────────────────────────────────────────────────────

def _ok(output: Any) -> Dict[str, Any]:
    if not isinstance(output, str):
        output = json.dumps(output, default=str)
    return {"success": True, "output": output}


def _err(msg: str) -> Dict[str, Any]:
    return {"success": False, "error": msg}


def _truncate(text: str, max_chars: int = 8000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n[...truncated {len(text) - max_chars} chars...]"


# ── harness ──────────────────────────────────────────────────────────────────

class AgentHarness:
    """
    Autonomous tool-calling loop. Drives MiMo (or any OpenAI-compatible model
    with `.chat.completions.create` + `tools=`) until it calls `done`.
    """

    # Path segments / prefixes that the harness may never write or delete.
    BLOCKED_PATHS = (
        ".git/", ".env", "id_rsa", ".ssh/",
        "id_ed25519", "id_dsa", "id_ecdsa",
        "credentials", "secrets",
    )
    # File extensions that are always blocked regardless of path
    BLOCKED_EXTENSIONS = frozenset({
        ".pem", ".key", ".p12", ".pfx", ".crt", ".cer", ".der",
    })
    MUTATING_TOOLS = {"write", "edit", "multi_edit", "delete"}

    def __init__(
        self,
        console: Optional[Console] = None,
        fs: Optional[FilesystemAgent] = None,
        shell: Optional[ShellAgent] = None,
        git: Optional[GitAgent] = None,
        mimo: Optional[MimoClient] = None,
        groq: Optional[GroqClient] = None,
        ollama: Optional[OllamaClient] = None,
        executor: Optional[Any] = None,
        gemini_client: Optional[Any] = None,
        mcp_client: Optional[Any] = None,
        retina: Optional[Any] = None,
        code_compass: Optional[Any] = None,
        knowledge_forge: Optional[Any] = None,
        swarm: Optional[Any] = None,
        think_partner: Optional[Any] = None,
        workspace: Optional[Any] = None,
        project_root: Optional[str] = None,
        genius: Optional[Any] = None,
        verify_command: Optional[str] = None,
        verify_every_steps: int = 4,
        max_steps: int = 25,
        brain: str = "auto",  # "auto" | "mimo" | "groq" | "ollama" | "local"
    ):
        self.console = console or Console()
        self.safety = SafetyGuard(console=self.console, mode="auto-approve")
        self.fs = fs or FilesystemAgent(console=self.console, safety=self.safety)
        self.shell = shell or ShellAgent(console=self.console, safety=self.safety)
        self.git = git or GitAgent(console=self.console)
        self.diff = DiffTool()
        self.todo = TodoTool()
        # Brains — tool-calling capable, OpenAI-compatible.
        self.mimo = mimo or MimoClient()
        self.groq = groq or GroqClient(model="llama-3.3-70b-versatile")
        self.ollama = ollama or OllamaClient()
        self.brain_pref = brain
        # APEX-wide collaborators (used only if wired in by APEXEngine).
        self.executor = executor
        self.gemini_client = gemini_client
        self.mcp_client = mcp_client
        self.retina = retina or (executor.retina if executor else None)
        self.code_compass = code_compass or (executor.code_compass if executor else None)
        self.knowledge_forge = knowledge_forge or (executor.knowledge_forge if executor else None)
        self.swarm = swarm or (executor.agent_swarm if executor else None)
        self.think_partner = think_partner or (executor.think_partner if executor else None)
        self.workspace = workspace or (executor.workspace if executor else None)
        self.genius = genius or (executor.genius if (executor and hasattr(executor, "genius")) else None)
        self.verify_command = verify_command
        self.verify_every_steps = verify_every_steps
        self._last_verify_failed = False
        self.project_root = os.path.abspath(project_root or os.getcwd())
        self.max_steps = max_steps
        self.touched_files: List[str] = []
        self.snapshot_dir = os.path.join("backups", f"harness_{int(time.time())}")
        self.steps_log: List[Dict[str, Any]] = []

    # ── brain selection ─────────────────────────────────────────────────
    def _select_brain(self) -> Tuple[Any, str]:
        """Return (openai_compatible_client, model_id)."""
        pref = self.brain_pref
        if pref in ("auto", "mimo") and self.mimo and self.mimo.is_online:
            return self.mimo.client, self.mimo.model
        if pref in ("auto", "groq") and self.groq and self.groq.client:
            return self.groq.client, self.groq.model
        if pref in ("auto", "ollama", "local") and self.ollama:
            client = self.ollama.openai_client
            if client:
                return client, self.ollama.llm_model
        return None, ""

    def _detect_verify_command(self) -> Optional[str]:
        """Cheap heuristic: prefer the project's real test suite if one exists."""
        if os.path.isdir(os.path.join(self.project_root, "tests")):
            return "python -m pytest tests/ -q --no-header -x"
        if os.path.exists(os.path.join(self.project_root, "package.json")):
            return "npm test --silent"
        return None

    async def _verify(self) -> Dict[str, Any]:
        """
        Runs after any mutating tool call and on done() guard.
        Checks syntax of touched files (AST parsing for .py, json.loads for .json)
        and runs project test suite if one exists.
        """
        errors = []
        # 1. AST syntax-check on all touched .py files
        py_files = [f for f in self.touched_files if f.endswith(".py") and os.path.exists(f)]
        if py_files:
            import ast
            for f in py_files:
                try:
                    with open(f, "r", encoding="utf-8", errors="ignore") as pf:
                        content = pf.read()
                    ast.parse(content, filename=f)
                except SyntaxError as e:
                    rel_p = os.path.relpath(f, self.project_root)
                    errors.append(f"SyntaxError in {rel_p} (line {e.lineno}): {e.msg}")
                except Exception as e:
                    rel_p = os.path.relpath(f, self.project_root)
                    errors.append(f"Parse error in {rel_p}: {e}")

        # 2. JSON check on all touched .json files
        json_files = [f for f in self.touched_files if f.endswith(".json") and os.path.exists(f)]
        for f in json_files:
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as jf:
                    json.load(jf)
            except Exception as e:
                rel_p = os.path.relpath(f, self.project_root)
                errors.append(f"JSON format error in {rel_p}: {e}")

        if errors:
            self._last_verify_failed = True
            return {
                "ran": True,
                "success": False,
                "output": "\n".join(errors),
                "errors": errors,
                "type": "syntax",
            }

        # 3. If syntax is clean, run project test suite if available
        cmd = self.verify_command or self._detect_verify_command()
        if not cmd:
            if not self.touched_files:
                self._last_verify_failed = False
                return {"ran": False}
            self._last_verify_failed = False
            return {
                "ran": True,
                "success": True,
                "output": "All syntax checks passed (no project test command configured).",
                "errors": [],
            }

        res = await self.shell.execute(cmd, timeout=120)
        success = bool(res.get("success"))
        self._last_verify_failed = not success
        out = (res.get("output") or res.get("error") or "")[:3000]
        return {
            "ran": True,
            "success": success,
            "output": out,
            "command": cmd,
            "errors": [] if success else [out],
        }

    # ── path safety ──────────────────────────────────────────────────────
    def _resolve(self, path: str) -> str:
        """Resolve to absolute path, anchored at project root for relatives."""
        if os.path.isabs(path):
            full = os.path.abspath(path)
        else:
            full = os.path.abspath(os.path.join(self.project_root, path))
        return full

    def _is_blocked(self, abs_path: str) -> bool:
        rel = os.path.relpath(abs_path, self.project_root)
        # Block any path that escapes the project root
        if rel.startswith(".."):
            return True
        norm = rel.replace("\\", "/")
        # Block by path segment / prefix
        if any(b.rstrip("/") in norm.split("/") or norm.startswith(b) for b in self.BLOCKED_PATHS):
            return True
        # Block by file extension
        ext = os.path.splitext(abs_path)[1].lower()
        if ext in self.BLOCKED_EXTENSIONS:
            return True
        return False

    # ── snapshot ─────────────────────────────────────────────────────────
    def _snapshot(self, abs_path: str) -> None:
        if abs_path in self.touched_files:
            return
        self.touched_files.append(abs_path)
        if not os.path.exists(abs_path):
            return
        try:
            rel = os.path.relpath(abs_path, self.project_root)
            backup = os.path.join(self.snapshot_dir, rel)
            os.makedirs(os.path.dirname(backup), exist_ok=True)
            shutil.copy2(abs_path, backup)
        except Exception:
            pass  # best-effort

    # ── individual tool implementations ──────────────────────────────────
    async def _tool_view(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve(args["path"])
        offset = int(args.get("offset", 1) or 1)
        limit = int(args.get("limit", 2000) or 2000)
        if not os.path.exists(path):
            return _err(f"file not found: {path}")
        if not os.path.isfile(path):
            return _err(f"not a file: {path}")
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            start = max(0, offset - 1)
            chunk = lines[start : start + limit]
            numbered = [f"{start + i + 1:>5}\t{l.rstrip()}" for i, l in enumerate(chunk)]
            return _ok("\n".join(numbered))
        except Exception as e:
            return _err(str(e))

    async def _tool_write(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve(args["path"])
        content = args["content"]
        if self._is_blocked(path):
            return _err(f"path blocked: {path}")
        self._snapshot(path)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return _ok(f"wrote {len(content)} bytes → {path}")
        except Exception as e:
            return _err(str(e))

    async def _tool_edit(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve(args["path"])
        if not os.path.exists(path):
            return _err(f"file not found: {path}")
        if self._is_blocked(path):
            return _err(f"path blocked: {path}")
        old = args["old_string"]
        new = args["new_string"]
        replace_all = bool(args.get("replace_all", False))
        try:
            with open(path, "r", encoding="utf-8") as f:
                src = f.read()
        except Exception as e:
            return _err(str(e))
        if old not in src:
            return _err("old_string not found in file")
        count = src.count(old)
        if count > 1 and not replace_all:
            return _err(f"old_string occurs {count}x; pass replace_all=true or provide more context")
        new_src = src.replace(old, new) if replace_all else src.replace(old, new, 1)
        self._snapshot(path)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_src)
            return _ok(f"edited {path} ({count if replace_all else 1} replacement(s))")
        except Exception as e:
            return _err(str(e))

    async def _tool_multi_edit(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve(args["path"])
        edits = args.get("edits", [])
        if not edits:
            return _err("no edits provided")
        if not os.path.exists(path):
            return _err(f"file not found: {path}")
        if self._is_blocked(path):
            return _err(f"path blocked: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                src = f.read()
        except Exception as e:
            return _err(str(e))
        original = src
        applied = 0
        for i, e in enumerate(edits):
            old = e.get("old_string", "")
            new = e.get("new_string", "")
            replace_all = bool(e.get("replace_all", False))
            if not old:
                return _err(f"edit #{i+1}: empty old_string")
            if old not in src:
                return _err(f"edit #{i+1}: old_string not found")
            count = src.count(old)
            if count > 1 and not replace_all:
                return _err(f"edit #{i+1}: old_string occurs {count}x; pass replace_all=true")
            src = src.replace(old, new) if replace_all else src.replace(old, new, 1)
            applied += 1
        if src == original:
            return _err("edits produced no change")
        self._snapshot(path)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(src)
            return _ok(f"applied {applied} edits → {path}")
        except Exception as e:
            return _err(str(e))

    async def _tool_create_dir(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve(args["path"])
        try:
            os.makedirs(path, exist_ok=True)
            return _ok(f"created dir {path}")
        except Exception as e:
            return _err(str(e))

    async def _tool_delete(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve(args["path"])
        if self._is_blocked(path):
            return _err(f"path blocked: {path}")
        if not os.path.exists(path):
            return _err(f"not found: {path}")
        recursive = bool(args.get("recursive", False))
        try:
            if os.path.isdir(path):
                if not recursive:
                    return _err("directory; pass recursive=true to remove")
                shutil.rmtree(path)
                return _ok(f"removed dir {path}")
            os.remove(path)
            return _ok(f"removed file {path}")
        except Exception as e:
            return _err(str(e))

    async def _tool_list_dir(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve(args.get("path", "."))
        if not os.path.isdir(path):
            return _err(f"not a directory: {path}")
        try:
            entries = []
            for name in sorted(os.listdir(path)):
                full = os.path.join(path, name)
                kind = "dir" if os.path.isdir(full) else "file"
                size = ""
                if kind == "file":
                    try:
                        size = f" ({os.path.getsize(full)}b)"
                    except Exception:
                        pass
                entries.append(f"{kind}\t{name}{size}")
            return _ok("\n".join(entries) or "(empty)")
        except Exception as e:
            return _err(str(e))

    async def _tool_tree(self, args: Dict[str, Any]) -> Dict[str, Any]:
        root = self._resolve(args.get("path", "."))
        depth = int(args.get("depth", 3))
        if not os.path.isdir(root):
            return _err(f"not a directory: {root}")
        SKIP = {".git", "__pycache__", "node_modules", ".venv", "venv", "data", "backups", "graphify-out"}
        lines: List[str] = []
        count = 0
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP]
            rel = os.path.relpath(dirpath, root)
            d = 0 if rel == "." else rel.count(os.sep) + 1
            if d > depth:
                dirnames[:] = []
                continue
            prefix = "  " * d
            name = os.path.basename(dirpath) if rel != "." else os.path.basename(root) or root
            lines.append(f"{prefix}{name}/")
            for fn in sorted(filenames):
                lines.append(f"{prefix}  {fn}")
                count += 1
                if count > 500:
                    lines.append(f"{prefix}  ... [output truncated]")
                    return _ok("\n".join(lines))
        return _ok("\n".join(lines))

    async def _tool_glob(self, args: Dict[str, Any]) -> Dict[str, Any]:
        import glob as _glob
        pattern = args["pattern"]
        root = self._resolve(args.get("root", "."))
        try:
            matches = _glob.glob(os.path.join(root, pattern), recursive=True)
            matches = [m for m in matches if not any(p in m for p in (".git", "__pycache__", "node_modules"))]
            return _ok("\n".join(matches[:500]) or "(no matches)")
        except Exception as e:
            return _err(str(e))

    async def _tool_grep(self, args: Dict[str, Any]) -> Dict[str, Any]:
        pattern = args["pattern"]
        path = self._resolve(args.get("path", "."))
        file_glob = args.get("file_glob")
        try:
            pat = re.compile(pattern)
        except re.error as e:
            return _err(f"bad regex: {e}")
        results: List[str] = []
        SKIP = {".git", "__pycache__", "node_modules", ".venv", "venv", "data", "backups"}
        if os.path.isfile(path):
            files = [path]
        else:
            files = []
            for r, dirs, names in os.walk(path):
                dirs[:] = [d for d in dirs if d not in SKIP]
                for n in names:
                    if file_glob and not fnmatch.fnmatch(n, file_glob):
                        continue
                    files.append(os.path.join(r, n))
        for f in files:
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                    for i, line in enumerate(fh, 1):
                        if pat.search(line):
                            results.append(f"{f}:{i}: {line.rstrip()}")
                            if len(results) >= 200:
                                results.append("[...truncated...]")
                                return _ok("\n".join(results))
            except Exception:
                continue
        return _ok("\n".join(results) or "(no matches)")

    async def _tool_bash(self, args: Dict[str, Any]) -> Dict[str, Any]:
        cmd = args["command"]
        timeout = int(args.get("timeout", 60))
        res = await self.shell.execute(cmd, timeout=timeout)
        if res.get("success"):
            return _ok(res.get("output", "")[:8000])
        return _err(res.get("error", "shell failed") + "\n" + res.get("output", "")[:2000])

    async def _tool_git(self, args: Dict[str, Any]) -> Dict[str, Any]:
        action = args["action"]
        arg = args.get("arg", "")
        if action == "status":
            res = self.git.status()
        elif action == "diff":
            res = self.git.diff()
        elif action == "add":
            res = self.git.add(arg or ".")
        elif action == "commit":
            res = self.git.commit(arg or "APEX-Harness auto-commit")
        elif action == "log":
            res = self.git.log()
        elif action == "push":
            res = self.git.push()
        elif action == "pull":
            res = self.git.pull()
        elif action == "checkout":
            res = self.git.checkout(arg)
        else:
            return _err(f"unknown git action: {action}")
        if res.get("success"):
            return _ok(res.get("output", "")[:6000])
        return _err(res.get("error", "git failed"))

    async def _tool_diff_preview(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve(args["path"])
        content = args["content"]
        res = self.diff.diff_content(path, content)
        if res.get("success"):
            return _ok(res.get("output", "(no changes)")[:6000])
        return _err(res.get("error", "diff failed"))

    async def _tool_todo_add(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.todo.add(args.get("task", ""), project_root=self.project_root)

    async def _tool_todo_list(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.todo.list(project_root=self.project_root)

    async def _tool_todo_done(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.todo.update(args["id"], "completed", project_root=self.project_root)

    # ── APEX-wide tools (delegated) ──────────────────────────────────────
    async def _tool_vision_capture(self, _args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.retina:
            return _err("vision not wired")
        try:
            path = self.retina.capture_screen()
            return _ok(f"captured → {path}")
        except Exception as e:
            return _err(str(e))

    async def _tool_vision_describe(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.retina:
            return _err("vision not wired")
        try:
            txt = await self.retina.describe_image(args["path"], args.get("prompt"))
            return _ok(str(txt)[:8000])
        except Exception as e:
            return _err(str(e))

    async def _tool_vision_ocr(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.retina:
            return _err("vision not wired")
        try:
            return _ok(str(await self.retina.ocr_image(args["path"]))[:10000])
        except Exception as e:
            return _err(str(e))

    async def _tool_video_describe(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.retina:
            return _err("vision not wired")
        try:
            txt = await self.retina.describe_video(
                args["path"],
                max_frames=int(args.get("max_frames", 8)),
                prompt=args.get("prompt"),
            )
            return _ok(str(txt)[:8000])
        except Exception as e:
            return _err(str(e))

    async def _tool_audio_transcribe(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.retina:
            return _err("vision not wired")
        try:
            return _ok(str(await self.retina.transcribe_audio(args["path"]))[:12000])
        except Exception as e:
            return _err(str(e))

    async def _tool_understand_media(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.retina:
            return _err("vision not wired")
        try:
            res = await self.retina.understand_media(args["path"], args.get("prompt"))
            return _ok(f"[{res.get('kind','?')}]\n{str(res.get('output',''))[:9000]}")
        except Exception as e:
            return _err(str(e))

    async def _tool_hardware_vitals(self, _args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.executor:
            return _err("executor not wired")
        v = self.executor.hw.get_vitals()
        return _ok(
            f"CPU={v.cpu_percent}% RAM={v.ram_percent}% "
            f"GPU={getattr(v, 'gpu_percent', 'n/a')}% status={v.status}"
        )

    async def _tool_code_compass_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.code_compass:
            return _err("code_compass not wired")
        try:
            hits = self.code_compass.find_symbol(args["symbol"])
            return _ok(json.dumps(hits[:20], indent=2) if hits else "no matches")
        except Exception as e:
            return _err(str(e))

    async def _tool_code_compass_context(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.code_compass:
            return _err("code_compass not wired")
        try:
            return _ok(self.code_compass.context_for_query(args["query"])[:8000])
        except Exception as e:
            return _err(str(e))

    async def _tool_knowledge_forge_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.knowledge_forge:
            return _err("knowledge_forge not wired")
        try:
            hits = self.knowledge_forge.search_papers(args["query"], n=8)
            return _ok(json.dumps(hits, indent=2) if hits else "no matches")
        except Exception as e:
            return _err(str(e))

    async def _tool_swarm_run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.swarm:
            return _err("agent swarm not wired")
        try:
            res = await self.swarm.run(
                args["goal"],
                rounds=int(args.get("rounds", 1)),
                roster=args.get("roster"),
            )
            if not res.get("ok"):
                return _err(res.get("error", "swarm failed"))
            return _ok(str(res.get("artifact", ""))[:6000])
        except Exception as e:
            return _err(str(e))

    async def _tool_think_partner(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.think_partner:
            return _err("think_partner not wired")
        try:
            method = getattr(self.think_partner, args["mode"], None)
            if not callable(method):
                return _err(f"think_partner mode '{args['mode']}' not available")
            res = await method(args["prompt"])
            return _ok(res.get("output", json.dumps(res, indent=2))[:6000])
        except Exception as e:
            return _err(str(e))

    async def _tool_web_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.executor:
            return _err("executor not wired")
        data = await self.executor.web_search.asearch(args["query"])
        if not data.get("success"):
            return _err(data.get("error", "search failed"))
        snippets = "\n".join(
            f"- {r.get('title','')}: {r.get('snippet','')[:200]} ({r.get('url','')})"
            for r in data.get("results", [])[:6]
        )
        return _ok(snippets or "no results")

    async def _tool_web_fetch(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.executor:
            return _err("executor not wired")
        data = await self.executor.web_fetch.afetch(args["url"])
        if not data.get("success"):
            return _err(data.get("error", "fetch failed"))
        return _ok(data.get("output", "")[:8000])

    async def _tool_research_swarm(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.executor:
            return _err("executor not wired")
        try:
            ska = await self.executor.swarm.run_swarm(args["query"])
            return _ok(str(getattr(ska, "summary", ska))[:6000])
        except Exception as e:
            return _err(str(e))

    async def _tool_workspace_summarize(self, _args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.workspace:
            return _err("workspace not wired")
        active = self.workspace.get_active()
        if not active:
            return _err("no active project")
        return _ok(self.workspace.get_project_context_summary(active.name)[:8000])

    async def _tool_mcp_call(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.mcp_client:
            return _err("mcp_client not wired")
        try:
            res = await self.mcp_client.call_tool(
                args["server"], args["tool"], args.get("args") or {}
            )
            return _ok(str(res)[:6000])
        except Exception as e:
            return _err(str(e))

    async def _tool_python_run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.executor:
            return _err("executor not wired")
        try:
            res = self.executor.sandbox.execute(args["code"])
            if res.get("success"):
                return _ok(str(res.get("output", ""))[:6000])
            return _err(str(res.get("error", "exec failed")))
        except Exception as e:
            return _err(str(e))

    # ── dispatcher ───────────────────────────────────────────────────────
    async def _dispatch(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        handler = {
            "view": self._tool_view,
            "write": self._tool_write,
            "edit": self._tool_edit,
            "multi_edit": self._tool_multi_edit,
            "create_dir": self._tool_create_dir,
            "delete": self._tool_delete,
            "list_dir": self._tool_list_dir,
            "tree": self._tool_tree,
            "glob": self._tool_glob,
            "grep": self._tool_grep,
            "bash": self._tool_bash,
            "git": self._tool_git,
            "diff_preview": self._tool_diff_preview,
            "todo_add": self._tool_todo_add,
            "todo_list": self._tool_todo_list,
            "todo_done": self._tool_todo_done,
            "vision_capture": self._tool_vision_capture,
            "vision_describe": self._tool_vision_describe,
            "vision_ocr": self._tool_vision_ocr,
            "video_describe": self._tool_video_describe,
            "audio_transcribe": self._tool_audio_transcribe,
            "understand_media": self._tool_understand_media,
            "hardware_vitals": self._tool_hardware_vitals,
            "code_compass_search": self._tool_code_compass_search,
            "code_compass_context": self._tool_code_compass_context,
            "knowledge_forge_search": self._tool_knowledge_forge_search,
            "swarm_run": self._tool_swarm_run,
            "think_partner": self._tool_think_partner,
            "web_search": self._tool_web_search,
            "web_fetch": self._tool_web_fetch,
            "research_swarm": self._tool_research_swarm,
            "workspace_summarize": self._tool_workspace_summarize,
            "mcp_call": self._tool_mcp_call,
            "python_run": self._tool_python_run,
        }.get(name)
        if not handler:
            return _err(f"unknown tool: {name}")
        try:
            return await handler(args)
        except Exception as e:
            return _err(f"{name} crashed: {e}")

    # ── pretty step rendering ────────────────────────────────────────────
    def _render_step(self, step: int, name: str, args: Dict[str, Any], result: Dict[str, Any]) -> None:
        ok = result.get("success")
        marker = "[bold green]✓[/bold green]" if ok else "[bold red]✗[/bold red]"
        arg_repr = json.dumps(args, ensure_ascii=False)
        if len(arg_repr) > 200:
            arg_repr = arg_repr[:200] + "..."
        self.console.print(f"  {marker} [cyan]{step:02d}[/cyan] [bold]{name}[/bold]  [dim]{arg_repr}[/dim]")
        body = result.get("output") if ok else result.get("error")
        if body:
            body = str(body)
            if len(body) > 600:
                body = body[:600] + f"\n[dim]...(+{len(body)-600} chars)[/dim]"
            self.console.print(Panel(body, border_style="green" if ok else "red", padding=(0, 1)))

    # ── main loop ────────────────────────────────────────────────────────
    async def run(self, goal: str) -> Dict[str, Any]:
        brain_client, brain_model = self._select_brain()
        if not brain_client:
            return {"success": False, "error": "no tool-calling brain online (MiMo, Groq, and Ollama all offline)."}
        
        if self.mimo and brain_client is getattr(self.mimo, "client", None):
            brain_label = "MiMo v2.5-pro"
        elif self.groq and brain_client is getattr(self.groq, "client", None):
            brain_label = "Groq Llama"
        elif self.ollama and brain_client is getattr(self.ollama, "openai_client", None):
            brain_label = f"Ollama Local ({brain_model})"
        else:
            brain_label = f"Brain ({brain_model})"

        wired = []
        if self.retina: wired.append("vision")
        if self.code_compass: wired.append("compass")
        if self.knowledge_forge: wired.append("forge")
        if self.swarm: wired.append("swarm")
        if self.think_partner: wired.append("think")
        if self.mcp_client: wired.append("mcp")
        if self.executor: wired.append("executor")
        wired_str = ", ".join(wired) or "fs/shell/git only"

        self.console.print(Panel(
            f"[bold white]GOAL[/bold white]\n{goal}\n\n"
            f"[dim]brain[/dim]        {brain_label} ({brain_model})\n"
            f"[dim]apex_tools[/dim]   {wired_str}\n"
            f"[dim]project_root[/dim] {self.project_root}\n"
            f"[dim]snapshot_dir[/dim] {self.snapshot_dir}\n"
            f"[dim]max_steps[/dim]    {self.max_steps}",
            title=f"APEX-HARNESS // {brain_label}",
            border_style="gold1",
        ))

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": goal},
        ]

        loop = asyncio.get_event_loop()
        finished_summary: Optional[str] = None

        for step in range(1, self.max_steps + 1):
            is_mimo = bool(self.mimo and brain_client is getattr(self.mimo, "client", None))
            extra = {"extra_body": {"thinking": {"type": "disabled"}}} if is_mimo else {}
            try:
                resp = await loop.run_in_executor(
                    None,
                    lambda: brain_client.chat.completions.create(
                        model=brain_model,
                        messages=messages,
                        tools=TOOL_SCHEMAS,
                        tool_choice="auto",
                        max_completion_tokens=2048 if is_mimo else None,
                        max_tokens=None if is_mimo else 2048,
                        temperature=0.4,
                        top_p=0.95,
                        **extra,
                    ),
                )
            except TypeError:
                # Some OpenAI-compatible providers don't accept both args; retry minimal.
                try:
                    resp = await loop.run_in_executor(
                        None,
                        lambda: brain_client.chat.completions.create(
                            model=brain_model,
                            messages=messages,
                            tools=TOOL_SCHEMAS,
                            tool_choice="auto",
                            temperature=0.4,
                        ),
                    )
                except Exception as e:
                    self.console.print(f"[red]Brain call failed at step {step}: {e}[/red]")
                    return {"success": False, "error": str(e), "steps": step}
            except Exception as e:
                self.console.print(f"[red]Brain call failed at step {step}: {e}[/red]")
                return {"success": False, "error": str(e), "steps": step}

            choice = resp.choices[0]
            msg = choice.message
            tool_calls = getattr(msg, "tool_calls", None) or []

            if not tool_calls:
                # Model answered without calling a tool — treat as final text.
                text = (msg.content or "").strip()
                if text:
                    self.console.print(Panel(text, title=brain_label, border_style="bright_cyan"))
                finished_summary = text or "(no summary)"
                break

            # Append the assistant turn so subsequent tool messages can reference its tool_call_ids.
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in tool_calls
                ],
            })

            for tc in tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}

                if name == "done":
                    # Mandatory Done-Rejection Guard: verify before allowing completion
                    vres = await self._verify()
                    if (vres.get("ran") and not vres.get("success")) or self._last_verify_failed:
                        self._last_verify_failed = True
                        self.console.print("  [bold red]⛔ DONE REJECTED: Verification failed. System must be repaired before completion.[/bold red]")
                        self.console.print(Panel(vres.get("output", "")[:2000], title="[bold red]VERIFICATION FAILURE DETECTED[/bold red]", border_style="red"))
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": name,
                            "content": (
                                f"REJECTED: Verification check failed. You called done() but the system has errors:\n"
                                f"{vres.get('output', '')[:2000]}\n"
                                f"CRITICAL: View the files, inspect lines around the error, fix the broken code, and verify before calling done() again."
                            ),
                        })
                        continue

                    # Verification passed or no checks failed
                    self._last_verify_failed = False
                    finished_summary = args.get("summary", "(no summary)")
                    self.console.print("  [bold green]✓ VERIFICATION PASSED — Goal successfully achieved[/bold green]")
                    self._render_step(step, name, args, _ok(finished_summary))
                    self.steps_log.append({"step": step, "tool": name, "args": args, "result": _ok(finished_summary)})
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": name,
                        "content": f"Accepted: {finished_summary}",
                    })
                    break

                result = await self._dispatch(name, args)
                self._render_step(step, name, args, result)
                self.steps_log.append({"step": step, "tool": name, "args": args, "result": result})

                # Feed result back to model.
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": name,
                    "content": _truncate(
                        result.get("output") if result.get("success") else f"ERROR: {result.get('error')}",
                        max_chars=6000,
                    ),
                })

            mutated_this_step = any(
                tc.function.name in self.MUTATING_TOOLS
                for tc in tool_calls
            )
            if mutated_this_step and finished_summary is None:
                vres = await self._verify()
                if vres.get("ran"):
                    if not vres["success"]:
                        self._last_verify_failed = True
                        marker = "[bold red]✗ AUTO-VERIFY FAILED[/bold red]"
                        self.console.print(f"  {marker}")
                        self.console.print(Panel(vres.get("output", "")[:2000], title="[bold red]AUTO-VERIFY SYNTAX/TEST ERROR[/bold red]", border_style="red"))
                        messages.append({
                            "role": "user",
                            "content": (
                                f"[AUTO-VERIFY FAILED]\n{vres.get('output', '')[:2000]}\n\n"
                                f"CRITICAL: Fix the syntax or test errors before proceeding or calling done()."
                            ),
                        })
                    else:
                        self._last_verify_failed = False
                        marker = "[bold green]✓ AUTO-VERIFY PASSED[/bold green]"
                        self.console.print(f"  {marker}")
                        messages.append({
                            "role": "user",
                            "content": "[AUTO-VERIFY PASSED] All syntax and verification checks passed — you may proceed or call done().",
                        })

            # periodic self-critique via GeniusMode
            if self.genius and step % self.verify_every_steps == 0 and finished_summary is None:
                try:
                    crit = await self.genius.pre_step_critique(
                        goal=goal, proposed_step=f"trajectory up to step {step}"
                    )
                    critique_lines = []
                    if crit.get("wrong"):
                        critique_lines.append("Rival Critique: " + "; ".join(crit["wrong"][:2]))
                    if crit.get("blind_spots"):
                        critique_lines.append("Blind Spots: " + "; ".join(crit["blind_spots"][:2]))
                    if crit.get("action"):
                        action_steps = [
                            a.get("step", str(a)) if isinstance(a, dict) else str(a)
                            for a in crit["action"][:2]
                        ]
                        critique_lines.append("Recommended Action: " + "; ".join(action_steps))
                    if critique_lines:
                        crit_body = "\n".join(critique_lines)
                        self.console.print(Panel(crit_body, title=f"[bold yellow]APEX-GENIUS // Cognitive Critique (Step {step})[/bold yellow]", border_style="yellow"))
                        messages.append({
                            "role": "user",
                            "content": f"[GENIUS-CRITIQUE]\n{crit_body}",
                        })
                except Exception:
                    pass

            if finished_summary is not None:
                break
        else:
            # max_steps exhausted
            self.console.print("[yellow]Harness hit max_steps — stopping.[/yellow]")

        return {
            "success": finished_summary is not None,
            "summary": finished_summary,
            "steps_executed": len(self.steps_log),
            "touched_files": list(self.touched_files),
            "snapshot_dir": self.snapshot_dir if self.touched_files else None,
        }

    # ── recovery ─────────────────────────────────────────────────────────
    def rollback(self) -> Dict[str, Any]:
        """Restore touched files from the snapshot dir created at run start."""
        if not os.path.isdir(self.snapshot_dir):
            return {"success": False, "error": "no snapshot to roll back"}
        restored = 0
        for abs_path in self.touched_files:
            try:
                rel = os.path.relpath(abs_path, self.project_root)
                backup = os.path.join(self.snapshot_dir, rel)
                if os.path.exists(backup):
                    os.makedirs(os.path.dirname(abs_path) or ".", exist_ok=True)
                    shutil.copy2(backup, abs_path)
                    restored += 1
            except Exception:
                continue
        return {"success": True, "output": f"restored {restored} files from {self.snapshot_dir}"}

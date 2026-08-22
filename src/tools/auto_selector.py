"""
AutoToolSelector — APEX picks tools on its own without going through full
DAG planning for every prompt.

Two-tier:
  - tier 1 (regex):   instant pattern match for common single-tool intents
                      ("git status", "read X.py", "search for foo")
  - tier 2 (Gemini):  LLM classifier returns ranked tool list with confidence
                      and action hint, only invoked for non-trivial prompts

If tier 1 matches with high confidence → direct invocation, skip Gemini DAG
planning (saves ~2-5s per prompt). Tier 2 falls back to standard planner if
unclear.

Wired into main.py input flow BEFORE thinking_path so simple "git status"
returns instantly without firing the full architect prompt.
"""

import os
import re
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple

from dotenv import load_dotenv

try:
    from google import genai
except Exception:
    genai = None

from src.tools.registry import resolve_tool_name, REGISTRY


# ── tier 1: regex patterns ───────────────────────────────────────────────────
# Each entry: (compiled_regex, tool, action, input_extractor_fn)
# input_extractor takes the regex match and returns input_data string.

def _passthrough(m: re.Match) -> str:
    return (m.group("arg") or "").strip()


def _empty(_m: re.Match) -> str:
    return ""


def _extract_write(m: re.Match) -> str:
    path = (m.group("path") or "").strip()
    content = (m.group("content") or "").strip()
    return json.dumps({"path": path, "content": content})


_PATTERNS: List[Tuple[re.Pattern, str, str, Any]] = [
    # git
    (re.compile(r"^\s*git\s+status\s*$", re.I), "git", "status", _empty),
    (re.compile(r"^\s*git\s+diff(\s+(?P<arg>.*))?\s*$", re.I), "git", "diff", _passthrough),
    (re.compile(r"^\s*git\s+log\s*$", re.I), "git", "log", _empty),
    (re.compile(r"^\s*git\s+pull\s*$", re.I), "git", "pull", _empty),
    (re.compile(r"^\s*git\s+push\s*$", re.I), "git", "push", _empty),
    (re.compile(r"^\s*git\s+add\s+(?P<arg>.+)$", re.I), "git", "add", _passthrough),
    (re.compile(r"^\s*git\s+commit\s+[\"'-]m?\s*[\"']?(?P<arg>.+?)[\"']?\s*$", re.I), "git", "commit", _passthrough),
    (re.compile(r"^\s*git\s+checkout\s+(?P<arg>\S+)\s*$", re.I), "git", "checkout", _passthrough),

    # filesystem CRUD
    # create / touch / mkdir
    (re.compile(r"^\s*(?:create|touch|make)\s+(?:a\s+)?(?:new\s+)?(?:file\s+)?(?P<arg>[\w./\\\-]+\.\w+)\s*$", re.I),
     "filesystem", "create", _passthrough),
    (re.compile(r"^\s*(?:create|make|mkdir)\s+(?:a\s+)?(?:new\s+)?(?:dir|directory|folder)\s+(?P<arg>[\w./\\\-]+)\s*$", re.I),
     "filesystem", "create_dir", _passthrough),

    # read / cat / view
    (re.compile(r"^\s*(?:read|cat|show|open|view)\s+(?:the\s+)?(?:file\s+)?(?P<arg>[\w./\\\-]+\.\w+)\s*$", re.I),
     "filesystem", "read", _passthrough),

    # write
    (re.compile(r"^\s*(?:write|save)\s+(?:to\s+)?(?:file\s+)?(?P<path>[\w./\\\-]+\.\w+)\s*:\s*(?P<content>.+)$", re.I),
     "filesystem", "write", _extract_write),

    # delete / rm
    (re.compile(r"^\s*(?:delete|remove|rm)\s+(?:the\s+)?(?:file\s+)?(?P<arg>[\w./\\\-]+\.\w+)\s*$", re.I),
     "filesystem", "delete", _passthrough),
    (re.compile(r"^\s*(?:delete|remove|rmdir|rm\s+-r|rm\s+-rf)\s+(?:the\s+)?(?:dir|directory|folder)\s+(?P<arg>[\w./\\\-]+)\s*$", re.I),
     "filesystem", "delete", _passthrough),

    # list / ls
    (re.compile(r"^\s*ls(?:\s+(?P<arg>\S+))?\s*$", re.I), "filesystem", "list", _passthrough),
    (re.compile(r"^\s*list\s+(?:files\s+in\s+)?(?P<arg>[\w./\\\-]+)\s*$", re.I),
     "filesystem", "list", _passthrough),

    # search / glob
    (re.compile(r"^\s*(?:grep|search\s+for)\s+(?P<arg>.+)$", re.I),
     "filesystem", "search", _passthrough),
    (re.compile(r"^\s*(?:glob|find\s+files?\s+matching)\s+(?P<arg>.+)$", re.I),
     "filesystem", "glob", _passthrough),

    # hardware
    (re.compile(r"^\s*(?:vitals|hw\s+status|hardware|cpu(?:\s+usage)?|gpu(?:\s+usage)?|ram(?:\s+usage)?)\s*$", re.I),
     "hardware", "vitals", _empty),

    # vision
    (re.compile(r"^\s*(?:screenshot|capture\s+screen|see\s+(?:my\s+)?screen|what'?s\s+on\s+(?:my\s+)?screen)\s*$", re.I),
     "vision", "capture", _empty),

    # web search
    (re.compile(r"^\s*(?:google|search\s+web\s+for|look\s+up)\s+(?P<arg>.+)$", re.I),
     "web_search", "search", _passthrough),

    # workspace
    (re.compile(r"^\s*(?:project\s+summary|workspace\s+summary|summarize\s+project)\s*$", re.I),
     "workspace", "summarize", _empty),
    (re.compile(r"^\s*(?:scan\s+project|scan\s+workspace|rescan)\s*$", re.I),
     "workspace", "scan", _empty),

    # code_compass
    (re.compile(r"^\s*(?:find|locate|where\s+is)\s+(?:the\s+)?(?:symbol|class|function|def)\s+(?P<arg>\w+)\s*$", re.I),
     "code_compass", "search", _passthrough),
    (re.compile(r"^\s*compass\s+(?:search\s+)?(?P<arg>.+)$", re.I),
     "code_compass", "search", _passthrough),

    # knowledge_forge
    (re.compile(r"^\s*(?:papers?|research)\s+(?:about\s+|on\s+|for\s+)(?P<arg>.+)$", re.I),
     "knowledge_forge", "search_papers", _passthrough),

    # shell
    (re.compile(r"^\s*(?:run|exec|execute)\s+(?P<arg>.+)$", re.I), "shell", "execute", _passthrough),

    # web_fetch — explicit URL pull
    (re.compile(r"^\s*(?:fetch|get|download|pull|open)\s+(?P<arg>https?://\S+)\s*$", re.I),
     "web_fetch", "fetch", _passthrough),
    (re.compile(r"^\s*(?P<arg>https?://\S+)\s*$", re.I), "web_fetch", "fetch", _passthrough),

    # todo
    (re.compile(r"^\s*(?:todos?|tasks?)\s*$", re.I), "todo", "list", _empty),
    (re.compile(r"^\s*(?:todos?|tasks?)\s+list\s*$", re.I), "todo", "list", _empty),
    (re.compile(r"^\s*(?:add\s+todo|todo\s+add)\s+(?P<arg>.+)$", re.I), "todo", "add", _passthrough),
]


def regex_match(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Tier 1 — instant regex match. Returns the tool/action/input or None.
    Use for high-confidence single-tool intents.
    """
    if not prompt:
        return None
    for pattern, tool, action, extractor in _PATTERNS:
        m = pattern.match(prompt)
        if m:
            return {
                "tool": tool,
                "action": action,
                "input_data": extractor(m),
                "confidence": 0.95,
                "source": "regex",
            }
    return None


# ── tier 2: LLM classifier ───────────────────────────────────────────────────

class AutoToolSelector:
    """
    Stateless tool-picking helper.

    classify(prompt) → ranked list of tool candidates with confidence + action.
    pick_best(prompt) → top candidate or None.
    """

    def __init__(self, model_id: str = "gemini-2.5-flash-lite"):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if (genai and api_key) else None
        self.model_id = model_id

    async def classify(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Returns list of {tool, action, input_data, confidence} sorted by
        confidence descending. Returns empty list if LLM unavailable or no
        clear tool match.
        """
        # Tier 1 first — cheap and instant
        rx = regex_match(prompt)
        if rx:
            return [rx]

        if not self.client:
            return []

        tool_lines = []
        for name, spec in REGISTRY.items():
            tool_lines.append(f"- {name}: actions={spec.actions}; {spec.when_to_use}")
        tools_block = "\n".join(tool_lines)

        sys_prompt = f"""You are APEX's tool selector. Decide which APEX tool(s)
the user prompt needs. Output JSON only.

USER PROMPT:
{prompt}

TOOLS AVAILABLE:
{tools_block}

Output JSON:
{{
  "candidates": [
    {{"tool": "<canonical_name>", "action": "<verb>",
      "input_data": "<arg or empty>", "confidence": 0.0-1.0,
      "rationale": "<=80 chars"}}
  ],
  "needs_planning": true|false
}}

Rules:
- 0-3 candidates. Empty list if no tool fits or prompt is conversational.
- "needs_planning" = true if multiple steps required (use full DAG planner).
- confidence > 0.85 only if intent is unambiguous AND single tool suffices.
- "tool" MUST be one of the canonical names above (no aliases).
"""
        try:
            res = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=sys_prompt,
                config={"response_mime_type": "application/json"},
            )
            data = json.loads(res.text or "{}")
        except Exception:
            return []

        candidates = data.get("candidates", []) or []
        # Validate tool names against registry
        valid = []
        for c in candidates:
            tool = c.get("tool", "")
            canonical = resolve_tool_name(tool)
            if canonical:
                c["tool"] = canonical
                c["source"] = "llm"
                valid.append(c)
        valid.sort(key=lambda x: float(x.get("confidence", 0) or 0), reverse=True)
        # Surface needs_planning hint via top candidate metadata
        if valid and data.get("needs_planning"):
            valid[0]["needs_planning"] = True
        return valid

    async def pick_best(self, prompt: str,
                        confidence_threshold: float = 0.85) -> Optional[Dict[str, Any]]:
        """
        Returns top candidate above threshold, or None. Use when you want
        to skip full planning for simple single-tool calls.
        """
        candidates = await self.classify(prompt)
        if not candidates:
            return None
        top = candidates[0]
        if top.get("needs_planning"):
            return None
        if float(top.get("confidence", 0) or 0) < confidence_threshold:
            return None
        return top

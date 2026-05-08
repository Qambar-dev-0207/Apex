import os
import json
import asyncio
import shlex
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


class HookManager:
    """
    Lightweight Claude-Code-style hook system.
    Loads hooks from .apex/hooks.json (project) and ~/.apex/hooks.json (global).

    Hook events:
      - SessionStart       : fired once when APEX boots
      - UserPromptSubmit   : fired after each user input
      - PreToolUse         : fired before a tool runs (ctx contains tool, action, input)
      - PostToolUse        : fired after a tool runs (ctx contains tool, action, result)
      - Stop               : fired on graceful shutdown

    Hook config format:
      {
        "SessionStart": [ {"command": "echo booting"} ],
        "PostToolUse":  [ {"matcher": "shell", "command": "echo post-shell"} ]
      }
    """

    EVENTS = {
        "SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop",
        # Forge lifecycle
        "ForgeCycleStart", "ForgeCycleDone",
        "ApexPaperFound",       # fired per applicable paper ingested
        "ApexEcosystemNew",     # fired when eco scan finds applicable items
        "ForgeProposalAdded",   # fired when synthesizer enqueues new proposals
        "ForgeApplied",         # fired after a proposal is successfully applied
        "ForgeRolledBack",      # fired after a regression rollback
    }

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root or os.getcwd()
        self.hooks: Dict[str, List[Dict[str, Any]]] = {e: [] for e in self.EVENTS}
        self._load()

    def _load(self):
        global_path = Path.home() / ".apex" / "hooks.json"
        project_path = Path(self.project_root) / ".apex" / "hooks.json"
        for p in (global_path, project_path):
            if p.exists():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    for event, entries in data.items():
                        if event in self.EVENTS and isinstance(entries, list):
                            self.hooks[event].extend(entries)
                except Exception as e:
                    print(f"[Hooks] Failed to load {p}: {e}")

    async def fire(self, event: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if event not in self.EVENTS:
            return []
        ctx = context or {}
        results: List[Dict[str, Any]] = []
        for entry in self.hooks.get(event, []):
            matcher = entry.get("matcher")
            if matcher and not self._matches(matcher, ctx):
                continue
            cmd = entry.get("command")
            if not cmd:
                continue
            res = await self._run(cmd, ctx)
            results.append(res)
        return results

    def _matches(self, matcher: str, ctx: Dict[str, Any]) -> bool:
        for k, v in ctx.items():
            if isinstance(v, str) and matcher in v:
                return True
        return False

    async def _run(self, cmd: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        env = {**os.environ, "APEX_HOOK_CONTEXT": json.dumps(ctx)[:4000]}
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=20)
            except asyncio.TimeoutError:
                proc.kill()
                return {"success": False, "error": "hook timeout", "command": cmd}
            return {
                "success": proc.returncode == 0,
                "output": stdout.decode("utf-8", errors="ignore"),
                "error": stderr.decode("utf-8", errors="ignore") if proc.returncode else None,
                "command": cmd,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "command": cmd}

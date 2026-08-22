"""
DiffTool — compare two files, or a file against arbitrary content, returning
a unified diff. Useful as a planner pre-flight check ("what will change?")
before invoking filesystem:write.

Inputs accepted by `run`:
  - JSON {"a": "<path>", "b": "<path>"}            — compare two files
  - JSON {"path": "<path>", "content": "<text>"}   — compare disk vs proposed text
"""

import difflib
import json
import os
from typing import Dict, Any, List


class DiffTool:
    MAX_LINES = 4000  # cap output to keep prompts sane

    def _read(self, path: str) -> List[str]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().splitlines(keepends=True)

    def diff_files(self, a: str, b: str) -> Dict[str, Any]:
        if not os.path.exists(a):
            return {"success": False, "error": f"file not found: {a}"}
        if not os.path.exists(b):
            return {"success": False, "error": f"file not found: {b}"}
        a_lines = self._read(a)
        b_lines = self._read(b)
        return self._unified(a_lines, b_lines, fromfile=a, tofile=b)

    def diff_content(self, path: str, content: str) -> Dict[str, Any]:
        on_disk = self._read(path)
        proposed = content.splitlines(keepends=True)
        # Ensure trailing newline parity so identical text doesn't show as diff.
        if proposed and not proposed[-1].endswith("\n"):
            proposed[-1] = proposed[-1] + "\n"
        return self._unified(
            on_disk, proposed, fromfile=f"{path} (current)", tofile=f"{path} (proposed)"
        )

    def _unified(
        self,
        a_lines: List[str],
        b_lines: List[str],
        fromfile: str,
        tofile: str,
    ) -> Dict[str, Any]:
        diff_iter = difflib.unified_diff(
            a_lines, b_lines, fromfile=fromfile, tofile=tofile, lineterm=""
        )
        lines = list(diff_iter)
        if not lines:
            return {"success": True, "output": "(no changes)", "changed": False}
        added = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
        removed = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
        truncated = False
        if len(lines) > self.MAX_LINES:
            lines = lines[: self.MAX_LINES] + ["[... truncated ...]"]
            truncated = True
        return {
            "success": True,
            "output": "\n".join(lines),
            "changed": True,
            "added": added,
            "removed": removed,
            "truncated": truncated,
        }

    def run(self, input_data: str) -> Dict[str, Any]:
        """Routed entrypoint used by ParallelExecutor."""
        if not input_data:
            return {"success": False, "error": "diff requires JSON input"}
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"bad JSON: {e}"}
        if "a" in data and "b" in data:
            return self.diff_files(data["a"], data["b"])
        if "path" in data and "content" in data:
            return self.diff_content(data["path"], data["content"])
        return {
            "success": False,
            "error": "expected {a,b} or {path,content} in JSON input",
        }

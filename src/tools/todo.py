"""
TodoTool — persistent task list for APEX. Mirrors Claude Code's TodoWrite.

Stored at data/todos.json so it survives across sessions. Per-project scoping
keyed by absolute project root path.

Statuses: pending, in_progress, completed
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional


VALID_STATUS = {"pending", "in_progress", "completed"}


class TodoTool:
    def __init__(self, path: str = "data/todos.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    # ── storage ──────────────────────────────────────────────────────────
    def _load(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def _project_key(project_root: Optional[str]) -> str:
        return os.path.abspath(project_root or os.getcwd())

    # ── operations ──────────────────────────────────────────────────────
    def add(self, task: str, project_root: Optional[str] = None) -> Dict[str, Any]:
        if not task or not task.strip():
            return {"success": False, "error": "empty task"}
        data = self._load()
        key = self._project_key(project_root)
        todos = data.setdefault(key, [])
        entry = {
            "id": uuid.uuid4().hex[:8],
            "task": task.strip(),
            "status": "pending",
            "created": datetime.utcnow().isoformat(timespec="seconds"),
            "updated": datetime.utcnow().isoformat(timespec="seconds"),
        }
        todos.append(entry)
        self._save(data)
        return {"success": True, "output": f"added #{entry['id']}: {entry['task']}", "entry": entry}

    def list(self, project_root: Optional[str] = None) -> Dict[str, Any]:
        data = self._load()
        key = self._project_key(project_root)
        todos = data.get(key, [])
        if not todos:
            return {"success": True, "output": "no todos", "items": []}
        lines = []
        for t in todos:
            mark = {
                "pending": "○",
                "in_progress": "◐",
                "completed": "✓",
            }.get(t["status"], "?")
            lines.append(f"{mark} [{t['id']}] {t['task']} ({t['status']})")
        return {"success": True, "output": "\n".join(lines), "items": todos}

    def update(
        self,
        todo_id: str,
        status: str,
        project_root: Optional[str] = None,
    ) -> Dict[str, Any]:
        if status not in VALID_STATUS:
            return {"success": False, "error": f"bad status; want one of {sorted(VALID_STATUS)}"}
        data = self._load()
        key = self._project_key(project_root)
        todos = data.get(key, [])
        for t in todos:
            if t["id"] == todo_id:
                t["status"] = status
                t["updated"] = datetime.utcnow().isoformat(timespec="seconds")
                self._save(data)
                return {"success": True, "output": f"#{todo_id} → {status}"}
        return {"success": False, "error": f"todo #{todo_id} not found"}

    def remove(self, todo_id: str, project_root: Optional[str] = None) -> Dict[str, Any]:
        data = self._load()
        key = self._project_key(project_root)
        todos = data.get(key, [])
        before = len(todos)
        data[key] = [t for t in todos if t["id"] != todo_id]
        if len(data[key]) == before:
            return {"success": False, "error": f"todo #{todo_id} not found"}
        self._save(data)
        return {"success": True, "output": f"removed #{todo_id}"}

    def clear_completed(self, project_root: Optional[str] = None) -> Dict[str, Any]:
        data = self._load()
        key = self._project_key(project_root)
        todos = data.get(key, [])
        kept = [t for t in todos if t["status"] != "completed"]
        removed = len(todos) - len(kept)
        data[key] = kept
        self._save(data)
        return {"success": True, "output": f"cleared {removed} completed"}

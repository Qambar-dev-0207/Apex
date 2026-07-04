import os
import json
import fnmatch
from typing import Dict, Any, List, Optional
from src.core.models import ProjectManifest
from pathlib import Path

class WorkspaceManager:
    """
    Manages multiple projects and their manifests.
    """
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            # Global config in ~/.apex/workspace.json
            home = str(Path.home())
            storage_path = os.path.join(home, ".apex", "workspace.json")
            
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.projects: Dict[str, ProjectManifest] = {}
        self.active_project_name: Optional[str] = None
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                self.projects = {k: ProjectManifest(**v) for k, v in data.get("projects", {}).items()}
                self.active_project_name = data.get("active_project")

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump({
                "projects": {k: v.model_dump() for k, v in self.projects.items()},
                "active_project": self.active_project_name
            }, f, indent=2)

    def create_project(self, name: str, description: str, root_dir: str, goals: List[str]):
        abs_root = os.path.abspath(root_dir)
        # Create project-local metadata dir
        os.makedirs(os.path.join(abs_root, ".apex"), exist_ok=True)
        
        manifest = ProjectManifest(
            name=name,
            description=description,
            root_dir=abs_root,
            goals=goals
        )
        self.projects[name] = manifest
        self.active_project_name = name
        self._save()
        return manifest

    def set_active(self, name: str):
        if name in self.projects:
            self.active_project_name = name
            self._save()
            return True
        return False

    def get_active(self) -> Optional[ProjectManifest]:
        if self.active_project_name:
            return self.projects.get(self.active_project_name)
        return None

    def add_todo(self, name: str, task: str):
        if name in self.projects:
            self.projects[name].todos.append({"task": task, "done": False})
            self._save()

    def complete_todo(self, name: str, index: int) -> bool:
        if name not in self.projects:
            return False
        todos = self.projects[name].todos
        if 0 <= index < len(todos):
            todos[index]["done"] = True
            self._save()
            return True
        return False

    def update_file_tree(self, name: str, tree: List[str]):
        if name in self.projects:
            self.projects[name].file_tree = tree
            self._save()

    def get_directives(self, name: str) -> str:
        """
        Loads project-level instruction files (CLAUDE.md, APEX.md, AGENTS.md).
        Mimics Claude Code's CLAUDE.md auto-load: high-priority context injected
        into every model call.
        """
        if name not in self.projects:
            return ""
        proj = self.projects[name]
        directives = []
        for fname in ("APEX.md", "CLAUDE.md", "AGENTS.md", ".apex/instructions.md"):
            path = os.path.join(proj.root_dir, fname)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        directives.append(f"--- {fname} ---\n{f.read(4000)}")
                except Exception:
                    pass
        return "\n\n".join(directives)

    def _load_ignore_patterns(self, root: str) -> List[str]:
        """
        Loads .apexignore (preferred) or falls back to .gitignore patterns.
        """
        patterns: List[str] = []
        for fname in (".apexignore", ".gitignore"):
            path = os.path.join(root, fname)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#"):
                                patterns.append(line)
                    if fname == ".apexignore":
                        break
                except Exception:
                    pass
        return patterns

    def _is_ignored(self, rel_path: str, patterns: List[str]) -> bool:
        norm = rel_path.replace(os.sep, "/")
        for pat in patterns:
            p = pat.rstrip("/")
            if fnmatch.fnmatch(norm, p) or fnmatch.fnmatch(os.path.basename(norm), p):
                return True
            if p in norm.split("/"):
                return True
        return False

    def get_project_context_summary(self, name: str, include_directives: bool = False) -> str:
        if name not in self.projects:
            return ""

        proj = self.projects[name]

        tree_lines = ["DIRECTORY STRUCTURE:"]
        for f in proj.file_tree[:100]:
            depth = f.count(os.sep)
            indent = "  " * depth
            tree_lines.append(f"{indent}- {f}")

        summary = [
            f"--- WORKSPACE CONTEXT: {proj.name} ---",
            f"ROOT: {proj.root_dir}",
            f"GOALS: {', '.join(proj.goals)}",
            "\n".join(tree_lines),
        ]

        if include_directives:
            directives = self.get_directives(name)
            if directives:
                summary.append("\nPROJECT DIRECTIVES (auto-loaded):\n" + directives)

        anchors = ["README.md", "architecture.md", "requirements.txt", "package.json", "pyproject.toml", ".env.example"]
        anchor_data = []
        for anchor in anchors:
            path = os.path.join(proj.root_dir, anchor)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read(1500)
                        anchor_data.append(f"FILE: {anchor}\nCONTENT:\n{content}")
                except Exception:
                    pass

        if anchor_data:
            summary.append("\nANCHOR FILES:")
            summary.extend(anchor_data)

        return "\n\n".join(summary)

    def scan_local_files(self, name: str) -> List[str]:
        if name not in self.projects:
            return []
        root = self.projects[name].root_dir
        patterns = self._load_ignore_patterns(root)
        default_skip = {".git", "__pycache__", "node_modules", "venv", ".venv", "data", "dist", "build", ".apex"}
        tree: List[str] = []
        try:
            for root_dir, dirs, files in os.walk(root):
                dirs[:] = [d for d in dirs if d not in default_skip]
                rel_dir = os.path.relpath(root_dir, root)
                if rel_dir != "." and self._is_ignored(rel_dir, patterns):
                    dirs[:] = []
                    continue
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root_dir, file), root)
                    if self._is_ignored(rel_path, patterns):
                        continue
                    tree.append(rel_path)
                    if len(tree) > 5000:
                        break
                if len(tree) > 5000:
                    break
            self.projects[name].file_tree = tree
            self._save()
        except Exception as e:
            print(f"Error scanning files: {e}")
        return tree

import os
import shutil
import re
from typing import Dict, Any, Optional, List
from rich.console import Console
from src.tools.safety import SafetyGuard

class FilesystemAgent:
    """
    Handles comprehensive file and directory CRUD operations (Create, Read, Write, Update, Delete),
    search, and discovery across the workspace.
    """
    def __init__(self, console: Optional[Console] = None, safety: Optional[SafetyGuard] = None):
        self.console = console or Console()
        self.safety = safety or SafetyGuard(console=self.console)

    async def create_file(self, path: str, content: str = "", overwrite: bool = True) -> Dict[str, Any]:
        """
        Creates a new file at path with optional initial content.
        Ensures parent directories exist.
        """
        try:
            if not overwrite and os.path.exists(path):
                return {"success": False, "error": f"File already exists: {path}"}

            authorized = await self.safety.check_filesystem("create", path, content)
            if not authorized:
                return {"success": False, "error": "Permission denied by user."}

            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            line_count = len(content.splitlines()) if content else 0
            byte_count = len(content.encode("utf-8")) if content else 0
            return {
                "success": True,
                "output": f"Created file {path} ({line_count} lines, {byte_count} bytes)",
                "path": os.path.abspath(path),
                "lines": line_count,
                "bytes": byte_count
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_dir(self, path: str) -> Dict[str, Any]:
        """
        Creates a directory (and any necessary intermediate parents).
        """
        try:
            authorized = await self.safety.check_filesystem("create_dir", path)
            if not authorized:
                return {"success": False, "error": "Permission denied by user."}

            os.makedirs(path, exist_ok=True)
            return {
                "success": True,
                "output": f"Created directory {path}",
                "path": os.path.abspath(path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def read_file(
        self,
        path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Reads contents of a file. Supports text, PDF, and image files.
        Optionally extracts a specific 1-indexed line range [start_line, end_line].
        """
        try:
            if not os.path.exists(path):
                return {"success": False, "error": f"File not found: {path}"}

            ext = os.path.splitext(path)[1].lower()

            # Handle PDF
            if ext == ".pdf":
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return {"success": True, "output": text, "type": "pdf", "path": os.path.abspath(path)}
                except Exception as e:
                    return {"success": False, "error": f"Failed to read PDF: {e}"}

            # Handle Images (Metadata, content handled by Retina/Vision)
            if ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"]:
                return {
                    "success": True,
                    "output": f"Image file detected: {path}. APEX is loading visual buffers.",
                    "type": "image",
                    "path": os.path.abspath(path)
                }

            # Default: Text-based (MD, TXT, PY, JSON, TS, etc.)
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            lines = content.splitlines(keepends=True)
            total_lines = len(lines)

            if start_line is not None or end_line is not None:
                s = max(1, start_line) if start_line is not None else 1
                e = min(total_lines, end_line) if end_line is not None else total_lines
                if s > e or s > total_lines:
                    return {"success": False, "error": f"Line range {s}-{e} out of bounds (file has {total_lines} lines)"}
                sliced = "".join(lines[s-1:e])
                formatted = "\n".join(f"{i:4d} | {lines[i-1].rstrip()}" for i in range(s, e+1))
                return {
                    "success": True,
                    "output": formatted,
                    "raw_content": sliced,
                    "type": "text",
                    "path": os.path.abspath(path),
                    "total_lines": total_lines,
                    "start_line": s,
                    "end_line": e
                }

            return {
                "success": True,
                "output": content,
                "type": "text",
                "path": os.path.abspath(path),
                "total_lines": total_lines,
                "bytes": len(content.encode("utf-8"))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Writes (or overwrites) a file with content.
        Creates parent directories automatically.
        """
        try:
            authorized = await self.safety.check_filesystem("write", path, content)
            if not authorized:
                return {"success": False, "error": "Permission denied by user."}

            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            line_count = len(content.splitlines()) if content else 0
            byte_count = len(content.encode("utf-8")) if content else 0
            return {
                "success": True,
                "output": f"Successfully wrote {path} ({line_count} lines, {byte_count} bytes)",
                "path": os.path.abspath(path),
                "lines": line_count,
                "bytes": byte_count
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def update_file(
        self,
        path: str,
        content: Optional[str] = None,
        old_string: Optional[str] = None,
        new_string: Optional[str] = None,
        mode: str = "replace",  # "replace" | "patch" | "append"
        edits: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Updates an existing file via surgical search/replace, atomic multi-edit, appending, or replacement.
        """
        try:
            if not os.path.exists(path):
                return {"success": False, "error": f"File not found for update: {path}"}

            authorized = await self.safety.check_filesystem("update", path, content or new_string)
            if not authorized:
                return {"success": False, "error": "Permission denied by user."}

            with open(path, "r", encoding="utf-8", errors="replace") as f:
                original = f.read()

            updated = original

            # Case 1: Multi-edit batch
            if edits:
                for idx, edit in enumerate(edits):
                    old_str = edit.get("old_string", "")
                    new_str = edit.get("new_string", "")
                    if not old_str:
                        return {"success": False, "error": f"Edit #{idx+1} missing 'old_string'"}
                    count = updated.count(old_str)
                    if count == 0:
                        return {"success": False, "error": f"Edit #{idx+1} failed: 'old_string' not found in {path}"}
                    if count > 1:
                        return {"success": False, "error": f"Edit #{idx+1} failed: 'old_string' occurs {count} times (must be unique)"}
                    updated = updated.replace(old_str, new_str, 1)

            # Case 2: Surgical search/replace
            elif old_string is not None and new_string is not None:
                count = original.count(old_string)
                if count == 0:
                    return {"success": False, "error": f"old_string not found in {path}"}
                if count > 1:
                    return {"success": False, "error": f"old_string occurs {count} times; provide more surrounding lines for unique match"}
                updated = original.replace(old_string, new_string, 1)

            # Case 3: Append mode
            elif mode == "append" and content is not None:
                updated = original + ("\n" if original and not original.endswith("\n") else "") + content

            # Case 4: Full replacement
            elif content is not None:
                updated = content

            else:
                return {"success": False, "error": "No update operation specified (provide content, old_string/new_string, or edits)"}

            with open(path, "w", encoding="utf-8") as f:
                f.write(updated)

            return {
                "success": True,
                "output": f"Successfully updated {path}",
                "path": os.path.abspath(path),
                "lines": len(updated.splitlines()),
                "bytes": len(updated.encode("utf-8"))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def edit_file(self, path: str, old_string: str, new_string: str) -> Dict[str, Any]:
        """
        Surgically replaces a unique instance of old_string with new_string in path.
        """
        return await self.update_file(path, old_string=old_string, new_string=new_string)

    async def delete_file(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """
        Deletes a file or directory.
        """
        try:
            authorized = await self.safety.check_filesystem("delete", path)
            if not authorized:
                return {"success": False, "error": "Permission denied by user."}

            if not os.path.exists(path):
                return {"success": False, "error": f"File or directory not found: {path}"}

            if os.path.isdir(path):
                if recursive:
                    shutil.rmtree(path)
                    return {"success": True, "output": f"Deleted directory recursively: {path}"}
                else:
                    os.rmdir(path)
                    return {"success": True, "output": f"Deleted directory: {path}"}
            else:
                os.remove(path)
                return {"success": True, "output": f"Deleted {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def delete_dir(self, path: str, recursive: bool = True) -> Dict[str, Any]:
        """
        Deletes a directory (recursively by default).
        """
        return await self.delete_file(path, recursive=recursive)

    async def list_dir(self, path: str = ".") -> Dict[str, Any]:
        """
        Lists files and subdirectories at path.
        """
        try:
            if os.path.isdir(path):
                entries = sorted(os.listdir(path))
                return {
                    "success": True,
                    "output": "\n".join(entries),
                    "entries": entries,
                    "path": os.path.abspath(path),
                    "count": len(entries)
                }
            return {"success": False, "error": f"Path '{path}' is not a directory."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def search_grep(self, pattern: str, dir_path: str = ".") -> Dict[str, Any]:
        """
        Finds text patterns in workspace files.
        """
        try:
            results = []
            for root, _, files in os.walk(dir_path):
                if any(x in root for x in ['.git', '__pycache__', 'node_modules', 'venv', 'data', '.apex']):
                    continue
                for file in files:
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            for i, line in enumerate(f):
                                if re.search(pattern, line, re.IGNORECASE):
                                    results.append(f"{path}:L{i+1}: {line.strip()}")
                                    if len(results) >= 100:
                                        break
                    except Exception:
                        pass
                if len(results) >= 100:
                    break
            return {
                "success": True,
                "output": "\n".join(results) if results else "No matches found.",
                "matches_count": len(results)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def find_glob(self, pattern: str, dir_path: str = ".") -> Dict[str, Any]:
        """
        Finds files matching a glob pattern.
        """
        try:
            import glob
            search_pattern = os.path.join(dir_path, pattern) if not os.path.isabs(pattern) else pattern
            files = sorted(glob.glob(search_pattern, recursive=True))
            return {
                "success": True,
                "output": "\n".join(files) if files else "No matching files.",
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def exists(self, path: str) -> bool:
        """Checks if a file or directory exists."""
        return os.path.exists(path)

    def is_file(self, path: str) -> bool:
        """Checks if path is a regular file."""
        return os.path.isfile(path)

    def is_dir(self, path: str) -> bool:
        """Checks if path is a directory."""
        return os.path.isdir(path)

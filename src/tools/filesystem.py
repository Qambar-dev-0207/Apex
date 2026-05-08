import os
import json
from typing import Dict, Any, Optional
from rich.console import Console
from rich.prompt import Confirm
from src.tools.safety import SafetyGuard

class FilesystemAgent:
    """
    Handles file CRUD operations, enabling the agent to write code and modify the codebase.
    """
    def __init__(self, console: Optional[Console] = None, safety: Optional[SafetyGuard] = None):
        self.console = console or Console()
        self.safety = safety or SafetyGuard(console=self.console)

    async def write_file(self, path: str, content: str) -> Dict[str, Any]:
        try:
            # POLICY CHECK: Ask user before writing to filesystem
            authorized = await self.safety.check_filesystem("write", path, content)
            if not authorized:
                return {"success": False, "error": "Permission denied by user."}

            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "output": f"Successfully wrote to {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def read_file(self, path: str) -> Dict[str, Any]:
        try:
            ext = os.path.splitext(path)[1].lower()
            
            # Handle PDF
            if ext == ".pdf":
                from pypdf import PdfReader
                reader = PdfReader(path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return {"success": True, "output": text, "type": "pdf"}
            
            # Handle Images (Metadata only, content handled by Retina/ThinkingPath)
            if ext in [".png", ".jpg", ".jpeg", ".webp"]:
                return {"success": True, "output": f"Image file detected: {path}. APEX is loading visual buffers.", "type": "image", "path": os.path.abspath(path)}

            # Default: Text-based (MD, TXT, PY, etc.)
            with open(path, "r", encoding="utf-8") as f:
                return {"success": True, "output": f.read(), "type": "text"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def delete_file(self, path: str) -> Dict[str, Any]:
        try:
            # POLICY CHECK: Ask user before deleting from filesystem
            authorized = await self.safety.check_filesystem("delete", path)
            if not authorized:
                return {"success": False, "error": "Permission denied by user."}

            if os.path.exists(path):
                os.remove(path)
                return {"success": True, "output": f"Deleted {path}"}
            return {"success": False, "error": "File not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def list_dir(self, path: str = ".") -> Dict[str, Any]:
        try:
            if os.path.isdir(path):
                return {"success": True, "output": "\n".join(os.listdir(path))}
            return {"success": False, "error": f"Path '{path}' is not a directory."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def search_grep(self, pattern: str, dir_path: str = ".") -> Dict[str, Any]:
        """
        Mimics Gemini CLI's grep_search. Finds text patterns in files.
        """
        try:
            import re
            results = []
            for root, _, files in os.walk(dir_path):
                if any(x in root for x in ['.git', '__pycache__', 'node_modules', 'venv', 'data']): continue
                for file in files:
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            for i, line in enumerate(f):
                                if re.search(pattern, line, re.IGNORECASE):
                                    results.append(f"{path}:L{i+1}: {line.strip()}")
                                    if len(results) > 100: break # Safety limit
                    except: pass
            return {"success": True, "output": "\n".join(results) if results else "No matches found."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def find_glob(self, pattern: str, dir_path: str = ".") -> Dict[str, Any]:
        """
        Mimics Gemini CLI's glob. Finds files matching a pattern.
        """
        try:
            import glob
            files = glob.glob(os.path.join(dir_path, pattern), recursive=True)
            return {"success": True, "output": "\n".join(files)}
        except Exception as e:
            return {"success": False, "error": str(e)}

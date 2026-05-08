import asyncio
import os
import re
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from src.tools.web_search import WebSearchTool


class BaseResearchAgent(ABC):
    @abstractmethod
    async def research(self, query: str) -> Dict[str, Any]:
        pass


class WebResearcher(BaseResearchAgent):
    """
    Real web research via DuckDuckGo / Tavily / Brave.
    """
    def __init__(self):
        self.search = WebSearchTool()

    async def research(self, query: str) -> Dict[str, Any]:
        try:
            data = await self.search.asearch(query, max_results=5)
            results = data.get("results", []) or []
            findings = [f"{r.get('title','')}: {r.get('snippet','')}" for r in results if r.get("snippet")]
            return {
                "agent": "WebResearcher",
                "findings": findings or ["No web results."],
                "source": data.get("provider", "duckduckgo"),
                "urls": [r.get("url") for r in results if r.get("url")],
            }
        except Exception as e:
            return {"agent": "WebResearcher", "findings": [f"Web error: {e}"], "source": "error"}


class FileResearcher(BaseResearchAgent):
    """
    Greps the local workspace for relevant content.
    """
    def __init__(self, workspace_root: str = "."):
        self.root = workspace_root
        self.skip_dirs = {".git", "__pycache__", "node_modules", "venv", "data", "dist", "build", ".apex", ".venv"}
        self.text_exts = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".cpp", ".c", ".h", ".hpp", ".rb", ".swift", ".kt"}

    async def research(self, query: str) -> Dict[str, Any]:
        keywords = [w.lower() for w in re.findall(r"\w{3,}", query)]
        if not keywords:
            return {"agent": "FileResearcher", "findings": ["Query too short."], "source": "Local Workspace"}

        findings: List[str] = []
        loop = asyncio.get_running_loop()
        try:
            findings = await loop.run_in_executor(None, self._scan, keywords)
        except Exception as e:
            findings = [f"Scan error: {e}"]

        return {
            "agent": "FileResearcher",
            "findings": findings or ["No relevant files found."],
            "source": "Local Workspace",
        }

    def _scan(self, keywords: List[str]) -> List[str]:
        hits: List[str] = []
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext not in self.text_exts:
                    continue
                path = os.path.join(root, f)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        for i, line in enumerate(fh):
                            ll = line.lower()
                            if any(k in ll for k in keywords):
                                hits.append(f"{os.path.relpath(path, self.root)}:L{i+1}: {line.strip()[:160]}")
                                if len(hits) >= 30:
                                    return hits
                                break
                except Exception:
                    continue
        return hits


class CodeAnalyst(BaseResearchAgent):
    """
    Static analysis: counts symbol kinds and finds query-related definitions.
    """
    def __init__(self, workspace_root: str = "."):
        self.root = workspace_root
        self.skip_dirs = {".git", "__pycache__", "node_modules", "venv", "data", ".apex"}

    async def research(self, query: str) -> Dict[str, Any]:
        keywords = [w.lower() for w in re.findall(r"\w{3,}", query)]
        loop = asyncio.get_running_loop()
        try:
            stats = await loop.run_in_executor(None, self._analyze, keywords)
        except Exception as e:
            return {"agent": "CodeAnalyst", "findings": [f"Analysis error: {e}"], "source": "Static Analysis"}

        findings = [
            f"Python files: {stats['py_files']}",
            f"Classes: {stats['classes']}, Functions: {stats['functions']}, Async functions: {stats['async_functions']}",
        ]
        if stats["matches"]:
            findings.append("Query-related definitions:")
            findings.extend(stats["matches"][:10])
        return {"agent": "CodeAnalyst", "findings": findings, "source": "Static Analysis Engine"}

    def _analyze(self, keywords: List[str]) -> Dict[str, Any]:
        py_files = classes = functions = async_functions = 0
        matches: List[str] = []
        class_re = re.compile(r"^\s*class\s+(\w+)")
        def_re = re.compile(r"^\s*def\s+(\w+)")
        async_re = re.compile(r"^\s*async\s+def\s+(\w+)")
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            for f in files:
                if not f.endswith(".py"):
                    continue
                py_files += 1
                path = os.path.join(root, f)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        for i, line in enumerate(fh):
                            cm = class_re.match(line)
                            am = async_re.match(line)
                            dm = def_re.match(line)
                            name = None
                            if cm:
                                classes += 1
                                name = cm.group(1)
                            elif am:
                                async_functions += 1
                                name = am.group(1)
                            elif dm:
                                functions += 1
                                name = dm.group(1)
                            if name and any(k in name.lower() for k in keywords):
                                matches.append(f"{os.path.relpath(path, self.root)}:L{i+1}: {name}")
                except Exception:
                    continue
        return {
            "py_files": py_files,
            "classes": classes,
            "functions": functions,
            "async_functions": async_functions,
            "matches": matches,
        }

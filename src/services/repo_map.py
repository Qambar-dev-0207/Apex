import os
import re
import ast
import fnmatch
from typing import Dict, List, Any

class RepoMapGenerator:
    """
    Generates a token-efficient Repository Map of the codebase.
    Walks directories, extracts class and function signatures using AST (Python)
    or refined Regex patterns (other languages), and builds a nested outline.
    Enforces a strict token/character budget by degrading detail levels dynamically.
    """
    
    SUPPORTED_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".cs"}
    DEFAULT_SKIP = {".git", "__pycache__", "node_modules", "venv", ".venv", "data", "dist", "build", ".apex", "backups", "graphify-out"}

    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)

    def _load_ignore_patterns(self) -> List[str]:
        patterns: List[str] = []
        for fname in (".apexignore", ".gitignore"):
            path = os.path.join(self.root_dir, fname)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#"):
                                patterns.append(line)
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

    def scan_files(self) -> List[str]:
        """Walk directories, returning only supported and non-ignored files."""
        patterns = self._load_ignore_patterns()
        scanned: List[str] = []
        
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in self.DEFAULT_SKIP]
            
            # Check if directory itself is ignored
            rel_dir = os.path.relpath(root, self.root_dir)
            if rel_dir != "." and self._is_ignored(rel_dir, patterns):
                dirs[:] = []
                continue
                
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in self.SUPPORTED_EXT:
                    continue
                rel_path = os.path.relpath(os.path.join(root, file), self.root_dir)
                if self._is_ignored(rel_path, patterns):
                    continue
                scanned.append(rel_path)
                
        return sorted(scanned)

    def _extract_python(self, src: str) -> Dict[str, Any]:
        """Extract classes and functions using AST."""
        try:
            tree = ast.parse(src)
        except Exception as e:
            return {"classes": [], "functions": [], "error": str(e)}

        classes = []
        functions = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(self._py_method_sig(item))
                doc = ast.get_docstring(node) or ""
                classes.append({
                    "name": node.name,
                    "doc": doc.split("\n")[0][:100] if doc else "",
                    "methods": methods
                })
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(self._py_method_sig(node))

        return {"classes": classes, "functions": functions}

    def _py_method_sig(self, node) -> Dict[str, Any]:
        args = []
        for a in node.args.args:
            ann = ""
            if a.annotation is not None:
                try:
                    ann = ast.unparse(a.annotation)
                except Exception:
                    ann = "?"
            args.append(f"{a.arg}: {ann}" if ann else a.arg)
        ret = ""
        if node.returns is not None:
            try:
                ret = ast.unparse(node.returns)
            except Exception:
                ret = "?"
        prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        doc = ast.get_docstring(node) or ""
        return {
            "name": node.name,
            "signature": f"{prefix}def {node.name}({', '.join(args)}){' -> ' + ret if ret else ''}",
            "doc": doc.split("\n")[0][:100] if doc else ""
        }

    def _extract_regex(self, src: str, ext: str) -> Dict[str, Any]:
        """Fall back to regex for non-Python source files."""
        funcs = []
        classes = []

        if ext in {".js", ".ts", ".tsx", ".jsx"}:
            for m in re.finditer(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)", src, re.MULTILINE):
                funcs.append({"name": m.group(1), "signature": f"function {m.group(1)}({m.group(2).strip()})", "doc": ""})
            for m in re.finditer(r"^\s*(?:export\s+)?class\s+(\w+)", src, re.MULTILINE):
                classes.append({"name": m.group(1), "doc": "", "methods": []})
            for m in re.finditer(r"^\s*(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>", src, re.MULTILINE):
                funcs.append({"name": m.group(1), "signature": f"const {m.group(1)} = ({m.group(2).strip()}) => ...", "doc": ""})
        elif ext == ".go":
            for m in re.finditer(r"^func\s+(?:\(\s*\w+\s+\*?\w+\s*\)\s+)?(\w+)\s*\(([^)]*)\)", src, re.MULTILINE):
                funcs.append({"name": m.group(1), "signature": f"func {m.group(1)}({m.group(2).strip()})", "doc": ""})
            for m in re.finditer(r"^type\s+(\w+)\s+struct", src, re.MULTILINE):
                classes.append({"name": m.group(1), "doc": "", "methods": []})
        elif ext == ".rs":
            for m in re.finditer(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\(([^)]*)\)", src, re.MULTILINE):
                funcs.append({"name": m.group(1), "signature": f"fn {m.group(1)}({m.group(2).strip()})", "doc": ""})
            for m in re.finditer(r"^\s*(?:pub\s+)?struct\s+(\w+)", src, re.MULTILINE):
                classes.append({"name": m.group(1), "doc": "", "methods": []})
        elif ext in {".java", ".cs"}:
            for m in re.finditer(r"^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:[\w<>\[\]]+\s+)?(\w+)\s*\(([^)]*)\)\s*\{", src, re.MULTILINE):
                funcs.append({"name": m.group(1), "signature": f"{m.group(1)}({m.group(2).strip()})", "doc": ""})
            for m in re.finditer(r"^\s*(?:public\s+)?class\s+(\w+)", src, re.MULTILINE):
                classes.append({"name": m.group(1), "doc": "", "methods": []})
        elif ext in {".c", ".cpp", ".h"}:
            for m in re.finditer(r"^\s*(?:[\w\*]+\s+)+(\w+)\s*\(([^)]*)\)\s*(?:;|\{)", src, re.MULTILINE):
                funcs.append({"name": m.group(1), "signature": f"{m.group(1)}({m.group(2).strip()})", "doc": ""})

        return {"classes": classes, "functions": funcs}

    def parse_file(self, rel_path: str) -> Dict[str, Any]:
        """Read and parse a single file's symbols."""
        abs_path = os.path.join(self.root_dir, rel_path)
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                src = f.read()
        except Exception as e:
            return {"classes": [], "functions": [], "error": str(e)}

        ext = os.path.splitext(rel_path)[1].lower()
        if ext == ".py":
            return self._extract_python(src)
        else:
            return self._extract_regex(src, ext)

    def _render_tree(self, files_data: Dict[str, Any], level: int, include_docs: bool = True) -> str:
        """
        Renders the gathered files and symbols into a text tree.
        Level 1: Only files and directories.
        Level 2: + Class and top-level function names (no signatures/docstrings).
        Level 3: + Class methods and full signatures, function signatures, docstrings.
        """
        lines = []
        
        # Build folder structure
        tree = {}
        for path in files_data.keys():
            parts = path.split(os.sep)
            curr = tree
            for part in parts:
                curr = curr.setdefault(part, {})
                
        def walk_render(node, path_parts, depth=0):
            indent = "  " * depth
            for name, children in sorted(node.items()):
                curr_parts = path_parts + [name]
                rel_path = os.sep.join(curr_parts)
                
                if children:
                    lines.append(f"{indent}{name}/")
                    walk_render(children, curr_parts, depth + 1)
                else:
                    lines.append(f"{indent}{name}")
                    if rel_path in files_data:
                        data = files_data[rel_path]
                        if level >= 2:
                            sym_indent = "  " * (depth + 1)
                            for cls in data.get("classes", []):
                                doc_str = f" # {cls['doc']}" if include_docs and cls.get("doc") else ""
                                lines.append(f"{sym_indent}class {cls['name']}{doc_str}")
                                if level == 3:
                                    method_indent = "  " * (depth + 2)
                                    for m in cls.get("methods", []):
                                        m_doc = f" # {m['doc']}" if include_docs and m.get("doc") else ""
                                        lines.append(f"{method_indent}{m['signature']}{m_doc}")
                            for fn in data.get("functions", []):
                                if level == 3:
                                    fn_doc = f" # {fn['doc']}" if include_docs and fn.get("doc") else ""
                                    lines.append(f"{sym_indent}{fn['signature']}{fn_doc}")
                                else:
                                    lines.append(f"{sym_indent}def {fn['name']}")
                                    
        walk_render(tree, [])
        return "\n".join(lines)

    def generate_map(self, level: int = 3, max_chars: int = 6000) -> str:
        """
        Generates the repository map, ensuring it stays under the max_chars budget.
        Degrades gracefully down to level 1 and truncates if necessary.
        """
        files = self.scan_files()
        files_data = {}
        for f in files:
            files_data[f] = self.parse_file(f)

        # Attempt 1: Full Level 3 with Docs
        if level >= 3:
            rendered = self._render_tree(files_data, level=3, include_docs=True)
            if len(rendered) <= max_chars:
                return rendered
                
            # Attempt 2: Level 3 without docstrings
            rendered = self._render_tree(files_data, level=3, include_docs=False)
            if len(rendered) <= max_chars:
                return rendered

        # Attempt 3: Level 2 (symbol names only)
        if level >= 2:
            rendered = self._render_tree(files_data, level=2, include_docs=False)
            if len(rendered) <= max_chars:
                return rendered

        # Attempt 4: Level 1 (Directories/files only)
        rendered = self._render_tree(files_data, level=1, include_docs=False)
        if len(rendered) <= max_chars:
            return rendered

        # Fallback: Truncate lines of Level 1 to fit budget
        lines = rendered.splitlines()
        truncated_lines = []
        current_len = 0
        for line in lines:
            if current_len + len(line) + 1 > max_chars - 30:
                truncated_lines.append("... (truncated to fit token budget)")
                break
            truncated_lines.append(line)
            current_len += len(line) + 1
            
        return "\n".join(truncated_lines)

    def save_map(self, level: int = 3, max_chars: int = 6000, output_path: str = None) -> str:
        """Generates the map, saves it to output_path, and returns it."""
        if output_path is None:
            output_path = os.path.join(self.root_dir, ".apex", "repo_map.txt")
            
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        repo_map = self.generate_map(level=level, max_chars=max_chars)
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(repo_map)
        except Exception:
            pass
            
        return repo_map

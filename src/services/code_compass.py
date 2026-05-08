import os
import re
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional


class CodeCompass:
    """
    Token-efficient codebase analyzer.

    Instead of feeding raw source files to the LLM (~40k tokens per medium codebase),
    builds a compressed symbol map that captures:
      - imports (deps signal)
      - class names + signatures
      - function names + arg signatures + 1-line docstring summary
      - LoC, hash for cache invalidation

    Typical compression: 5-12% of original size (i.e., 8-20x token savings).
    Persisted to .apex/code_compass.json with hash-keyed cache so unchanged files
    skip re-parsing.
    """

    SUPPORTED_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"}
    SKIP_DIRS = {".git", "__pycache__", "node_modules", "venv", ".venv", "data", "dist", "build", ".apex", "backups"}

    def __init__(self, root: str = ".", cache_path: Optional[str] = None):
        self.root = os.path.abspath(root)
        self.cache_path = cache_path or os.path.join(self.root, ".apex", "code_compass.json")
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        self.index: Dict[str, Any] = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_path):
            try:
                return json.loads(Path(self.cache_path).read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_cache(self):
        try:
            Path(self.cache_path).write_text(json.dumps(self.index, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _hash(self, content: str) -> str:
        return hashlib.sha1(content.encode("utf-8", errors="ignore")).hexdigest()[:12]

    def _extract_python(self, src: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(src)
        except Exception as e:
            return {"error": f"parse_failed: {e}"}

        imports: List[str] = []
        classes: List[Dict[str, Any]] = []
        functions: List[Dict[str, Any]] = []

        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                imports.extend(f"{mod}.{a.name}" for a in node.names)
            elif isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        sig = self._py_signature(item)
                        methods.append(sig)
                doc = ast.get_docstring(node) or ""
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "doc": doc.split("\n")[0][:120] if doc else "",
                    "methods": methods,
                })
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(self._py_signature(node))

        return {"imports": imports, "classes": classes, "functions": functions}

    def _py_signature(self, node) -> Dict[str, Any]:
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
        doc = ast.get_docstring(node) or ""
        prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        return {
            "name": node.name,
            "line": node.lineno,
            "signature": f"{prefix}def {node.name}({', '.join(args)}){' -> ' + ret if ret else ''}",
            "doc": doc.split("\n")[0][:120] if doc else "",
        }

    def _extract_generic(self, src: str, ext: str) -> Dict[str, Any]:
        # Cheap symbol extraction for non-Python files
        funcs = []
        classes = []

        if ext in {".js", ".ts", ".tsx", ".jsx"}:
            for m in re.finditer(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)", src, re.MULTILINE):
                funcs.append({"name": m.group(1), "signature": f"function {m.group(1)}({m.group(2)})"})
            for m in re.finditer(r"^\s*(?:export\s+)?class\s+(\w+)", src, re.MULTILINE):
                classes.append({"name": m.group(1), "methods": []})
            for m in re.finditer(r"^\s*(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\(", src, re.MULTILINE):
                funcs.append({"name": m.group(1), "signature": f"const {m.group(1)} = (...)"})
        elif ext == ".go":
            for m in re.finditer(r"^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(([^)]*)\)", src, re.MULTILINE):
                funcs.append({"name": m.group(1), "signature": f"func {m.group(1)}({m.group(2)})"})
            for m in re.finditer(r"^type\s+(\w+)\s+struct", src, re.MULTILINE):
                classes.append({"name": m.group(1), "methods": []})
        elif ext == ".rs":
            for m in re.finditer(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\(([^)]*)\)", src, re.MULTILINE):
                funcs.append({"name": m.group(1), "signature": f"fn {m.group(1)}({m.group(2)})"})
            for m in re.finditer(r"^\s*(?:pub\s+)?struct\s+(\w+)", src, re.MULTILINE):
                classes.append({"name": m.group(1), "methods": []})
        elif ext == ".java":
            for m in re.finditer(r"^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:[\w<>\[\]]+\s+)?(\w+)\s*\(([^)]*)\)\s*\{", src, re.MULTILINE):
                funcs.append({"name": m.group(1), "signature": f"{m.group(1)}({m.group(2)})"})
            for m in re.finditer(r"^\s*(?:public\s+)?class\s+(\w+)", src, re.MULTILINE):
                classes.append({"name": m.group(1), "methods": []})

        return {"imports": [], "classes": classes, "functions": funcs}

    def index_file(self, path: str) -> Optional[Dict[str, Any]]:
        rel = os.path.relpath(path, self.root)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                src = f.read()
        except Exception:
            return None

        h = self._hash(src)
        cached = self.index.get(rel)
        if cached and cached.get("hash") == h:
            return cached

        ext = os.path.splitext(path)[1].lower()
        if ext == ".py":
            data = self._extract_python(src)
        else:
            data = self._extract_generic(src, ext)

        entry = {
            "hash": h,
            "loc": src.count("\n") + 1,
            "size": len(src),
            **data,
        }
        self.index[rel] = entry
        return entry

    def build(self) -> Dict[str, Any]:
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext not in self.SUPPORTED_EXT:
                    continue
                self.index_file(os.path.join(root, f))
        # Drop entries for files that no longer exist
        present = set()
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in self.SUPPORTED_EXT:
                    present.add(os.path.relpath(os.path.join(root, f), self.root))
        self.index = {k: v for k, v in self.index.items() if k in present}
        self._save_cache()
        return self.index

    def query(self, term: str, limit: int = 25) -> List[Dict[str, Any]]:
        term_lower = term.lower()
        hits: List[Dict[str, Any]] = []
        for rel, data in self.index.items():
            for cls in data.get("classes", []):
                if term_lower in cls["name"].lower():
                    hits.append({"file": rel, "kind": "class", "name": cls["name"], "line": cls.get("line")})
            for fn in data.get("functions", []):
                if term_lower in fn["name"].lower():
                    hits.append({"file": rel, "kind": "function", "name": fn["name"], "line": fn.get("line"), "sig": fn.get("signature")})
            if term_lower in rel.lower():
                hits.append({"file": rel, "kind": "file"})
            if len(hits) >= limit:
                break
        return hits[:limit]

    def summary(self) -> Dict[str, Any]:
        files = len(self.index)
        classes = sum(len(v.get("classes", [])) for v in self.index.values())
        functions = sum(len(v.get("functions", [])) for v in self.index.values())
        loc = sum(v.get("loc", 0) for v in self.index.values())
        compressed_size = len(json.dumps(self.index))
        raw_size = sum(v.get("size", 0) for v in self.index.values())
        ratio = compressed_size / raw_size if raw_size else 0
        return {
            "files": files,
            "classes": classes,
            "functions": functions,
            "lines_of_code": loc,
            "raw_bytes": raw_size,
            "compressed_bytes": compressed_size,
            "compression_ratio": round(ratio, 3),
            "approx_token_savings": max(0, (raw_size - compressed_size) // 4),
        }

    def context_for_query(self, term: str, max_files: int = 5) -> str:
        """Returns a compact text block for LLM context — way smaller than raw file reads."""
        hits = self.query(term, limit=max_files * 4)
        seen_files: List[str] = []
        for h in hits:
            if h["file"] not in seen_files:
                seen_files.append(h["file"])
            if len(seen_files) >= max_files:
                break
        out = []
        for rel in seen_files:
            data = self.index.get(rel, {})
            lines = [f"=== {rel} (loc={data.get('loc')}) ==="]
            for cls in data.get("classes", [])[:8]:
                lines.append(f"  class {cls['name']}: {cls.get('doc', '')}".rstrip(": ").rstrip())
                for m in cls.get("methods", [])[:6]:
                    lines.append(f"    {m['signature']}")
            for fn in data.get("functions", [])[:10]:
                lines.append(f"  {fn['signature']}")
            out.append("\n".join(lines))
        return "\n\n".join(out)

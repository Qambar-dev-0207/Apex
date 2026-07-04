import os
import hashlib
import json
import time
import asyncio
from typing import Dict, List, Any, Optional
from src.services.memory import MemoryManager
from src.tools.workspace import WorkspaceManager

class CodebaseIndexer:
    """
    Manages codebase chunking, embedding generation, and vector search.
    Stores chunks in the ChromaDB collection `apex_code_index` and performs
    incremental updates using file hashes in `.apex/code_index_hashes.json`.
    """

    def __init__(self, memory_manager: MemoryManager, workspace: WorkspaceManager):
        self.memory = memory_manager
        self.workspace = workspace
        self.collection_name = "apex_code_index"
        
        # Share the exact same client and embedding function to avoid duplicate model loads and SQLite locks
        self.client = self.memory.chroma.client
        self.ef = self.memory.chroma.ef
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name, embedding_function=self.ef
        )

    def _get_project_paths(self) -> tuple[str, str]:
        """Returns (root_dir, cache_path) for the active project."""
        active = self.workspace.get_active()
        root_dir = active.root_dir if active else os.getcwd()
        cache_path = os.path.join(root_dir, ".apex", "code_index_hashes.json")
        return root_dir, cache_path

    def _load_cache(self, cache_path: str) -> Dict[str, Any]:
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"files": {}}

    def _save_cache(self, cache_path: str, data: Dict[str, Any]):
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha1(content.encode("utf-8", errors="ignore")).hexdigest()

    def chunk_file(self, rel_path: str, content: str, max_chars: int = 800, overlap_lines: int = 3) -> List[Dict[str, Any]]:
        """
        Chunks file content into blocks of max_chars, ensuring embedding safety.
        Prepend metadata context to improve search matching.
        """
        lines = content.splitlines()
        chunks = []
        
        if not lines:
            return []

        file_hash = self._compute_hash(content)
        i = 0
        chunk_idx = 0
        
        while i < len(lines):
            # Pre-calculate baseline headers
            header = f"File: {rel_path} (Lines {i+1}-{{end_placeholder}})\n--------------------------------------------------\n"
            current_chunk_lines = []
            current_len = len(header)  # Start character budget
            
            # Pack lines
            j = i
            while j < len(lines):
                line_text = lines[j] + "\n"
                # If single line itself exceeds character limit, we must break it or just add it
                if current_len + len(line_text) > max_chars and current_chunk_lines:
                    break
                current_chunk_lines.append(lines[j])
                current_len += len(line_text)
                j += 1
                
            end_line = j
            start_line = i + 1
            
            # Format chunk content
            formatted_header = header.format(end_placeholder=end_line)
            chunk_content = formatted_header + "\n".join(current_chunk_lines)
            
            chunk_id = f"{rel_path}#chunk_{chunk_idx}"
            chunks.append({
                "id": chunk_id,
                "content": chunk_content,
                "metadata": {
                    "path": rel_path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "file_hash": file_hash,
                    "type": "code_chunk"
                }
            })
            
            chunk_idx += 1
            
            # Advance index. If j is at the end, we break. Otherwise, apply overlap.
            if j >= len(lines):
                break
            else:
                # Deduct overlap lines, but ensure we progress by at least 1 line
                i = max(i + 1, j - overlap_lines)

        return chunks

    async def index_codebase(self, rebuild: bool = False) -> Dict[str, Any]:
        """
        Runs incremental indexing on the active codebase.
        If rebuild=True, resets the database collection first.
        """
        root_dir, cache_path = self._get_project_paths()
        
        if rebuild:
            await asyncio.to_thread(self.client.delete_collection, self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name, embedding_function=self.ef
            )
            cache = {"files": {}}
        else:
            cache = self._load_cache(cache_path)

        active = self.workspace.get_active()
        if not active:
            return {"error": "No active project in workspace."}

        # Sync/get current file tree from WorkspaceManager
        file_tree = await asyncio.to_thread(self.workspace.scan_local_files, active.name)
        
        # Supported formats (same as RepoMapGenerator)
        supported_exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".cs"}
        
        scanned_files = [f for f in file_tree if os.path.splitext(f)[1].lower() in supported_exts]
        
        stats = {
            "scanned": len(scanned_files),
            "skipped": 0,
            "indexed": 0,
            "chunks_added": 0,
            "chunks_deleted": 0
        }

        # 1. Purge deleted files
        present_set = set(scanned_files)
        cached_files = list(cache.get("files", {}).keys())
        for rel_path in cached_files:
            if rel_path not in present_set:
                file_entry = cache["files"].pop(rel_path)
                chunk_ids = file_entry.get("chunk_ids", [])
                if chunk_ids:
                    try:
                        await asyncio.to_thread(self.collection.delete, ids=chunk_ids)
                        stats["chunks_deleted"] += len(chunk_ids)
                    except Exception:
                        pass

        # 2. Add or update modified files
        for rel_path in scanned_files:
            abs_path = os.path.join(root_dir, rel_path)
            if not os.path.exists(abs_path):
                continue
                
            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            current_hash = self._compute_hash(content)
            cached_entry = cache["files"].get(rel_path)
            
            if cached_entry and cached_entry.get("hash") == current_hash:
                stats["skipped"] += 1
                continue

            # Modified or new file: purge old chunks first
            if cached_entry:
                old_chunk_ids = cached_entry.get("chunk_ids", [])
                if old_chunk_ids:
                    try:
                        await asyncio.to_thread(self.collection.delete, ids=old_chunk_ids)
                        stats["chunks_deleted"] += len(old_chunk_ids)
                    except Exception:
                        pass

            # Generate new chunks
            new_chunks = self.chunk_file(rel_path, content)
            if new_chunks:
                ids = [c["id"] for c in new_chunks]
                docs = [c["content"] for c in new_chunks]
                metas = [c["metadata"] for c in new_chunks]
                
                # Write to ChromaDB
                try:
                    await asyncio.to_thread(
                        self.collection.add,
                        ids=ids,
                        documents=docs,
                        metadatas=metas
                    )
                    stats["chunks_added"] += len(new_chunks)
                    stats["indexed"] += 1
                    
                    # Update cache
                    cache["files"][rel_path] = {
                        "hash": current_hash,
                        "chunk_ids": ids
                    }
                except Exception:
                    pass
            else:
                # Empty file
                cache["files"][rel_path] = {
                    "hash": current_hash,
                    "chunk_ids": []
                }

        self._save_cache(cache_path, cache)
        return stats

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Queries the codebase index for matching code chunks."""
        try:
            results = await asyncio.to_thread(
                self.collection.query,
                query_texts=[query],
                n_results=limit
            )
        except Exception:
            return []

        if not results.get("documents") or not results["documents"][0]:
            return []

        formatted = []
        for i in range(len(results["documents"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                "distance": results["distances"][0][i] if results.get("distances") else None
            })
            
        return formatted

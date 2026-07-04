import json
from typing import Dict, Any

class CodebaseIndexTool:
    """
    CodebaseIndexTool wraps CodebaseIndexer for use in agent plans.
    Exposes codebase search capabilities to the LLM agent.
    """

    def __init__(self, indexer=None):
        self.indexer = indexer

    async def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        if not self.indexer:
            return {"success": False, "error": "Codebase indexer service is not wired."}

        if not query or not query.strip():
            return {"success": False, "error": "Query string is empty."}

        try:
            hits = await self.indexer.search(query, limit=limit)
            if not hits:
                return {"success": True, "output": "No matching code snippets found in the vector index."}

            output_lines = []
            for hit in hits:
                meta = hit.get("metadata", {})
                output_lines.append(
                    f"=== {meta.get('path')} (Lines {meta.get('start_line')}-{meta.get('end_line')}, Distance: {hit.get('distance', 0.0):.4f}) ===\n"
                    f"{hit.get('content')}\n"
                )
            return {
                "success": True,
                "output": "\n".join(output_lines),
                "hits": hits
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to search codebase index: {e}"}

    async def index(self, rebuild: bool = False) -> Dict[str, Any]:
        if not self.indexer:
            return {"success": False, "error": "Codebase indexer service is not wired."}

        try:
            stats = await self.indexer.index_codebase(rebuild=rebuild)
            return {
                "success": True,
                "output": f"Codebase indexing completed: {json.dumps(stats)}",
                "stats": stats
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to index codebase: {e}"}

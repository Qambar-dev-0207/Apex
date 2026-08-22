import sys
import os
import unittest
import tempfile
import shutil
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import codebase services and models
from src.services.repo_map import RepoMapGenerator
from src.services.codebase_index import CodebaseIndexer
from src.services.memory import MemoryManager
from src.tools.workspace import WorkspaceManager


class TestCodebaseIndexAndRepoMap(unittest.TestCase):

    def setUp(self):
        # Create a temp directory for mock project structure
        self.test_dir = tempfile.mkdtemp()
        self.root_path = os.path.abspath(self.test_dir)
        
        # Write dummy files
        self.py_file_content = """# Mock python file
import os

class DatabaseConnector:
    \"\"\"Manages database connections.\"\"\"
    def __init__(self, dsn: str):
        self.dsn = dsn

    async def connect(self) -> bool:
        return True

def standalone_func(x: int, y: int) -> int:
    \"\"\"Adds two numbers.\"\"\"
    return x + y
"""
        
        self.js_file_content = """// Mock JS file
class ApiClient {
  constructor() {
    this.endpoint = "/api";
  }
}

async function fetchData(url) {
  return fetch(url);
}
"""
        
        # Write files
        os.makedirs(os.path.join(self.root_path, "src", "db"), exist_ok=True)
        self.py_path = os.path.join(self.root_path, "src", "db", "connector.py")
        with open(self.py_path, "w", encoding="utf-8") as f:
            f.write(self.py_file_content)

        os.makedirs(os.path.join(self.root_path, "web"), exist_ok=True)
        self.js_path = os.path.join(self.root_path, "web", "api.js")
        with open(self.js_path, "w", encoding="utf-8") as f:
            f.write(self.js_file_content)

        # Create mock objects
        self.mock_memory = MagicMock(spec=MemoryManager)
        self.mock_chroma_mgr = MagicMock()
        self.mock_collection = MagicMock()
        
        # Wire mock client and collection
        self.mock_memory.chroma = self.mock_chroma_mgr
        self.mock_chroma_mgr.client = MagicMock()
        self.mock_chroma_mgr.ef = MagicMock()
        self.mock_chroma_mgr.client.get_or_create_collection.return_value = self.mock_collection
        
        self.mock_workspace = MagicMock(spec=WorkspaceManager)
        self.mock_active_proj = MagicMock()
        self.mock_active_proj.name = "TestProject"
        self.mock_active_proj.root_dir = self.root_path
        # Return our files relative to root_path as file tree
        self.mock_active_proj.file_tree = [
            os.path.join("src", "db", "connector.py"),
            os.path.join("web", "api.js")
        ]
        self.mock_workspace.get_active.return_value = self.mock_active_proj
        self.mock_workspace.scan_local_files.return_value = self.mock_active_proj.file_tree

    def tearDown(self):
        # Clean up temp directory
        shutil.rmtree(self.test_dir)

    # ════════════════════════════════════════════════════════════════════════════
    # 1. Chunker and Size Limits Tests
    # ════════════════════════════════════════════════════════════════════════════

    def test_chunk_file_respects_max_chars(self):
        indexer = CodebaseIndexer(self.mock_memory, self.mock_workspace)
        long_content = "\n".join([f"line {i:04d}: dummy content that is fairly long" for i in range(100)])
        
        # Max chars is 400. Prepend header context, check chunk sizes.
        chunks = indexer.chunk_file("test.py", long_content, max_chars=400, overlap_lines=2)
        
        self.assertTrue(len(chunks) > 1)
        for c in chunks:
            self.assertTrue(len(c["content"]) <= 400)
            self.assertIn("File: test.py", c["content"])
            self.assertEqual(c["metadata"]["path"], "test.py")
            self.assertEqual(c["metadata"]["type"], "code_chunk")

    def test_chunk_file_overlap_math(self):
        indexer = CodebaseIndexer(self.mock_memory, self.mock_workspace)
        content = "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10"
        
        # Force tiny max_chars so it splits line-by-line or in pairs
        chunks = indexer.chunk_file("test.py", content, max_chars=120, overlap_lines=2)
        
        self.assertTrue(len(chunks) > 1)
        # Check that overlap lines appear in consecutive chunks
        first_chunk_lines = chunks[0]["content"].splitlines()
        second_chunk_lines = chunks[1]["content"].splitlines()
        
        # Overlap of 2 lines should mean the last lines of chunk 1 are the start lines of chunk 2
        last_of_first = first_chunk_lines[-1]
        self.assertIn(last_of_first, chunks[1]["content"])

    # ════════════════════════════════════════════════════════════════════════════
    # 2. Repository Mapping Tests
    # ════════════════════════════════════════════════════════════════════════════

    def test_repo_map_parsing_python_ast(self):
        generator = RepoMapGenerator(root_dir=self.root_path)
        rel_py_path = os.path.join("src", "db", "connector.py")
        
        parsed = generator.parse_file(rel_py_path)
        self.assertEqual(len(parsed["classes"]), 1)
        self.assertEqual(parsed["classes"][0]["name"], "DatabaseConnector")
        self.assertEqual(parsed["classes"][0]["doc"], "Manages database connections.")
        self.assertEqual(len(parsed["classes"][0]["methods"]), 2)
        self.assertEqual(parsed["classes"][0]["methods"][0]["name"], "__init__")
        self.assertEqual(parsed["classes"][0]["methods"][1]["name"], "connect")
        
        self.assertEqual(len(parsed["functions"]), 1)
        self.assertEqual(parsed["functions"][0]["name"], "standalone_func")

    def test_repo_map_parsing_js_regex(self):
        generator = RepoMapGenerator(root_dir=self.root_path)
        rel_js_path = os.path.join("web", "api.js")
        
        parsed = generator.parse_file(rel_js_path)
        self.assertEqual(len(parsed["classes"]), 1)
        self.assertEqual(parsed["classes"][0]["name"], "ApiClient")
        self.assertEqual(len(parsed["functions"]), 1)
        self.assertEqual(parsed["functions"][0]["name"], "fetchData")

    def test_repo_map_token_budget_degradation(self):
        generator = RepoMapGenerator(root_dir=self.root_path)
        
        # Test full map level 3
        full_map = generator.generate_map(level=3, max_chars=10000)
        self.assertIn("class DatabaseConnector", full_map)
        self.assertIn("def connect(self)", full_map)
        self.assertIn("Manages database connections.", full_map)
        self.assertIn("ApiClient", full_map)
        self.assertIn("fetchData", full_map)

        # Test degraded map with tiny character limit (forces Level 2 or Level 1)
        degraded_map = generator.generate_map(level=3, max_chars=200)
        # Should drop docstrings, method signatures, or even symbols to fit in 200 chars
        self.assertTrue(len(degraded_map) <= 200)

    # ════════════════════════════════════════════════════════════════════════════
    # 3. Incremental Indexing & Hash-Skip Logic
    # ════════════════════════════════════════════════════════════════════════════

    @patch("asyncio.to_thread")
    def test_incremental_index_skips_unchanged(self, mock_to_thread):
        mock_to_thread.side_effect = lambda f, *args, **kwargs: f(*args, **kwargs)
        
        indexer = CodebaseIndexer(self.mock_memory, self.mock_workspace)
        
        # First index run: should add documents
        stats1 = asyncio.run(indexer.index_codebase(rebuild=True))
        self.assertEqual(stats1["scanned"], 2)
        self.assertEqual(stats1["indexed"], 2)
        self.assertTrue(stats1["chunks_added"] > 0)
        
        # Verify collection.add was called
        self.assertTrue(self.mock_collection.add.called)
        self.mock_collection.add.reset_mock()
        
        # Second run: files are unchanged, should skip indexing
        stats2 = asyncio.run(indexer.index_codebase(rebuild=False))
        self.assertEqual(stats2["scanned"], 2)
        self.assertEqual(stats2["skipped"], 2)
        self.assertEqual(stats2["indexed"], 0)
        self.assertEqual(stats2["chunks_added"], 0)
        self.assertFalse(self.mock_collection.add.called)

    @patch("asyncio.to_thread")
    def test_incremental_index_updates_modified_and_deletes_removed(self, mock_to_thread):
        mock_to_thread.side_effect = lambda f, *args, **kwargs: f(*args, **kwargs)
        
        indexer = CodebaseIndexer(self.mock_memory, self.mock_workspace)
        
        # First index run
        asyncio.run(indexer.index_codebase(rebuild=True))
        self.mock_collection.delete.reset_mock()
        self.mock_collection.add.reset_mock()
        
        # 1. Modify a file
        with open(self.py_path, "w", encoding="utf-8") as f:
            f.write(self.py_file_content + "\n# Added comments for hash trigger")
            
        # 2. Delete a file (we will update file_tree to simulate file deletion)
        os.remove(self.js_path)
        self.mock_active_proj.file_tree = [
            os.path.join("src", "db", "connector.py")
        ]
        self.mock_workspace.scan_local_files.return_value = self.mock_active_proj.file_tree
        
        stats = asyncio.run(indexer.index_codebase(rebuild=False))
        
        # Scanned files is now 1 (connector.py)
        self.assertEqual(stats["scanned"], 1)
        # connector.py is modified, so it should be indexed
        self.assertEqual(stats["indexed"], 1)
        # chunks_deleted should reflect old chunks from connector.py AND api.js
        self.assertTrue(stats["chunks_deleted"] > 0)
        self.assertTrue(self.mock_collection.delete.called)


if __name__ == "__main__":
    unittest.main()

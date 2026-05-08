import asyncio
import os
import sys
import unittest
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.filesystem import FilesystemAgent

class TestGeminiTechnique(unittest.TestCase):
    def setUp(self):
        self.fs = FilesystemAgent()

    async def test_grep_search(self):
        # Search for 'APEX' in the current project
        res = await self.fs.search_grep("APEX", dir_path=".")
        self.assertTrue(res['success'])
        self.assertIn("L", res['output']) # Line number indicator
        print(f"[green]✓ Grep Search verified. Matches: {len(res['output'].splitlines())}[/green]")

    async def test_find_glob(self):
        # Find all python files
        res = await self.fs.find_glob("**/*.py", dir_path="src")
        self.assertTrue(res['success'])
        self.assertIn(".py", res['output'])
        print(f"[green]✓ Glob verified. Python files found in src: {len(res['output'].splitlines())}[/green]")

    def test_all(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.test_grep_search())
            loop.run_until_complete(self.test_find_glob())
        finally:
            loop.close()

if __name__ == "__main__":
    unittest.main()

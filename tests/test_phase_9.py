import asyncio
import sys
import os
import unittest
from unittest.mock import patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.workspace import WorkspaceManager
from src.tools.git_agent import GitAgent
from src.services.memory import MemoryManager
from src.models.thinking_path import GeminiClient

class TestPhase9(unittest.TestCase):
    def setUp(self):
        self.workspace = WorkspaceManager(storage_path="data/test_workspace.json")
        self.git = GitAgent(working_dir=".")

    def tearDown(self):
        if os.path.exists("data/test_workspace.json"):
            os.remove("data/test_workspace.json")

    def test_workspace_management(self):
        self.workspace.create_project("TestProj", "Test Desc", ".", ["Goal 1"])
        active = self.workspace.get_active()
        self.assertIsNotNone(active)
        self.assertEqual(active.name, "TestProj")
        
        self.workspace.add_todo("TestProj", "Task 1")
        self.assertEqual(len(self.workspace.projects["TestProj"].todos), 1)

    @patch('subprocess.run')
    def test_git_agent(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "On branch main"
        
        res = self.git.status()
        self.assertTrue(res['success'])
        self.assertIn("On branch main", res['output'])

    @patch('google.genai.Client')
    def test_socratic_mode_toggle(self, mock_client):
        client = GeminiClient()
        self.assertFalse(client.socratic_mode)
        client.socratic_mode = True
        self.assertTrue(client.socratic_mode)

    @patch('src.services.memory.RedisManager')
    @patch('src.services.memory.ChromaManager')
    @patch('google.genai.Client')
    def test_relational_memory(self, mock_genai, mock_chroma, mock_redis):
        memory = MemoryManager()
        
        # Use AsyncMock for async methods
        from unittest.mock import AsyncMock
        memory.redis.load_session = AsyncMock(return_value=None)
        memory.redis.save_session = AsyncMock()
        memory.chroma.search_memories = AsyncMock(return_value=[
            {"id": "uuid-1", "content": "Initial fact", "metadata": {"related_ids": ""}}
        ])
        memory.chroma.add_memory = AsyncMock()
        
        # Run test
        asyncio.run(memory.store_interaction("sid", "New info", "Resp"))
        
        # Verify chroma was called with related_ids="uuid-1"
        memory.chroma.add_memory.assert_called()
        args, kwargs = memory.chroma.add_memory.call_args
        self.assertEqual(kwargs['metadata']['related_ids'], "uuid-1")

if __name__ == '__main__':
    unittest.main()

import unittest
import sys
import os
import json
import asyncio
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.learning import LearningManager, FailureLogger, SkillManager
from src.core.models import Skill, ExecutionPlan, TaskStep, MemoryEntry
from src.services.memory import MemoryManager

class TestLearningSystem(unittest.TestCase):
    def setUp(self):
        # Mock ChromaDB
        self.patcher_chroma = patch('chromadb.PersistentClient')
        self.mock_chroma = self.patcher_chroma.start()
        
        # Mock MemoryManager
        self.mock_memory = MagicMock(spec=MemoryManager)
        
    def tearDown(self):
        self.patcher_chroma.stop()
        if os.path.exists("data/test_failures.json"):
            os.remove("data/test_failures.json")

    def test_failure_logger(self):
        logger = FailureLogger(file_path="data/test_failures.json")
        logger.log("test_tool", "input", "error message", "sid")
        
        with open("data/test_failures.json", "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['tool'], "test_tool")
            self.assertEqual(data[0]['error'], "error message")

    def test_skill_manager_matching(self):
        # Mock collection query
        mock_collection = MagicMock()
        self.mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
        
        mgr = SkillManager()
        
        plan = ExecutionPlan(
            task_plan=[TaskStep(id=1, action="test", description="desc")],
            tools_required=[],
            requires_clarification=False,
            summary="test plan"
        )
        
        # Setup mock for find_matching_skill
        mock_collection.query.return_value = {
            'documents': [["query pattern"]],
            'metadatas': [[{
                'name': 'test_skill',
                'description': 'desc',
                'plan_template': plan.json()
            }]],
            'distances': [[0.1]]
        }
        
        match = mgr.find_matching_skill("query pattern")
        self.assertIsNotNone(match)
        self.assertEqual(match.name, "test_skill")

    @patch('src.services.learning.SkillManager.find_matching_skill')
    @patch('src.services.learning.SkillManager.add_skill')
    def test_learning_manager_logic(self, mock_add_skill, mock_find_skill):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        lm = LearningManager(self.mock_memory)
        
        # No skill exists
        mock_find_skill.return_value = None
        
        plan = ExecutionPlan(
            task_plan=[
                TaskStep(id=1, action="step1", description="desc1"),
                TaskStep(id=2, action="step2", description="desc2")
            ],
            tools_required=[],
            requires_clarification=False,
            summary="complex task"
        )
        
        # Test skill creation for successful multi-step task
        loop.run_until_complete(lm.learn("sid", "Do complex task", "Success", plan))
        mock_add_skill.assert_called_once()
        
        # Test failure logging
        with patch('src.services.learning.FailureLogger.log') as mock_log:
            loop.run_until_complete(lm.learn("sid", "Fail task", "ERROR: tool crashed", None))
            mock_log.assert_called_with("unknown", "Fail task", "ERROR: tool crashed", "sid")

if __name__ == '__main__':
    unittest.main()

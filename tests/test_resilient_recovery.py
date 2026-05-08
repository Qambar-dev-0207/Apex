import asyncio
import sys
import os
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from rich.console import Console

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.routers.router import ParallelExecutor
from src.core.models import ExecutionPlan, TaskStep
from src.models.thinking_path import GeminiClient

class TestResilientRecovery(unittest.TestCase):
    def setUp(self):
        self.console = Console()
        self.gemini = MagicMock() # Use general mock to allow sub-attributes
        self.executor = ParallelExecutor(console=self.console, primary_brain=self.gemini)

    @patch('src.models.fallback_path.TertiaryReasoningClient.generate_response', new_callable=AsyncMock)
    async def run_fallback_chain_test(self, mock_tertiary):
        # 1. Setup a step that will fail in Tier 1
        step = {"id": 1, "action": "break_something", "tool": "unknown", "input_data": "data", "dependencies": []}
        
        # 2. Mock Tier 2 Failure (Gemini failure)
        # self.gemini.client.models.generate_content
        self.gemini.client.models.generate_content.side_effect = Exception("Gemini Down")
        self.gemini.model_id = "test-model"
        
        # 3. Mock Tier 3 Success (DeepSeek)
        mock_tertiary.return_value = "DeepSeek recovered this task."
        
        # 4. Trigger recovery
        res = await self.executor._fallback_recovery(step, "Tier 1 Crash")
        
        # 5. Verify results
        self.assertTrue(res['success'])
        self.assertIn("RECOVERY_TIER_3", res['output'])
        print(f"[Test] Fallback Chain verified: {res['output']}")

    def test_recovery_flow(self):
        asyncio.run(self.run_fallback_chain_test())

    def test_skill_seeding(self):
        from src.services.learning import LearningManager
        from src.services.memory import MemoryManager
        mm = MemoryManager()
        lm = LearningManager(mm)
        # Mock skill manager to avoid real chroma calls
        lm.skill_manager.find_matching_skill = MagicMock(return_value=None)
        lm.skill_manager.add_skill = MagicMock()
        
        lm.seed_skills()
        self.assertGreater(lm.skill_manager.add_skill.call_count, 0)
        print(f"[Test] Skill seeding verified.")

if __name__ == '__main__':
    unittest.main()

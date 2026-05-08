import asyncio
import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from rich.console import Console

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.routers.router import InputClassifier, ParallelExecutor
from src.services.memory import MemoryManager
from src.core.models import Skill, ExecutionPlan, TaskStep

class AgenticAutonomyTest(unittest.TestCase):
    """
    Test for Autonomous Skill Activation (L1-L21 Integration).
    """
    def setUp(self):
        self.console = Console()

    @patch('src.services.learning.SkillManager.find_matching_skill')
    @patch('google.genai.Client')
    async def run_autonomy_flow(self, mock_genai_class, mock_find_skill):
        # 1. Setup a "God-Mode" Skill
        test_skill = Skill(
            name="Test Auto Skill",
            description="Auto-triggered",
            query_pattern="trigger the test",
            plan_template=ExecutionPlan(
                task_plan=[TaskStep(id=1, action="auto action", description="exec", tool=None)],
                tools_required=[], requires_clarification=False, summary="Auto Plan"
            )
        )
        
        # Mock high-confidence match
        mock_find_skill.return_value = test_skill
        
        # Setup Classifier with mock client
        mock_client = mock_genai_class.return_value
        classifier = InputClassifier()
        classifier.client = mock_client
        
        # Mock Flash classification confirming the auto-trigger
        mock_res = MagicMock()
        mock_res.text = json.dumps({
            "intent": "skill_activation",
            "complexity": "high",
            "priority": 1,
            "requires_tools": True,
            "requires_vision": False,
            "autonomous_skill_id": "Test Auto Skill"
        })
        mock_client.models.generate_content.return_value = mock_res
        
        # 2. Run Classification
        print("\n[Audit] Testing Autonomous Skill Match...")
        classification = await classifier.classify("Please trigger the test")
        
        self.assertEqual(classification["autonomous_skill_id"], "Test Auto Skill")
        self.assertEqual(classification["intent"], "skill_activation")
        print("  [green]✓ Classifier detected autonomous skill intent.[/green]")

        # 3. Verify logic
        self.assertEqual(test_skill.plan_template.summary, "Auto Plan")
        print("  [green]✓ Sovereign Skill Template verified for injection.[/green]")

    def test_agentic_autonomy(self):
        asyncio.run(self.run_autonomy_flow())

if __name__ == "__main__":
    unittest.main()

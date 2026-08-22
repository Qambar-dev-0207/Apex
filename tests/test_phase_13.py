import asyncio
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.proactive import BriefingAgent
from src.models.thinking_path import GeminiClient
from src.tools.workspace import WorkspaceManager
from src.core.telemetry import SpendTracker

class TestPhase13(unittest.TestCase):
    def setUp(self):
        self.workspace = WorkspaceManager(storage_path="data/test_workspace.json")
        self.spend = SpendTracker(db_path="data/test_spend.db")
        self.briefing = BriefingAgent(self.workspace, self.spend)

    def tearDown(self):
        if os.path.exists("data/test_workspace.json"): os.remove("data/test_workspace.json")
        if os.path.exists("data/test_spend.db"): os.remove("data/test_spend.db")

    @patch('google.genai.Client')
    async def run_proactive_test(self, mock_genai):
        # 1. Test Briefing Generation
        self.workspace.create_project("BriefingTest", "Test", ".", ["Goal A"])
        self.workspace.add_todo("BriefingTest", "Task X")
        
        # Mock strategy synthesis
        mock_res = MagicMock()
        mock_res.text = "Cunning strategy: Execute Task X immediately to maintain technical lead."
        self.briefing.client.models.generate_content = MagicMock(return_value=mock_res)
        
        report = await self.briefing.generate_briefing()
        self.assertEqual(report.high_priority_tasks[0], "Task X")
        self.assertIn("Cunning", report.suggested_strategy)
        print(f"[Test] Briefing verified: {report.suggested_strategy}")

    @patch('google.genai.Client')
    async def run_steelman_test(self, mock_genai):
        # 2. Test Steelman Mode logic
        client = GeminiClient()
        client.steelman_mode = True
        
        mock_res = MagicMock()
        mock_res.text = '{"task_plan": [], "tools_required": [], "requires_clarification": false, "summary": "S", "socratic_insight": "The strongest counter-argument is..."}'
        client.client.models.generate_content = MagicMock(return_value=mock_res)
        
        plan = await client.generate_plan("Why build recursion?", "sid")
        self.assertIn("counter-argument", plan.socratic_insight)
        print(f"[Test] Steelman reasoning verified.")

    def test_proactive_intelligence(self):
        asyncio.run(self.run_proactive_test())

    def test_steelman_mode(self):
        asyncio.run(self.run_steelman_test())

if __name__ == '__main__':
    unittest.main()

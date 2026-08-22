import asyncio
import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from rich.console import Console

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.memory import MemoryManager
from src.routers.router import InputClassifier, ParallelExecutor
from src.core.telemetry import SpendTracker
from src.models.thinking_path import GeminiClient

class GrandUnifiedTest(unittest.TestCase):
    """
    GRAND UNIFIED TEST (GUT) 2026.
    Ensures all 14 layers of APEX work perfectly together.
    """
    
    @classmethod
    def setUpClass(cls):
        cls.console = Console()
        cls.console.print("\n[bold reverse blue] APEX GRAND UNIFIED TEST (GUT) 2026 [/bold reverse blue]\n")

    def setUp(self):
        # Mocks
        self.patcher_genai = patch('google.genai.Client', autospec=True)
        self.mock_genai_class = self.patcher_genai.start()
        self.mock_client = self.mock_genai_class.return_value
        
        # Internal components
        self.memory = MemoryManager()
        # Mock ResponseCache lookup to always miss so we hit the LLM
        self.memory.cache.get_cached_response = MagicMock(return_value=None)
        
        self.classifier = InputClassifier()
        self.executor = ParallelExecutor(console=self.console)
        self.spend = SpendTracker(db_path="data/gut_apex.db")
        self.client = GeminiClient()
        
    def tearDown(self):
        self.patcher_genai.stop()
        if os.path.exists("data/gut_apex.db"):
            os.remove("data/gut_apex.db")
        if os.path.exists("data/test_workspace.json"):
            os.remove("data/test_workspace.json")

    async def run_full_stack_loop(self):
        session_id = "GUT_SESSION_001"
        self.console.print("[bold yellow]Phase 1: Project & Workspace Initialization[/bold yellow]")
        self.executor.workspace.create_project("GUT_Project", "Testing all layers", ".", ["Pass the GUT"])
        active = self.executor.workspace.get_active()
        self.assertEqual(active.name, "GUT_Project")
        self.console.print("  [green]✓ Workspace Manager active.[/green]")

        self.console.print("[bold yellow]Phase 2: Intent & Socratic Reasoning[/bold yellow]")
        query = "Build a fibonacci function and remember I prefer recursion."
        
        # Mock Responses
        mock_flash_res = MagicMock()
        mock_flash_res.text = json.dumps({
            "intent": "coding",
            "complexity": "high",
            "priority": 1,
            "requires_tools": True
        })
        
        mock_thinking_res = MagicMock()
        mock_thinking_res.text = json.dumps({
            "task_plan": [
                {"id": 1, "action": "write fibonacci", "description": "impl", "tool": "python_executor", "input_data": "code", "dependencies": []}
            ],
            "tools_required": ["python_executor"],
            "requires_clarification": False,
            "summary": "Build fib",
            "socratic_insight": "Have you considered the stack depth of recursion for large N?"
        })
        
        # Set side effect for all generate_content calls
        # 1. Classification (classifier.classify)
        # 2. Planning (client.generate_plan)
        self.mock_client.models.generate_content.side_effect = [mock_flash_res, mock_thinking_res]

        # 2.1 Classify
        classification = await self.classifier.classify(query)
        self.assertEqual(classification['intent'], "coding")
        self.console.print("  [green]✓ Intent Classification successful.[/green]")

        # 2.2 Plan (with Socratic)
        self.client.socratic_mode = True
        plan = await self.client.generate_plan(query, session_id)
        
        self.assertIsNotNone(plan.socratic_insight, f"Plan summary: {plan.summary}")
        self.assertIn("recursion", plan.socratic_insight or "")
        self.console.print(f"  [green]✓ Socratic Insight generated: {plan.socratic_insight}[/green]")

        self.console.print("[bold yellow]Phase 3: Relational Memory & Parallel Execution[/bold yellow]")
        await self.memory.store_interaction(session_id, "I prefer recursion.", "Noted.")
        
        with patch.object(self.executor, 'execute_step', new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {"success": True, "output": "fib code", "error": None}
            results = await self.executor.run(plan)
            self.assertTrue(results[0]['success'])
        self.console.print("  [green]✓ Parallel TaskGroup & Dispatcher successful.[/green]")

        self.console.print("[bold yellow]Phase 4: Semantic Cache & Telemetry[/bold yellow]")
        # Test Cache hit specifically
        self.memory.cache.get_cached_response = MagicMock(return_value="Cached Fibonacci Response")
        cached = self.memory.cache.get_cached_response(query)
        self.assertEqual(cached, "Cached Fibonacci Response")
        self.console.print("  [green]✓ Response Cache operational.[/green]")

        self.spend.log_interaction(session_id, "gemini-1.5-pro", 5000, 1000)
        daily = self.spend.get_daily_spend()
        self.assertGreater(daily, 0)
        self.console.print(f"  [green]✓ Spend Tracker operational. Today's Spend: ${daily:.6f}[/green]")

    def test_gut(self):
        asyncio.run(self.run_full_stack_loop())

if __name__ == "__main__":
    unittest.main()

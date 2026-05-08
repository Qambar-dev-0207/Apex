import asyncio
import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch
from rich.console import Console

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.memory import MemoryManager
from src.routers.router import InputClassifier, SmartRouter, ParallelExecutor
from src.core.telemetry import SpendTracker
from src.core.models import TaskStep, ExecutionPlan

class SystemReadinessTest(unittest.TestCase):
    """
    Final System Readiness Test (SRT) for APEX.
    Validates that all layers (L1-L11) function cohesively.
    """
    
    @classmethod
    def setUpClass(cls):
        cls.console = Console()
        cls.console.print("\n[bold reverse cyan] APEX SYSTEM READINESS TEST (SRT) 2026 [/bold reverse cyan]\n")

    def setUp(self):
        # Mocks for external APIs
        self.patcher_genai = patch('google.genai.Client', autospec=True)
        self.mock_genai = self.patcher_genai.start()
        
        self.patcher_groq = patch('groq.Groq', autospec=True)
        self.mock_groq = self.patcher_groq.start()
        
        # Internal Managers
        self.memory = MemoryManager()
        self.classifier = InputClassifier()
        self.router = SmartRouter()
        self.executor = ParallelExecutor(console=self.console)
        self.spend = SpendTracker(db_path="data/test_apex.db")
        
    def tearDown(self):
        self.patcher_genai.stop()
        self.patcher_groq.stop()
        if os.path.exists("data/test_apex.db"):
            os.remove("data/test_apex.db")

    async def run_srt_flow(self):
        session_id = "SRT_FINAL_VERIFY"
        
        # STAGE 1: Memory & Intent (L1, L2)
        self.console.print("[yellow]STAGE 1: Intent Classification & Context Injection[/yellow]")
        query = "Store this fact: I am an expert in Quantum Computing. Now, what is my expertise?"
        
        # Mock Flash Classifier
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "intent": "chat",
            "complexity": "low",
            "priority": 1,
            "requires_tools": False
        })
        self.mock_genai.return_value.models.generate_content.return_value = mock_response
        
        classification = await self.classifier.classify(query)
        self.assertEqual(classification['intent'], "chat")
        self.console.print("  [green]✓ Flash Intent Classification correct.[/green]")
        
        # STAGE 2: Memory Retrieval (L2 Hybrid)
        self.console.print("[yellow]STAGE 2: Tiered Memory Persistence[/yellow]")
        await self.memory.store_interaction(session_id, "I am a Quantum Expert.", "Understood.")
        context = await self.memory.get_relevant_context("expertise", session_id)
        self.assertIn("Quantum", context)
        self.console.print("  [green]✓ Context Injection contains persisted facts.[/green]")
        
        # STAGE 3: Parallel Execution (L4, L6)
        self.console.print("[yellow]STAGE 3: Multi-Agent Parallel Execution (DAG)[/yellow]")
        plan = ExecutionPlan(
            task_plan=[
                TaskStep(id=1, action="task1", description="desc", tool=None, dependencies=[]),
                TaskStep(id=2, action="task2", description="desc", tool=None, dependencies=[1])
            ],
            tools_required=[],
            requires_clarification=False,
            summary="Parallel Test"
        )
        results = await self.executor.run(plan)
        self.assertEqual(len(results), 2)
        self.console.print("  [green]✓ DAG Resolution & TaskGroup execution successful.[/green]")
        
        # STAGE 4: Semantic Caching (L8.5)
        self.console.print("[yellow]STAGE 4: Semantic Deduplication Cache[/yellow]")
        resp = "The result is 42."
        self.memory.cache.cache_response("What is the meaning of life?", resp)
        cached = self.memory.cache.get_cached_response("What is the meaning of life?")
        self.assertEqual(cached, resp)
        self.console.print("  [green]✓ Semantic Response Cache hit verified.[/green]")
        
        # STAGE 5: Cost Telemetry (L11)
        self.console.print("[yellow]STAGE 5: Cost & Usage Telemetry[/yellow]")
        self.spend.log_interaction(session_id, "gemini-1.5-pro", 1000, 200)
        daily = self.spend.get_daily_spend()
        self.assertGreater(daily, 0)
        self.console.print(f"  [green]✓ Telemetry logged. Today's Spend: ${daily:.6f}[/green]")

    def test_complete_system_integration(self):
        """Wrapper to run async SRT in unittest."""
        asyncio.run(self.run_srt_flow())

if __name__ == "__main__":
    unittest.main()

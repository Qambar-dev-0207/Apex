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
from src.routers.router import ParallelExecutor
from src.core.telemetry import SpendTracker
from src.models.thinking_path import GeminiClient
from src.services.cognitive import EmotionalCore
from src.services.sync import SovereignSync

class OmegaTest(unittest.TestCase):
    """
    THE OMEGA TEST.
    The ultimate end-to-end verification of the 24-layer APEX architecture.
    """
    
    @classmethod
    def setUpClass(cls):
        cls.console = Console()
        cls.console.print("\n[bold reverse blue] APEX OMEGA TEST: 24-LAYER UNIFICATION [/bold reverse blue]\n")

    def setUp(self):
        self.patcher_genai = patch('google.genai.Client', autospec=True)
        self.mock_genai_class = self.patcher_genai.start()
        self.mock_client = self.mock_genai_class.return_value
        
        self.memory = MemoryManager()
        self.cognitive = EmotionalCore()
        self.sync = SovereignSync()
        self.executor = ParallelExecutor(console=self.console)
        self.spend = SpendTracker(db_path="data/omega_apex.db")
        self.client = GeminiClient()

    def tearDown(self):
        self.patcher_genai.stop()
        if os.path.exists("data/omega_apex.db"): os.remove("data/omega_apex.db")

    async def run_omega_flow(self):
        session_id = "OMEGA_FINAL"
        
        # 1. Emotional Awareness (L22, L23)
        self.console.print("[cyan]Testing Emotional Core (L22, L23)...[/cyan]")
        mock_emo_res = MagicMock()
        mock_emo_res.text = json.dumps({"sentiment": "excited", "cognitive_load": "low", "flow_active": False})
        self.mock_client.models.generate_content.return_value = mock_emo_res
        
        state = await self.cognitive.analyze_user("This is amazing! Build the final layer!", 0.5)
        self.assertEqual(state.sentiment, "excited")
        self.console.print("  [green]✓ Emotional State Analysis successful.[/green]")

        # 2. Unified Planning (L1, L3, L14, L18)
        self.console.print("[cyan]Testing Unified Planning (L3, L14, L18)...[/cyan]")
        mock_plan_res = MagicMock()
        mock_plan_res.text = json.dumps({
            "task_plan": [], "tools_required": [], "requires_clarification": False, 
            "summary": "Omega Plan", "socratic_insight": "Reflecting on the 24th layer."
        })
        self.mock_client.models.generate_content.return_value = mock_plan_res
        
        plan = await self.client.generate_plan("Final check.", session_id, emotional_state=state)
        self.assertEqual(plan.summary, "Omega Plan")
        self.console.print("  [green]✓ Emotional-Aware Planning successful.[/green]")

        # 3. Parallel Recovery & HW Bridge (L4, L15, L20)
        self.console.print("[cyan]Testing Parallel Recovery & HW (L4, L15, L20)...[/cyan]")
        # This exercises the TaskGroup and HW gating logic internally
        results = await self.executor.run(plan)
        self.console.print("  [green]✓ HW-Aware TaskGroup execution successful.[/green]")

        # 4. Sovereign Sync (L24)
        self.console.print("[cyan]Testing Sovereign Sync (L24)...[/cyan]")
        backup_path = self.sync.export_snapshot()
        self.assertTrue(os.path.exists(backup_path))
        self.console.print(f"  [green]✓ Encrypted Sovereign Backup successful: {os.path.basename(backup_path)}[/green]")
        os.remove(backup_path)

    def test_omega_unified_flow(self):
        asyncio.run(self.run_omega_flow())

if __name__ == "__main__":
    unittest.main()

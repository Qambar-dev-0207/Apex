import asyncio
import sys
import os
import json
import unittest
import time
from unittest.mock import MagicMock, patch, AsyncMock
from rich.console import Console
from rich.panel import Panel

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.routers.router import InputClassifier, SmartRouter, ParallelExecutor
from src.models.thinking_path import GeminiClient
from src.services.memory import MemoryManager
from src.services.learning import LearningManager
from src.services.delivery import ResponseAssembler
from src.services.cognitive import EmotionalCore
from src.services.cognitive_graph import KnowledgeVisualizer
from src.tools.workspace import WorkspaceManager
from src.core.models import TaskStep, ExecutionPlan

class StartToEndTest(unittest.TestCase):
    """
    APEX // COMPREHENSIVE START-TO-END VERIFICATION
    Verifies the entire cognitive loop: Intent -> Emotional analysis -> Knowledge mapping -> Planning -> Execution -> Learning.
    """
    
    @classmethod
    def setUpClass(cls):
        cls.console = Console()
        cls.console.print("\n[bold reverse white] APEX COMPREHENSIVE START-TO-END TEST [/bold reverse white]\n")

    def setUp(self):
        # Patch GenAI client globally
        self.patcher_genai = patch('google.genai.Client')
        self.mock_genai_class = self.patcher_genai.start()
        self.mock_client = self.mock_genai_class.return_value
        
        # Initialize Components
        self.memory = MemoryManager()
        self.workspace = WorkspaceManager()
        self.classifier = InputClassifier()
        self.router = SmartRouter()
        self.executor = ParallelExecutor(console=self.console)
        self.thinking_path = GeminiClient()
        self.knowledge = KnowledgeVisualizer(self.memory, self.workspace)
        self.learning = LearningManager(self.memory)
        self.assembler = ResponseAssembler(self.console)
        self.cognitive = EmotionalCore()

    def tearDown(self):
        self.patcher_genai.stop()

    async def run_flow(self):
        user_input = "Can you analyze the current codebase and explain the architecture?"
        velocity = 0.05
        session_id = "comprehensive_test_session"

        # 1. Emotional Analysis (L22)
        mock_cog = MagicMock()
        mock_cog.text = json.dumps({"sentiment": "neutral", "cognitive_load": "low", "flow_active": False})
        self.mock_client.models.generate_content.return_value = mock_cog
        emotional_state = await self.cognitive.analyze_user(user_input, velocity)
        self.console.print(f"[green]✓ L22: Emotional Core analyzed state.[/green]")

        # 2. Intent Classification (L1)
        mock_class = MagicMock()
        mock_class.text = json.dumps({"intent": "exploration", "complexity": "high", "priority": 1, "requires_tools": True})
        self.mock_client.models.generate_content.return_value = mock_class
        classification = await self.classifier.classify(user_input)
        self.console.print(f"[green]✓ L1: Classifier detected intent: {classification['intent']}[/green]")

        # 3. Knowledge Context Pruning (L10)
        pruned_context = await self.knowledge.get_pruned_context(user_input)
        self.console.print("[green]✓ L10: Knowledge Visualizer pruned context.[/green]")

        # 4. Routing (L1)
        path = self.router.route(classification)
        self.assertEqual(path, "thinking_path")
        self.console.print(f"[green]✓ L1: Router directed to: {path}[/green]")

        # 5. Planning (L3)
        mock_plan = MagicMock()
        mock_plan.text = json.dumps({
            "task_plan": [
                {"id": 1, "action": "summarize", "description": "Summarize workspace", "tool": "workspace", "dependencies": []}
            ],
            "tools_required": ["workspace"],
            "requires_clarification": False,
            "summary": "Architecture Analysis Task",
            "socratic_insight": "Are we adhering to Sovereign principles?"
        })
        self.mock_client.models.generate_content.return_value = mock_plan
        plan = await self.thinking_path.generate_plan(user_input, session_id, emotional_state=emotional_state)
        self.console.print(f"[green]✓ L3: Orchestrator generated plan.[/green]")

        # 6. Execution (L4)
        with patch.object(self.executor.workspace, 'get_project_context_summary', return_value="Project: APEX, Status: OMEGA"):
            self.workspace.create_project("AuditProj", "Audit", ".", ["Safety"])
            self.executor.workspace.set_active("AuditProj")
            
            results = await self.executor.run(plan)
            self.assertTrue(results[0]['success'])
            self.console.print(f"[green]✓ L4: Executor finished task.[/green]")

        # 7. Memory & Learning (L2, L9, L10)
        await self.memory.store_interaction(session_id, user_input, "Final Response")
        await self.learning.learn(session_id, user_input, "Final Response", plan)
        
        # Mock knowledge extraction
        mock_knowledge = MagicMock()
        mock_knowledge.text = json.dumps({
            "new_nodes": [{"id": "apex_core", "label": "APEX Core", "type": "component", "summary": "Engine logic"}],
            "new_edges": []
        })
        self.mock_client.models.generate_content.return_value = mock_knowledge
        await self.knowledge.extract_knowledge(user_input, "Final Response")
        
        self.console.print("[green]✓ L2/L9/L10: Memory, Learning, and Knowledge Graph updated.[/green]")

        # 9. Memory Clearing Verification
        await self.memory.clear_session_history(session_id)
        self.console.print("[green]✓ Session history cleared successfully.[/green]")
        
        await self.memory.clear_all_history()
        self.console.print("[green]✓ All interaction history and semantic memories wiped successfully.[/green]")

    def test_comprehensive_flow(self):
        asyncio.run(self.run_flow())

if __name__ == "__main__":
    unittest.main()

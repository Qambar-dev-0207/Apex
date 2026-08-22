import asyncio
import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from rich.console import Console

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.cognitive_graph import KnowledgeVisualizer
from src.core.models import KnowledgeMap, KnowledgeNode, KnowledgeEdge

class TestCognitiveGraph(unittest.TestCase):
    """
    Unit tests for Layer 10: Knowledge Visualizer & Cognitive Graph.
    """
    
    def setUp(self):
        self.console = Console()
        self.memory_manager = MagicMock()
        self.memory_manager.chroma = MagicMock()
        self.memory_manager.redis = MagicMock()
        self.workspace = MagicMock()
        self.workspace.get_active.return_value = MagicMock(root_dir=".")
        
        # Mock Chroma search
        self.memory_manager.chroma.search_memories = AsyncMock(return_value=[
            {"content": "The APEX Engine is fast.", "id": "m1", "metadata": {}}
        ])
        
        # Patch GenAI client
        self.patcher_genai = patch('google.genai.Client')
        self.mock_genai_class = self.patcher_genai.start()
        self.mock_client = self.mock_genai_class.return_value
        
        self.visualizer = KnowledgeVisualizer(self.memory_manager, self.workspace)
        # Mock _get_map_path to return isolated path
        self.visualizer._get_map_path = MagicMock(return_value="data/test_knowledge_map.json")
        # Reset map for testing
        self.visualizer.current_map = KnowledgeMap()

    def tearDown(self):
        self.patcher_genai.stop()
        if os.path.exists("data/test_knowledge_map.json"):
            try:
                os.remove("data/test_knowledge_map.json")
            except:
                pass
        if os.path.exists("data/knowledge_graph.svg"):
            try:
                os.remove("data/knowledge_graph.svg")
            except:
                pass

    async def run_extraction_test(self):
        self.visualizer.current_map = KnowledgeMap() # Reset
        # Mock Gemini extraction response
        mock_res = MagicMock()
        mock_res.text = json.dumps({
            "new_nodes": [
                { "id": "n1", "label": "APEX Engine", "type": "component", "summary": "Core logic" },
                { "id": "n2", "label": "Fast Path", "type": "logic", "summary": "Speed layer" }
            ],
            "new_edges": [
                { "source": "n1", "target": "n2", "relation": "contains" }
            ]
        })
        self.mock_client.models.generate_content.return_value = mock_res
        
        await self.visualizer.extract_knowledge("Tell me about APEX", "The APEX Engine has a Fast Path.")
        
        self.assertEqual(len(self.visualizer.current_map.nodes), 2)
        self.assertEqual(len(self.visualizer.current_map.edges), 1)
        self.assertEqual(self.visualizer.current_map.nodes[0].label, "APEX Engine")
        self.console.print("[green]✓ Knowledge Extraction test passed.[/green]")

    def test_svg_generation(self):
        # Add dummy data
        self.visualizer.current_map.nodes = [
            KnowledgeNode(id="a", label="A", type="t", summary="s", last_accessed="now"),
            KnowledgeNode(id="b", label="B", type="t", summary="s", last_accessed="now")
        ]
        self.visualizer.current_map.edges = [KnowledgeEdge(source="a", target="b", relation="r")]
        
        path = self.visualizer.generate_svg()
        self.assertTrue(os.path.exists(path))
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("<svg", content)
            self.assertIn("circle", content)
            self.assertIn("line", content)
        self.console.print("[green]✓ SVG Generation test passed.[/green]")

    async def run_pruning_test(self):
        self.visualizer.current_map = KnowledgeMap() # Reset
        # Setup nodes
        self.visualizer.current_map.nodes = [
            KnowledgeNode(id="n1", label="APEX Engine", type="component", summary="Core", last_accessed="now"),
            KnowledgeNode(id="n2", label="Distant Node", type="misc", summary="Irrelevant", last_accessed="now")
        ]
        
        # Memory mentions "APEX Engine"
        context = await self.visualizer.get_pruned_context("Tell me about the engine")
        
        self.assertIn("APEX Engine", context)
        self.assertNotIn("Distant Node", context) # Should be pruned if not mentioned or linked
        self.console.print("[green]✓ Semantic Pruning test passed.[/green]")

    def test_all_async(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_extraction_test())
            loop.run_until_complete(self.run_pruning_test())
        finally:
            loop.close()

if __name__ == "__main__":
    unittest.main()

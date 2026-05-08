import asyncio
import sys
import os
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from rich.console import Console

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.research import ResearchSwarm, KnowledgeSynthesizer
from src.core.models import KnowledgeArtifact

class TestResearchSwarm(unittest.TestCase):
    def setUp(self):
        self.console = Console()

    @patch('google.genai.Client')
    async def run_swarm_test(self, mock_genai):
        swarm = ResearchSwarm()
        
        # Mock Synthesis
        mock_res = MagicMock()
        mock_res.text = """
        {
            "topic": "test topic",
            "summary": "Synthesized summary here.",
            "findings": [{"agent": "Web", "info": "found stuff"}],
            "sources": ["source1"],
            "confidence_score": 0.9
        }
        """
        swarm.synthesizer.client.models.generate_content = MagicMock(return_value=mock_res)
        
        ska = await swarm.run_swarm("test topic")
        self.assertEqual(ska.topic, "test topic")
        self.assertGreater(ska.confidence_score, 0.5)
        self.console.print(f"[green]✓ Swarm Synthesis verified: {ska.summary}[/green]")

    def test_swarm(self):
        asyncio.run(self.run_swarm_test())

if __name__ == '__main__':
    unittest.main()

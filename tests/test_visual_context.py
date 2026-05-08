import asyncio
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.vision import RetinaTool
from src.routers.router import InputClassifier

class TestVisualContext(unittest.TestCase):
    def test_screen_capture(self):
        retina = RetinaTool(storage_dir="data/test_vision")
        path = retina.capture_screen("test_snap.png")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(path.endswith(".jpg")) # Optimized format
        os.remove(path)

    async def run_classification_vision_test(self):
        classifier = InputClassifier()
        # Mock LLM response for vision detection
        classifier.client = MagicMock()
        mock_res = MagicMock()
        mock_res.text = '{"intent": "chat", "complexity": "low", "priority": 1, "requires_tools": false, "requires_vision": true}'
        classifier.client.models.generate_content.return_value = mock_res
        
        classification = await classifier.classify("What is on my screen?")
        self.assertTrue(classification['requires_vision'])

    def test_vision_classification(self):
        asyncio.run(self.run_classification_vision_test())

if __name__ == '__main__':
    unittest.main()

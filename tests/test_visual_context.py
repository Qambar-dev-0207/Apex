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
        from PIL import Image as PILImage
        dummy_img = PILImage.new("RGB", (100, 100), color="blue")
        with patch("pyautogui.screenshot", return_value=dummy_img):
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

    async def run_ocr_tier_routing_test(self):
        retina = RetinaTool(storage_dir="data/test_vision")
        
        # 1. Verify _is_ocr_request classifications
        self.assertTrue(retina._is_ocr_request("dummy.png", "Extract text from screen"))
        self.assertTrue(retina._is_ocr_request("snap_123.jpg", None)) # Screenshot source
        self.assertTrue(retina._is_ocr_request("dummy.jpg", "read the console log"))
        self.assertFalse(retina._is_ocr_request("photo.jpg", "describe this landscape"))

        # 2. Mock _run_local_ocr to return simulated extracted text
        with patch.object(retina, "_run_local_ocr", return_value="SIMULATED OCR TEXT") as mock_local_ocr, \
             patch('os.path.exists', return_value=True):
            
            # Simple extraction prompt: should return OCR text directly without calling Gemini client
            res = await retina.describe_image("snap_123.jpg", "extract text")
            self.assertEqual(res, "SIMULATED OCR TEXT")
            mock_local_ocr.assert_called_once_with("snap_123.jpg")
            
            # Reset mock
            mock_local_ocr.reset_mock()
            
            # OCR-shaped query with specific question: should call Gemini text-only generate_content
            retina._gemini = MagicMock()
            mock_gemini_res = MagicMock()
            mock_gemini_res.text = "Answer from text"
            retina._gemini.models.generate_content.return_value = mock_gemini_res
            
            res_question = await retina.describe_image("snap_123.jpg", "find the error message")
            self.assertEqual(res_question, "Answer from text")
            mock_local_ocr.assert_called_once_with("snap_123.jpg")
            
            # Verify the call to generate_content passed text only (not a Part with image data)
            called_args = retina._gemini.models.generate_content.call_args[1]
            contents = called_args.get("contents")
            self.assertIsInstance(contents, str)
            self.assertIn("SIMULATED OCR TEXT", contents)
            self.assertIn("find the error message", contents)

    def test_ocr_tier_routing(self):
        asyncio.run(self.run_ocr_tier_routing_test())

if __name__ == '__main__':
    unittest.main()

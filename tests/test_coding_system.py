import unittest
import asyncio
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.sandbox import SandboxExecutor
from src.services.validation import CodeValidator
from src.services.coding import CodingPipeline
from src.core.models import CodeSpec, ValidationResult, TaskStep, ExecutionPlan
from src.routers.router import ParallelExecutor

class TestCodingSystem(unittest.TestCase):
    def test_sandbox_executor(self):
        executor = SandboxExecutor(timeout=2)
        
        # Test basic execution
        res = executor.execute("print('hello world')")
        self.assertTrue(res['success'])
        self.assertEqual(res['output'].strip(), "hello world")
        
        # Test error capture
        res = executor.execute("raise ValueError('test error')")
        self.assertFalse(res['success'])
        self.assertIn("ValueError: test error", res['error'])
        
        # Test timeout
        res = executor.execute("import time; time.sleep(5)")
        self.assertFalse(res['success'])
        self.assertIn("timed out", res['error'])

    @patch('google.genai.models.Models.generate_content')
    @patch('google.genai.Client', autospec=True)
    def test_code_validator(self, mock_client_class, mock_gen):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Setup mock client
        mock_client = mock_client_class.return_value
        validator = CodeValidator()
        validator.client = mock_client
        
        # Mock test generation
        mock_response = MagicMock()
        mock_response.text = "import unittest\nclass Test(unittest.TestCase):\n  def test_x(self): self.assertTrue(True)\nif __name__ == '__main__': unittest.main()"
        mock_client.models.generate_content.return_value = mock_response
        
        spec = CodeSpec(
            task_description="test",
            file_tree=[],
            interfaces=[],
            test_scenarios=["test"],
            architecture_notes="test"
        )
        
        # Manually run sandbox for the test to avoid real subprocess issues in mock environment if any
        # But SandboxExecutor should work as long as it's not mocked.
        
        res = loop.run_until_complete(validator.validate("x = 1", spec))
        self.assertTrue(res.success or "Ran 1 test" in res.test_output)

    @patch('src.services.coding.CodingPipeline.__init__', return_value=None)
    @patch('src.services.coding.CodingPipeline.execute_task')
    def test_router_integration(self, mock_pipeline, mock_init):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Mock successful pipeline run
        mock_pipeline.return_value = {
            "spec": MagicMock(),
            "code": "print('ok')",
            "validation": ValidationResult(success=True, test_output="OK", generated_code="print('ok')")
        }
        
        executor = ParallelExecutor()
        executor.coding_pipeline = MagicMock(spec=CodingPipeline)
        executor.coding_pipeline.execute_task = mock_pipeline
        
        plan = ExecutionPlan(
            task_plan=[
                TaskStep(id=1, action="implement a calculator", description="coding task", tool="python_executor", input_data="calc logic")
            ],
            tools_required=["python_executor"],
            requires_clarification=False,
            summary="test"
        )
        
        results = loop.run_until_complete(executor.run(plan))
        self.assertTrue(results[0]['success'])
        self.assertIn("Code Generated and Validated", results[0]['output'])

if __name__ == '__main__':
    unittest.main()

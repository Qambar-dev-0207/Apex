import unittest
import asyncio
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.routers.router import ParallelExecutor
from src.core.models import ExecutionPlan, TaskStep

class TestParallelExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = ParallelExecutor()
        self.executor.hw = MagicMock()
        mock_vitals = MagicMock()
        mock_vitals.status = "nominal"
        mock_vitals.cpu_percent = 10.0
        mock_vitals.ram_percent = 50.0
        self.executor.hw.get_vitals.return_value = mock_vitals
        
        async def mock_gate():
            pass
        self.executor._resource_gate = mock_gate

    def test_dag_resolution_order(self):
        # Create a plan with dependencies
        # 1 -> 2
        # 3 (independent)
        plan = ExecutionPlan(
            task_plan=[
                TaskStep(id=1, action="task1", description="desc1", tool=None, input_data=None, dependencies=[]),
                TaskStep(id=2, action="task2", description="desc2", tool=None, input_data=None, dependencies=[1]),
                TaskStep(id=3, action="task3", description="desc3", tool=None, input_data=None, dependencies=[])
            ],
            tools_required=[],
            requires_clarification=False,
            summary="test plan"
        )
        
        # Mock execute_step to track call order
        call_order = []
        async def mock_execute(step):
            call_order.append(step['id'])
            return {"success": True, "output": f"out{step['id']}", "error": None}
            
        self.executor.execute_step = mock_execute
        
        # Run the executor
        results = asyncio.run(self.executor.run(plan))
        
        # 1 and 3 should be able to run first (order might vary)
        # 2 MUST run after 1
        self.assertEqual(len(results), 3)
        self.assertLess(call_order.index(1), call_order.index(2))
        self.assertIn(3, call_order[:2]) # 3 should be in the first batch

    @patch('src.tools.web_search.WebSearchTool.asearch')
    def test_parallel_tool_execution(self, mock_asearch):
        # Mock web search to be slow
        async def slow_search(query):
            await asyncio.sleep(0.1)
            return {"success": True, "results": [{"title": "found", "url": "http://found", "snippet": "found"}], "error": None}
        mock_asearch.side_effect = slow_search
        
        plan = ExecutionPlan(
            task_plan=[
                TaskStep(id=1, action="search1", description="desc1", tool="web_search", input_data="query1", dependencies=[]),
                TaskStep(id=2, action="search2", description="desc2", tool="web_search", input_data="query2", dependencies=[])
            ],
            tools_required=["web_search"],
            requires_clarification=False,
            summary="parallel search"
        )
        
        import time
        start = time.time()
        asyncio.run(self.executor.run(plan))
        end = time.time()
        
        print(f"Mock asearch call count: {mock_asearch.call_count}")
        print(f"Execution took: {end - start} seconds")
        self.assertEqual(mock_asearch.call_count, 2)
        
        # If they ran in parallel, total time should be ~0.1s, not 0.2s
        self.assertLess(end - start, 0.3)

if __name__ == '__main__':
    unittest.main()

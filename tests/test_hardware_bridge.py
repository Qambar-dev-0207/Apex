import asyncio
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.hardware import HardwareMonitor
from src.routers.router import ParallelExecutor
from src.core.models import TaskStep, ExecutionPlan

class TestHardwareBridge(unittest.TestCase):
    def test_hardware_monitoring(self):
        monitor = HardwareMonitor()
        vitals = monitor.get_vitals()
        self.assertGreaterEqual(vitals.cpu_percent, 0)
        self.assertGreaterEqual(vitals.ram_percent, 0)
        self.assertIn(vitals.status, ["nominal", "warning", "critical"])

    async def run_throttling_test(self):
        executor = ParallelExecutor()
        # Mock critical status
        executor.hw.get_vitals = MagicMock(return_value=MagicMock(status="critical"))
        
        # This should trigger the "SYSTEM OVERLOAD" print and pause
        # We'll just verify the semaphore is lowered
        await executor._resource_gate()
        # Since it's critical, semaphore should have been reset to 1
        # (Internal check of semaphore value is tricky, but we can check the logic)
        self.assertEqual(executor.concurrency_limit._value, 1)

    def test_throttling(self):
        asyncio.run(self.run_throttling_test())

if __name__ == '__main__':
    unittest.main()

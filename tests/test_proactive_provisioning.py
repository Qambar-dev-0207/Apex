import asyncio
import os
import json
import unittest
import sys
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.proactive_provisioning import AutoProvisioner
from src.services.learning import SkillManager
from src.tools.mcp_client import MCPClient
from src.tools.workspace import WorkspaceManager
from src.core.models import CapabilityGap

class TestAutoProvisioning(unittest.TestCase):
    def setUp(self):
        self.skill_manager = MagicMock(spec=SkillManager)
        # Mock the ChromaDB collection inside skill_manager
        self.skill_manager.collection = MagicMock()
        self.skill_manager.collection.get.return_value = {'metadatas': []}
        
        self.mcp_client = MagicMock(spec=MCPClient)
        self.workspace = MagicMock(spec=WorkspaceManager)
        self.workspace.get_project_context_summary.return_value = "Project Context: React Frontend with Node.js Backend."
        
        # Patch genai.Client
        self.patcher = patch('google.genai.Client', autospec=True)
        self.mock_genai = self.patcher.start()
        self.mock_client = self.mock_genai.return_value
        
        self.provisioner = AutoProvisioner(self.skill_manager, self.mcp_client, self.workspace)

    def tearDown(self):
        self.patcher.stop()

    async def run_test(self):
        # 1. Test Gap Analysis
        mock_res = MagicMock()
        mock_res.text = json.dumps([{
            "id": "gap-1",
            "type": "skill",
            "description": "Handle React component migrations.",
            "suggested_name": "ReactMigrator",
            "reason": "Large legacy codebase detected.",
            "priority": 1
        }])
        self.mock_client.models.generate_content.return_value = mock_res
        
        gaps = await self.provisioner.analyze_project_gaps("TestProj")
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0].suggested_name, "ReactMigrator")
        print("[Test] Gap analysis verified.")

        # 2. Test Skill Provisioning
        mock_skill_res = MagicMock()
        mock_skill_res.text = json.dumps({
            "name": "ReactMigrator",
            "description": "Handle React component migrations.",
            "query_pattern": "migrate react",
            "plan_template": {
                "task_plan": [{"id": 1, "action": "migrate", "description": "migrate", "tool": "shell", "input_data": "cmd", "dependencies": []}],
                "tools_required": ["shell"],
                "requires_clarification": False,
                "summary": "Migration Plan"
            }
        })
        self.mock_client.models.generate_content.return_value = mock_skill_res
        
        await self.provisioner.provision_skill(gaps[0])
        self.skill_manager.add_skill.assert_called()
        print("[Test] Skill provisioning verified.")

        # 3. Test MCP Provisioning
        mock_mcp_res = MagicMock()
        mock_mcp_res.text = "print('Generated MCP Server')"
        self.mock_client.models.generate_content.return_value = mock_mcp_res
        
        mcp_gap = CapabilityGap(id="gap-2", type="mcp", description="Connect to AWS", suggested_name="AWSConnector", reason="Deployment needed.", priority=2)
        await self.provisioner.provision_mcp(mcp_gap)
        
        mcp_path = os.path.join(os.getcwd(), "src", "tools", "mcp_extensions", "awsconnector_mcp.py")
        self.assertTrue(os.path.exists(mcp_path))
        print("[Test] MCP provisioning verified.")
        
        # Cleanup
        if os.path.exists(mcp_path): os.remove(mcp_path)

    def test_provisioning_flow(self):
        asyncio.run(self.run_test())

if __name__ == "__main__":
    unittest.main()

import os
import json
from typing import List
from google import genai
from src.core.models import CapabilityGap, Skill
from src.services.learning import SkillManager
from src.tools.mcp_client import MCPClient
from src.tools.workspace import WorkspaceManager
from dotenv import load_dotenv

class AutoProvisioner:
    """
    Autonomous tool creation service.
    Analyzes project requirements and creates missing Skills/MCPs.
    """
    def __init__(self, skill_manager: SkillManager, mcp_client: MCPClient, workspace: WorkspaceManager):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.skill_manager = skill_manager
        self.mcp_client = mcp_client
        self.workspace = workspace
        self.model_id = "gemini-2.5-flash-lite" # Optimized for cost/speed analysis

    async def analyze_project_gaps(self, project_name: str) -> List[CapabilityGap]:
        """
        Scans a project's context and determines what tools it lacks.
        """
        if not self.client: return []
        
        context = self.workspace.get_project_context_summary(project_name)
        try:
            raw = self.skill_manager.collection.get()
            existing_skills = [m.get('name', '') for m in (raw.get('metadatas') or []) if m]
        except Exception:
            existing_skills = []
        
        prompt = f"""
        IDENT: APEX // PROACTIVE PROVISIONING PROTOCOL
        
        Analyze this project and identify gaps in APEX's current capabilities.
        Compare project goals and tech stack with existing skills.
        
        EXISTING SKILLS: {existing_skills}
        PROJECT CONTEXT:
        {context}
        
        Identify 1-3 critical gaps that could be filled by either:
        1. A new Sovereign Skill (logic/workflow).
        2. A new MCP Server (external integration/tool).
        
        Output MUST be valid JSON list of CapabilityGap objects:
        [{{ "id": "uuid", "type": "skill"|"mcp", "description": "...", "suggested_name": "...", "reason": "...", "priority": 1-5 }}]
        """
        
        try:
            res = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            gaps_data = json.loads(res.text)
            return [CapabilityGap(**g) for g in gaps_data]
        except Exception as e:
            print(f"[Provisioner] Gap analysis failed: {e}")
            return []

    async def provision_skill(self, gap: CapabilityGap):
        """
        Generates and registers a new Sovereign Skill.
        """
        print(f"[Provisioner] Creating Skill: {gap.suggested_name}...")
        
        prompt = f"""
        Generate a Sovereign Skill manifest (SKILL.md style) for: {gap.description}
        
        The skill should have a clear intent and a robust ExecutionPlan DAG.
        NAME: {gap.suggested_name}
        
        Output valid JSON for a Skill model:
        {{
            "name": "{gap.suggested_name}",
            "description": "{gap.description}",
            "query_pattern": "triggering query phrase",
            "plan_template": {{ 
                "task_plan": [{{ "id": 1, "action": "...", "description": "...", "tool": "...", "input_data": "...", "dependencies": [] }}],
                "tools_required": ["..."],
                "requires_clarification": false,
                "summary": "..."
            }}
        }}
        """
        
        try:
            res = self.client.models.generate_content(
                model="gemini-3.5-flash", # Use higher reasoning for manifest generation
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            skill_data = json.loads(res.text)
            new_skill = Skill(**skill_data)
            self.skill_manager.add_skill(new_skill)
            
            # Persist to repo if possible
            skills_dir = os.path.join(os.getcwd(), "src", "core", "skills_library_extended")
            os.makedirs(skills_dir, exist_ok=True)
            with open(os.path.join(skills_dir, f"{gap.suggested_name}.json"), "w") as f:
                f.write(new_skill.model_dump_json(indent=2))
                
            print(f"[Provisioner] Skill {new_skill.name} successfully established and persisted.")
        except Exception as e:
            print(f"[Provisioner] Skill creation failed: {e}")

    async def provision_mcp(self, gap: CapabilityGap):
        """
        Generates a Python-based MCP server for a missing integration.
        """
        print(f"[Provisioner] Designing MCP Server: {gap.suggested_name}...")
        
        prompt = f"""
        Write a complete Python script for an MCP Server that handles: {gap.description}
        Use the 'mcp' library and FastAPI/Starlette style.
        Include tools relevant to: {gap.reason}
        
        Output ONLY the raw Python code.
        """
        
        try:
            res = self.client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )
            code = res.text.replace("```python", "").replace("```", "").strip()
            
            mcp_dir = os.path.join(os.getcwd(), "src", "tools", "mcp_extensions")
            os.makedirs(mcp_dir, exist_ok=True)
            file_path = os.path.join(mcp_dir, f"{gap.suggested_name.lower().replace(' ', '_')}_mcp.py")
            
            with open(file_path, "w") as f:
                f.write(code)
                
            print(f"[Provisioner] MCP Server code written to {file_path}. Ready for integration.")
        except Exception as e:
            print(f"[Provisioner] MCP creation failed: {e}")

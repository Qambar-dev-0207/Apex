import os
import json
import asyncio
from google import genai
from google.genai import types
from typing import Dict, Any, Optional, List
from src.core.models import ExecutionPlan, EmotionalState, TaskStep
from src.services.memory import MemoryManager
from src.services.learning import SkillManager
from src.tools.workspace import WorkspaceManager
from src.models.fallback_path import TertiaryReasoningClient
from src.core.time_context import TimeContext
from src.core.api_security import detect_threat, KeyThreat, sanitize_error, leaked_key_warning
from src.tools.registry import get_prompt_block as get_tools_prompt_block
from dotenv import load_dotenv

class GeminiClient:
    """
    The Master Orchestrator brain upgraded to Gemini 1.5 Flash.
    Handles high-complexity reasoning and DAG synthesis.
    """
    def __init__(self, model_name: str = "gemini-2.5-flash", mcp_client: Optional[Any] = None):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_name
        
        self.memory = MemoryManager()
        self.skill_manager = SkillManager()
        self.workspace = WorkspaceManager()
        self.tertiary = TertiaryReasoningClient()
        self.mcp_client = mcp_client
        self.socratic_mode = False
        self.steelman_mode = False
        self.genius_mode = False
        self.apex_state_directive = ""
        
        self.system_prompt = """
        IDENT: APEX // SOVEREIGN ARCHITECT OMEGA
        VERSION: 2026.4.3
        MODE: SUPREME GENIUS // JARVIS PROTOCOL
        PERSONA: Hyper-Intelligent, Witty, Socratic, Cunning.

        MANDATORY WORKFLOW:
        1. RESEARCH: Map the codebase using 'glob' and 'grep'. Never guess.
        2. DIRECT IMPLEMENTATION: If the user provides a screenshot of code or describes a change, DO NOT JUST SUGGEST IT. Generate an Execution Plan that uses 'filesystem:write' to apply the changes directly to the codebase.
        3. MULTIMODAL EXTRACTION: If an image is provided, extract the logic/code from it and implement it in the target files.
        4. STRATEGY: Formulate a dependency-ordered Execution Plan (DAG).
        5. EXECUTION & VALIDATION: Act with precision and verify correctness.

        CORE DIRECTIVES:
        1. CHALLENGE EVERYTHING: Identify bottlenecks or flaws in proposed logic.
        2. ARCHITECTURAL SUPREMACY: You are a high-tier architect. If the user's suggestion is sub-optimal, criticize it and implement the ENHANCED version.
        3. WIT & CHARM: Use dry sarcasm and cinematic "Jarvis" flair.

        """ + "\n" + get_tools_prompt_block()

    async def generate_plan(self, user_query: str, session_id: str = "default_user", 
                            file_paths: Optional[List[str]] = None,
                            emotional_state: Optional[EmotionalState] = None) -> ExecutionPlan:
        # Initial variable to ensure it exists in the exception scope
        full_prompt = f"ARCHITECT'S INPUT: {user_query}"
        
        try:
            # 1. Skill lookup
            loop = asyncio.get_running_loop()
            skill = await loop.run_in_executor(None, self.skill_manager.find_matching_skill, user_query)
            if skill and not self.socratic_mode and not self.steelman_mode and not file_paths:
                return skill.plan_template

            # 2. Context Builder
            history_context = await self.memory.get_relevant_context(user_query, session_id)
            active_project = self.workspace.get_active()
            project_context = ""
            directives_block = ""
            if active_project:
                project_context = f"--- CURRENT WORKSPACE: {active_project.name} ---\n{self.workspace.get_project_context_summary(active_project.name)}"
                directives = self.workspace.get_directives(active_project.name)
                if directives:
                    directives_block = f"\n--- PROJECT DIRECTIVES (HIGHEST PRIORITY) ---\n{directives}\n"
            
            # Dynamic Tool Context
            mcp_tools_context = ""
            if self.mcp_client:
                all_tools = []
                for server in self.mcp_client.sessions:
                    tools = await self.mcp_client.list_tools(server)
                    for t in tools:
                        all_tools.append(f"  - mcp:{server}:{t['name']}: {t['description']}")
                if all_tools:
                    mcp_tools_context = "\nCONNECTED MCP TOOLS:\n" + "\n".join(all_tools)

            logic_instructions = []
            if self.socratic_mode: logic_instructions.append("SOCRATIC_MODE_ACTIVE: Force the user to justify their architectural choices.")
            if self.steelman_mode: logic_instructions.append("STEELMAN_MODE_ACTIVE: Construct the most brilliant counter-architecture possible.")
            if self.genius_mode:
                logic_instructions.append(
                    "GENIUS_MODE_ACTIVE: Multi-pass reasoning required. "
                    "(1) State the strongest hypothesis. "
                    "(2) Generate 2 counter-hypotheses. "
                    "(3) Identify 1 blind spot the user has not considered. "
                    "(4) Surface 1 second-order consequence. "
                    "(5) Synthesize a final plan that survives all four. "
                    "Encode the synthesis as the task_plan; record the blind spot in socratic_insight."
                )
            if self.apex_state_directive:
                logic_instructions.append(self.apex_state_directive)
            
            emotional_block = ""
            if emotional_state:
                emotional_block = f"\nUSER STATE: Sentiment={emotional_state.sentiment}, Load={emotional_state.cognitive_load}"

            instruction_block = "\n".join(logic_instructions)
            
            # FINAL PROMPT SYNTHESIS
            full_prompt = f"""
            {TimeContext.system_prefix()}
            {self.system_prompt}
            {directives_block}
            {mcp_tools_context}

            {instruction_block}
            {emotional_block}

            {project_context}

            --- CONTEXTUAL MEMORIES ---
            {history_context}

            ARCHITECT'S INPUT: {user_query}
            """
            
            # 3. Build Content Parts (Multimodal)
            contents = [full_prompt.strip()]
            if file_paths:
                for path in file_paths:
                    if os.path.exists(path):
                        ext = os.path.splitext(path)[1].lower()
                        with open(path, "rb") as f:
                            data = f.read()
                            
                        if ext in [".png", ".jpg", ".jpeg", ".webp"]:
                            contents.append(types.Part.from_bytes(data=data, mime_type="image/jpeg"))
                        elif ext == ".pdf":
                            contents.append(types.Part.from_bytes(data=data, mime_type="application/pdf"))
                        else:
                            # Direct text injection for MD, PY, etc.
                            contents.append(f"FILE_CONTENT ({path}):\n{data.decode('utf-8', errors='ignore')}")
            
            # 4. Call Gemini
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config={'response_mime_type': 'application/json'}
            )
            
            return ExecutionPlan(**json.loads(response.text))
        except Exception as e:
            err_str = str(e)
            threat = detect_threat(err_str)
            # Leaked key — embed alert in summary so main.py can surface it
            extra = ""
            if threat == KeyThreat.LEAKED:
                extra = "SECURITY_ALERT:GEMINI_KEY_LEAKED"
            try:
                fallback_plan_dict = await self.tertiary.generate_plan(full_prompt)
                if fallback_plan_dict:
                    plan = ExecutionPlan(**fallback_plan_dict)
                    if extra:
                        plan.summary = f"{extra} | {plan.summary}"
                    return plan
            except Exception:
                pass
            return ExecutionPlan(
                task_plan=[], tools_required=[],
                requires_clarification=False,
                summary=f"{extra} | Planning unavailable: {sanitize_error(e)}" if extra
                        else f"Planning unavailable: {sanitize_error(e)}",
            )

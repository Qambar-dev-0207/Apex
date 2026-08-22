import os
import json
import glob
import re
from datetime import datetime
from typing import Optional
from src.core.models import Skill, FailureRecord, ExecutionPlan, TaskStep
from src.services.memory import MemoryManager
import chromadb

class FailureLogger:
    """
    Logs tool execution failures to a local file.
    """
    def __init__(self, file_path: str = "data/failures.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def log(self, tool: str, input_data: str, error: str, session_id: str):
        record = FailureRecord(
            timestamp=datetime.now().isoformat(),
            tool=tool,
            input_data=input_data,
            error=error,
            session_id=session_id
        )
        with open(self.file_path, "r+") as f:
            data = json.load(f)
            data.append(record.model_dump())
            f.seek(0)
            json.dump(data, f, indent=2)

class SkillManager:
    """
    Manages the 'apex_skills' collection in ChromaDB.
    Reuses the singleton sentence-transformer EF from memory.py to avoid
    loading the ~80MB model twice on boot.
    """
    def __init__(self):
        from src.services.memory import _get_shared_ef
        path = os.getenv("CHROMA_PATH", "./data/chroma")
        self.client = chromadb.PersistentClient(path=path)
        self.ef = _get_shared_ef()
        self.collection = self.client.get_or_create_collection(
            name="apex_skills",
            embedding_function=self.ef
        )

    def add_skill(self, skill: Skill):
        self.collection.add(
            documents=[skill.query_pattern],
            metadatas=[{
                "name": skill.name,
                "description": skill.description,
                "plan_template": skill.plan_template.model_dump_json()
            }],
            ids=[skill.name]
        )

    def find_matching_skill(self, query: str, threshold: float = 0.5) -> Optional[Skill]:
        results = self.collection.query(
            query_texts=[query],
            n_results=1
        )
        if results['documents'] and results['documents'][0] and results['distances'][0][0] < threshold:
            meta = results['metadatas'][0][0]
            return Skill(
                name=meta['name'],
                description=meta['description'],
                query_pattern=results['documents'][0][0],
                plan_template=ExecutionPlan.model_validate_json(meta['plan_template'])
            )
        return None

class LearningManager:
    """
    Central manager for self-improvement logic.
    """
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.failure_logger = FailureLogger()
        self.skill_manager = SkillManager()

    async def learn(self, session_id: str, query: str, assistant_output: str, plan: Optional[ExecutionPlan] = None):
        """
        Background task to process an interaction and extract knowledge.
        """
        if "ERROR" in assistant_output.upper() or "FAILED" in assistant_output.upper():
            self.failure_logger.log("unknown", query, assistant_output, session_id)

        if plan and len(plan.task_plan) > 1:
            existing_skill = self.skill_manager.find_matching_skill(query)
            if not existing_skill:
                new_skill = Skill(
                    name=f"skill_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    description=f"Automated skill for: {plan.summary}",
                    query_pattern=query,
                    plan_template=plan
                )
                self.skill_manager.add_skill(new_skill)
                print(f"[Learning] New skill created: {new_skill.name}")
            else:
                print(f"[Learning] Skill reinforced: {existing_skill.name}")

    def log_tool_failure(self, tool: str, input_data: str, error: str, session_id: str):
        self.failure_logger.log(tool, input_data, error, session_id)

    def seed_skills(self):
        """
        Pre-populates the skill registry with high-tier templates.
        """
        from src.core.skills_library import get_god_mode_skills
        for skill in get_god_mode_skills():
            try:
                if not self.skill_manager.find_matching_skill(skill.query_pattern, threshold=0.01):
                    self.skill_manager.add_skill(skill)
                    print(f"[Seed] Skill initialized: {skill.name}")
            except:
                pass

    def load_markdown_skills(self, skills_dir: str):
        """
        Scans a directory for SKILL.md files and registers them.
        Mimics Gemini CLI's skill loading logic.
        """
        if not os.path.exists(skills_dir):
            return
            
        skill_files = glob.glob(os.path.join(skills_dir, "**", "SKILL.md"), recursive=True)
        for skill_path in skill_files:
            try:
                with open(skill_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                name_match = re.search(r"name:\s*(.*)", content)
                desc_match = re.search(r"description:\s*(.*)", content)
                
                if name_match and desc_match:
                    name = name_match.group(1).strip()
                    description = desc_match.group(1).strip()
                    
                    plan = ExecutionPlan(
                        task_plan=[TaskStep(id=1, action=f"Activate Skill: {name}", description=description)],
                        tools_required=[],
                        requires_clarification=False,
                        summary=f"Skill '{name}' activated from markdown."
                    )
                    
                    skill = Skill(
                        name=name,
                        description=description,
                        query_pattern=name,
                        plan_template=plan
                    )
                    
                    if not self.skill_manager.find_matching_skill(name, threshold=0.01):
                        self.skill_manager.add_skill(skill)
                        print(f"[Skills] Loaded markdown skill: {name}")
            except Exception as e:
                print(f"[Skills] Error loading {skill_path}: {e}")

    async def capture_style_override(self, generated_code: str, user_code: str):
        """
        Uses Gemini to extract style preferences from code changes.
        """
        if generated_code.strip() == user_code.strip():
            return

        prompt = f"""
        Analyze the difference between the generated code and the user's final version.
        Identify specific style preferences (e.g., typing, formatting, logic patterns).
        
        GENERATED:
        {generated_code}
        
        USER VERSION:
        {user_code}
        
        Output a single sentence preference summary (e.g., "User prefers X over Y").
        """
        
        try:
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)
            res = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
            pref = res.text.strip()
            print(f"[Learning] Style preference captured: {pref}")
        except:
            pass

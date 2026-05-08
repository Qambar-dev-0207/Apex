import os
import json
import asyncio
import httpx
from openai import OpenAI
from typing import Dict, Any, List, Optional
from src.core.models import CodeSpec, ValidationResult
from src.services.validation import CodeValidator
from dotenv import load_dotenv

class CodingPipeline:
    """
    Upgraded Coding Pipeline (L5B).
    Uses ChatGPT Codex (OpenAI) for core logic and MiniMax 2.5 (OpenRouter) for architecture/aux.
    """
    def __init__(self):
        load_dotenv()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.validator = CodeValidator(model_name="gemini-2.5-flash")

    async def _call_minimax(self, prompt: str) -> str:
        """
        Calls MiniMax 2.5 via OpenRouter.
        """
        if not self.openrouter_api_key:
            return "MiniMax Error: OPENROUTER_API_KEY missing."

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "minimax/minimax-m2.5:free",
            "messages": [{"role": "user", "content": prompt}]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            data = res.json()
            return data['choices'][0]['message']['content']

    async def execute_task(self, task_description: str) -> Dict[str, Any]:
        """
        Pipeline: 
        1. Architecture Spec (MiniMax 2.5)
        2. Core Implementation (ChatGPT Codex / GPT-4o)
        3. Automated Validation (Gemini 2.0 Flash)
        """
        # STAGE 1: Architecture (MiniMax 2.5)
        spec_prompt = f"""
        Design an architecture for the following coding task. 
        Detect the required tech stack from the description.
        TASK: {task_description}
        Output valid JSON matching: {{ "task_description": "...", "file_tree": [], "interfaces": [], "test_scenarios": [], "architecture_notes": "..." }}
        """
        spec_text = await self._call_minimax(spec_prompt)
        try:
            clean_json = spec_text.replace("```json", "").replace("```", "").strip()
            spec_dict = json.loads(clean_json)
        except:
            spec_dict = {
                "task_description": task_description, "file_tree": ["main.py"], 
                "interfaces": [], "test_scenarios": ["basic execution"], 
                "architecture_notes": "Fallback architecture due to parsing error."
            }
        spec = CodeSpec(**spec_dict)

        # STAGE 2: Core Implementation (ChatGPT Codex / GPT-4o)
        impl_prompt = f"""
        Implement the following task based on this architectural spec: {spec.model_dump_json()}
        Ensure you follow professional standards for the target language.
        If multiple files are involved, output them in a structured way.
        Output ONLY the code content.
        """
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: self.openai_client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": impl_prompt}]
        ))
        code = response.choices[0].message.content.strip()

        # STAGE 3: Validation
        validation_result = await self.validator.validate(code, spec)
        
        return {
            "spec": spec,
            "code": code,
            "validation": validation_result,
            "agents_used": ["MiniMax 2.5", "ChatGPT Codex", "Gemini 2.0 Flash"]
        }

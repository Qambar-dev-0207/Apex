import os
import json
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from src.core.models import CodeSpec, ValidationResult
from src.services.validation import CodeValidator
from src.models.mimo_path import MimoClient
from dotenv import load_dotenv


class CodingPipeline:
    """
    Upgraded Coding Pipeline (L5B).
    Stack:
      1. Architecture Spec   — MiniMax 2.5 via OpenRouter (free, broad context)
      2. Core Implementation — Xiaomi MiMo v2.5-pro (replaces ChatGPT Codex)
      3. Automated Validation — Gemini 2.5 Flash
    """

    def __init__(self):
        load_dotenv()
        self.mimo = MimoClient()
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.validator = CodeValidator(model_name="gemini-2.5-flash")

    async def _call_minimax(self, prompt: str) -> str:
        if not self.openrouter_api_key:
            return "MiniMax Error: OPENROUTER_API_KEY missing."
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "minimax/minimax-m2.5:free",
            "messages": [{"role": "user", "content": prompt}],
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            data = res.json()
            return data["choices"][0]["message"]["content"]

    async def execute_task(self, task_description: str) -> Dict[str, Any]:
        """
        Pipeline:
          1. Architecture Spec (MiniMax 2.5)
          2. Core Implementation (Xiaomi MiMo v2.5-pro)
          3. Automated Validation (Gemini 2.5 Flash)
        """
        # STAGE 1: Architecture (MiniMax 2.5)
        spec_prompt = f"""
        Design an architecture for the following coding task.
        Detect the required tech stack from the description.
        TASK: {task_description}
        Output valid JSON matching:
        {{ "task_description": "...", "file_tree": [], "interfaces": [],
           "test_scenarios": [], "architecture_notes": "..." }}
        """
        spec_text = await self._call_minimax(spec_prompt)
        try:
            clean_json = spec_text.replace("```json", "").replace("```", "").strip()
            spec_dict = json.loads(clean_json)
        except Exception:
            spec_dict = {
                "task_description": task_description,
                "file_tree": ["main.py"],
                "interfaces": [],
                "test_scenarios": ["basic execution"],
                "architecture_notes": "Fallback architecture due to parsing error.",
            }
        spec = CodeSpec(**spec_dict)

        # STAGE 2: Core Implementation (Xiaomi MiMo v2.5-pro)
        impl_prompt = f"""
        Implement the following task based on this architectural spec:
        {spec.model_dump_json()}

        Requirements:
          - Follow professional standards for the target language.
          - If multiple files are involved, output them as fenced blocks with file headers.
          - Output ONLY code (no prose).
        """
        code = await self.mimo.aget_completion(
            impl_prompt,
            system_prompt=(
                "You are MiMo (Xiaomi) — APEX's core code-implementation brain. "
                "Generate production-grade code, no commentary."
            ),
            max_tokens=4096,
            temperature=0.7,
        )
        code = (code or "").strip()

        # STAGE 3: Validation
        validation_result = await self.validator.validate(code, spec)

        return {
            "spec": spec,
            "code": code,
            "validation": validation_result,
            "agents_used": ["MiniMax 2.5", "Xiaomi MiMo v2.5-pro", "Gemini 2.5 Flash"],
        }

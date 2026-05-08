import os
import json
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class TertiaryReasoningClient:
    """
    Final fallback client using OpenRouter (gpt-oss-120b:free).
    Provides massive-scale reasoning as a free fail-safe.
    """
    def __init__(self, model_id: str = "openai/gpt-oss-120b:free"):
        load_dotenv()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_id = model_id
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate_response(self, prompt: str) -> str:
        """
        Generates a text response using the tertiary model.
        """
        if not self.api_key:
            return "Tertiary Recovery Offline: OPENROUTER_API_KEY missing."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://apex-os.local",
            "X-Title": "APEX Sovereign OS"
        }

        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": "You are the final reasoning recovery layer for APEX, a 24-layer AI OS. The primary orchestrator has failed. Perform the task with maximum architectural precision using your 120B parameter depth."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(self.url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Tertiary Recovery Failure: {str(e)}"

    async def generate_plan(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Specialized fallback to generate an ExecutionPlan DAG.
        """
        instructions = "\nReturn the plan as valid JSON matching the ExecutionPlan schema: { 'task_plan': [], 'tools_required': [], 'requires_clarification': bool, 'summary': '...' }"
        response_text = await self.generate_response(prompt + instructions)
        try:
            # Basic cleanup in case of markdown blocks
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except:
            return None

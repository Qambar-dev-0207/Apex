import os
import json
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_OR_HEADERS = lambda key: {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://apex-os.local",
    "X-Title": "APEX Sovereign OS",
}


class HighReasoningClient:
    """
    OpenRouter ring-2.6-1t (1T-param) — high-reasoning fallback for ThinkPartner and GeniusMode.
    Fires silently when Gemini hits rate limits or quota exhaustion.
    """

    def __init__(self, model_id: str = "inclusionai/ring-2.6-1t:free"):
        load_dotenv()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_id = model_id

    @property
    def is_online(self) -> bool:
        return bool(self.api_key)

    async def generate(self, prompt: str, system: str = "") -> str:
        if not self.api_key:
            return ""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(
                    _OPENROUTER_URL,
                    headers=_OR_HEADERS(self.api_key),
                    json={"model": self.model_id, "messages": messages},
                )
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            return ""


class TertiaryReasoningClient:
    """
    OpenRouter gpt-oss-120b — DAG planner recovery when Gemini fails.
    Fires silently as the last resort in the planning pipeline.
    """

    def __init__(self, model_id: str = "openai/gpt-oss-120b:free"):
        load_dotenv()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_id = model_id

    async def generate_response(self, prompt: str) -> str:
        if not self.api_key:
            return ""
        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are APEX's recovery brain. The primary planner failed. "
                        "Complete the task with precision."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                r = await client.post(
                    _OPENROUTER_URL,
                    headers=_OR_HEADERS(self.api_key),
                    json=payload,
                )
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            return ""

    async def generate_plan(self, prompt: str) -> Optional[Dict[str, Any]]:
        instructions = (
            "\nReturn the plan as valid JSON: "
            "{ 'task_plan': [], 'tools_required': [], 'requires_clarification': bool, 'summary': '...' }"
        )
        text = await self.generate_response(prompt + instructions)
        if not text:
            return None
        try:
            clean = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except Exception:
            return None

"""
MiMo (Xiaomi) reasoning client — replaces ChatGPT Codex.

Endpoint: https://api.xiaomimimo.com/v1 (OpenAI-compatible)
Model:    mimo-v2.5-pro
Auth:     MIMO_API_KEY env var

Used by:
  - CodingPipeline (core implementation stage)
  - Anywhere a sturdy reasoning model is needed without paying for GPT-4o
"""

import os
import asyncio
from typing import Optional, List, Dict, Any

from openai import OpenAI
from dotenv import load_dotenv

from src.core.time_context import TimeContext
from src.core.api_security import sanitize_error, detect_threat, KeyThreat


class MimoClient:
    """
    Xiaomi MiMo v2.5-pro client. OpenAI-compatible API surface.
    Synchronous core; async wrappers exposed for use inside the event loop.
    """

    DEFAULT_MODEL = "mimo-v2.5-pro"
    DEFAULT_BASE_URL = "https://api.xiaomimimo.com/v1"

    DEFAULT_SYSTEM = (
        "You are MiMo, an AI assistant developed by Xiaomi, embedded inside APEX "
        "(a 24-layer sovereign AI OS) as the core code-implementation brain. "
        "Generate production-grade code, no commentary unless asked. "
        "Match existing code style. Prefer correctness over cleverness."
    )

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        api_key_env: str = "MIMO_API_KEY",
        thinking: bool = False,
    ):
        load_dotenv()
        api_key = os.getenv(api_key_env)
        self.model = model
        self.thinking = thinking
        self.client: Optional[OpenAI] = None
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)

    @property
    def is_online(self) -> bool:
        return self.client is not None

    def _build_messages(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        sys_msg = system_prompt or self.DEFAULT_SYSTEM
        # Always inject time context so MiMo never hallucinates the date.
        sys_msg = f"{TimeContext.system_prefix()}\n{sys_msg}"
        return [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt},
        ]

    def get_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        top_p: float = 0.95,
    ) -> str:
        if not self.client:
            return "[MiMo Offline] MIMO_API_KEY missing."
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self._build_messages(prompt, system_prompt),
                max_completion_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=False,
                frequency_penalty=0,
                presence_penalty=0,
                extra_body={
                    "thinking": {"type": "enabled" if self.thinking else "disabled"}
                },
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            return f"[MiMo error] {sanitize_error(e)}"

    async def aget_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        top_p: float = 0.95,
    ) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.get_completion(
                prompt, system_prompt, max_tokens, temperature, top_p
            ),
        )

    def stream_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        top_p: float = 0.95,
    ):
        if not self.client:
            yield "[MiMo Offline]"
            return
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=self._build_messages(prompt, system_prompt),
                max_completion_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=True,
                extra_body={
                    "thinking": {"type": "enabled" if self.thinking else "disabled"}
                },
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            yield f"[MiMo stream error] {sanitize_error(e)}"

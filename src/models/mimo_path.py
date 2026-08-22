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
from typing import Optional, List, Dict

from openai import OpenAI
from dotenv import load_dotenv

from src.core.time_context import TimeContext
from src.core.api_security import sanitize_error


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
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key_env: str = "MIMO_API_KEY",
        thinking: bool = False,
    ):
        load_dotenv()
        
        nvidia_key = os.getenv("NVIDIA_API_KEY")
        if nvidia_key and nvidia_key.strip():
            self.model = model or "z-ai/glm-5.2"
            self.base_url = base_url or "https://integrate.api.nvidia.com/v1"
            self.api_key = nvidia_key
            self.is_nvidia = True
        else:
            self.model = model or self.DEFAULT_MODEL
            self.base_url = base_url or self.DEFAULT_BASE_URL
            self.api_key = os.getenv(api_key_env)
            self.is_nvidia = False
            
        self.thinking = thinking
        self.client: Optional[OpenAI] = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

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
            return "[Client Offline] API key missing."
        try:
            kwargs = {
                "model": self.model,
                "messages": self._build_messages(prompt, system_prompt),
                "temperature": temperature,
                "top_p": top_p,
                "stream": False,
            }
            if self.is_nvidia:
                kwargs["max_tokens"] = max_tokens
                kwargs["seed"] = 42
            else:
                kwargs["max_completion_tokens"] = max_tokens
                kwargs["frequency_penalty"] = 0
                kwargs["presence_penalty"] = 0
                kwargs["extra_body"] = {
                    "thinking": {"type": "enabled" if self.thinking else "disabled"}
                }
                
            completion = self.client.chat.completions.create(**kwargs)
            return completion.choices[0].message.content or ""
        except Exception as e:
            return f"[Client error] {sanitize_error(e)}"

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
            yield "[Client Offline]"
            return
        try:
            kwargs = {
                "model": self.model,
                "messages": self._build_messages(prompt, system_prompt),
                "temperature": temperature,
                "top_p": top_p,
                "stream": True,
            }
            if self.is_nvidia:
                kwargs["max_tokens"] = max_tokens
                kwargs["seed"] = 42
            else:
                kwargs["max_completion_tokens"] = max_tokens
                kwargs["extra_body"] = {
                    "thinking": {"type": "enabled" if self.thinking else "disabled"}
                }
                
            stream = self.client.chat.completions.create(**kwargs)
            for chunk in stream:
                if not getattr(chunk, "choices", None) or len(chunk.choices) == 0:
                    continue
                delta = chunk.choices[0].delta
                if getattr(delta, "content", None) is not None:
                    yield delta.content
        except Exception as e:
            yield f"[Client stream error] {sanitize_error(e)}"

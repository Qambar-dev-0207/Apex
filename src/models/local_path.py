"""
Local Sovereignty Path — Ollama integration for APEX.

Provides local-first, zero-cloud sovereign inference for:
  - Fast text synthesis & casual conversation (replaces cloud fast_path)
  - Tool-calling & autonomous execution via OpenAI-compatible endpoint
  - DAG plan generation (replaces Gemini thinking_path)
  - Local embeddings (nomic-embed-text)
  - Local vision analysis (llava)

When APEX_SOVEREIGN=1, APEX_LOCAL=1, or cloud keys are unavailable,
SmartRouter routes requests to this module.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Generator, AsyncGenerator
from pydantic import ValidationError

from src.core.models import ExecutionPlan, TaskStep
from src.models.thinking_path import coerce_plan_dict

logger = logging.getLogger("apex.local_path")


class OllamaClient:
    """
    Local sovereignty path wrapping Ollama client and providing OpenAI-compatible
    adapters for seamless drop-in routing across all APEX subsystems.
    """

    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        self.host = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.llm_model = model or os.getenv("APEX_LOCAL_LLM", "qwen2.5-coder:latest")
        self.embed_model = os.getenv("APEX_LOCAL_EMBED", "nomic-embed-text:latest")
        self.vision_model = os.getenv("APEX_LOCAL_VISION", "llava:latest")
        
        self._async_client = None
        self._sync_client = None
        self._openai_client = None
        self._is_online_cache: Optional[bool] = None
        self._last_checked: float = 0.0

    @property
    def model(self) -> str:
        """Alias for compatibility with GroqClient and MimoClient."""
        return self.llm_model

    @property
    def client(self):
        """Async client from ollama package (lazy loaded)."""
        if self._async_client is None:
            try:
                from ollama import AsyncClient
                self._async_client = AsyncClient(host=self.host)
            except Exception as e:
                logger.debug(f"Could not initialize AsyncClient from ollama package: {e}")
                self._async_client = None
        return self._async_client

    @property
    def sync_client(self):
        """Sync client from ollama package (lazy loaded)."""
        if self._sync_client is None:
            try:
                import ollama
                self._sync_client = ollama.Client(host=self.host)
            except Exception as e:
                logger.debug(f"Could not initialize sync Client from ollama package: {e}")
                self._sync_client = None
        return self._sync_client

    @property
    def openai_client(self):
        """
        OpenAI-compatible client pointing to Ollama's /v1 endpoint.
        Allows AgentHarness and tool-calling loops to drive local models seamlessly.
        """
        if self._openai_client is None:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(
                    base_url=f"{self.host}/v1",
                    api_key="ollama",
                )
            except Exception as e:
                logger.debug(f"Could not initialize OpenAI client adapter for Ollama: {e}")
                self._openai_client = None
        return self._openai_client

    @property
    def is_online(self) -> bool:
        """Quick check if Ollama is accessible (cached for 15s)."""
        import time
        now = time.time()
        if self._is_online_cache is not None and (now - self._last_checked < 15.0):
            return self._is_online_cache
        
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.host}/api/tags", headers={"User-Agent": "APEX/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                online = (resp.status == 200)
        except Exception:
            online = False
        
        self._is_online_cache = online
        self._last_checked = now
        return online

    async def check_connection(self) -> bool:
        """Asynchronously check if Ollama is running and responsive."""
        if not self.client:
            return self.is_online
        try:
            await self.client.list()
            self._is_online_cache = True
            return True
        except Exception as e:
            logger.debug(f"Ollama connection check failed: {e}")
            self._is_online_cache = False
            return False

    async def aget_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.4,
    ) -> str:
        """Asynchronously get completion from Ollama."""
        if system_prompt is None:
            system_prompt = "APEX // SOVEREIGN-PATH. Direct, intelligent, concise."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        if self.client:
            try:
                response = await self.client.chat(
                    model=self.llm_model,
                    messages=messages,
                    options={"temperature": temperature, "num_predict": max_tokens},
                )
                return response.message.content
            except Exception as e:
                logger.warning(f"Ollama aget_completion error: {e}")
        return self.get_completion(prompt, system_prompt)

    def get_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Synchronously get completion from Ollama (matches GroqClient interface)."""
        if system_prompt is None:
            system_prompt = "APEX // SOVEREIGN-PATH. Direct, intelligent, concise."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        if self.sync_client:
            try:
                response = self.sync_client.chat(
                    model=self.llm_model,
                    messages=messages,
                )
                return response.message.content
            except Exception as e:
                logger.debug(f"Ollama sync chat error: {e}")
        
        # Fallback via urllib to /api/chat if ollama package client unavailable
        try:
            import urllib.request
            payload = json.dumps({
                "model": self.llm_model,
                "messages": messages,
                "stream": False,
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{self.host}/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("message", {}).get("content", "")
        except Exception as e:
            return f"[Local Sovereign Offline] Ollama unreachable on {self.host}: {e}"

    def stream_completion(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Synchronously stream completions from Ollama (matches GroqClient interface)."""
        if system_prompt is None:
            system_prompt = "APEX // SOVEREIGN-PATH. Direct, intelligent, concise."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        if self.sync_client:
            try:
                stream = self.sync_client.chat(
                    model=self.llm_model,
                    messages=messages,
                    stream=True,
                )
                for chunk in stream:
                    content = (
                        chunk.get("message", {}).get("content", "")
                        if isinstance(chunk, dict)
                        else getattr(chunk.message, "content", "")
                    )
                    if content:
                        yield content
                return
            except Exception as e:
                logger.debug(f"Ollama sync stream error: {e}")
        
        # Fallback via direct HTTP stream
        try:
            import urllib.request
            payload = json.dumps({
                "model": self.llm_model,
                "messages": messages,
                "stream": True,
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{self.host}/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                for line in resp:
                    if not line:
                        continue
                    try:
                        chunk_obj = json.loads(line.decode("utf-8"))
                        piece = chunk_obj.get("message", {}).get("content", "")
                        if piece:
                            yield piece
                    except Exception:
                        pass
        except Exception as e:
            yield f"[Local Sovereign Offline] {e}"

    async def astream_completion(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Asynchronously stream completions from Ollama."""
        if system_prompt is None:
            system_prompt = "APEX // SOVEREIGN-PATH. Direct, intelligent, concise."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        if self.client:
            try:
                stream = await self.client.chat(
                    model=self.llm_model,
                    messages=messages,
                    stream=True,
                )
                async for chunk in stream:
                    content = (
                        chunk.get("message", {}).get("content", "")
                        if isinstance(chunk, dict)
                        else getattr(chunk.message, "content", "")
                    )
                    if content:
                        yield content
                return
            except Exception as e:
                logger.debug(f"Ollama async stream error: {e}")
        
        for piece in self.stream_completion(prompt, system_prompt):
            yield piece

    async def generate_plan(self, prompt: str, session_id: Optional[str] = None) -> ExecutionPlan:
        """
        Generate a structured execution plan from Ollama chat.
        Decomposes complex requests into a dependency-ordered ExecutionPlan DAG.
        """
        system_prompt = """\
You are APEX OMEGA sovereign local coordinator.
Decompose the user's request into a strict dependency-ordered Execution Plan (DAG).

OUTPUT SCHEMA (STRICT — emit ONLY valid JSON, no markdown fences):
{
  "task_plan": [
    {
      "id": 1,
      "action": "short imperative action",
      "description": "one-line rationale",
      "tool": "canonical tool name or null",
      "input_data": "string arguments or null",
      "dependencies": []
    }
  ],
  "tools_required": ["tool_name"],
  "requires_clarification": false,
  "summary": "one-paragraph overview"
}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        if self.client:
            try:
                response = await self.client.chat(
                    model=self.llm_model,
                    messages=messages,
                    options={"temperature": 0.1},
                )
                content = response.message.content.strip()
                if content.startswith("```"):
                    lines = content.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    content = "\n".join(lines).strip()
                
                plan_dict = json.loads(content)
                coerced = coerce_plan_dict(plan_dict)
                return ExecutionPlan(**coerced)
            except Exception as e:
                logger.warning(f"Ollama generate_plan failed or parsing failed: {e}. Returning fallback plan.")
        
        fallback_step = TaskStep(
            id=1,
            action=f"Process request locally: {prompt[:100]}",
            description="Ollama local fallback execution.",
            tool="python_executor" if "write" not in prompt.lower() else "filesystem",
            input_data=json.dumps({"code": f"# Sovereign local processing for {prompt}"}),
        )
        return ExecutionPlan(
            task_plan=[fallback_step],
            tools_required=["python_executor"],
            requires_clarification=False,
            summary="Sovereign local execution plan.",
        )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate local embedding vector for given text."""
        if self.client:
            try:
                response = await self.client.embed(
                    model=self.embed_model,
                    input=text,
                )
                embeddings = response.get("embeddings")
                if embeddings and isinstance(embeddings, list):
                    if isinstance(embeddings[0], list):
                        return embeddings[0]
                    return embeddings
                return [0.0] * 768
            except Exception as e:
                logger.warning(f"Ollama embedding failed: {e}. Returning zero vector.")
        return [0.0] * 768

    async def generate_vision_response(self, prompt: str, image_path: str) -> str:
        """Analyze local image using local vision model."""
        if not os.path.exists(image_path):
            return f"Error: Image path not found: {image_path}"
        if self.client:
            try:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                
                response = await self.client.generate(
                    model=self.vision_model,
                    prompt=prompt,
                    images=[image_bytes],
                )
                return response.get("response", "").strip()
            except Exception as e:
                logger.warning(f"Ollama vision query failed: {e}.")
                return f"Local vision analysis failed: {e}"
        return "Local vision model offline."

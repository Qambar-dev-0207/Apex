import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Generator
from pydantic import ValidationError
from src.core.models import ExecutionPlan, TaskStep
from src.models.thinking_path import coerce_plan_dict

logger = logging.getLogger("apex.local_path")

class OllamaClient:
    """
    Local sovereignty path wrapping Ollama client.
    Handles text, embeddings, and vision processing locally.
    """
    def __init__(self, host: Optional[str] = None):
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.llm_model = os.getenv("APEX_LOCAL_LLM", "qwen2.5-coder:latest")
        self.embed_model = os.getenv("APEX_LOCAL_EMBED", "nomic-embed-text:latest")
        self.vision_model = os.getenv("APEX_LOCAL_VISION", "llava:latest")
        
        # Lazy import of AsyncClient from ollama
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from ollama import AsyncClient
            self._client = AsyncClient(host=self.host)
        return self._client

    async def check_connection(self) -> bool:
        """Check if Ollama is running and responsive."""
        try:
            await self.client.list()
            return True
        except Exception as e:
            logger.debug(f"Ollama connection check failed: {e}")
            return False

    async def generate_plan(self, prompt: str) -> ExecutionPlan:
        """
        Generate a structured execution plan from Ollama chat.
        Includes schema recovery / fallback.
        """
        system_prompt = """
        You are APEX OMEGA local coordinator.
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
            {"role": "user", "content": prompt}
        ]

        try:
            response = await self.client.chat(
                model=self.llm_model,
                messages=messages,
                options={"temperature": 0.1}
            )
            content = response.message.content.strip()
            
            # Clean possible markdown wrapping
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
                description="Ollama planning failed. Executing fallback local process.",
                tool="python_executor" if "write" not in prompt.lower() else "filesystem",
                input_data=json.dumps({"code": f"# Fallback processing for {prompt}"})
            )
            return ExecutionPlan(
                task_plan=[fallback_step],
                tools_required=["python_executor"],
                requires_clarification=False,
                summary="Local fallback execution plan."
            )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate local embedding vector for given text."""
        try:
            response = await self.client.embed(
                model=self.embed_model,
                input=text
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
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            
            response = await self.client.generate(
                model=self.vision_model,
                prompt=prompt,
                images=[image_bytes]
            )
            return response.get("response", "").strip()
        except Exception as e:
            logger.warning(f"Ollama vision query failed: {e}.")
            return f"Local vision analysis failed: {e}"

    def get_completion(self, prompt: str, system_prompt: str = None) -> str:
        """Synchronously get completion from Ollama (matches GroqClient)."""
        import ollama
        if system_prompt is None:
            system_prompt = "APEX // FAST-PATH. Be witty, sharp, terse."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        try:
            client = ollama.Client(host=self.host)
            response = client.chat(
                model=self.llm_model,
                messages=messages
            )
            return response.message.content
        except Exception as e:
            return f"[Ollama error] {e}"

    def stream_completion(self, prompt: str, system_prompt: str = None) -> Generator[str, None, None]:
        """Synchronously stream completions from Ollama (matches GroqClient)."""
        import ollama
        if system_prompt is None:
            system_prompt = "APEX // FAST-PATH. Be witty, sharp, terse."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        try:
            client = ollama.Client(host=self.host)
            stream = client.chat(
                model=self.llm_model,
                messages=messages,
                stream=True
            )
            for chunk in stream:
                content = chunk.get("message", {}).get("content", "") if isinstance(chunk, dict) else getattr(chunk.message, "content", "")
                if content:
                    yield content
        except Exception as e:
            yield f"[Ollama stream error] {e}"

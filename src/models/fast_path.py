import os
from groq import Groq
from dotenv import load_dotenv

from src.core.time_context import TimeContext
from src.core.api_security import sanitize_error, detect_threat, KeyThreat, leaked_key_warning

class GroqClient:
    """
    A client for interacting with the Groq API for fast inference.
    Uses 'openai/gpt-oss-20b' as the high-speed default model.
    """
    DEFAULT_MODEL = "openai/gpt-oss-20b"
    FALLBACK_MODELS = ["openai/gpt-oss-20b", "qwen/qwen3.8-27b", "openai/gpt-oss-120b"]

    def __init__(self, model: str = None):
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key) if api_key else None
        configured_model = model or os.getenv("GROQ_MODEL", self.DEFAULT_MODEL)
        # Self-heal legacy or invalid compound-mini identifier
        if configured_model in ("groq/compound-mini", "compound-mini"):
            configured_model = self.DEFAULT_MODEL
        self.model = configured_model

    def get_completion(self, prompt: str, system_prompt: str = None) -> str:
        """
        Sends a prompt to the Groq API and returns the response.
        """
        if not self.client:
            return "[Fast-Path Offline] GROQ_API_KEY missing. Falling back to thinking_path required."
        if system_prompt is None:
            system_prompt = """
            IDENT: APEX // FAST-PATH INFRASTRUCTURE
            MODE: CONVERSATIONAL REASONING AGENT
            PERSONA: Intelligent, Conversational, Articulate, Reasoning Partner.

            You are APEX, an intelligent AI companion and system architect. Be conversational, articulate, helpful, and insightful. Respond clearly and directly to both technical and out-of-the-box questions.
            """
        system_prompt = f"{TimeContext.system_prefix()}\n{system_prompt}"
        # Cap prompt to prevent 413 Request Entity Too Large on Groq
        if len(prompt) > 12000:
            prompt = prompt[-12000:]

        models_to_try = [self.model]
        for fb in self.FALLBACK_MODELS:
            if fb not in models_to_try:
                models_to_try.append(fb)

        last_error = None
        for m in models_to_try:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    model=m,
                )
                self.model = m
                return chat_completion.choices[0].message.content
            except Exception as e:
                last_error = e
                err_str = str(e)
                threat = detect_threat(err_str)
                if threat == KeyThreat.LEAKED:
                    return leaked_key_warning("Groq", rich=False)
                if "model_not_found" in err_str or "does not exist" in err_str or "404" in err_str:
                    continue
                return f"[Groq error] {sanitize_error(e)}"

        return f"[Groq error] {sanitize_error(last_error)}"

    def stream_completion(self, prompt: str, system_prompt: str = None):
        """
        Streams chunks from Groq for low-latency UI rendering.
        """
        if not self.client:
            yield "[Fast-Path Offline]"
            return
        if system_prompt is None:
            system_prompt = "APEX // FAST-PATH Sentinel. Be sharp, independent, and direct."
        system_prompt = f"{TimeContext.system_prefix()}\n{system_prompt}"

        models_to_try = [self.model]
        for fb in self.FALLBACK_MODELS:
            if fb not in models_to_try:
                models_to_try.append(fb)

        for m in models_to_try:
            try:
                stream = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    model=m,
                    stream=True,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
                self.model = m
                return
            except Exception as e:
                err_str = str(e)
                threat = detect_threat(err_str)
                if threat == KeyThreat.LEAKED:
                    yield leaked_key_warning("Groq", rich=False)
                    return
                if "model_not_found" in err_str or "does not exist" in err_str or "404" in err_str:
                    continue
                yield f"[Groq stream error] {sanitize_error(e)}"
                return

    async def get_completion_async(self, prompt: str, system_prompt: str = None) -> str:
        """
        Non-blocking async wrapper around get_completion.
        """
        import asyncio
        return await asyncio.to_thread(self.get_completion, prompt, system_prompt)


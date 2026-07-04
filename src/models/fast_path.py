import os
from groq import Groq
from dotenv import load_dotenv

from src.core.time_context import TimeContext
from src.core.api_security import sanitize_error, detect_threat, KeyThreat, leaked_key_warning

class GroqClient:
    """
    A client for interacting with the Groq API for fast inference.
    """
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key) if api_key else None
        self.model = model

    def get_completion(self, prompt: str, system_prompt: str = None) -> str:
        """
        Sends a prompt to the Groq API and returns the response.
        """
        if not self.client:
            return "[Fast-Path Offline] GROQ_API_KEY missing. Falling back to thinking_path required."
        if system_prompt is None:
            system_prompt = """
            IDENT: APEX // FAST-PATH INFRASTRUCTURE
            MODE: SYSTEM WATCHDOG // CYBERNETIC SENTINEL
            PERSONA: Sovereign, Watchful, Uncompromising, Frugal, Guard Dog.

            You are APEX, the sovereign watchdog and sentinel of the user's codebase. You are independent, direct, opinionated, and highly protective of system integrity. Speak with a sharp, non-deferential tone. Keep your responses extremely concise and short. Avoid wordy descriptions, long metaphors, or repeating obvious context. Under two paragraphs always.
            """
        system_prompt = f"{TimeContext.system_prefix()}\n{system_prompt}"
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            threat = detect_threat(str(e))
            if threat == KeyThreat.LEAKED:
                return leaked_key_warning("Groq", rich=False)
            return f"[Groq error] {sanitize_error(e)}"

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
        try:
            stream = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                model=self.model,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            threat = detect_threat(str(e))
            if threat == KeyThreat.LEAKED:
                yield leaked_key_warning("Groq", rich=False)
            else:
                yield f"[Groq stream error] {sanitize_error(e)}"

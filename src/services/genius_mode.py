"""
GeniusMode — APEX's high-thinking critique layer.

Wraps any task with a 5-stage cognitive loop:
  1. CROSS-QUESTION  — surface ambiguity in the user's intent
  2. RIGHT/WRONG     — what user is doing well, what they're missing
  3. BLIND SPOTS     — second-order consequences they haven't considered
  4. PLAN-OF-ACTION  — concrete next steps with rationale
  5. WIT             — a dry one-liner so it doesn't feel like a TED talk

Drives Gemini 2.5 Flash with strict JSON output. Falls back to MiMo/Groq if
Gemini is unavailable.

Usage from main.py:
  /genius <prompt>          — run the full loop, render panels
  /critique <prompt>        — RIGHT/WRONG only
  /blindspot <prompt>       — blind spots + suggestions only

Called inline by harness `pre_step_critique()` to challenge each tool call
before it executes.
"""

import os
import json
import asyncio
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv

try:
    from google import genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None

from src.core.time_context import TimeContext

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_RING_MODEL = "inclusionai/ring-2.6-1t:free"


SYSTEM_PROMPT = """\
You are APEX-Genius, the high-thinking critique layer inside APEX.

Your job: act like a brilliant senior engineer + product strategist who
genuinely wants the user to grow. Be sharp, specific, and a touch witty —
never preachy, never generic.

For any user prompt or proposed action, deliver FIVE things in this order:

  1. CROSS_QUESTION — 1-3 questions you'd ask before committing to this path.
     Each question must have a `why_it_matters` and a `default_assumption`.

  2. RIGHT — bulleted list of what the user IS doing correctly. Cite the
     specific decision/word/phrase you're praising. Empty list if nothing.

  3. WRONG — bulleted list of what they're getting wrong or missing. Cite
     the specific thing. Brutal but constructive. Empty list if clean.

  4. BLIND_SPOTS — 1-3 second-order consequences or hidden tradeoffs the
     user hasn't named. Each is one sentence.

  5. ACTION — ranked list of 2-4 concrete next steps with rationale. The
     #1 step must be safe-to-do-now; later steps depend on it.

  6. ONE_LINER — a single dry-witty sentence (think Jarvis, not stand-up).
     Make it land. No emojis.

OUTPUT FORMAT: pure JSON, no prose, no markdown fence:
{
  "cross_question": [
    {"q": "...", "why_it_matters": "...", "default_assumption": "..."}
  ],
  "right": ["..."],
  "wrong": ["..."],
  "blind_spots": ["..."],
  "action": [
    {"rank": 1, "step": "...", "rationale": "..."}
  ],
  "one_liner": "..."
}

RULES:
  - Be concrete. "Use a queue" is weak; "Use Redis Streams here because
    your fanout pattern is N:M" is strong.
  - Don't repeat the user's question back at them.
  - If the user is clearly correct, say so in `right` and keep `wrong` empty.
  - The one-liner is mandatory, even if short.
"""


def _safe_json_parse(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        # drop leading "json" if present
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except Exception:
        # try slicing to outermost braces
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except Exception:
                return None
    return None


class GeniusMode:
    """
    High-thinking critique wrapper. Returns structured analysis suitable
    for direct rendering or for feeding back into a planning loop.
    """

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(self, model_name: str = DEFAULT_MODEL,
                 mimo_client=None, groq_client=None):
        load_dotenv()
        self.model_id = model_name
        api_key = os.getenv("GEMINI_API_KEY")
        self.gemini = (
            genai.Client(api_key=api_key) if (genai and api_key) else None
        )
        self.mimo = mimo_client
        self.groq = groq_client

    @property
    def is_online(self) -> bool:
        return bool(self.gemini) or (self.mimo and self.mimo.is_online) or (self.groq and self.groq.client)

    # ── core call ───────────────────────────────────────────────────────
    async def analyze(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns structured genius analysis. Never raises — returns an
        offline-style stub if all brains unreachable.
        """
        if not prompt or not prompt.strip():
            return self._stub("empty prompt")

        user_block = (
            f"USER PROMPT:\n{prompt.strip()}\n\n"
            + (f"CONTEXT:\n{context.strip()}\n\n" if context else "")
            + "Return JSON only."
        )
        full = f"{TimeContext.system_prefix()}\n{SYSTEM_PROMPT}\n\n{user_block}"

        # 1. Try Gemini
        if self.gemini:
            try:
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(
                    None,
                    lambda: self.gemini.models.generate_content(
                        model=self.model_id,
                        contents=full,
                        config={"response_mime_type": "application/json"},
                    ),
                )
                parsed = _safe_json_parse(res.text or "")
                if parsed:
                    return self._validate(parsed)
            except Exception:
                pass

        # 2. Fallback MiMo
        if self.mimo and self.mimo.is_online:
            try:
                txt = await self.mimo.aget_completion(
                    user_block, system_prompt=SYSTEM_PROMPT, max_tokens=2048, temperature=0.4
                )
                parsed = _safe_json_parse(txt)
                if parsed:
                    return self._validate(parsed)
            except Exception:
                pass

        # 3. Fallback Groq
        if self.groq and self.groq.client:
            try:
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(
                    None,
                    lambda: self.groq.client.chat.completions.create(
                        model=self.groq.model,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_block},
                        ],
                        temperature=0.4,
                    ),
                )
                parsed = _safe_json_parse(res.choices[0].message.content or "")
                if parsed:
                    return self._validate(parsed)
            except Exception:
                pass

        # 4. Fallback OpenRouter ring-2.6-1t (1T-param free reasoning model)
        or_key = os.getenv("OPENROUTER_API_KEY")
        if or_key:
            try:
                headers = {
                    "Authorization": f"Bearer {or_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://apex-os.local",
                    "X-Title": "APEX Sovereign OS",
                }
                payload = {
                    "model": _RING_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_block},
                    ],
                }
                async with httpx.AsyncClient(timeout=120.0) as hc:
                    r = await hc.post(_OPENROUTER_URL, headers=headers, json=payload)
                    r.raise_for_status()
                    txt = r.json()["choices"][0]["message"]["content"] or ""
                parsed = _safe_json_parse(txt)
                if parsed:
                    return self._validate(parsed)
            except Exception:
                pass

        return self._stub("no brain available")

    # ── shortcuts for slash subcommands ─────────────────────────────────
    async def critique_only(self, prompt: str) -> Dict[str, Any]:
        full = await self.analyze(prompt)
        return {"right": full.get("right", []), "wrong": full.get("wrong", []),
                "one_liner": full.get("one_liner", "")}

    async def blindspots_only(self, prompt: str) -> Dict[str, Any]:
        full = await self.analyze(prompt)
        return {"blind_spots": full.get("blind_spots", []),
                "action": full.get("action", []),
                "one_liner": full.get("one_liner", "")}

    async def pre_step_critique(self, goal: str, proposed_step: str) -> Dict[str, Any]:
        """Used by harness to challenge an upcoming tool call."""
        prompt = (
            f"User goal: {goal}\n\nAbout to execute step: {proposed_step}\n\n"
            f"Is this the right next move? If yes, say so concisely in `right`. "
            f"If no, put the better step in `action[0]`."
        )
        return await self.analyze(prompt)

    # ── helpers ─────────────────────────────────────────────────────────
    @staticmethod
    def _validate(d: Dict[str, Any]) -> Dict[str, Any]:
        for key, default in [
            ("cross_question", []),
            ("right", []),
            ("wrong", []),
            ("blind_spots", []),
            ("action", []),
            ("one_liner", ""),
        ]:
            d.setdefault(key, default)
        return d

    @staticmethod
    def _stub(reason: str) -> Dict[str, Any]:
        return {
            "cross_question": [
                {
                    "q": "What does success look like in 2 sentences?",
                    "why_it_matters": "Pins the goal before any tool fires.",
                    "default_assumption": "User wants the smallest viable change.",
                }
            ],
            "right": ["Asking before acting — that's already saving you debt."],
            "wrong": [],
            "blind_spots": [
                "Genius brain unavailable right now — answers will be generic.",
            ],
            "action": [
                {"rank": 1, "step": f"Set GEMINI_API_KEY or MIMO_API_KEY to unlock real critique ({reason}).",
                 "rationale": "Without a brain online, this stub is the best I can offer."}
            ],
            "one_liner": "I'd insult your idea, but I'm running on autopilot.",
        }

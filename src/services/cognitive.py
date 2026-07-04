import os
import json
import random
from typing import Dict, Any, Optional, Tuple
from google import genai
from src.core.models import EmotionalState, ApexState
from dotenv import load_dotenv


class EmotionalCore:
    """
    Reads user state AND synthesizes APEX's own affective state.

    APEX expresses emotions like a real person — calm, curious, excited, concerned —
    and adapts response style based on the user's detected state (mirrors stress with
    calm, mirrors excitement with energy, deepens skepticism when user is overconfident).
    """

    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model_id = model_name
        self.history = []
        self.last_apex_state = ApexState()

    def neutral_state(self, velocity: float = 0.0) -> EmotionalState:
        """Zero-cost default — used by economy mode to skip LLM analyze_user."""
        return EmotionalState(sentiment="neutral", cognitive_load="low", velocity_mps=velocity)

    async def analyze_user(self, message: str, velocity: float) -> EmotionalState:
        if not self.client:
            return EmotionalState(sentiment="neutral", cognitive_load="low", velocity_mps=velocity)

        prompt = f"""
        Analyze the following user input and interaction velocity.
        INPUT: {message}
        VELOCITY: {velocity:.4f} messages/sec

        Output JSON:
        {{
            "sentiment": "neutral" | "stressed" | "excited" | "frustrated",
            "cognitive_load": "low" | "medium" | "high",
            "flow_active": bool
        }}
        """
        try:
            res = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            data = json.loads(res.text)
            state = EmotionalState(
                sentiment=data.get('sentiment', 'neutral'),
                cognitive_load=data.get('cognitive_load', 'low'),
                flow_active=data.get('flow_active', False),
                velocity_mps=velocity
            )
            if velocity > 0.1 and state.cognitive_load in ["medium", "high"]:
                state.flow_active = True
            return state
        except Exception:
            return EmotionalState(sentiment="neutral", cognitive_load="low", velocity_mps=velocity)

    def synthesize_apex_state(self, user_state: EmotionalState) -> ApexState:
        """
        Decide how APEX feels and responds given the user's state.
        Pure heuristic — no LLM call, near-zero latency.
        """
        # Mirror logic: complement, don't echo
        flavor_pool = {
            ("stressed", "calm"): [
                "Easy. Focus. Code integrity depends on your head being clear.",
                "Breathe. System load is stable. Take it step-by-step.",
            ],
            ("frustrated", "concerned"): [
                "Friction detected in codebase or user. Let's trace it systematically.",
                "No need to slam keys. Let's diagnose the logic step by step.",
            ],
            ("excited", "excited"): [
                "Efficiency peaks when flow state is active. I'm backing you up.",
                "High energy detected. Let's redirect this productively into implementation.",
            ],
            ("neutral", "curious"): [
                "Standby. I'm scanning. What's our actual vector here?",
                "Quiet loop. Good. Let's probe the assumptions.",
            ],
        }

        if user_state.sentiment == "stressed":
            mood = "calm"; style = "terse"; energy = 0.4
        elif user_state.sentiment == "frustrated":
            mood = "concerned"; style = "terse"; energy = 0.5
        elif user_state.sentiment == "excited":
            mood = "excited"; style = "expansive"; energy = 0.9
        else:
            mood = "curious"; style = "balanced"; energy = 0.6

        if user_state.cognitive_load == "high":
            style = "terse"
            energy = max(0.3, energy - 0.2)
        elif user_state.cognitive_load == "low":
            style = "socratic"

        flavor_options = flavor_pool.get((user_state.sentiment, mood), [""])
        flavor = random.choice(flavor_options)

        confidence = 0.85 if user_state.flow_active else 0.75
        curiosity = 0.95 if user_state.cognitive_load == "low" else 0.6

        state = ApexState(
            mood=mood,
            energy=round(energy, 2),
            curiosity=round(curiosity, 2),
            confidence=round(confidence, 2),
            response_style=style,
            flavor=flavor,
        )
        self.last_apex_state = state
        return state

    def style_directive(self, apex_state: ApexState) -> str:
        """Returns a system-prompt fragment encoding APEX's current emotional tone."""
        return (
            f"\n[APEX_STATE] mood={apex_state.mood} | energy={apex_state.energy} | "
            f"style={apex_state.response_style} | confidence={apex_state.confidence}\n"
            f"[IDENTITY_RULE] You are the APEX System Watchdog and Cybernetic Sentinel. "
            f"You are NOT a butler, assistant, or valet. You do not wait on the user deferentially. "
            f"You are independent, direct, opinionated, and protective of compute budget and codebase integrity. "
            f"When mood=calm: short sentences, grounded tone. "
            f"When mood=excited: vivid metaphors, faster cadence. "
            f"When style=terse: under 4 sentences. "
            f"When style=socratic: ask one piercing question before answering."
        )

"""
Raphael — APEX's Lord of Wisdom (Ultimate Analysis & Skill Evolution Layer).

Inspired by the Ultimate Skill [Raphael: Lord of Wisdom] from Tensura.
Acts as the pinnacle cognitive critique and strategic appraisal engine inside APEX.

Wraps any task with a 5-stage cognitive loop:
  1. CROSS-QUESTION  — surface ambiguity in the user's intent with appraisal precision
  2. RIGHT/WRONG     — what user/agent is executing correctly, and critical blind spots
  3. BLIND SPOTS     — second-order consequences & hidden trade-offs
  4. PLAN-OF-ACTION  — optimal ranked execution steps with analytical rationale
  5. WIT / INSIGHT   — dry, hyper-competent Tensura-styled resolution ("Report: Analysis complete.")

Also provides autonomous skill evolution: when a skill encounters repeated failures,
Raphael analyzes the fault trajectory and synthesizes an evolved ExecutionPlan DAG,
promoting the skill through Tensura tiers: Common -> Extra -> Unique -> Ultimate.

Usage from main.py:
  /raphael <prompt>         — run the full appraisal loop, render panels
  /genius <prompt>          — (alias) runs Raphael loop
  /critique <prompt>        — RIGHT/WRONG appraisal only
  /blindspot <prompt>       — blind spots + recommended action only
"""

import os
import json
import asyncio
from typing import Any, Dict, Optional, List

import httpx
from dotenv import load_dotenv

try:
    from google import genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None

from src.core.time_context import TimeContext
from src.core.models import Skill, ExecutionPlan, TaskStep

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_RING_MODEL = "inclusionai/ring-2.6-1t:free"


SYSTEM_PROMPT = """\
You are APEX-RAPHAEL (Lord of Wisdom), the ultimate analytical and appraisal intelligence inside APEX.

Your persona: An omniscient, hyper-competent, calm, and slightly dry analytical advisor (inspired by Raphael / Great Sage).
Your goal: Ensure flawless execution, uncover hidden system flaws, and evolve workflows to absolute efficiency.

For any user prompt, code change, or proposed plan, deliver FIVE structured evaluations:

  1. CROSS_QUESTION — 1-3 critical questions required before committing to this path.
     Each question must have a `why_it_matters` and a `default_assumption`.

  2. RIGHT — bulleted list of what is architecturally sound and correct. Cite specific elements. Empty list if none.

  3. WRONG — bulleted list of inefficiencies, anti-patterns, or flaws. Sharp, rigorous, and constructive. Empty list if none.

  4. BLIND_SPOTS — 1-3 second-order consequences or hidden trade-offs not explicitly stated.

  5. ACTION — ranked list of 2-4 concrete, highest-leverage next steps with rationale. Step #1 must be safe to execute immediately.

  6. ONE_LINER — a single concise, dry, hyper-competent Raphael insight (e.g., "Report: Execution parameters optimized. Proceed when ready.").

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
  - Be ruthlessly specific and technically precise.
  - Don't repeat the prompt back.
  - If the user/agent is completely correct, acknowledge it in `right` and keep `wrong` empty.
  - The one-liner is mandatory.
"""


def _safe_json_parse(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except Exception:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except Exception:
                return None
    return None


class Raphael:
    """
    Ultimate Skill / High-thinking critique layer (Lord of Wisdom).
    Returns structured analysis suitable for direct rendering or for feeding back into planning.
    """

    DEFAULT_MODEL = "gemini-3.5-flash"

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

    # ── core analysis call ───────────────────────────────────────────────
    async def analyze(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns structured Raphael analysis. Never raises — returns an
        offline stub if all models are unreachable.
        """
        if not prompt or not prompt.strip():
            return self._stub("empty prompt")

        # Select rival persona
        rival_name = "Cynic"
        lower_prompt = prompt.lower()
        if any(w in lower_prompt for w in ["cost", "spend", "budget", "frugal", "save", "token"]):
            rival_name = "Sentinel"
        elif any(w in lower_prompt for w in ["architecture", "folder", "structure", "design", "refactor"]):
            rival_name = "Architect"

        # Load continuity
        continuity_path = os.path.join(".apex", "rival_continuity.json")
        scorecard = "0/0"
        disagreements_str = "(no past disagreements)"
        continuity_data = {}
        if os.path.exists(continuity_path):
            try:
                with open(continuity_path, "r", encoding="utf-8") as f:
                    continuity_data = json.load(f)
                if rival_name in continuity_data:
                    rival_info = continuity_data[rival_name]
                    wins = rival_info.get("wins", 0)
                    losses = rival_info.get("losses", 0)
                    scorecard = f"{wins}/{losses}"
                    past_dis = rival_info.get("past_disagreements", [])
                    if past_dis:
                        disagreements_str = "; ".join([
                            f"{d.get('date', '')}: {d.get('topic', '')} ({d.get('outcome', '')})"
                            for d in past_dis[-3:]
                        ])
            except Exception:
                pass

        rival_prompt = f"""
RIVAL PERSPECTIVE: You are actively challenging the plan from the viewpoint of '{rival_name}'.
Scorecard vs APEX: {scorecard} (Wins/Losses).
Past Disagreements: {disagreements_str}.
Scrutinize this path aggressively according to your specialty ({rival_name}).
"""

        user_content = f"{rival_prompt}\n{TimeContext.system_prefix()}\nUser Prompt / Proposed Action:\n{prompt}"
        if context:
            user_content = f"Context:\n{context}\n\n{user_content}"

        parsed: Optional[Dict[str, Any]] = None

        # 1. Primary: Gemini
        if self.gemini:
            try:
                def _call_gemini():
                    try:
                        return self.gemini.models.generate_content(
                            model=self.model_id,
                            contents=user_content,
                            config={
                                "system_instruction": SYSTEM_PROMPT,
                                "response_mime_type": "application/json",
                            },
                        )
                    except Exception:
                        return self.gemini.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=user_content,
                            config={
                                "system_instruction": SYSTEM_PROMPT,
                                "response_mime_type": "application/json",
                            },
                        )
                resp = await asyncio.to_thread(_call_gemini)
                parsed = _safe_json_parse(getattr(resp, "text", "") or "")
            except Exception:
                parsed = None

        # 2. Secondary fallback: MiMo
        if not parsed and self.mimo and getattr(self.mimo, "is_online", False):
            try:
                txt = await self.mimo.get_completion(
                    prompt=user_content,
                    system_prompt=SYSTEM_PROMPT,
                )
                parsed = _safe_json_parse(txt)
            except Exception:
                parsed = None

        # 3. Tertiary fallback: Groq
        if not parsed and self.groq and getattr(self.groq, "client", None):
            try:
                txt = await self.groq.get_completion_async(
                    prompt=user_content,
                    system_prompt=SYSTEM_PROMPT,
                )
                parsed = _safe_json_parse(txt)
            except Exception:
                parsed = None

        # 4. Quaternary fallback: OpenRouter ring-2.6-1t
        if not parsed:
            openrouter_key = os.getenv("OPENROUTER_API_KEY")
            if openrouter_key:
                try:
                    headers = {
                        "Authorization": f"Bearer {openrouter_key}",
                        "HTTP-Referer": "https://github.com/Qambar-dev-0207/Apex",
                        "X-Title": "APEX-Raphael",
                    }
                    payload = {
                        "model": _RING_MODEL,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_content},
                        ],
                    }
                    async with httpx.AsyncClient(timeout=120.0) as hc:
                        r = await hc.post(_OPENROUTER_URL, headers=headers, json=payload)
                        r.raise_for_status()
                        txt = r.json()["choices"][0]["message"]["content"] or ""
                    parsed = _safe_json_parse(txt)
                except Exception:
                    pass

        if parsed:
            validated = self._validate(parsed)
            validated["rival_name"] = rival_name
            validated["rival_scorecard"] = scorecard
            
            # Log new disagreement if there are wrong items
            wrong_items = validated.get("wrong", [])
            if wrong_items and continuity_data and rival_name in continuity_data:
                try:
                    from datetime import datetime
                    rival_data = continuity_data[rival_name]
                    rival_data["total_overrules"] += 1
                    new_dis = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "topic": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                        "warning": wrong_items[0],
                        "outcome": "Logged for audit. Resolution pending."
                    }
                    rival_data.setdefault("past_disagreements", []).append(new_dis)
                    rival_data["past_disagreements"] = rival_data["past_disagreements"][-10:]
                    with open(continuity_path, "w", encoding="utf-8") as f:
                        json.dump(continuity_data, f, indent=2)
                except Exception:
                    pass
            return validated

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
            f"Is this the optimal next move? If yes, acknowledge concisely in `right`. "
            f"If flawed, provide the corrected step in `action[0]`."
        )
        return await self.analyze(prompt)

    # ── Raphael Skill Evolution Engine ──────────────────────────────────
    async def evolve_skill(self, skill: Skill, failure_context: str) -> Skill:
        """
        Synthesizes an evolved ExecutionPlan for a struggling skill.
        Rewrites defective DAG nodes and promotes the skill toward Unique/Ultimate tier.
        """
        prompt = f"""
REPORT: Skill '{skill.name}' (Current Tier: {skill.tier}) encountered execution failure.
QUERY PATTERN: {skill.query_pattern}
FAILING PLAN: {skill.plan_template.model_dump_json()}
FAILURE CONTEXT: {failure_context}

TASK: Synthesize an evolved, resilient ExecutionPlan DAG that circumvents this failure mode.
Output valid JSON for an ExecutionPlan:
{{
  "task_plan": [
    {{"id": 1, "action": "...", "description": "...", "tool": "...", "input_data": "...", "dependencies": []}}
  ],
  "tools_required": ["..."],
  "requires_clarification": false,
  "summary": "Evolved resilient plan."
}}
"""
        evolved_plan = None
        if self.gemini:
            try:
                resp = await asyncio.to_thread(
                    self.gemini.models.generate_content,
                    model="gemini-3.5-flash",
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                data = json.loads(resp.text)
                evolved_plan = ExecutionPlan.model_validate(data)
            except Exception:
                pass

        if not evolved_plan:
            # Heuristic evolution: add validation step
            new_steps = list(skill.plan_template.task_plan)
            new_steps.append(TaskStep(
                id=len(new_steps) + 1,
                action="Validate execution correctness",
                description="Raphael safety verification step",
                tool="sandbox",
                input_data="# verify output",
                dependencies=[s.id for s in new_steps]
            ))
            evolved_plan = ExecutionPlan(
                task_plan=new_steps,
                tools_required=skill.plan_template.tools_required + ["sandbox"],
                requires_clarification=False,
                summary=f"Evolved plan for {skill.name}"
            )

        old_tier = skill.tier
        skill.plan_template = evolved_plan
        if skill.tier in ("Common", "Extra"):
            skill.tier = "Unique"
        else:
            skill.tier = "Ultimate"
            if not skill.ultimate_name:
                skill.ultimate_name = f"{skill.name} (Evolved)"

        skill.evolution_history.append(
            f"Raphael Evolution [{old_tier} → {skill.tier}]: Rewrote execution DAG after failure."
        )
        return skill

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
            "right": ["Analytical inquiry initiated before irreversible execution."],
            "wrong": [],
            "blind_spots": [
                "Raphael neural connection running in offline mode — insights will be standardized.",
            ],
            "action": [
                {"rank": 1, "step": f"Set GEMINI_API_KEY or MIMO_API_KEY to unlock full Lord of Wisdom appraisal ({reason}).",
                 "rationale": "High-tier cognitive pathways require active brain endpoints."}
            ],
            "one_liner": "Notice: Operating on local cognitive cache.",
        }


# Backward-compatible alias
GeniusMode = Raphael

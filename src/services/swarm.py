"""
Multi-agent swarm — APEX spawns specialist agents in parallel.

Minimal v1: Architect / Coder / Critic. Each agent reads shared blackboard,
posts own thoughts, runs in parallel. Coordinator decomposes goal, runs
specialists, synthesizes final artifact.

No tool scoping yet — thinking-only. Agents produce text artifacts; user (or
APEX execution path) acts on output. Tool-using agents = v2.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv

try:
    from google import genai
except Exception:
    genai = None

from src.core.time_context import TimeContext


SPECIALIST_PROMPTS = {
    "architect": """You are APEX's ARCHITECT specialist.
Role: design solutions at the system level.
Output style: stack choices with one-line rationale, component diagram (bullet hierarchy),
data flow in 3-5 sentences. Be specific. Cut filler.
""",
    "coder": """You are APEX's CODER specialist.
Role: propose concrete implementation.
Output style: file paths + code skeletons (not full files, just signatures + key logic).
Mention dependencies. Note language idioms. Be terse.
""",
    "critic": """You are APEX's CRITIC specialist.
Role: find flaws others missed.
Output style: numbered list of risks/gaps/edge-cases. Each item = 1 line.
Rank by severity. No flattery. If you genuinely have nothing to add, say "no significant gaps".
""",
    "researcher": """You are APEX's RESEARCHER specialist.
Role: surface relevant prior art / libraries / patterns.
Output style: bullet list of references with 1-line "why relevant" each.
Prefer well-known battle-tested options over novel ones.
""",
    "planner": """You are APEX's PLANNER specialist.
Role: decompose into ordered sub-tasks.
Output style: numbered list, verb-led, each task day-1 actionable.
Mark dependencies. Estimate effort (S/M/L) per task.
""",
}


class Blackboard:
    """Shared async-safe message log all agents read/write."""

    def __init__(self):
        self.posts: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def post(self, agent: str, role: str, content: str):
        async with self._lock:
            self.posts.append({
                "agent": agent,
                "role": role,
                "content": content,
                "ts": datetime.now().isoformat(),
            })

    def read_all(self) -> List[Dict[str, Any]]:
        return list(self.posts)

    def render_for_agent(self, exclude_agent: str = "") -> str:
        """Format blackboard as context string excluding given agent's own posts."""
        lines = []
        for p in self.posts:
            if p["agent"] == exclude_agent:
                continue
            lines.append(f"[{p['role'].upper()} / {p['agent']}]: {p['content'][:600]}")
        return "\n\n".join(lines) if lines else "(blackboard empty)"


class Agent:
    """A single specialist agent."""

    def __init__(self, name: str, role: str, console=None,
                 model_id: str = "gemini-2.5-flash",
                 client=None, system_prompt_override: str = ""):
        self.name = name
        self.role = role
        self.console = console
        self.model_id = model_id
        self.client = client
        self.system_prompt = system_prompt_override or SPECIALIST_PROMPTS.get(
            role, f"You are APEX's {role.upper()} specialist."
        )
        self.memory: List[Dict[str, str]] = []

    def _log(self, msg: str):
        if self.console:
            self.console.print(f"[dim cyan][Agent:{self.name}][/dim cyan] {msg}")

    async def think(self, goal: str, blackboard: Blackboard) -> str:
        """Read blackboard + own memory, produce next contribution."""
        if not self.client:
            return f"({self.name} offline — no Gemini client)"

        ctx = blackboard.render_for_agent(exclude_agent=self.name)
        own_history = "\n".join(f"[me]: {m['content'][:400]}" for m in self.memory[-3:])

        prompt = f"""{TimeContext.system_prefix()}

{self.system_prompt}

GOAL:
{goal}

OTHER AGENTS' CONTRIBUTIONS:
{ctx}

YOUR OWN PRIOR NOTES (if any):
{own_history or "(none yet)"}

Produce your next contribution. Be focused on YOUR role only — don't duplicate
what other specialists already covered. If they covered your angle adequately,
add ONE missing nuance instead of repeating.

Max 350 words. Markdown formatting.
""".strip()

        try:
            res = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=prompt,
            )
            output = (res.text or "").strip()
        except Exception as e:
            self._log(f"think fail: {e}")
            output = f"({self.name} error: {e})"

        self.memory.append({"content": output, "ts": datetime.now().isoformat()})
        await blackboard.post(self.name, self.role, output)
        return output


class Swarm:
    """
    Coordinator + specialists.

    Flow:
      1. Coordinator decomposes goal (which specialists are needed)
      2. Spawn requested specialists
      3. Run them in parallel for `rounds` rounds (each reads blackboard, posts)
      4. Coordinator synthesizes final artifact from blackboard
    """

    DEFAULT_ROSTER = ["architect", "coder", "critic"]

    def __init__(self, console=None, model_id: str = "gemini-2.5-flash",
                 deep_model_id: str = "gemini-2.5-pro"):
        load_dotenv()
        self.console = console
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if (genai and api_key) else None
        self.model_id = model_id
        self.deep_model_id = deep_model_id

    def _log(self, msg: str, level: str = "info"):
        if not self.console:
            return
        color = {"info": "bright_blue", "warn": "yellow", "err": "red", "ok": "green"}.get(level, "white")
        self.console.print(f"[bold {color}][Swarm] {msg}[/bold {color}]")

    async def _decompose(self, goal: str) -> List[str]:
        """Coordinator picks roster from available specialists."""
        if not self.client:
            return self.DEFAULT_ROSTER
        roster_options = list(SPECIALIST_PROMPTS.keys())
        prompt = f"""You are APEX's swarm coordinator. Pick which specialists to spawn for this goal.

GOAL: {goal}

AVAILABLE SPECIALISTS: {roster_options}

Output JSON: {{"roster": ["role1", "role2", "role3"]}}
Rules:
- 2-4 specialists max.
- Always include "critic" unless goal is purely informational.
- Pick by role-fit, not symmetry.
""".strip()
        try:
            res = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            data = json.loads(res.text or "{}")
            roster = data.get("roster", []) or self.DEFAULT_ROSTER
            roster = [r for r in roster if r in roster_options]
            return roster[:4] or self.DEFAULT_ROSTER
        except Exception as e:
            self._log(f"decompose fail: {e}, using default roster", level="warn")
            return self.DEFAULT_ROSTER

    async def _synthesize(self, goal: str, blackboard: Blackboard) -> str:
        """Coordinator merges blackboard into final artifact."""
        if not self.client:
            return blackboard.render_for_agent()

        all_posts = blackboard.render_for_agent()
        prompt = f"""You are APEX's swarm coordinator. Synthesize the final artifact from
the specialists' contributions. Resolve disagreements, drop redundancy, present
the unified verdict.

GOAL: {goal}

SPECIALIST CONTRIBUTIONS:
{all_posts}

Output markdown:

## Verdict
1-3 sentences. The bottom-line answer to the goal.

## Plan
Numbered, day-1 actionable steps. Cite which specialist contributed each.

## Risks (from Critic)
Top 3, ranked.

## Open Questions
What still needs the user's input.

Be terse. No filler.
""".strip()
        try:
            res = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.deep_model_id,
                contents=prompt,
            )
            return (res.text or "").strip() or "(empty synthesis)"
        except Exception as e:
            self._log(f"synth fail: {e}", level="err")
            return all_posts

    async def run(self, goal: str, rounds: int = 1,
                  roster: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run swarm against goal. Returns artifact + blackboard transcript.
        """
        if not self.client:
            return {
                "ok": False,
                "error": "no_gemini_client",
                "goal": goal,
            }

        roster = roster or await self._decompose(goal)
        self._log(f"roster: {roster}", level="info")

        blackboard = Blackboard()
        agents = [
            Agent(name=f"{r}-1", role=r, console=self.console,
                  model_id=self.model_id, client=self.client)
            for r in roster
        ]

        for rnd in range(max(1, rounds)):
            self._log(f"round {rnd + 1}/{rounds} — {len(agents)} agents thinking", level="info")
            await asyncio.gather(*[a.think(goal, blackboard) for a in agents])

        self._log("synthesizing...", level="info")
        artifact = await self._synthesize(goal, blackboard)

        return {
            "ok": True,
            "goal": goal,
            "roster": roster,
            "rounds": rounds,
            "artifact": artifact,
            "transcript": blackboard.read_all(),
        }

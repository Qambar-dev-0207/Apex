"""
ThinkPartner — APEX's cognitive collaborator.

Six capabilities:
  - cross_question:  surface ambiguity, force clarification before answering
  - architect:       propose optimal architecture for a project idea + critique user's
  - debate:          steelman opposing view, then synthesize
  - brainstorm:      divergent ideation (N distinct angles)
  - teach:           layered explanation tuned to inferred user level
  - extract_intent:  decompose vague prompt into structured task graph

Hands-free auto-trigger: InputClassifier routes ambiguous/architectural prompts here
before plan execution. Slash commands force a specific mode.
"""

import os
import re
import json
import asyncio
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv

try:
    from google import genai
except Exception:
    genai = None

from src.core.time_context import TimeContext


# ── pattern triggers (cheap heuristic before LLM classify) ──────────────────
_BUILD_RE = re.compile(
    r"\b("
    r"i want to build|i'm building|i am building|"
    r"build (?:a|an|the) |design (?:a|an|the) |"
    r"how (?:do|should|would) i build|"
    r"create (?:a|an|the) (?:project|system|app|service|api|tool|pipeline)|"
    r"architect (?:a|an|the) |"
    r"i'?m planning to build|i'?m planning a|"
    r"thinking (?:about|of) building|"
    r"considering (?:building|creating|making)|"
    r"review my (?:architecture|design|approach|plan|stack|code)|"
    r"check my (?:architecture|design|approach|plan)|"
    r"feedback on my (?:architecture|design|approach)|"
    r"how (?:do|should) i (?:get )?start(?:ed)?|where (?:do|should) i start"
    r")",
    re.IGNORECASE,
)
_DECIDE_RE = re.compile(
    r"\b("
    r"should i|"
    r"which is (?:better|right|best)|"
    r"what'?s the best|"
    r"how do i choose|"
    r"trade-?offs?|"
    r"pros and cons|"
    r"is it (?:better|worth|smart|wise)|"
    r"compare \w+ (?:and|to|vs|with) \w+|"
    r"\w+ vs\.? \w+|"
    r"\w+ or \w+\?$|"
    r"convince me"
    r")",
    re.IGNORECASE,
)
_BRAINSTORM_RE = re.compile(
    r"\b("
    r"brainstorm|"
    r"ideas? for|"
    r"alternatives?|"
    r"different (?:approaches|ways|options)|"
    r"what if we|how could we|"
    r"creative ways|"
    r"out of the box"
    r")",
    re.IGNORECASE,
)
_TEACH_RE = re.compile(
    r"\b("
    r"explain|"
    r"teach me|"
    r"what (?:is|are) (?:a |an |the )?[\w\-]+\??$|"
    r"how does .* work|"
    r"help me understand|"
    r"why does|"
    r"walk me through|"
    r"break down (?:the |how )"
    r")",
    re.IGNORECASE,
)
_HELP_RE = re.compile(
    r"\b("
    r"stuck on|"
    r"having trouble|"
    r"can'?t figure (?:it )?out|"
    r"don'?t know (?:how|where|what) to|"
    r"not sure (?:how|where|what)"
    r")",
    re.IGNORECASE,
)


def detect_think_mode(text: str) -> Optional[str]:
    """Cheap regex heuristic — returns mode name or None."""
    if _BUILD_RE.search(text):
        return "architect"
    if _DECIDE_RE.search(text):
        return "debate"
    if _BRAINSTORM_RE.search(text):
        return "brainstorm"
    if _TEACH_RE.search(text):
        return "teach"
    if _HELP_RE.search(text):
        return "cross_question"
    return None


# ── intent extraction gate ───────────────────────────────────────────────────
_COMMAND_LIKE = re.compile(
    r"^(git|npm|pip|cd|ls|mkdir|rm|mv|cp|cat|run|exec|kill|start|stop|"
    r"delete|remove|add|update|install|fix|implement|refactor|rename)\b",
    re.IGNORECASE,
)


def should_extract_intent(text: str) -> bool:
    """
    Returns True if prompt is non-trivial enough to justify a Gemini intent
    extraction call. Used to gate cost — short / command-like prompts skip.
    """
    t = text.strip()
    if len(t) < 25:
        return False
    if _COMMAND_LIKE.match(t):
        return False
    # at least 4 words for it to be worth the call
    if len(t.split()) < 4:
        return False
    return True


class ThinkPartner:
    """
    Cognitive collaborator. Wraps Gemini for structured thinking modes.

    All methods return a dict with at least:
      { "mode": str, "output": str (markdown), "questions": List[str] (optional),
        "next_action": str (suggested follow-up) }
    """

    def __init__(self, console=None, model_id: str = "gemini-2.5-flash",
                 deep_model_id: str = "gemini-2.5-pro",
                 fast_model_id: str = "gemini-2.5-flash-lite"):
        load_dotenv()
        self.console = console
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if (genai and api_key) else None
        self.model_id = model_id
        self.deep_model_id = deep_model_id
        self.fast_model_id = fast_model_id  # for cheap intent extraction

    def _log(self, msg: str, level: str = "info"):
        if not self.console:
            return
        color = {"info": "bright_magenta", "warn": "yellow", "err": "red"}.get(level, "white")
        self.console.print(f"[bold {color}][Think] {msg}[/bold {color}]")

    async def _gen(self, prompt: str, deep: bool = False, json_mode: bool = False,
                   fast: bool = False) -> str:
        if not self.client:
            return ""
        if fast:
            model = self.fast_model_id
        elif deep:
            model = self.deep_model_id
        else:
            model = self.model_id
        cfg = {"response_mime_type": "application/json"} if json_mode else {}
        prompt_with_time = f"{TimeContext.system_prefix()}\n\n{prompt}"
        try:
            res = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model,
                contents=prompt_with_time,
                config=cfg or None,
            )
            return res.text or ""
        except Exception as e:
            self._log(f"gen fail ({model}): {e}", level="warn")
            return ""

    # ────────────────────────────────────────────────────────────────────────
    # 1. cross_question — clarify before answering
    # ────────────────────────────────────────────────────────────────────────
    async def cross_question(self, prompt: str, context: str = "") -> Dict[str, Any]:
        """
        Surfaces ambiguity. Returns 3-6 high-leverage clarifying questions
        ordered by which most affect the answer. User answers them, then
        we proceed to the actual task.
        """
        sys_prompt = f"""
You are APEX's clarification engine. The user asked something. Before answering,
identify what's MISSING that would change the answer significantly.

USER PROMPT:
{prompt}

CONTEXT (may be empty):
{context[:2000]}

Output JSON:
{{
  "ambiguity_score": 0.0-1.0,
  "interpretation": "<=120 chars — your best read of what they want",
  "questions": [
    {{"q": "<the question>", "why_it_matters": "<=80 chars", "default_assumption": "<your guess if unanswered>"}}
  ],
  "ready_to_proceed_without_answers": true|false,
  "minimal_must_answer": ["q_text", "..."]   // 1-2 questions that BLOCK progress
}}

Rules:
- 3-6 questions max. Cut anything cosmetic.
- Each question must change the answer if answered differently.
- Prefer concrete questions ("Postgres or SQLite?") over vague ones ("what's the scale?").
- If prompt is unambiguous, set ambiguity_score < 0.3 and questions = [].
""".strip()
        raw = await self._gen(sys_prompt, json_mode=True, fast=True)
        try:
            data = json.loads(raw) if raw else {}
        except Exception:
            data = {}
        return {
            "mode": "cross_question",
            "ambiguity_score": data.get("ambiguity_score", 0.5),
            "interpretation": data.get("interpretation", ""),
            "questions": data.get("questions", []),
            "must_answer": data.get("minimal_must_answer", []),
            "ready": data.get("ready_to_proceed_without_answers", False),
            "next_action": "Answer the must-answer questions, then re-run.",
        }

    # ────────────────────────────────────────────────────────────────────────
    # 2. architect — design + critique
    # ────────────────────────────────────────────────────────────────────────
    async def architect(self, idea: str, user_architecture: str = "",
                        constraints: str = "") -> Dict[str, Any]:
        """
        For project ideas. Three passes:
          1. Optimal architecture (APEX's proposal)
          2. Critique of user's architecture (if provided)
          3. Synthesis: which to pick + why + concrete next steps
        """
        sys_prompt = f"""
You are APEX's principal architect. The user has a project idea. Produce a
rigorous design review.

PROJECT IDEA:
{idea}

USER'S PROPOSED ARCHITECTURE (may be empty):
{user_architecture or "(none provided)"}

CONSTRAINTS (timeline, budget, stack lock-ins):
{constraints or "(none specified)"}

Produce markdown sections:

## 1. Optimal Architecture (my proposal)
- Stack choices with one-line rationale per choice (LANGUAGE / FRAMEWORK / DB / DEPLOYMENT / KEY LIBS)
- Component diagram (ASCII or bullet hierarchy)
- Data flow: 3-5 sentences end-to-end
- Why this beats alternatives — name 2 alternatives you rejected and why

## 2. Critique of Your Architecture
{"" if not user_architecture else "(Honest pushback. Be specific.)"}
{"Skip this section — no user architecture provided." if not user_architecture else ""}
- What's missing
- What's over-engineered
- Hidden costs / scaling cliffs
- Security/correctness risks

## 3. Synthesis
- Which approach wins (mine / yours / hybrid) and one-line reason
- Top 3 risks ranked by severity, with mitigation
- First 3 concrete next steps (verb-led, day-1 actionable)
- One question I'd ask before writing code

Be terse. Cut filler. Push back hard if their idea has flaws — flattery is harmful here.
""".strip()
        output = await self._gen(sys_prompt, deep=True)
        return {
            "mode": "architect",
            "output": output or "(no response — Gemini key may be missing)",
            "next_action": "Pick winning approach, address top risk, start step 1.",
        }

    # ────────────────────────────────────────────────────────────────────────
    # 3. debate — adversarial pushback
    # ────────────────────────────────────────────────────────────────────────
    async def debate(self, claim: str, user_position: str = "") -> Dict[str, Any]:
        """
        Steelman the OPPOSITE of the user's position, then synthesize. Used
        when user is about to make a decision and you want a stress test.
        """
        sys_prompt = f"""
You are APEX's adversarial reviewer. Steelman the opposing view, then synthesize.

USER'S CLAIM / DECISION:
{claim}

USER'S CURRENT POSITION (may be empty):
{user_position or "(implied as supporting the claim)"}

Produce markdown:

## Strongest Counter-Argument
The most compelling case AGAINST the user's position. No strawmen.
3-5 bullets, each specific and concrete. Cite real evidence/examples when possible.

## What the Counter-Argument Misses
The strongest defense of the user's original position against that counter.

## Synthesis
- Where the user is right
- Where the counter is right
- The reframe: what's the RIGHT question they should be asking?
- Recommendation: stay / pivot / dig deeper, with one-line rationale

Be direct. If you genuinely agree with the user after steelmanning, say so —
don't manufacture disagreement.
""".strip()
        output = await self._gen(sys_prompt, deep=True)
        return {
            "mode": "debate",
            "output": output or "(no response — Gemini key may be missing)",
            "next_action": "Reread synthesis. If reframe lands, restart from new question.",
        }

    # ────────────────────────────────────────────────────────────────────────
    # 4. brainstorm — divergent ideation
    # ────────────────────────────────────────────────────────────────────────
    async def brainstorm(self, topic: str, n: int = 6,
                         constraints: str = "") -> Dict[str, Any]:
        """
        Generate N distinct angles. Each must use a DIFFERENT mental model
        (first principles / analogy / inversion / scaling / constraint-relax / steal-from-other-domain).
        """
        sys_prompt = f"""
You are APEX's idea generator. Produce {n} GENUINELY DIFFERENT ideas — not
variations on a theme. Use distinct mental models.

TOPIC:
{topic}

CONSTRAINTS (may be empty):
{constraints or "(none)"}

For each idea use a DIFFERENT lens:
1. First principles: strip to the smallest version that solves the core
2. Analogy: borrow from a different domain (biology, games, physics, finance)
3. Inversion: solve the OPPOSITE problem and see what falls out
4. Scaling: 100x / 0.01x — what changes structurally?
5. Constraint relax: remove the most binding constraint — what becomes possible?
6. Steal-from-domain: pick a high-performing system in an unrelated field; copy its mechanism

Output as markdown numbered list. For each idea:
- **Lens** (which of the 6 above)
- **Idea** (1 sentence)
- **Why it might win** (1 sentence)
- **Why it might fail** (1 sentence)

End with: **Top pick + reason** (your highest-leverage bet).

Be ambitious. Boring ideas are worse than wrong ideas here.
""".strip()
        output = await self._gen(sys_prompt, deep=True)
        return {
            "mode": "brainstorm",
            "output": output or "(no response — Gemini key may be missing)",
            "next_action": "Pick 1-2 to prototype. Don't spread thin.",
        }

    # ────────────────────────────────────────────────────────────────────────
    # 5. teach — layered explanation
    # ────────────────────────────────────────────────────────────────────────
    async def teach(self, topic: str, user_level_hint: str = "") -> Dict[str, Any]:
        """
        Layered explanation. Goes from intuition → mechanism → edge cases →
        common misconceptions → exercise.
        """
        sys_prompt = f"""
You are APEX's teacher. Build understanding in layers — don't dump facts.

TOPIC:
{topic}

USER LEVEL (may be empty — infer from topic phrasing):
{user_level_hint or "(infer)"}

Produce markdown:

## Intuition (what & why it matters)
3-4 sentences. Use a concrete metaphor. No jargon yet.

## Mechanism (how it works)
The actual working model. Use precise terms now. Diagram if helpful.

## Worked Example
ONE concrete example showing the mechanism. Walk through it step-by-step.

## Common Misconceptions
2-3 mistakes people make + the right mental model to fix each.

## Edge Cases & Gotchas
2-3 cases where the simple model breaks.

## Self-Test
ONE question that tests whether they actually got it. Provide the answer in
a collapsible spoiler-style: "Answer: ..." at the end.

Aim for the smallest explanation that actually transfers understanding —
NOT a comprehensive textbook chapter.
""".strip()
        output = await self._gen(sys_prompt, deep=True)
        return {
            "mode": "teach",
            "output": output or "(no response — Gemini key may be missing)",
            "next_action": "Try the self-test. If wrong, ask follow-up on the failed step.",
        }

    # ────────────────────────────────────────────────────────────────────────
    # auto_route — smart router (regex first, LLM if non-trivial)
    # ────────────────────────────────────────────────────────────────────────
    async def auto_route(self, text: str, ambiguity_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Decides which mode (if any) APEX should run automatically.

        Returns:
          {
            "mode": "architect|debate|brainstorm|teach|cross_question|execute",
            "source": "regex|intent|ambiguity|skip",
            "ambiguity_score": float,
            "blocking_questions": [str],   # only if mode=cross_question
            "interpretation": str,
          }
        """
        # tier 1: cheap regex
        regex_match = detect_think_mode(text)
        if regex_match:
            return {
                "mode": regex_match,
                "source": "regex",
                "ambiguity_score": 0.0,
                "blocking_questions": [],
                "interpretation": "",
            }

        # tier 2: skip LLM call for trivial/command-like prompts
        if not should_extract_intent(text):
            return {
                "mode": "execute",
                "source": "skip",
                "ambiguity_score": 0.0,
                "blocking_questions": [],
                "interpretation": "",
            }

        # tier 3: LLM intent extraction
        intent = await self.extract_intent(text)
        rec_mode = intent.get("recommended_mode", "execute")
        ambiguity = float(intent.get("ambiguity_score", 0.0) or 0.0)
        blocking = intent.get("blocking_questions", []) or []

        # high ambiguity overrides — force cross_question even if intent says execute
        if ambiguity >= ambiguity_threshold and blocking:
            return {
                "mode": "cross_question",
                "source": "ambiguity",
                "ambiguity_score": ambiguity,
                "blocking_questions": blocking,
                "interpretation": intent.get("implicit_goal", ""),
            }

        if rec_mode in ("architect", "debate", "brainstorm", "teach", "cross_question"):
            return {
                "mode": rec_mode,
                "source": "intent",
                "ambiguity_score": ambiguity,
                "blocking_questions": blocking,
                "interpretation": intent.get("implicit_goal", ""),
            }

        return {
            "mode": "execute",
            "source": "intent",
            "ambiguity_score": ambiguity,
            "blocking_questions": [],
            "interpretation": intent.get("implicit_goal", ""),
        }

    # ────────────────────────────────────────────────────────────────────────
    # 6. extract_intent — structured decomposition
    # ────────────────────────────────────────────────────────────────────────
    async def extract_intent(self, prompt: str, context: str = "") -> Dict[str, Any]:
        """
        Decompose a vague/multi-goal prompt into a structured task graph.
        Used by the router as a smarter pre-classifier.
        """
        sys_prompt = f"""
You are APEX's intent decomposer. Convert the user prompt into structured
intent + actionable sub-tasks.

USER PROMPT:
{prompt}

CONTEXT (may be empty):
{context[:1500]}

Output JSON:
{{
  "primary_intent": "build|debug|explain|decide|research|automate|other",
  "explicit_goal": "<=120 chars — what they literally said",
  "implicit_goal": "<=120 chars — what they probably actually want",
  "ambiguity_score": 0.0-1.0,
  "needs_clarification": true|false,
  "blocking_questions": ["q1", "q2"],
  "sub_tasks": [
    {{"task": "<verb-led>", "depends_on": [], "tool_hint": "filesystem|shell|web|gemini|skill", "effort": "S|M|L"}}
  ],
  "recommended_mode": "execute|cross_question|architect|debate|brainstorm|teach"
}}

Rules:
- sub_tasks: 1-5 items, ordered by dependency.
- recommended_mode: "execute" only if the prompt is concrete and unambiguous.
- needs_clarification: true if blocking_questions has any items.
""".strip()
        raw = await self._gen(sys_prompt, json_mode=True, fast=True)
        safe_default = {
            "mode": "extract_intent", "primary_intent": "other",
            "ambiguity_score": 0.5, "needs_clarification": False,
            "sub_tasks": [], "recommended_mode": "execute",
            "blocking_questions": [],
        }
        if not raw:
            return safe_default
        try:
            return {"mode": "extract_intent", **json.loads(raw)}
        except Exception:
            return safe_default

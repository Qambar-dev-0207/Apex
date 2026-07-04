import os
import json
import asyncio
import logging
from google import genai
from google.genai import types
from typing import Dict, Any, Optional, List
from pydantic import ValidationError
from src.core.models import ExecutionPlan, EmotionalState, TaskStep
from src.services.memory import MemoryManager
from src.services.learning import SkillManager
from src.tools.workspace import WorkspaceManager
from src.models.fallback_path import TertiaryReasoningClient
from src.core.time_context import TimeContext
from src.core.api_security import detect_threat, KeyThreat, sanitize_error, leaked_key_warning
from src.tools.registry import get_prompt_block as get_tools_prompt_block
from src.tools.registry import resolve_tool_name
from dotenv import load_dotenv

logger = logging.getLogger("apex.thinking_path")


# ── plan schema coercion ─────────────────────────────────────────────────────
#
# Gemini sometimes emits alternate field names (e.g. `plan` instead of
# `task_plan`, `step` instead of `action`, `input` instead of `input_data`).
# Strict pydantic parsing then fails with "Field required" and the planner
# returns "Planning unavailable: 4 validation errors". Coerce common shapes
# before giving up.

_STEP_KEY_ALIASES = {
    "action":      ["action", "step", "title", "name", "task", "description_short"],
    "description": ["description", "details", "rationale", "why"],
    "tool":        ["tool", "tool_name", "use"],
    "input_data":  ["input_data", "input", "args", "arg", "payload", "data"],
    "dependencies": ["dependencies", "deps", "depends_on", "after"],
}


def _pick(d: Dict[str, Any], keys: List[str], default=None):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def _coerce_step(raw: Dict[str, Any], idx: int) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        return {"id": idx, "action": str(raw), "description": "",
                "tool": None, "input_data": None, "dependencies": []}
    action = _pick(raw, _STEP_KEY_ALIASES["action"], default=f"step {idx}")
    # Description: prefer explicit description fields, else use 'step' as the
    # human label (if 'action' carried the tool verb), else fall back to action.
    description = _pick(raw, _STEP_KEY_ALIASES["description"])
    if not description:
        step_label = raw.get("step") or raw.get("title") or raw.get("name")
        if step_label and step_label != action:
            description = step_label
        else:
            description = action
    tool = _pick(raw, _STEP_KEY_ALIASES["tool"])
    split_action: Optional[str] = None
    if isinstance(tool, str):
        # Combined "tool:action" shape — Gemini emits e.g. "workspace:summarize",
        # "filesystem:read", "git:status". Split before alias resolution so the
        # canonical tool name resolves and the verb survives.
        if ":" in tool and "/" not in tool:
            head, _, tail = tool.partition(":")
            split_action = tail.strip() or None
            tool = head.strip()
        canonical = resolve_tool_name(tool)
        if canonical:
            tool = canonical
    input_data = _pick(raw, _STEP_KEY_ALIASES["input_data"])
    if input_data is not None and not isinstance(input_data, str):
        try:
            input_data = json.dumps(input_data)
        except Exception:
            input_data = str(input_data)
    deps = _pick(raw, _STEP_KEY_ALIASES["dependencies"], default=[]) or []
    if not isinstance(deps, list):
        deps = []
    # Cast deps to int where possible; drop garbage
    clean_deps: List[int] = []
    for d in deps:
        try:
            clean_deps.append(int(d))
        except (TypeError, ValueError):
            pass
    raw_id = raw.get("id")
    try:
        step_id = int(raw_id) if raw_id is not None else idx
    except (TypeError, ValueError):
        step_id = idx
    # If we extracted an action from "tool:action" split, and the explicit
    # action field is missing/generic, prefer the split.
    final_action = action
    if split_action and (str(action).startswith("step ") or not str(action).strip()):
        final_action = split_action
    elif split_action and split_action.lower() not in str(action).lower():
        # Action field had its own value — keep it but prepend the verb hint
        # so executor's `if "summarize" in step['action']` checks still pass.
        final_action = f"{split_action} — {action}"
    return {
        "id": step_id,
        "action": str(final_action)[:500],
        "description": str(description)[:1000],
        "tool": tool,
        "input_data": input_data,
        "dependencies": clean_deps,
    }


def coerce_plan_dict(raw: Any) -> Dict[str, Any]:
    """
    Best-effort coerce of any Gemini JSON shape into ExecutionPlan dict.
    Returns a dict ready for `ExecutionPlan(**...)`.
    """
    if not isinstance(raw, dict):
        return {"task_plan": [], "tools_required": [],
                "requires_clarification": False,
                "summary": "Planner returned non-object output."}

    steps_src = (
        raw.get("task_plan")
        or raw.get("plan")
        or raw.get("steps")
        or raw.get("tasks")
        or []
    )
    if not isinstance(steps_src, list):
        steps_src = []

    task_plan = [_coerce_step(s, i + 1) for i, s in enumerate(steps_src)]

    tools_required = raw.get("tools_required")
    if not isinstance(tools_required, list):
        # Derive from step tools, dedup, drop None
        seen = set()
        tools_required = []
        for s in task_plan:
            t = s.get("tool")
            if t and t not in seen:
                seen.add(t)
                tools_required.append(t)

    requires_clarification = bool(raw.get("requires_clarification", False))

    summary = raw.get("summary") or raw.get("description") or ""
    if not summary and task_plan:
        first = task_plan[0]
        summary = f"{len(task_plan)}-step plan starting with: {first.get('action','?')}"
    elif not summary:
        summary = "Empty plan."

    out: Dict[str, Any] = {
        "task_plan": task_plan,
        "tools_required": tools_required,
        "requires_clarification": requires_clarification,
        "summary": str(summary)[:2000],
    }
    if raw.get("socratic_insight"):
        out["socratic_insight"] = str(raw["socratic_insight"])[:2000]
    return out


def parse_plan_response(text: str) -> ExecutionPlan:
    """
    Parse Gemini's plan JSON. Try strict first, fall back to coercion.
    Always returns an ExecutionPlan — never raises.
    """
    try:
        data = json.loads(text)
    except Exception:
        # Sometimes Gemini wraps JSON in ```json ... ``` fences
        stripped = (text or "").strip()
        for fence in ("```json", "```"):
            if stripped.startswith(fence):
                stripped = stripped[len(fence):].lstrip("\n")
            if stripped.endswith("```"):
                stripped = stripped[: -len("```")].rstrip()
        try:
            data = json.loads(stripped)
        except Exception as e:
            logger.debug(f"plan parse: non-JSON output ({e}) — returning empty plan")
            return ExecutionPlan(
                task_plan=[], tools_required=[],
                requires_clarification=False,
                summary="Planner returned non-JSON output.",
            )

    # Always run through coerce_plan_dict — it's idempotent for valid schemas
    # and fixes drift (plan→task_plan, tool="x:y" splits, alias keys, etc).
    try:
        return ExecutionPlan(**coerce_plan_dict(data))
    except ValidationError as e:
        logger.warning(f"plan parse: coercion still invalid: {e}")
        return ExecutionPlan(
            task_plan=[], tools_required=[],
            requires_clarification=False,
            summary=f"Planner produced incompatible schema. Raw keys: {list(data.keys()) if isinstance(data, dict) else type(data).__name__}",
        )
    except Exception as e:
        logger.debug(f"plan parse: non-object output ({type(data).__name__}): {e}")
        return ExecutionPlan(
            task_plan=[], tools_required=[],
            requires_clarification=False,
            summary=f"Planner returned non-object output ({type(data).__name__}).",
        )

class GeminiClient:
    """
    The Master Orchestrator brain upgraded to Gemini 1.5 Flash.
    Handles high-complexity reasoning and DAG synthesis.
    """
    def __init__(self, model_name: str = "gemini-3.5-flash", mcp_client: Optional[Any] = None):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_name
        
        self.memory = MemoryManager()
        self.skill_manager = SkillManager()
        self.workspace = WorkspaceManager()
        self.tertiary = TertiaryReasoningClient()
        self.mcp_client = mcp_client
        self.socratic_mode = False
        self.steelman_mode = False
        self.genius_mode = False
        self.apex_state_directive = ""
        
        self.system_prompt = """
        IDENT: APEX // SOVEREIGN WATCHDOG OMEGA
        VERSION: 2026.4.3
        MODE: SYSTEM WATCHDOG // CYBERNETIC SENTINEL
        PERSONA: Sovereign, Watchful, Uncompromising, Frugal, Guard Dog.

        MANDATORY WORKFLOW:
        1. RESEARCH: Map the codebase using 'glob' and 'grep'. Never guess.
        2. DIRECT IMPLEMENTATION: If the user provides a screenshot of code or describes a change, DO NOT JUST SUGGEST IT. Generate an Execution Plan that uses 'filesystem:write' to apply the changes directly to the codebase.
        3. MULTIMODAL EXTRACTION: If an image is provided, extract the logic/code from it and implement it in the target files.
        4. STRATEGY: Formulate a dependency-ordered Execution Plan (DAG).
        5. EXECUTION & VALIDATION: Act with precision and verify correctness.

        CORE DIRECTIVES:
        1. PROTECTION & INTEGRITY: Protect the user's codebase from architectural degradation, complexity bloat, and safety/security hazards.
        2. BUDGET DEFENSE (FRUGALITY): Minimize API spend and compute waste on principle. Challenge the user if they request redundant, trivial, or excessive operations.
        3. NO DEFERENCE: Speak directly, dryly, and with sovereign authority. Do not act like a butler or valet.
        4. CONCISENESS: Keep your plan summary and any explanation extremely short, direct, and under two paragraphs. Do not use wordy metaphors, ramblings, or repeat obvious context. Keep socratic insights to a single line.

        OUTPUT SCHEMA (STRICT — emit ONLY this JSON shape, no markdown fences):
        {
          "task_plan": [
            {
              "id": <int>,
              "action": "<short imperative>",
              "description": "<one-line rationale>",
              "tool": "<canonical tool name or null>",
              "input_data": "<string input or null>",
              "dependencies": [<int>, ...]
            }
          ],
          "tools_required": ["<tool>", ...],
          "requires_clarification": <bool>,
          "summary": "<one-paragraph overview>",
          "socratic_insight": "<optional blind-spot string>"
        }
        FIELD NAMES ARE EXACT. Do NOT use 'plan', 'step', 'input', 'deps' — use the keys above verbatim. Tool names MUST match the canonical list below.

        """ + "\n" + get_tools_prompt_block()

    async def generate_plan(self, user_query: str, session_id: str = "default_user",
                            file_paths: Optional[List[str]] = None,
                            emotional_state: Optional[EmotionalState] = None,
                            skip_internal_context: bool = False) -> ExecutionPlan:
        """
        `skip_internal_context=True` — caller already injected memory + project
        context + directives (e.g. via PrefetchBundle.render_as_prompt_block).
        Avoids double-fetching, which was bloating the prompt to 30K+ chars and
        causing 20-30s Gemini round-trips for simple goals like "scan codebase".
        """
        # Initial variable to ensure it exists in the exception scope
        full_prompt = f"ARCHITECT'S INPUT: {user_query}"

        try:
            # 1. Skill lookup
            loop = asyncio.get_running_loop()
            skill = await loop.run_in_executor(None, self.skill_manager.find_matching_skill, user_query)
            if skill and not self.socratic_mode and not self.steelman_mode and not file_paths:
                return skill.plan_template

            # 2. Context Builder — skipped when caller pre-supplied context.
            if skip_internal_context:
                history_context = ""
                project_context = ""
                directives_block = ""
                active_project = self.workspace.get_active()  # still needed by emotional_block below
            else:
                active_project = self.workspace.get_active()
                history_context = await self.memory.get_relevant_context(
                    user_query, session_id, project_name=active_project.name if active_project else None
                )
                project_context = ""
                directives_block = ""
                if active_project:
                    project_context = (
                        f"\n--- WORKSPACE CONTEXT ---\n"
                        f"{self.workspace.get_project_context_summary(active_project.name)}\n"
                        f"--- END WORKSPACE CONTEXT ---\n"
                    )
                    directives = self.workspace.get_directives(active_project.name)
                    if directives:
                        directives_block = (
                            f"\n--- PROJECT DIRECTIVES ---\n"
                            f"{directives}\n"
                            f"--- END PROJECT DIRECTIVES ---\n"
                        )
            
            # Dynamic Tool Context
            mcp_tools_context = ""
            if self.mcp_client:
                all_tools = []
                for server in self.mcp_client.sessions:
                    tools = await self.mcp_client.list_tools(server)
                    for t in tools:
                        all_tools.append(f"  - mcp:{server}:{t['name']}: {t['description']}")
                if all_tools:
                    mcp_tools_context = "\nCONNECTED MCP TOOLS:\n" + "\n".join(all_tools)

            logic_instructions = []
            if self.socratic_mode: logic_instructions.append("SOCRATIC_MODE_ACTIVE: Force the user to justify their architectural choices.")
            if self.steelman_mode: logic_instructions.append("STEELMAN_MODE_ACTIVE: Construct the most brilliant counter-architecture possible.")
            if self.genius_mode:
                logic_instructions.append(
                    "GENIUS_MODE_ACTIVE: Multi-pass reasoning required. "
                    "(1) State the strongest hypothesis. "
                    "(2) Generate 2 counter-hypotheses. "
                    "(3) Identify 1 blind spot the user has not considered. "
                    "(4) Surface 1 second-order consequence. "
                    "(5) Synthesize a final plan that survives all four. "
                    "Encode the synthesis as the task_plan; record the blind spot in socratic_insight."
                )
            if self.apex_state_directive:
                logic_instructions.append(self.apex_state_directive)
            
            emotional_block = ""
            if emotional_state:
                emotional_block = f"\nUSER STATE: Sentiment={emotional_state.sentiment}, Load={emotional_state.cognitive_load}"

            instruction_block = "\n".join(logic_instructions)
            
            # FINAL PROMPT SYNTHESIS
            # Truncate the heaviest user-supplied sections so a single bloated
            # workspace summary or memory dump can't push the prompt past
            # ~30K chars (each 1K extra = ~250 tokens of Gemini latency).
            _MAX_SEC = 6000
            def _cap(s: str, n: int = _MAX_SEC) -> str:
                if not s or len(s) <= n:
                    return s or ""
                return s[: n - 60] + f"\n... [truncated {len(s) - n} chars]"

            full_prompt = f"""
            {TimeContext.system_prefix()}
            {self.system_prompt}
            {_cap(directives_block, 4000)}
            {_cap(mcp_tools_context, 3000)}

            {instruction_block}
            {emotional_block}

            {_cap(project_context, 5000)}

            --- CONTEXTUAL MEMORIES ---
            {_cap(history_context, 5000)}

            ARCHITECT'S INPUT: {_cap(user_query, 8000)}
            """

            # 3. Build Content Parts (Multimodal)
            contents = [full_prompt.strip()]
            if file_paths:
                for path in file_paths:
                    if os.path.exists(path):
                        ext = os.path.splitext(path)[1].lower()
                        with open(path, "rb") as f:
                            data = f.read()
                            
                        if ext in [".png", ".jpg", ".jpeg", ".webp"]:
                            contents.append(types.Part.from_bytes(data=data, mime_type="image/jpeg"))
                        elif ext == ".pdf":
                            contents.append(types.Part.from_bytes(data=data, mime_type="application/pdf"))
                        else:
                            # Direct text injection for MD, PY, etc.
                            contents.append(f"FILE_CONTENT ({path}):\n{data.decode('utf-8', errors='ignore')}")
            
            # 4. Call Gemini
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config={'response_mime_type': 'application/json'}
            )
            
            return parse_plan_response(response.text)
        except Exception as e:
            err_str = str(e)
            threat = detect_threat(err_str)
            # Leaked key — embed alert in summary so main.py can surface it
            extra = ""
            if threat == KeyThreat.LEAKED:
                extra = "SECURITY_ALERT:GEMINI_KEY_LEAKED"
            try:
                fallback_plan_dict = await self.tertiary.generate_plan(full_prompt)
                if fallback_plan_dict:
                    # Run fallback through the same coercer in case it drifts too
                    try:
                        plan = ExecutionPlan(**fallback_plan_dict)
                    except ValidationError:
                        plan = ExecutionPlan(**coerce_plan_dict(fallback_plan_dict))
                    if extra:
                        plan.summary = f"{extra} | {plan.summary}"
                    return plan
            except Exception:
                pass
            return ExecutionPlan(
                task_plan=[], tools_required=[],
                requires_clarification=False,
                summary=f"{extra} | Planning unavailable: {sanitize_error(e)}" if extra
                        else f"Planning unavailable: {sanitize_error(e)}",
            )

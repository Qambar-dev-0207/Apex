"""
Reflex Brain — deterministic + embedding-based pre-LLM router.

Goal: handle the "no-thinking-needed" decisions WITHOUT paid LLM calls.
Routes the bulk of inputs (~80%) locally; only escalates to Gemini /
ThinkPartner when confidence is low.

What Reflex decides locally:
  - intent (greeting, identity, chat, coding, search, fs, git, vision, ...)
  - complexity (low/medium/high)
  - path  (trivial | tool | fast_path | thinking_path | think_partner:<mode>)
  - tool_pick (canonical tool + action + input_data, when high-conf)
  - autonomous_skill_id (via SkillManager embedding match)
  - requires_memory  (skip RAG for trivial intents)
  - requires_vision  (keyword + file-ext check)
  - needs_llm  (escalate to InputClassifier.classify if confidence low)

Cost model:
  - L1 cache hit:          ~0 ms, $0
  - regex tool match:      <1 ms, $0
  - skill embedding:       5-30 ms (Chroma local), $0
  - intent embedding NN:   10-50 ms (sentence-transformers local), $0
  - LLM fallback (rare):   400-900 ms, $$ (only when needs_llm=True)

Telemetry: Reflex.stats() returns hit/miss/llm-escalation counts so the
caller can prove the savings.
"""

from __future__ import annotations

import re
import time
import math
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List, Tuple

from src.tools.auto_selector import regex_match as tool_regex_match
from src.tools.registry import resolve_tool_name

logger = logging.getLogger("apex.reflex")


# ── intent prototypes (local NN target set) ──────────────────────────────────

INTENT_PROTOTYPES: Dict[str, List[str]] = {
    "greeting":    ["hi", "hello", "hey", "good morning", "yo", "sup", "howdy"],
    "identity":    ["what are you", "who are you", "what is apex",
                    "describe yourself", "what can you do"],
    "chat":        ["explain", "tell me about", "what do you think",
                    "thoughts on", "your opinion"],
    "coding":      ["write code", "implement function", "fix bug",
                    "refactor this", "build a feature", "write a function",
                    "add a method", "create a class"],
    "search":      ["search the web", "look up", "google for",
                    "find online", "what's the latest", "news about"],
    "fs":          ["read file", "open file", "show me file",
                    "list directory", "grep for", "search the codebase",
                    "find files matching"],
    "git":         ["git status", "commit changes", "push to remote",
                    "show diff", "checkout branch", "git log"],
    "exploration": ["analyze project", "what is in this repo",
                    "summarize codebase", "explore the project",
                    "scan workspace"],
    "vision":      ["look at screen", "describe this image",
                    "what's on screen", "ocr this", "see my screen"],
    "media":       ["transcribe", "describe video",
                    "summarize this video", "what's in this audio"],
    "skill":       ["security audit", "optimize performance",
                    "deploy to cloud", "create a new skill"],
    "architect":   ["design a system", "architect this",
                    "how should i build", "trade-offs",
                    "what's the right structure"],
    "debate":      ["argue against", "pushback on",
                    "is this a good idea", "challenge my plan"],
    "brainstorm":  ["brainstorm", "ideas for", "what could i do",
                    "give me options"],
    "teach":       ["teach me", "explain like", "walk me through",
                    "how does X work"],
    # Auto-spawn intents — Reflex routes these directly to swarm/harness
    # without going through Gemini DAG planning.
    "swarm_goal":  ["multi-agent", "spawn agents", "orchestrate agents",
                    "swarm on this", "build end-to-end with agents",
                    "use multiple specialists", "agent team for"],
    "harness_goal": ["do it for me", "act on this autonomously",
                     "go ahead and execute", "run autonomously",
                     "agentic loop on", "make it happen end-to-end",
                     "implement this on your own"],
}

PATH_BY_INTENT: Dict[str, str] = {
    "greeting":    "trivial",
    "identity":    "trivial",
    "chat":        "fast_path",
    "coding":      "thinking_path",
    "search":      "thinking_path",
    "fs":          "tool",
    "git":         "tool",
    "exploration": "thinking_path",
    "vision":      "tool",
    "media":       "tool",
    "skill":       "thinking_path",
    "architect":   "think_partner:architect",
    "debate":      "think_partner:debate",
    "brainstorm":  "think_partner:brainstorm",
    "teach":       "think_partner:teach",
    "swarm_goal":  "swarm",
    "harness_goal": "harness",
}

# Intents where memory retrieval adds no value (skip RAG → save embed + Chroma).
MEMORY_SKIP_INTENTS = {"greeting", "identity", "git", "fs", "vision", "media"}

VISION_KEYWORDS = (
    "screen", "screenshot", "see ", "look at", "ocr", "image",
    "picture", "photo", "what's on",
)
MEDIA_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif",
              ".mp4", ".mov", ".avi", ".webm",
              ".m4a", ".mp3", ".wav", ".ogg")

# Tokens that bump complexity up
COMPLEX_HINTS = (
    "design", "architect", "refactor", "migrate", "audit",
    "optimize", "benchmark", "compare", "trade-off", "strategy",
    "plan", "blueprint", "swarm", "multi-step",
)
TRIVIAL_HINTS = (
    "ls", "pwd", "time", "date", "hello", "hi", "what time",
)


# ── decision schema ──────────────────────────────────────────────────────────

@dataclass
class ReflexDecision:
    intent: str = "chat"
    complexity: str = "low"            # low | medium | high
    priority: int = 3                  # 1 (high) → 3 (low)
    path: str = "fast_path"            # trivial|tool|fast_path|thinking_path|think_partner:<mode>
    tool_pick: Optional[Dict[str, Any]] = None     # {tool, action, input_data}
    autonomous_skill_id: Optional[str] = None
    requires_tools: bool = False
    requires_vision: bool = False
    requires_memory: bool = True
    confidence: float = 0.0            # 0..1
    source_kind: str = "embed"         # regex | trivial | skill | embed | token | empty
    needs_llm: bool = False            # only False for deterministic regex/trivial
    sources: List[str] = field(default_factory=list)  # ["regex","skill","embed",...]
    prefetch_hint: List[str] = field(default_factory=list)   # ["memory","compass","skill","workspace"]
    elapsed_ms: float = 0.0

    def to_classification(self) -> Dict[str, Any]:
        """Adapter — shape that downstream router/main.py already expects."""
        return {
            "intent": self.intent,
            "complexity": self.complexity,
            "priority": self.priority,
            "requires_tools": self.requires_tools,
            "requires_vision": self.requires_vision,
            "autonomous_skill_id": self.autonomous_skill_id,
            "_reflex": {
                "path": self.path,
                "tool_pick": self.tool_pick,
                "requires_memory": self.requires_memory,
                "confidence": self.confidence,
                "needs_llm": self.needs_llm,
                "source_kind": self.source_kind,
                "sources": self.sources,
                "prefetch_hint": list(self.prefetch_hint),
                "elapsed_ms": self.elapsed_ms,
            },
        }


# ── trivial-intent matchers ──────────────────────────────────────────────────

_GREETING_RX = re.compile(
    r"^\s*(hi|hello|hey|yo|sup|howdy|good\s+(morning|afternoon|evening|night))[\s!.,?]*$",
    re.I,
)
_IDENTITY_RX = re.compile(
    r"^\s*(what\s+are\s+you|who\s+are\s+you|what\s+is\s+apex|"
    r"tell\s+me\s+about\s+yourself|what\s+do\s+you\s+do|what\s+can\s+you\s+do|"
    r"are\s+you\s+(an\s+ai|chatgpt|claude))[\s?.!]*$",
    re.I,
)
# Casual small-talk — short open-ended conversational openers that must NOT
# trigger memory retrieval / project directives / compass injection. Without
# this gate, Groq retrieves session memory (recent technical talk) and
# answers "how is life?" with an architecture lecture.
_CASUAL_RX = re.compile(
    r"^\s*("
    r"how\s+(are|is)\s+(you|things|life|it\s+going|everything)|"
    r"how'?s\s+(life|it\s+going|everything|things)|"
    r"what'?s\s+(up|new|good|happening)|"
    r"you\s+(good|ok|okay|there|alive)|"
    r"all\s+good|"
    r"how\s+have\s+you\s+been|"
    r"long\s+time\s+no\s+see|"
    r"nice\s+to\s+(meet|see)\s+you|"
    r"thanks?\s*(you)?|thank\s+you|thx|"
    r"bye|goodbye|see\s+you|see\s+ya|cya|later|gn|good\s+night"
    r")[\s!.,?]*$",
    re.I,
)


# ── token-overlap fallback (when embeddings unavailable) ─────────────────────

_TOKEN_RX = re.compile(r"[a-z0-9]+")


def _tokens(s: str) -> set:
    return set(_TOKEN_RX.findall(s.lower()))


def _token_score(a: str, b: str) -> float:
    """Jaccard similarity with mild length penalty."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union


# ── Reflex brain ─────────────────────────────────────────────────────────────

class Reflex:
    """
    Local routing brain. Wraps regex + embedding + heuristic stages.

    Usage:
        reflex = Reflex(skill_manager=engine.classifier.skill_manager)
        decision = await reflex.decide(prompt)
        if decision.needs_llm:
            classification = await classifier.classify(prompt)
        else:
            classification = decision.to_classification()
    """

    def __init__(
        self,
        skill_manager=None,
        cache_size: int = 256,
        confidence_threshold: float = 0.62,
        adaptive_waste_threshold: float = 0.60,
        adaptive_window: int = 20,
    ):
        self.skill_manager = skill_manager
        self.cache_size = cache_size
        self.confidence_threshold = confidence_threshold

        # LRU cache: prompt → ReflexDecision
        self._cache: Dict[str, ReflexDecision] = {}
        self._cache_order: List[str] = []

        # Telemetry
        self.counters = {
            "calls": 0, "cache_hits": 0, "trivial": 0, "regex_tool": 0,
            "skill_match": 0, "embed_nn": 0, "token_nn": 0, "llm_escalations": 0,
            # Prefetch telemetry — PrefetchBundle reports to Reflex.
            "prefetch_started": 0, "prefetch_used": 0, "prefetch_wasted": 0,
            "prefetch_cache_hits": 0, "prefetch_bytes_saved": 0,
            "prefetch_disabled_auto": 0,
        }

        # Adaptive-disable state: tracks last N scout-mode calls' used/wasted.
        self.adaptive_waste_threshold = adaptive_waste_threshold
        self.adaptive_window = adaptive_window
        self._recent_results: List[bool] = []   # True = bundle used, False = wasted
        self.prefetch_enabled: bool = True       # user-toggleable + auto-toggleable
        self._auto_disabled: bool = False        # set True when adaptive trip fires

        # Lazy embedding model
        self._ef = None
        self._intent_vectors: Optional[Dict[str, Any]] = None

    # ── prefetch telemetry hooks (called by PrefetchBundle) ──────────────────

    def _record_prefetch_started(self, hint_count: int):
        self.counters["prefetch_started"] += 1

    def _record_prefetch_used(self, bytes_saved: int = 0):
        self.counters["prefetch_used"] += 1
        self.counters["prefetch_bytes_saved"] += int(bytes_saved)
        self._push_result(True)

    def _record_prefetch_wasted(self):
        self.counters["prefetch_wasted"] += 1
        self._push_result(False)

    def _record_prefetch_cache_hit(self):
        self.counters["prefetch_cache_hits"] += 1

    def _push_result(self, used: bool):
        self._recent_results.append(used)
        if len(self._recent_results) > self.adaptive_window:
            self._recent_results.pop(0)
        # Trip adaptive disable when enough samples + waste over threshold.
        if (
            self.prefetch_enabled
            and not self._auto_disabled
            and len(self._recent_results) >= self.adaptive_window
        ):
            waste_rate = 1.0 - (sum(self._recent_results) / len(self._recent_results))
            if waste_rate > self.adaptive_waste_threshold:
                self.prefetch_enabled = False
                self._auto_disabled = True
                self.counters["prefetch_disabled_auto"] += 1
                logger.info(
                    f"Reflex: prefetch auto-disabled — waste {waste_rate:.0%} > "
                    f"{self.adaptive_waste_threshold:.0%} over last {self.adaptive_window} calls"
                )

    def set_prefetch_enabled(self, enabled: bool):
        """Manual override (e.g. via `/reflex prefetch on|off`). Clears auto-disable trip."""
        self.prefetch_enabled = enabled
        self._auto_disabled = False
        self._recent_results.clear()

    # ── public ───────────────────────────────────────────────────────────────

    async def decide(self, prompt: str) -> ReflexDecision:
        self.counters["calls"] += 1
        t0 = time.perf_counter()
        key = (prompt or "").strip().lower()[:300]

        if key in self._cache:
            self.counters["cache_hits"] += 1
            d = self._cache[key]
            # Move to MRU
            try:
                self._cache_order.remove(key)
            except ValueError:
                pass
            self._cache_order.append(key)
            return d

        d = self._decide_uncached(prompt)
        d.elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self._cache_put(key, d)
        if d.needs_llm:
            self.counters["llm_escalations"] += 1
        return d

    def stats(self) -> Dict[str, Any]:
        c = dict(self.counters)
        c["cache_size"] = len(self._cache)
        c["hit_rate"] = (c["cache_hits"] / c["calls"]) if c["calls"] else 0.0
        c["llm_skip_rate"] = (
            1.0 - (c["llm_escalations"] / c["calls"]) if c["calls"] else 0.0
        )
        # Prefetch derived metrics
        started = c["prefetch_started"]
        used = c["prefetch_used"]
        c["prefetch_use_rate"] = (used / started) if started else 0.0
        c["prefetch_waste_rate"] = (c["prefetch_wasted"] / started) if started else 0.0
        c["prefetch_enabled"] = self.prefetch_enabled
        c["prefetch_auto_disabled"] = self._auto_disabled
        c["adaptive_window_filled"] = len(self._recent_results)
        return c

    def reset_cache(self):
        self._cache.clear()
        self._cache_order.clear()

    # ── internal ─────────────────────────────────────────────────────────────

    def _cache_put(self, key: str, d: ReflexDecision):
        if key in self._cache:
            return
        self._cache[key] = d
        self._cache_order.append(key)
        while len(self._cache_order) > self.cache_size:
            old = self._cache_order.pop(0)
            self._cache.pop(old, None)

    def _decide_uncached(self, prompt: str) -> ReflexDecision:
        d = ReflexDecision()
        p = (prompt or "").strip()
        low = p.lower()
        if not p:
            d.confidence = 1.0
            d.path = "trivial"
            d.requires_memory = False
            d.source_kind = "empty"
            d.sources.append("empty")
            d.needs_llm = False
            return d

        # Stage A — trivial intents (greeting / identity). Deterministic; safe to skip Gemini.
        if _GREETING_RX.match(p):
            self.counters["trivial"] += 1
            d.intent = "greeting"
            d.path = "trivial"
            d.requires_memory = False
            d.confidence = 0.99
            d.source_kind = "trivial"
            d.sources.append("regex:greeting")
            d.needs_llm = False
            return d

        if _IDENTITY_RX.match(p):
            self.counters["trivial"] += 1
            d.intent = "identity"
            d.path = "trivial"
            d.requires_memory = False
            d.confidence = 0.99
            d.source_kind = "trivial"
            d.sources.append("regex:identity")
            d.needs_llm = False
            return d

        # Casual small-talk: route to clean fast_path WITHOUT injecting memory,
        # directives, compass, or pruned_knowledge. Groq still answers — but
        # with a stripped prompt. Gemini classify is skipped (deterministic).
        if _CASUAL_RX.match(p):
            self.counters["trivial"] += 1
            d.intent = "conversational"
            d.path = "fast_path"
            d.requires_memory = False
            d.requires_tools = False
            d.complexity = "low"
            d.priority = 3
            d.confidence = 0.97
            d.source_kind = "regex"
            d.sources.append("regex:casual")
            d.needs_llm = False  # deterministic intent — no Gemini classify needed
            return d

        # Stage B — regex tool match (instant single-tool intents). Deterministic.
        rx = tool_regex_match(p)
        if rx:
            self.counters["regex_tool"] += 1
            d.tool_pick = rx
            d.intent = self._intent_for_tool(rx["tool"])
            d.path = "tool"
            d.requires_tools = True
            d.requires_memory = False
            d.requires_vision = rx["tool"] == "vision"
            d.complexity = "low"
            d.priority = 2
            d.confidence = float(rx.get("confidence", 0.95))
            d.source_kind = "regex"
            d.sources.append("regex:tool")
            d.needs_llm = False
            return d

        # ── Beyond this point: every path goes through Gemini for thinking ──
        # Reflex is now a *scout* — it pre-picks tools/skill/memory hints and
        # signals which prefetch tasks to spawn in parallel with Gemini.

        # Stage C — skill embedding match (Chroma local, free). Surfaces skill
        # name as a HINT for Gemini — does NOT short-circuit thinking.
        if self.skill_manager is not None:
            try:
                skill = self.skill_manager.find_matching_skill(p, threshold=0.35)
                if skill:
                    self.counters["skill_match"] += 1
                    d.autonomous_skill_id = skill.name
                    d.sources.append("skill")
            except Exception as e:
                logger.debug(f"skill match failed: {e}")

        # Stage D — intent embedding NN (local sentence-transformer).
        intent, sim, src = self._nearest_intent(p)
        d.intent = intent
        d.sources.append(src)
        if src == "embed_nn":
            self.counters["embed_nn"] += 1
        else:
            self.counters["token_nn"] += 1

        # Map intent → path
        d.path = PATH_BY_INTENT.get(intent, "fast_path")
        d.requires_tools = d.path in ("tool", "thinking_path") or d.path.startswith("think_partner:")
        d.requires_memory = intent not in MEMORY_SKIP_INTENTS

        # Complexity heuristic
        d.complexity, d.priority = self._estimate_complexity(p, intent)

        # Vision flags
        self._apply_vision_flags(d, low)

        # Confidence = intent NN similarity
        d.confidence = float(sim)
        d.source_kind = "embed" if src == "embed_nn" else "token"

        # Embedding/token NN ALWAYS escalates to Gemini — local NN cannot be
        # trusted to skip thinking on novel prompts. Reflex only saves the
        # parallel prefetch work, not the reasoning step.
        d.needs_llm = True

        # Targeted prefetch hint — only what this intent will actually use.
        # Adaptive gate: if waste rate has been too high, skip prefetch entirely.
        if self.prefetch_enabled:
            d.prefetch_hint = self._prefetch_for_intent(intent, d.confidence)
        else:
            d.prefetch_hint = []

        return d

    def _prefetch_for_intent(self, intent: str, conf: float) -> List[str]:
        """
        Path-targeted prefetch. NEVER shotgun — only prewarm what the matched
        intent will actually consume. Avoids wasted CPU when Gemini disagrees.

        Confidence floor: don't prefetch at all if conf < 0.30 — Reflex has
        no idea what the prompt is and any prefetch would be a blind guess.
        """
        if conf < 0.30:
            return []
        table = {
            "coding":       ["compass", "memory"],
            "exploration":  ["workspace", "compass"],
            "search":       ["memory"],
            "fs":           ["compass"],
            "git":          [],
            "vision":       [],
            "media":        [],
            "chat":         ["memory"],
            "architect":    ["memory", "compass"],
            "debate":       ["memory"],
            "brainstorm":   ["memory"],
            "teach":        ["memory"],
            "skill":        ["memory"],
            # Auto-spawn intents — feed minimal context; swarm/harness do their own gathering.
            "swarm_goal":   ["memory"],
            "harness_goal": ["compass"],
        }
        return list(table.get(intent, ["memory"]))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _intent_for_tool(self, tool: str) -> str:
        return {
            "git": "git",
            "filesystem": "fs",
            "shell": "fs",
            "web_search": "search",
            "web_fetch": "search",
            "vision": "vision",
            "hardware": "exploration",
            "workspace": "exploration",
            "code_compass": "exploration",
            "knowledge_forge": "search",
            "todo": "chat",
        }.get(tool, "chat")

    def _apply_vision_flags(self, d: ReflexDecision, low: str):
        if any(k in low for k in VISION_KEYWORDS):
            d.requires_vision = True
        if any(low.endswith(ext) or (" " + ext) in low for ext in MEDIA_EXTS):
            d.requires_vision = True

    def _estimate_complexity(self, prompt: str, intent: str) -> Tuple[str, int]:
        low = prompt.lower()
        words = len(prompt.split())
        if any(h in low for h in TRIVIAL_HINTS) or words < 4:
            if intent in ("coding", "architect", "exploration", "skill"):
                return "medium", 2
            return "low", 3
        if any(h in low for h in COMPLEX_HINTS) or words > 40:
            return "high", 1
        if intent in ("coding", "architect", "skill", "exploration"):
            return "high", 1
        if intent in ("search", "fs", "git", "vision"):
            return "low", 3
        return "medium", 2

    # ── intent NN: sentence-transformer if available, else token Jaccard ────

    def _load_ef(self):
        if self._ef is not None:
            return self._ef
        try:
            from src.services.memory import _get_shared_ef
            self._ef = _get_shared_ef()
        except Exception as e:
            logger.debug(f"Reflex: shared EF unavailable, using token fallback: {e}")
            self._ef = False  # sentinel: tried + failed
        return self._ef

    def _build_intent_vectors(self):
        if self._intent_vectors is not None:
            return
        ef = self._load_ef()
        if not ef:
            self._intent_vectors = {}
            return
        vecs: Dict[str, List[List[float]]] = {}
        for intent, protos in INTENT_PROTOTYPES.items():
            try:
                vecs[intent] = ef(protos)  # chroma EF returns list[list[float]]
            except Exception as e:
                logger.debug(f"Reflex: failed to embed {intent}: {e}")
                vecs = {}
                break
        self._intent_vectors = vecs

    def _nearest_intent(self, prompt: str) -> Tuple[str, float, str]:
        """Returns (intent, similarity 0..1, source)."""
        self._build_intent_vectors()
        if self._intent_vectors:
            ef = self._load_ef()
            try:
                qv = ef([prompt])[0]
                best_intent, best_sim = "chat", 0.0
                for intent, vlist in self._intent_vectors.items():
                    for v in vlist:
                        s = _cosine(qv, v)
                        if s > best_sim:
                            best_sim, best_intent = s, intent
                return best_intent, best_sim, "embed_nn"
            except Exception as e:
                logger.debug(f"Reflex: embed NN failed, falling back: {e}")

        # Token-overlap fallback
        best_intent, best_score = "chat", 0.0
        for intent, protos in INTENT_PROTOTYPES.items():
            for proto in protos:
                s = _token_score(prompt, proto)
                if s > best_score:
                    best_score, best_intent = s, intent
        return best_intent, best_score, "token_nn"


# ── math ─────────────────────────────────────────────────────────────────────

# ── PrefetchBundle ───────────────────────────────────────────────────────────

class PrefetchBundle:
    """
    Speculative prefetch runner. Spawns the targeted local-only prefetch tasks
    requested by Reflex's `prefetch_hint`, in parallel with Gemini's classify
    + plan-build round-trip.

    Design constraints (CPU-frugal):
      - Only prefetch what Reflex's intent table says to. No shotgun.
      - Cache by prompt-hash; identical prompts within TTL skip the work.
      - Cancellable: caller can `bundle.cancel()` if Gemini's decision lands
        on a path that doesn't need the prefetched data.
      - Local-only. Never trigger a paid API call from prefetch (no web search,
        no LLM-based pruning, no MCP).

    Returns a dict shaped like:
        {
          "memory": "<retrieved snippets>",
          "compass": "<compressed symbol context>",
          "workspace": "<project summary>",
          "skill": "<skill_id or None>",
          "elapsed_ms": <float>,
        }
    Keys are only present if requested by `hints` and the underlying provider
    succeeded.
    """

    _CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
    _CACHE_TTL = 300.0    # 5 min

    def __init__(
        self,
        hints: List[str],
        prompt: str,
        session_id: str,
        memory_manager=None,
        code_compass=None,
        workspace=None,
        knowledge_visualizer=None,
        skill_manager=None,
        active_project_name: Optional[str] = None,
        reflex: Optional["Reflex"] = None,
    ):
        self.hints = set(hints or [])
        self.prompt = prompt
        self.session_id = session_id
        self.memory_manager = memory_manager
        self.code_compass = code_compass
        self.workspace = workspace
        self.knowledge_visualizer = knowledge_visualizer
        self.skill_manager = skill_manager
        self.active_project_name = active_project_name
        self.reflex = reflex  # optional — for telemetry callbacks

        self._tasks: Dict[str, "asyncio.Task[Any]"] = {}
        self._started_at: float = 0.0
        self._cache_key = f"{session_id}:{prompt.strip().lower()[:200]}"
        self._used: bool = False  # caller flips via mark_used()
        self._closed: bool = False

    @property
    def used(self) -> bool:
        return self._used

    @used.setter
    def used(self, val: bool):
        # Trigger telemetry exactly once on first transition to True.
        if val and not self._used and not self._closed:
            self._used = True
            self._closed = True
            if self.reflex is not None:
                # Estimate bytes saved by summing string lengths of bundle results
                # (rough proxy — actual savings depend on Gemini's token use).
                try:
                    self.reflex._record_prefetch_used(0)
                except Exception:
                    pass
        else:
            self._used = val

    def mark_used(self, bytes_saved: int = 0) -> None:
        """Explicit telemetry hook with byte estimate."""
        if self._closed:
            return
        self._used = True
        self._closed = True
        if self.reflex is not None:
            try:
                self.reflex._record_prefetch_used(bytes_saved)
            except Exception:
                pass

    def mark_wasted(self) -> None:
        """Caller signals bundle was abandoned (path mismatch, error, etc)."""
        if self._closed:
            return
        self._closed = True
        if self.reflex is not None:
            try:
                self.reflex._record_prefetch_wasted()
            except Exception:
                pass

    # ── entry points ─────────────────────────────────────────────────────────

    def start(self) -> "PrefetchBundle":
        """Fire all prefetch tasks (non-blocking). Returns self for chaining."""
        import asyncio as _asyncio
        self._started_at = time.time()
        if self.reflex is not None and self.hints:
            try:
                self.reflex._record_prefetch_started(len(self.hints))
            except Exception:
                pass

        cached = self._cache_get(self._cache_key)
        if cached is not None:
            if self.reflex is not None:
                try:
                    self.reflex._record_prefetch_cache_hit()
                except Exception:
                    pass
            # Wrap cached value in already-done futures so await_all is uniform.
            loop = _asyncio.get_event_loop()
            for k, v in cached.items():
                if k in self.hints:
                    fut = loop.create_future()
                    fut.set_result(v)
                    self._tasks[k] = fut  # type: ignore[assignment]
            return self

        if "memory" in self.hints and self.memory_manager is not None:
            self._tasks["memory"] = _asyncio.create_task(self._do_memory())
        if "compass" in self.hints and self.code_compass is not None:
            self._tasks["compass"] = _asyncio.create_task(self._do_compass())
        if "workspace" in self.hints and self.workspace is not None:
            self._tasks["workspace"] = _asyncio.create_task(self._do_workspace())
        if "skill" in self.hints and self.skill_manager is not None:
            self._tasks["skill"] = _asyncio.create_task(self._do_skill())
        return self

    async def await_all(self, timeout: float = 3.0) -> Dict[str, Any]:
        """
        Wait for all prefetch tasks to complete (or timeout).
        Returns a dict with whatever finished in time.
        """
        import asyncio as _asyncio
        if not self._tasks:
            return {"elapsed_ms": 0.0}

        results: Dict[str, Any] = {}
        try:
            done, pending = await _asyncio.wait(
                list(self._tasks.values()),
                timeout=timeout,
                return_when=_asyncio.ALL_COMPLETED,
            )
            for key, task in self._tasks.items():
                if task in done:
                    try:
                        results[key] = task.result()
                    except _asyncio.CancelledError:
                        # Caller pre-cancelled this task; treat as missing.
                        pass
                    except Exception as e:
                        logger.debug(f"prefetch[{key}] failed: {e}")
            # Cancel any pending tasks that overran timeout
            for task in pending:
                task.cancel()
        except Exception as e:
            logger.debug(f"prefetch await_all error: {e}")

        results["elapsed_ms"] = (time.time() - self._started_at) * 1000.0
        # Cache the per-source results (not elapsed_ms)
        cacheable = {k: v for k, v in results.items() if k != "elapsed_ms"}
        if cacheable:
            self._cache_put(self._cache_key, cacheable)
        return results

    def cancel(self) -> None:
        """Abandon all in-flight prefetch tasks (Gemini took different path)."""
        for task in self._tasks.values():
            if not task.done():
                task.cancel()

    # ── per-source workers (local I/O only) ──────────────────────────────────

    async def _do_memory(self) -> str:
        try:
            return await self.memory_manager.get_relevant_context(
                self.prompt, self.session_id
            )
        except Exception as e:
            logger.debug(f"prefetch memory failed: {e}")
            return ""

    async def _do_compass(self) -> str:
        try:
            # Build index lazily on first hit
            if hasattr(self.code_compass, "index") and not self.code_compass.index:
                # build is sync — push to thread to keep loop responsive
                import asyncio as _asyncio
                await _asyncio.to_thread(self.code_compass.build)
            ctx = self.code_compass.context_for_query(self.prompt, max_files=5)
            return ctx or ""
        except Exception as e:
            logger.debug(f"prefetch compass failed: {e}")
            return ""

    async def _do_workspace(self) -> str:
        try:
            if not self.active_project_name:
                active = self.workspace.get_active()
                if not active:
                    return ""
                self.active_project_name = active.name
            return self.workspace.get_project_context_summary(self.active_project_name)
        except Exception as e:
            logger.debug(f"prefetch workspace failed: {e}")
            return ""

    async def _do_skill(self) -> Optional[str]:
        try:
            import asyncio as _asyncio
            skill = await _asyncio.to_thread(
                self.skill_manager.find_matching_skill, self.prompt, 0.35
            )
            return skill.name if skill else None
        except Exception as e:
            logger.debug(f"prefetch skill failed: {e}")
            return None

    # ── cache (class-level, TTL'd) ───────────────────────────────────────────

    @classmethod
    def _cache_get(cls, key: str) -> Optional[Dict[str, Any]]:
        item = cls._CACHE.get(key)
        if not item:
            return None
        ts, val = item
        if time.time() - ts > cls._CACHE_TTL:
            cls._CACHE.pop(key, None)
            return None
        return val

    @classmethod
    def _cache_put(cls, key: str, val: Dict[str, Any]):
        cls._CACHE[key] = (time.time(), val)
        # Trim if too big
        if len(cls._CACHE) > 128:
            oldest_key = min(cls._CACHE, key=lambda k: cls._CACHE[k][0])
            cls._CACHE.pop(oldest_key, None)

    # ── inject helper ────────────────────────────────────────────────────────

    @staticmethod
    def render_as_prompt_block(bundle: Dict[str, Any]) -> str:
        """
        Format a prefetch result dict as a prompt block to inject into
        Gemini's input. Keeps section names stable so Gemini learns to
        consume them.
        """
        if not bundle:
            return ""
        out = ["--- REFLEX PREFETCH BUNDLE (pre-warmed local context) ---"]
        if bundle.get("skill"):
            out.append(f"PRE_MATCHED_SKILL: {bundle['skill']}")
        if bundle.get("workspace"):
            out.append(f"WORKSPACE_SUMMARY:\n{bundle['workspace']}")
        if bundle.get("memory"):
            out.append(f"RELEVANT_MEMORY:\n{bundle['memory']}")
        if bundle.get("compass"):
            out.append(f"CODE_COMPASS:\n{bundle['compass']}")
        out.append("--- END PREFETCH BUNDLE ---")
        return "\n".join(out)


def _cosine(a, b) -> float:
    # Accepts list[float] or numpy.ndarray. Avoid bool-coercion of arrays.
    try:
        la, lb = len(a), len(b)
    except TypeError:
        return 0.0
    if la == 0 or lb == 0:
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        fx = float(x)
        fy = float(y)
        dot += fx * fy
        na += fx * fx
        nb += fy * fy
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Run & develop

```bash
# Entry point — interactive CLI
python main.py

# Tests (no network required; mocked LLMs/keys)
python -m pytest tests/ -v
python -m pytest tests/test_e2e_full_apex.py -v                       # E2E only
python -m pytest tests/test_e2e_full_apex.py::test_harness_fs_crud_end_to_end -v   # single test

# Windows + Unicode (Rich UI breaks on cp1252 in some terminals)
$env:PYTHONIOENCODING="utf-8"; python main.py
```

There is no Makefile, no linter config, and no build step. The project is a runtime CLI — `python main.py` is the only artifact.

## Environment

`.env` in repo root (see `.env.example`). Required: `GEMINI_API_KEY`, `GROQ_API_KEY`. Optional: `MIMO_API_KEY` (coding pipeline), `OPENROUTER_API_KEY` (fallback brain), `TAVILY_API_KEY`/`BRAVE_API_KEY` (real web search), `REDIS_HOST`/`REDIS_PORT`, `CHROMA_PATH`.

Runtime flags via env:
- `APEX_ECONOMY=1` (default **ON**) — disables cognitive analysis + knowledge pruning + background learning to minimize LLM fan-out. Flip to `0` for "full" mode.
- `APEX_BG_LOOPS=1` — enables `SelfEvolver` + `KnowledgeForge` background ticks (default off).
- `APEX_DAILY_CALL_LIMIT=40` — auto-flips to economy mode after N LLM calls.

## Big-picture architecture

APEX is a layered router that tries to answer in **the cheapest tier that works**, falling through to heavier tiers only when needed. The input pipeline lives in `main.py` (around line 1470+, the `while True:` REPL).

```
  → ! prefix         → shell passthrough
  → / prefix         → handle_slash (60+ commands, main.py:1693)
  → greeting regex   → TimeContext canned reply           [no LLM]
  → identity regex   → canned identity panel              [no LLM]
  → auto_selector regex_match → execute_step              [no LLM, single tool]
  → auto-think       → ThinkPartner.auto_route → architect/debate/etc.
  → core analysis    ← THIS IS THE HOT PATH (see below)
  → fast_path (Groq) OR thinking_path (Gemini DAG) OR skill plan template
  → if plan.task_plan is empty (Conversational / Q&A out-of-the-box question):
      → render single-panel APEX // INTELLECTUAL SYNTHESIS & store memory  [SKIP EXECUTION]
  → else (Multi-step code/system task):
      → ParallelExecutor.run (DAG with asyncio.TaskGroup)
      → assembler.render_final_response + memory store + bg learn
```

### Visual Identity & Mascot System

`src/core/animations.py` (`ApexMascot`):
- **14 Mascot States**: `focus`, `coding`, `thinking`, `learning`, `building`, `analyzing`, `deploying`, `connected`, `happy`, `excited`, `focused`, `determined`, `curious`, `proud`.
- **`ApexMascot.render_blockart(state)`**: Renders crisp full-color terminal block art (Claude Code style) using `▀`/`▄` half-block cells and exact RGB palette colors (`(255, 215, 0)` gold eyes, `#141419` black screen, `#D7C6B2` beige body, status dots). Hand-crafted 16x16 pixel sprite matrices eliminate all JPEG downsampling blur.


### Hot path: Reflex scout + speculative prefetch

`src/core/reflex.py` is the **local pre-LLM router**. It is the single most important file for understanding routing decisions. Two-mode behavior:

1. **Deterministic skip** (`source_kind in {regex, trivial}`): greetings, identity, regex-matched tool intents (`git status`, `read foo.py`). Returns `needs_llm=False`. Gemini classify is bypassed.
2. **Scout-mode** (`source_kind in {embed, token}`): embedding NN match against `INTENT_PROTOTYPES`. Returns `needs_llm=True` always — Gemini still does the thinking. Reflex's job is to fire `PrefetchBundle` (memory + compass + workspace + skill) in **parallel** with Gemini's classify call.

In `main.py`'s `_core_analysis` block: `asyncio.gather(prefetch_bundle.await_all(), classifier.classify())`. Prefetch results get injected into the plan-build prompt via `PrefetchBundle.render_as_prompt_block()`.

Invariant: **never put a paid LLM call inside Reflex or PrefetchBundle.** They must stay local-only (Chroma embed, compass AST, regex). Cost is in CPU only, so waste is cheap. To add a new intent, register a prototype phrase in `INTENT_PROTOTYPES` and a path in `PATH_BY_INTENT`. To add a new prefetch target, extend `_prefetch_for_intent` and add a `_do_<name>` worker.

`InputClassifier.classify` (in `src/routers/router.py`) internally calls `reflex.decide()` first — downstream classification dicts carry a `_reflex` key with `{path, tool_pick, prefetch_hint, source_kind, needs_llm, ...}`. `SmartRouter.route` honors `_reflex.path` over its own heuristics.

### Brains (model providers)

| Role | Module | Provider |
|---|---|---|
| Planner (DAG, architect, genius-mode) | `src/models/thinking_path.py` | Gemini 2.5 Flash |
| Fast chat + stream + synth | `src/models/fast_path.py` | Groq llama-3.1-8b |
| Code implementation | `src/models/mimo_path.py` | Xiaomi MiMo v2.5-pro (OpenAI-compatible) |
| Architecture spec (stage 1 of coding) | `src/models/minimax_path.py` | MiniMax 2.5 |
| Tertiary fallback | `src/models/fallback_path.py` | OpenRouter `gpt-oss-120b` |

Every brain gracefully degrades when its key is missing — `engine.gemini_client` is `None` rather than raising, and the fast path is the universal fallback.

### Tools & execution

Two **separate** tool surfaces — do not confuse them:
- `src/tools/registry.py` — 17 canonical tools used by Gemini DAG planner. Source of truth: the `REGISTRY` dict. Aliases resolved via `resolve_tool_name`. Adding a tool here also requires a matching `elif step['tool'] == "..."` branch in `ParallelExecutor.execute_step` (`src/routers/router.py`).
- `src/core/harness.py` — 35 tools for `AgentHarness`, the autonomous MiMo-driven tool-calling loop invoked via `/harness`. Independent surface; do not mirror changes between them blindly.

### Memory (`src/services/memory.py`)

Three layers, all auto-reconnecting:
- `RedisManager` — short-term session (history, last_plan). Self-heals after 30s cooldown on failure.
- `ChromaManager` — long-term semantic memory, async-safe via `asyncio.to_thread`.
- `ResponseCache` — semantic dedupe of past responses (sub-100ms hits).

A singleton `_get_shared_ef()` returns the sentence-transformer embedding function shared by Chroma, ResponseCache, and Reflex's intent NN — **never load a second EF**.

### Cognitive services

- `src/services/think_partner.py` — 6 modes (`cross_question`, `architect`, `debate`, `brainstorm`, `teach`, `extract_intent`) with `auto_route` (regex → flash-lite escalation). Drives `/think`, `/architect`, etc.
- `src/services/swarm.py` — multi-agent (architect/coder/critic/researcher/planner) over a blackboard, invoked via `/swarm`.
- `src/services/genius_mode.py` — 5-stage critique pipeline. Wired into `gemini_client.genius_mode` toggle.
- `src/services/knowledge_forge/` — ingests arxiv papers + ecosystem feed → capability proposals → optional self-application.
- `src/services/self_evolution.py` — idle-tick self-improvement loop (gated by `APEX_BG_LOOPS`).
- `src/services/code_compass.py` — AST symbol index. Used by Reflex prefetch and the thinking path. Build is lazy; first call builds, subsequent calls reuse.

## Slash commands

All wired in `handle_slash` (`main.py:608`). Full reference: `docs/COMMANDS.md`. Notable ones to know when changing behavior:

- `/reflex` — Reflex telemetry (cache hits, LLM skip rate, per-source counters).
- `/tools` — per-tool success/fail telemetry.
- `/economy on|off` / `/full` — flip the economy gate.
- `/autotool on|off` — toggle regex bypass-planner.
- `/autothink on|off` — toggle auto-routing to ThinkPartner.
- `/harness <goal>` — run the autonomous loop.

## Docs

Detailed docs live in `docs/` — start at `docs/INDEX.md`. Read `docs/ARCHITECTURE.md` for the full input pipeline, `docs/MODELS.md` for brain selection rules, `docs/TOOLS.md` for both tool surfaces, `docs/HARNESS.md` for the autonomous loop, and `docs/TESTING.md` for the 286-test suite layout.

## When adding features

- A new tool: register in `REGISTRY` (`src/tools/registry.py`) **and** add the dispatch branch in `ParallelExecutor.execute_step` (`src/routers/router.py`). Optionally extend `auto_selector._PATTERNS` for a regex fast path.
- A new intent / routing path: add prototype phrases in `reflex.INTENT_PROTOTYPES` + a `PATH_BY_INTENT` entry. If it should bypass memory, add it to `MEMORY_SKIP_INTENTS`. If it needs prewarm, extend `_prefetch_for_intent`.
- A new slash command: extend `handle_slash` in `main.py` and the `SLASH_HELP` constant above it.
- A new brain provider: add a client module under `src/models/`, mirror the graceful-degradation pattern (return `None` when key absent, no exceptions in `__init__`).

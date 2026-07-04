# APEX — Changelog

> Cumulative changes by session. Most-recent first.

---

## 2026-06-16 — Workspace Memory Isolation & Prompt Formatting Fixes

Resolved workspace context bleeding issues, prompt bloating, and LLM directive duplication.

### Added & Modified — Memory Isolation (`src/services/memory.py`)
- **Project-Specific Chroma Filtering**: Modified `MemoryManager.get_relevant_context` and `MemoryManager.store_interaction` to store and filter memories based on `project_name` metadata (`where={"project_name": project_name}`).
- **Integration Across Core Layers**: Propagated active project name context through the prefetch layer (`reflex.py`), thinking path generation (`thinking_path.py`), and the main system loop (`main.py`).

### Added & Modified — Prompt Formatting (`src/tools/workspace.py`, `main.py`, `src/models/thinking_path.py`)
- **Clean Prompt Boundary Tags**: Enclosed `--- PROJECT DIRECTIVES ---` and `--- WORKSPACE CONTEXT ---` sections in distinct opening and closing tags, preventing reasoning models from leaking or repeating headers.
- **Directives Duplication Fix**: Modified workspace context summary generation (`get_project_context_summary`) to exclude directives by default, and conditionalized directive prepending in thinking path prompts to only run when prefetch is active.

---

## 2026-05-08 — Cognitive + Tools + Time + Memory rewrite

Massive build session. 7 new modules + 1 full rewrite + 7 test suites.

### Added — TimeContext (`src/core/time_context.py`)
- Static helper, single source of truth for wall-clock time
- `system_prefix()` auto-prepended to every LLM call (thinking_path / fast_path / think_partner / swarm)
- `is_greeting(text)` detects "hi", "hello", "good morning", "what's up"
- `craft_greeting_response()` time-aware reply ("Good morning. Monday — what's first?" / "Up late — what's the mission?")
- `relative(ts)` — "5 min ago", "yesterday", "last week"
- main.py greeting interceptor → instant reply, skips DAG planner
- `/now` slash — shows date/time/weekday/late-night flag
- 36 tests in `tests/test_time_context.py`

### Added — ThinkPartner (`src/services/think_partner.py`)
Cognitive collaborator with 6 modes:
- `cross_question` — surfaces blocking ambiguity before answering
- `architect` — proposes optimal architecture + critiques user's
- `debate` — steelmans opposing view, then synthesizes
- `brainstorm` — 6 distinct angles via different mental models (first principles / analogy / inversion / scaling / constraint-relax / cross-domain)
- `teach` — layered: intuition → mechanism → example → misconceptions → self-test
- `extract_intent` — structured intent decomposition

Auto-routing in main.py:
- Tier 1: regex `detect_think_mode()` — instant pattern match
- Tier 2: LLM `extract_intent` (flash-lite) for non-trivial prompts
- Ambiguity ≥ 0.6 → cross_question with interactive answer loop

Slash commands: `/think`, `/architect`, `/debate`, `/brainstorm`, `/teach`, `/intent`, `/autothink on|off`. 23 tests in `tests/test_think_partner.py`.

### Added — Multi-Agent Swarm (`src/services/swarm.py`)
Minimal v1 spawn:
- 5 specialists registered: architect, coder, critic, researcher, planner
- `Coordinator` decomposes goal → picks 2-4 specialists via Gemini
- Each `Agent` has private memory + reads shared `Blackboard`
- `Blackboard` async-safe message log; agents excluded from own posts
- Synthesis via Gemini 2.5 Pro

Slash: `/swarm <goal>`, `/swarm <goal> | coder,critic`, `/swarm <goal> rounds=2`. 23 tests in `tests/test_swarm.py`.

### Added — Tool Registry (`src/tools/registry.py`)
14 tools registered with full spec (name + aliases + actions + schema + when-to-use + examples):
- Pre-existing: `filesystem`, `shell`, `git`, `python_executor`, `research_swarm`, `web_search`, `workspace`, `mcp`
- **Newly exposed**: `vision`, `hardware`, `code_compass`, `knowledge_forge`, `swarm`, `think_partner`

Features:
- `resolve_tool_name(raw)` — fuzzy alias map (fs→filesystem, web→web_search, hw→hardware, etc.)
- `get_prompt_block()` auto-generates AVAILABLE TOOLS markdown — replaces hardcoded list in `thinking_path.py`
- `ToolTelemetry` per-tool ok/fail + last-error tracking

Router upgrades (`src/routers/router.py`):
- Aliases resolved at dispatch
- 6 new tool branches for vision/hardware/code_compass/knowledge_forge/swarm/think_partner
- Unknown tools fail loudly with hint listing known tools (was silent success)
- Telemetry recorded on every dispatch

Slash: `/tools` shows registry + per-tool stats. 23 tests in `tests/test_tool_registry.py`.

### Added — AutoToolSelector (`src/tools/auto_selector.py`)
Two-tier autonomous tool picker:
- **Tier 1 — regex**: ~25 patterns for common single-tool intents (git status, read X.py, ls, grep, screenshot, vitals, papers about Y, etc.). Confidence 0.95.
- **Tier 2 — LLM**: `gemini-2.5-flash-lite` ranks candidates with confidence + needs_planning flag.

Wired into main.py before DAG planner: high-confidence single-tool intents bypass full planning. Saves 2-5s per simple prompt.

Slash: `/autotool on|off`. 30 tests in `tests/test_auto_selector.py`.

### Rewrote — Memory subsystem (`src/services/memory.py`)
13 bugs fixed + missing logic added:
- **Self-healing Redis** — 30s retry-after-failure (was permanently dead)
- **Single Redis round-trip** in `store_interaction` (was race-prone)
- **Summarize-before-drop** — when history > cap, oldest entries collapse into `[SUMMARY]` via flash-lite (heuristic fallback)
- **Async Chroma** — all ops via `asyncio.to_thread` (was blocking event loop)
- **TTL pruning** — `prune_older_than(days)`
- **Shared embedding function** — singleton (was 2x model load)
- **Cache stats** — hits/misses/hit_rate
- **Logger** instead of bare `except: pass`
- **Truncation by oldest first**, not mid-cut
- `clear_all_history(include_forge=True)` extends to forge collections

37 tests in `tests/test_memory_system.py`.

### KnowledgeForge expansions
- `ProposalApplier` — diff mode (`<<<SEARCH===REPLACE>>>`) with full-rewrite fallback
- `PipSandbox` — temp venv → install → import-validate → only then install to active env
- `prune_old_backups`, `list_backups`, `restore_backup` ops
- Per-project `.apex/forge_state.json` (was global `data/forge/`)
- arxiv `scan_backfill(days=N)` for catch-up
- `_write_forge_log` → `~/.apex/forge_log.md` after each cycle
- Slash additions: `/forge backfill <N>`, `/forge undo <id>`, `/forge log`, `/forge implement <id> diff`

93 tests in `tests/test_knowledge_forge.py`.

### Stats
- 7 new modules
- 1 full rewrite (memory.py)
- 7 test suites — 279 tests, 100% pass
- ~3500 lines added
- 0 regressions in existing tests

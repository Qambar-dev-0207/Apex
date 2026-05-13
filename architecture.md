# APEX Architecture

> Reflects current code as of 2026-05-13. Full docs: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Core principle

APEX layers smart routing under a "fast path always wins" rule. Simple prompts execute in ms via regex/cache; only ambiguous or multi-step goals reach the full Gemini DAG planner. Every layer ships with a fallback so degradation is graceful, not fatal.

---

## Input pipeline

```
1. user_input
2. UserPromptSubmit hook fires
3. self_evolver.mark_input + knowledge_forge.mark_input
4. ! prefix       → direct shell passthrough
5. / prefix       → handle_slash (~60 commands)
6. greeting?      → TimeContext.craft_greeting_response (instant)
7. autotool on?   → regex_match (git status, ls, ...)
                  → execute_step directly (skip DAG planner)
8. autothink on?  → ThinkPartner.detect_think_mode (regex)
                  → ThinkPartner.extract_intent (LLM tier)
                  → if ambiguity_score >= 0.6 → cross_question (interactive Q&A)
                  → if recommended_mode in (architect/debate/brainstorm/teach) → run mode
9. pending_clarification? → merge user answer with original prompt → re-run
10. fall-through  → cognitive_core.analyze_user → InputClassifier.classify
                  → SmartRouter.route → fast_path or thinking_path
                  → ExecutionPlan (DAG)
                  → ParallelExecutor.run
11. response → memory_manager.store_interaction (Redis + Chroma + summarize)
            → knowledge_visualizer.extract_knowledge
            → learning_manager.learn (background)
            → assembler.render_final_response
```

---

## Brain layer

### Multi-model routing (`src/routers/router.py`)
- `InputClassifier` (Gemini 2.5 Flash Lite) — assigns intent + complexity + tool requirements
- `SmartRouter` — picks `fast_path` (low complexity) or `thinking_path` (tools/high complexity)
- `ParallelExecutor` — DAG-aware concurrent dispatcher with hardware gating + 3-tier failover (agent → Gemini retry → OpenRouter fallback)

### Thinking path (`src/models/thinking_path.py`)
- Gemini 2.5 Flash for plan generation
- System prompt auto-prefixed with `TimeContext.system_prefix()` and `tool_registry.get_prompt_block()` — no hardcoded tool drift
- Modes: `socratic_mode`, `steelman_mode`, `genius_mode` (multi-pass: hypothesis → counters → blind-spot → synthesis)
- Outputs `ExecutionPlan` with task DAG + dependencies

### Fast path (`src/models/fast_path.py`)
- Groq llama-3.1-8b streaming
- TimeContext-injected system prompt

### Code brain (`src/models/mimo_path.py`)
- Xiaomi MiMo v2.5-pro via OpenAI-compatible endpoint at `https://api.xiaomimimo.com/v1`
- Primary brain for AgentHarness autonomous loop
- Stage 2 of 3-stage CodingPipeline (MiniMax arch spec → **MiMo implementation** → Gemini validation)
- Sync, async, streaming interfaces
- `is_online` property; graceful offline fallback

### Fallback (`src/models/fallback_path.py`)
- `TertiaryReasoningClient` — OpenRouter `gpt-oss-120b` for DAG planner recovery
- `HighReasoningClient` — OpenRouter `inclusionai/ring-2.6-1t:free` (1T-param) for ThinkPartner + GeniusMode fallback

### Cognitive collaborator (`src/services/think_partner.py`)
- Six modes: `cross_question`, `architect`, `debate`, `brainstorm`, `teach`, `extract_intent`
- `auto_route()` — 2-tier: regex first (cheap), LLM intent extraction (flash-lite) if non-trivial
- High ambiguity → forces cross_question with blocking-question loop

### Multi-agent swarm (`src/services/swarm.py`)
- `Coordinator` decomposes goal → picks roster from {architect, coder, critic, researcher, planner}
- `Agent` — private memory + reads shared `Blackboard` (excludes own posts)
- `Blackboard` — async-safe message log
- Synthesis via Gemini 2.5 Pro

---

## Memory layer (`src/services/memory.py`)

### `RedisManager` — short-term session
- Self-healing: `RETRY_AFTER=30s` cooldown after failure, then auto-reactivate
- Single round-trip writes (no race in `store_interaction`)
- `delete_session`, `list_session_ids` for resume

### `ChromaManager` — long-term semantic memory
- All ops via `asyncio.to_thread` — no event loop blocking
- `prune_older_than(days)` — TTL-based cleanup
- Auto-injects `ts_unix` metadata for time-aware queries

### `ResponseCache` — semantic LLM dedup
- Threshold-gated semantic similarity match
- Hit/miss stats via `cache.stats()`
- Robust to malformed metadata

### `MemoryManager` — orchestrator
- `history_cap=20` (configurable via `APEX_HISTORY_CAP` env)
- **Summarize-before-drop**: when history exceeds cap, oldest entries collapse into `[SUMMARY]` entry via `gemini-2.5-flash-lite` (heuristic fallback if no key)
- `get_relevant_context` drops oldest history first instead of mid-truncating (preserves structure of recent code/JSON)
- `clear_all_history(include_forge=True)` wipes Redis + Chroma + cache + (optionally) forge collections

### Shared embedding function
- `_get_shared_ef()` singleton — no duplicate sentence-transformer model load

---

## Tools layer

### Registry (`src/tools/registry.py`)
17 registered tools (added: `web_fetch`, `todo`, `diff`), each with: canonical name + aliases + actions + input schema + when-to-use + examples.

| Tool | Actions | When |
|---|---|---|
| `filesystem` | read/write/delete/list/search/glob | source code I/O, ripgrep |
| `shell` | execute | system commands, builds |
| `git` | commit/status/diff/add/push/pull/log/checkout | VCS |
| `python_executor` | write/run | code-gen via pipeline OR sandbox exec |
| `research_swarm` | search | web/file/code multi-agent research |
| `web_search` | search | quick lookup (Tavily/Brave/DDG) |
| `workspace` | scan/summarize/directives/list_projects | project context |
| `mcp` | connect/call | external MCP servers |
| `vision` | capture/ocr/describe/describe_video/transcribe_audio/understand_media | screen, image, video, audio |
| `hardware` | vitals/load | CPU/GPU/RAM check |
| `web_fetch` | fetch | URL → stripped plain text |
| `todo` | add/list/update/remove/clear_completed | persistent todo list |
| `diff` | diff_files/diff_content | unified diff |
| `code_compass` | search/stats/context | AST symbol search |
| `knowledge_forge` | search_papers/list_proposals/status/digest | arxiv + ecosystem |
| `swarm` | run | spawn specialist agents |
| `think_partner` | cross_question/architect/debate/brainstorm/teach | cognitive collab |

- `get_prompt_block()` auto-generates AVAILABLE TOOLS markdown for Gemini's system prompt
- `resolve_tool_name(raw)` — alias map (fs→filesystem, web→web_search, hw→hardware, forge→knowledge_forge, etc.)
- `ToolTelemetry` records per-tool ok/fail counts + last error

### Auto-selector (`src/tools/auto_selector.py`)
**Tier 1 — regex (instant):** ~25 patterns covering "git status", "read X.py", "ls", "grep", "screenshot", "vitals", "papers about Y", etc. Confidence 0.95.

**Tier 2 — LLM (~500ms):** `gemini-2.5-flash-lite` ranks candidates with `confidence` + `needs_planning` flag. `pick_best(prompt, threshold=0.85)` returns top candidate or None.

Wired into main.py before DAG planner — high-confidence single-tool intents bypass full planning.

### Execution (`src/routers/router.py:ParallelExecutor`)
- Aliases resolved before dispatch
- 14 tool branches in `execute_step`
- Unknown tool → loud failure with hint listing known tools
- Telemetry recorded on every dispatch
- DAG runner: `TaskGroup` parallel batches, dependency-aware, hardware-gated via `_resource_gate`
- 3-tier `_fallback_recovery`: agent retry → primary brain → tertiary

---

## Knowledge & evolution

### KnowledgeForge (`src/services/knowledge_forge/`)
- `paper_reader.py` — arxiv API, pypdf extract, Gemini score, ChromaDB persist (`apex_forge_papers` collection); `scan_backfill(days)` for catch-up
- `ecosystem_watcher.py` — PyPI RSS + GitHub Trending + HuggingFace + HN Algolia + npm; PyPI version stripping for dedup
- `capability_synthesizer.py` — Gemini → queued capability proposals; deterministic IDs `fp_<sha1[:10]>`
- `benchmark_self.py` — 5 HumanEval-lite tasks; per-model pass-rate; regression detection
- `proposal_applier.py` — Gemini code-gen (full or diff mode) → AST validate → backup → bench gate → rollback if pass-rate drops ≥ 0.15
- `PipSandbox` — temp venv → install deps → import-validate → only then install to active env
- `forge.py` — orchestrator; per-project `.apex/forge_state.json`; cycle log to `~/.apex/forge_log.md`; daily background loop (idle + HW gated)

### Self-evolution (`src/services/self_evolution.py`)
- Background loop: every 60s, fires when idle ≥5 min and HW not critical
- Scans own AST for complexity/TODOs
- Pulls approved-but-unapplied Forge proposals (tagged `[FORGE]`)

### Code Compass (`src/services/code_compass.py`)
- Token-efficient AST symbol map at `.apex/code_compass.json`
- 5-12% of raw size; used by thinking_path for context-efficient lookups

---

## Hardware & senses

- `src/tools/hardware.py` — `HardwareMonitor.get_vitals()` returns `cpu_percent`, `ram_percent`, `gpu_percent`, `status` (ok/warn/critical); used by `_resource_gate` for throttling
- `src/tools/vision.py` — `RetinaTool.capture_screen()` for screenshot; OCR + describe via Gemini Vision

---

## Awareness layer

### TimeContext (`src/core/time_context.py`)
- `system_prefix()` injected into every LLM call (thinking_path, fast_path, think_partner, swarm)
- `is_greeting(text)` — regex catches bare salutations
- `craft_greeting_response()` — context-aware reply ("Good morning. Monday — what's first?" / "Up late — what's the mission?")
- `relative(ts)` — human-readable delta ("5 min ago", "yesterday", "last week")

### Hooks (`src/core/hooks.py`)
- 12 events: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `ForgeCycleStart/Done`, `ApexPaperFound`, `ApexEcosystemNew`, `ForgeProposalAdded`, `ForgeApplied`, `ForgeRolledBack`
- Loaded from `.apex/hooks.json` (project) and `~/.apex/hooks.json` (global)
- Subprocess-based with 20s timeout

### Cognitive (`src/services/cognitive.py`)
- `EmotionalCore.analyze_user(text, velocity)` — sentiment + cognitive load
- `synthesize_apex_state(emotional)` — APEX's mirror state
- `style_directive(apex_state)` — injects tone modifier into thinking_path prompt

---

## Failure handling

- **Redis down** → `is_active=False` for 30s, then auto-retry; everything else continues
- **Chroma error** → ops return empty/False; downstream gracefully degrades
- **Gemini error** → 3-tier fallback (agent recovery → Gemini fallback → OpenRouter tertiary)
- **Unknown tool name** → loud failure with hint listing known tools
- **Bench regression after apply** → automatic rollback from backup
- **Hardware critical** → throttling via `_resource_gate`, concurrency drops to 1
- **Hook timeout** → 20s cap, returns failure dict, doesn't block

---

## Persistence layout

```
realjarvis/
├── .apex/                          per-project workspace state
│   ├── forge_state.json            last cycle timestamp + summary
│   ├── code_compass.json           AST symbol map
│   ├── hooks.json                  hook configuration
│   └── knowledge_map.json          relational graph
├── data/
│   ├── chroma/                     vector DB (memories, cache, papers)
│   └── forge/
│       ├── papers.jsonl            arxiv ingestion log
│       ├── ecosystem.jsonl         ecosystem feed
│       ├── ecosystem_state.json    seen keys
│       ├── proposals.json          capability proposals queue
│       ├── bench.json              self-benchmark history
│       ├── papers_seen.json        arxiv ID dedup set
│       ├── backups/<id>/<ts>/      proposal apply backups
│       └── venvs/<id>/             pip sandbox venvs
└── ~/.apex/
    ├── hooks.json                  global hook config
    └── forge_log.md                cross-project forge cycle log
```

---

## Test architecture

7 modern suites, 279 tests, all pass:

- `test_knowledge_forge.py` (93) — paper reader, ecosystem, synthesizer, applier, bench, hooks
- `test_memory_system.py` (37) — Redis self-heal, async Chroma, cache stats, summarize-before-drop
- `test_think_partner.py` (23) — 6 modes + auto-route
- `test_swarm.py` (23) — blackboard, agent, coordinator, multi-round
- `test_time_context.py` (36) — time-of-day, greetings, relative deltas
- `test_tool_registry.py` (23) — registry completeness, alias resolution, telemetry
- `test_auto_selector.py` (30) — regex tier patterns, LLM tier classifier

Mock pattern: `httpx.AsyncClient`, `genai.Client`, `redis.Redis`, `chromadb.PersistentClient` via `unittest.mock`. Real subprocess for SelfBenchmark code execution.

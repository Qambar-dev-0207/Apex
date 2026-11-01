# APEX — Full Architecture

> Reflects current code as of 2026-05-13.

---

## Core design principle

APEX layers smart routing under a "fast path always wins" rule:
- Simple prompts → regex match → instant execution (ms)
- Moderate prompts → LLM auto-selector → single-tool dispatch (< 1s)
- Complex prompts → Gemini DAG planner → parallel executor (multi-step)
- Agentic tasks → AgentHarness autonomous loop (MiMo-driven, 35 tools)

Every layer ships with a fallback so degradation is graceful, not fatal.

---

## Input pipeline & Reflex Scout Architecture

```
1.  user_input
2.  UserPromptSubmit hook fires
3.  self_evolver.mark_input + knowledge_forge.mark_input
4.  ! prefix         → direct shell passthrough
5.  / prefix         → handle_slash (60+ commands)
6.  Reflex Stage A   → Deterministic Skip (Greeting / Identity / Casual Chit-Chat) [p95: 0.003 ms, $0]
7.  Reflex Stage B   → AutoSelector Regex Tool Match (git status, read file, open app, vitals) [Instant tool execution]
8.  Reflex Stage C/D → Scout Mode (Intent Prototypes Embedding NN):
                       ├── Fire PrefetchBundle (parallel async fetch of memory, compass, workspace)
                       └── Concurrently call InputClassifier / Gemini classify
9.  autothink on?    → ThinkPartner.detect_think_mode (regex / flash-lite)
10. SmartRouter.route→ fast_path (Groq) or thinking_path (Gemini 3.8 Flash Master Orchestration DAG)
11. ExecutionPlan:
    ├── if plan.task_plan is empty (Conversational Q&A / Out-of-the-Box reasoning):
    │   → Render single-panel APEX // INTELLECTUAL SYNTHESIS
    │   → Store interaction in memory & return [SKIP TOOL EXECUTION]
    └── else (Multi-step code/system task):
        → ParallelExecutor.run (asyncio.TaskGroup DAG execution)
12. Response delivery→ ResponseAssembler renders final DAG tree, vitals, and output
                     → memory_manager.store_interaction (Redis session + Chroma long-term)
                     → learning_manager.learn (background skill extraction)
```

### Reflex Scout & Speculative Prefetch (`src/core/reflex.py`)
Reflex is the **local pre-LLM gateway** that eliminates unnecessary API calls and hides retrieval latency:
- **Mode 1: Deterministic Skip (`needs_llm=False`)**: Handles greetings, identity queries, casual chat (`_CASUAL_RX`), and single-action regex tool intents (`tool_regex_match`) in < 10 microseconds with zero token spend.
- **Mode 2: Scout Mode (`needs_llm=True`)**: Performs local embedding nearest-neighbor matching against `INTENT_PROTOTYPES`. While Gemini plans, Reflex fires a `PrefetchBundle` in parallel across:
  - `memory`: Pre-fetches Chroma semantic vectors and session history.
  - `compass`: Pre-extracts AST signatures from `CodeCompass`.
  - `workspace`: Pre-summarizes active project directives.
- **Adaptive Waste Gating**: Tracks the ratio of used vs. wasted prefetches over a rolling 20-call window. If the waste rate exceeds 60%, prefetching auto-disables to protect system CPU/RAM.

---

## Brain layer

### Primary Orchestrator & Planner — Gemini 3.8 Flash (`src/models/thinking_path.py`)
- Google's master orchestration brain for Task DAG decomposition, dependency graph calculation, and execution planning
- System prompt auto-prefixed with `TimeContext.system_prefix()` + `tool_registry.get_prompt_block()`
- **Prompt Boundary Tags**: Encloses directives (`--- PROJECT DIRECTIVES ---` ... `--- END PROJECT DIRECTIVES ---`) and workspace context (`--- WORKSPACE CONTEXT ---` ... `--- END WORKSPACE CONTEXT ---`) in clear opening/closing tags to prevent LLM leaking/repetition.
- **Conditional Directives**: Resolves directives early and prepends them to the thinking path plan prompt only when prefetch is active (`_has_prefetch` is `True`), avoiding context duplication.
- Modes: `socratic_mode`, `steelman_mode`, `genius_mode` (multi-pass: hypothesis → counters → blind-spot → synthesis)
- Outputs `ExecutionPlan` with task DAG + dependency graph
- Also used for: GeniusMode critique, ResumeTool rewrite, KnowledgeForge scoring

### Fast path — Groq (`src/models/fast_path.py`)
- Groq `llama-3.1-8b` streaming
- Used for: low-complexity responses, AgentHarness fallback brain, fast summaries

### Code brain — Xiaomi MiMo v2.5-pro (`src/models/mimo_path.py`)
- OpenAI-compatible endpoint at `https://api.xiaomimimo.com/v1`
- Used for: code implementation (CodingPipeline stage 2), AgentHarness primary brain
- Sync, async, and streaming interfaces
- TimeContext injected into every call
- Graceful offline degradation when `MIMO_API_KEY` absent

### Architecture spec — MiniMax 2.5 (`src/models/minimax_path.py`)
- Used for: CodingPipeline stage 1 (architecture spec before implementation)

### Tertiary fallback — OpenRouter (`src/models/fallback_path.py`)
- `gpt-oss-120b` via OpenRouter
- Used only when Gemini + agent retry both fail

### Cognitive collaborator — ThinkPartner (`src/services/think_partner.py`)
- 6 modes: `cross_question`, `architect`, `debate`, `brainstorm`, `teach`, `extract_intent`
- `auto_route()` — regex first, then flash-lite LLM if intent is ambiguous
- High ambiguity → blocking cross_question loop

### Multi-agent Swarm (`src/services/swarm.py`)
- Coordinator decomposes goal → spawns roster from {architect, coder, critic, researcher, planner}
- `Blackboard` — async-safe shared message log (each agent sees others' posts, not own)
- Synthesis via Gemini 2.5 Pro

### Genius critique — GeniusMode (`src/services/genius_mode.py`)
- 5-stage JSON critique: `cross_question`, `right`, `wrong`, `blind_spots`, `action`, `one_liner`
- Brain cascade: Gemini (JSON mime-type forced) → MiMo → Groq
- Offline stub returns valid shape with witty `one_liner` when all brains unreachable
- See [GENIUS_MODE.md](GENIUS_MODE.md) for full details

### Coding pipeline (`src/services/coding.py`)
```
Stage 1: MiniMax 2.5        → architecture spec
Stage 2: MiMo v2.5-pro      → implementation
Stage 3: Gemini 2.5 Flash   → validation + review
```

---

## AgentHarness (`src/core/harness.py`)

Autonomous tool-calling loop that acts as a mini-agent runtime. The harness receives a goal, selects tools via OpenAI function-calling format, executes them, and loops until `done()` is called or max iterations reached.

**Brain**: MiMo v2.5-pro (primary) → Groq (fallback)
**Tools**: 35 tools (see [HARNESS.md](HARNESS.md))
**Security**: `BLOCKED_PATHS = (".git/", ".env", "id_rsa", ".ssh/")`
**Snapshot**: auto-backup of any existing file on first write → `backups/harness_<ts>/`
**Rollback**: `harness.rollback()` restores from snapshot

Key behaviors:
- `multi_edit` is fully atomic — validates ALL edits before writing; rolls back on partial failure
- Ambiguous edits rejected (string appears more than once in file)
- `.env` writes blocked at OS level

---

## Memory layer (`src/services/memory.py`)

| Component | Backend | Role |
|---|---|---|
| `RedisManager` | Redis | Short-term session history, self-healing (30s retry) |
| `ChromaManager` | ChromaDB | Long-term semantic memory, async, TTL pruning, project-specific isolation |
| `ResponseCache` | ChromaDB collection | Semantic LLM dedup, hit/miss stats |
| `MemoryManager` | Orchestrator | summarize-before-drop at `history_cap`, single round-trip store, project name propagation |

**Summarize-before-drop**: when history > `APEX_HISTORY_CAP` (default 20), oldest entries collapse into a `[SUMMARY]` via `gemini-2.5-flash-lite`.

**Project-Specific Memory Isolation**: Chroma long-term semantic memory stores the active `project_name` in document metadata and queries it with `where={"project_name": project_name}` to isolate retrieval results. The project context propagates cleanly through the prefetch layer (`reflex.py`), thinking path (`thinking_path.py`), and the main engine loop (`main.py`) to prevent cross-project context bleeding.

---

## Tools layer

### Registry (`src/tools/registry.py`)
22 registered canonical tools. Each `ToolSpec` defines: canonical name + aliases + actions + input schema + when-to-use + examples.

Auto-generates the `AVAILABLE TOOLS` prompt block for Gemini — preventing manual prompt drift.

| Tool | Aliases | Core actions |
|---|---|---|
| `filesystem` | fs, file | read/write/delete/list/search/glob |
| `shell` | bash, sh, run | execute |
| `git` | vcs | commit/status/diff/add/push/pull/log |
| `python_executor` | python, py | write/run |
| `research_swarm` | research, rs | search |
| `web_search` | search, ws | search (Tavily/Brave/DDG) |
| `web_fetch` | fetch, url, wf | fetch URL, strip HTML |
| `workspace` | ws2 | scan/summarize/directives |
| `mcp` | mcp_call | connect/call external MCP servers |
| `vision` | retina | capture/ocr/describe/video/audio |
| `hardware` | hw, vitals | vitals/load |
| `code_compass` | compass | search/stats/context (AST map) |
| `knowledge_forge` | forge | papers/proposals/status/digest |
| `swarm` | agents | run specialist agent swarm |
| `think_partner` | think | cross_question/architect/debate/brainstorm/teach |
| `todo` | todos, tasks | add/list/update/remove/clear |
| `diff` | compare, patch | diff_files/diff_content |
| `desktop_control` | desktop, window | list_apps/search_app/launch_app/active_window |
| `codebase_index` | cindex, index | index_workspace/search_symbols/find_references |
| `weather` | forecast | current/forecast/connect |
| `api_connector` | apikey, keys | save_key/list_keys/test_connection |
| `app_launcher` | open_app, apps | launch/search/list |

### Desktop Control & App Launcher (`src/services/app_launcher.py`)
Provides deterministic, sub-millisecond desktop application resolution across Windows:
- **Tier 1: O(1) Exact & Compact Hash Map**: Direct match for installed software and builtins (`calc`, `notepad`, `cmd`, `powershell`, `code`).
- **Tier 2: Semantic Alias Dictionary**: Intent mapping (`notes` → Notepad, `tasks` → Task Manager, `browser` → Chrome/Edge).
- **Tier 3: Fuzzy Typo Matching**: Levenshtein / SequenceMatcher fallback for misspelled queries (e.g. `calculater` → Calculator with confidence ≥ 0.75).
- **Security Guardrails**: Rejects shell metacharacters (`&`, `;`, `\|`, `` ` ``, `$`), verifies UWP AppID syntax, and blocks prohibited destructive binaries (`format.com`, `reg.exe`, `vssadmin.exe`).

### Auto-selector (`src/tools/auto_selector.py`)
**Tier 1 — regex (instant, 0.95 confidence):** ~30+ patterns
- `git status/log/diff` → git
- `read/write/delete/grep X.py` → filesystem
- `https://...` → web_fetch
- `todos / tasks` → todo list
- `todo add / add todo X` → todo add
- `open/launch/start <app>` → app_launcher
- `vitals / cpu / ram` → hardware
- `weather in <city>` → weather
- `papers about Y` → knowledge_forge

**Tier 2 — LLM (~500ms):** `gemini-2.5-flash-lite` ranks candidates + `confidence` score. Threshold 0.85 to bypass planner.

---

## Vision & media (`src/tools/vision.py`)

`RetinaTool` handles all media understanding:

| Method | Input | Backend |
|---|---|---|
| `describe_image(path)` | jpg/png/webp/bmp/gif | Gemini multimodal |
| `ocr_image(path)` | image file | Gemini (verbatim text extraction) |
| `describe_video(path, max_frames=8)` | mp4/avi/mov/mkv/webm | cv2 → frame array → Gemini |
| `transcribe_audio(path)` | mp3/wav/flac/ogg/m4a | Groq Whisper-large-v3 |
| `understand_media(path)` | any above | auto-routes by extension |
| `capture_screen()` | live screen | PIL screenshot |

Video understanding: cv2 samples `max_frames` uniformly across duration, encodes frames as base64, sends all to Gemini in a single multimodal call.

See [VISION.md](VISION.md) for full details.

---

## Animations (`src/core/animations.py`)

Rich-powered terminal effects, all tty-safe (degrade to static print on non-tty):

| Function | Effect |
|---|---|
| `matrix_rain(duration)` | Boot decoration — green character rain |
| `pulse_banner(title)` | Figlet wordmark with diagonal color wave |
| `type_text(text, cps)` | Typewriter character-by-character print |
| `progress_trail(steps)` | Animated checklist with spinning → locked ✓ |
| `sparkle_panel(text)` | Animated border-color cycling panel |
| `thinking_orb(coro, label)` | Async spinner wrapper while awaitable runs |

Boot sequence: `matrix_rain` → `pulse_banner("APEX")` → tagline + model badges → `thinking_orb(loader_task)` → `progress_trail(checklist)`.

See [ANIMATIONS.md](ANIMATIONS.md) for full details.

---

## Knowledge & self-evolution

### KnowledgeForge (`src/services/knowledge_forge/`)
- `paper_reader.py` — arxiv API, pypdf extract, Gemini score → ChromaDB persist
- `ecosystem_watcher.py` — PyPI RSS, GitHub Trending, HuggingFace, HN, npm
- `capability_synthesizer.py` — Gemini → queued proposals with deterministic IDs
- `benchmark_self.py` — 5 HumanEval-lite tasks, pass-rate gating
- `proposal_applier.py` — Gemini code-gen → AST validate → backup → bench gate → rollback on regression
- `PipSandbox` — temp venv → install → import-validate → then install to active env

### Self-evolution (`src/services/self_evolution.py`)
- Fires when idle ≥ 5 min + HW not critical
- Scans own AST for complexity/TODOs
- Pulls approved-but-unapplied Forge proposals

### Code Compass (`src/services/code_compass.py`)
- Token-efficient AST symbol map at `.apex/code_compass.json`
- 5–12% of raw source size; used by thinking_path for context-efficient lookups

---

## Awareness

### TimeContext (`src/core/time_context.py`)
- `system_prefix()` injected into EVERY LLM call
- `is_greeting(text)` + `craft_greeting_response()` — instant time-aware greeting
- `relative(ts)` — human-readable delta ("5 min ago", "last week")

### Hooks (`src/core/hooks.py`)
- 12 events: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `ForgeCycleStart/Done`, `ApexPaperFound`, `ApexEcosystemNew`, `ForgeProposalAdded`, `ForgeApplied`, `ForgeRolledBack`
- Loaded from `.apex/hooks.json` (project) + `~/.apex/hooks.json` (global)
- Subprocess-based, 20s timeout

### Cognitive (`src/services/cognitive.py`)
- `EmotionalCore.analyze_user(text, velocity)` — sentiment + cognitive load
- `style_directive(apex_state)` — injects tone modifier into thinking_path prompt

---

## Failure handling

| Failure | Behavior |
|---|---|
| Redis down | `is_active=False` for 30s, auto-retry; rest continues |
| Chroma error | ops return empty/False, downstream degrades gracefully |
| Gemini error | 3-tier: agent retry → Gemini fallback → OpenRouter |
| MiMo offline | AgentHarness falls back to Groq |
| Bench regression after apply | automatic rollback from backup |
| Hardware critical | `_resource_gate` drops concurrency to 1 |
| Hook timeout | 20s cap, returns failure dict, doesn't block |
| Unknown tool | loud failure with hint listing known tools |
| All brains offline | GeniusMode returns valid offline stub with witty one_liner |

---

## Verification, Testing & Evaluation Architecture

APEX implements a continuous verification and evaluation system to safeguard against regressions, maintain sub-millisecond execution speeds, and enforce strict security boundaries.

### Continuous Evaluation Framework
- **Speed & Latency**: Reflex regex fast-path achieves **0.003 ms (p95)**, local scout matching achieves **0.008 ms (p95)**, and AppLauncher resolves desktop apps in **1.08 ms (mean)**.
- **Answer Quality**: HumanEval-lite tasks run in isolated subprocesses verifying code generation with 100% pass rate.
- **Safety Barriers**: Hardened protections block unauthorized writes to `.env`, `.git/`, or parent directories outside the workspace.
- **Transactional Rollback**: Multi-chunk file modifications operate atomically; if any single chunk fails, all previous chunks are restored.
- **Retrieval Precision**: ChromaDB semantic memory achieves **Recall@3 = 1.0**, **Precision@3 = 1.0**, and **MRR = 1.0**.

### Regression Gating
- `SelfBenchmark` (`src/services/knowledge_forge/benchmark_self.py`): Tracks algorithmic coding pass rates.
- `ProposalApplier` (`src/services/knowledge_forge/proposal_applier.py`): Automatically triggers code rollback if self-evolution causes a benchmark drop ≥ 15%.
- See [EVALUATIONS.md](EVALUATIONS.md) and [TESTING.md](TESTING.md) for full benchmark tables and methodology.

---

## Persistence layout

```
realjarvis/
├── .apex/
│   ├── forge_state.json        last cycle timestamp + summary
│   ├── code_compass.json       AST symbol map
│   ├── hooks.json              hook configuration
│   └── knowledge_map.json      relational graph
├── data/
│   ├── chroma/                 vector DB (memories, cache, papers)
│   ├── todos.json              todo list
│   └── forge/
│       ├── papers.jsonl
│       ├── ecosystem.jsonl
│       ├── proposals.json
│       ├── bench.json
│       ├── backups/<id>/<ts>/  proposal apply backups
│       └── venvs/<id>/         pip sandbox venvs
├── backups/
│   └── harness_<ts>/           AgentHarness file snapshots
└── ~/.apex/
    ├── hooks.json              global hooks
    └── forge_log.md            cross-project forge log
```

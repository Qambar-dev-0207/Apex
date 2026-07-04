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

## Input pipeline

```
1.  user_input
2.  UserPromptSubmit hook fires
3.  self_evolver.mark_input + knowledge_forge.mark_input
4.  ! prefix         → direct shell passthrough
5.  / prefix         → handle_slash (60+ commands)
6.  greeting?        → TimeContext.craft_greeting_response  [INSTANT]
7.  autotool on?     → regex_match (git status, ls, URLs, todos, ...)
                     → execute_step directly  [SKIP DAG]
8.  autothink on?    → ThinkPartner.detect_think_mode (regex)
                     → ThinkPartner.extract_intent (flash-lite LLM)
                     → ambiguity_score >= 0.6 → cross_question loop
                     → known mode → architect / debate / brainstorm / teach
9.  pending_clarification? → merge answer → re-run
10. fall-through     → cognitive_core.analyze_user
                     → InputClassifier.classify
                     → SmartRouter.route → fast_path or thinking_path
                     → ExecutionPlan (DAG)
                     → ParallelExecutor.run
11. response         → memory_manager.store_interaction (Redis + Chroma)
                     → knowledge_visualizer.extract_knowledge
                     → learning_manager.learn (background)
                     → assembler.render_final_response
```

---

## Brain layer

### Primary planner — Gemini 2.5 Flash (`src/models/thinking_path.py`)
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
17 registered tools. Each `ToolSpec` has: canonical name + aliases + actions + input schema + when-to-use + examples.

Auto-generates AVAILABLE TOOLS block for Gemini system prompt — no hardcoded tool drift.

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

### Auto-selector (`src/tools/auto_selector.py`)
**Tier 1 — regex (instant, 0.95 confidence):** ~25+ patterns
- `git status/log/diff` → git
- `read/write/delete/grep X.py` → filesystem
- `https://...` → web_fetch
- `todos / tasks` → todo list
- `todo add / add todo X` → todo add
- `vitals / cpu / ram` → hardware
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

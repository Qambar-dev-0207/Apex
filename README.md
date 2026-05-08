# APEX — Sovereign Agentic AI OS

A personal AI operating system. Multi-model, self-evolving, memory-aware, token-efficient. Runs locally, thinks deeply, adapts emotionally.

---

## Architecture

```
User Input
   ↓
InputClassifier (Gemini 2.5 Flash Lite)
   ↓
SmartRouter
   ├── Fast Path  → Groq / Llama-3.1-8b (streaming)
   └── Thinking Path → Gemini 2.5 Flash (DAG planner)
          ↓
     ParallelExecutor (asyncio DAG, Semaphore(10))
          ↓
     Tools: filesystem · shell · git · web_search · research_swarm · mcp · python_executor · workspace
          ↓
     ResponseAssembler (rich UI)
   ↓
Async: Memory store · Learning · KnowledgeGraph · SelfEvolver · CodeCompass
```

**Fallback chain:** Gemini 2.5 Flash → Groq fast-path → OpenRouter gpt-oss-120b (tertiary)

---

## Models

| Role | Model | Provider |
|---|---|---|
| Planner / Architect | gemini-2.5-flash | Google |
| Classifier / Lite ops | gemini-2.5-flash-lite | Google |
| Fast path / Streaming | llama-3.1-8b-instant | Groq |
| Tertiary fallback | gpt-oss-120b:free | OpenRouter |

---

## Memory System

| Layer | Backend | Purpose |
|---|---|---|
| Short-term | Redis | Last 10 turns per session, sub-ms |
| Long-term | ChromaDB | Semantic search over all interactions |
| Response cache | ChromaDB | Near-duplicate query dedup |
| Knowledge graph | JSON + SVG | Relational entity/edge map per project |
| Code compass | JSON (AST) | Token-efficient symbol index |

---

## Setup

```bash
pip install -r requirements.txt
```

Create `.env`:
```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
OPENROUTER_API_KEY=your_key       # optional — tertiary fallback
TAVILY_API_KEY=your_key           # optional — web search tier 1
BRAVE_API_KEY=your_key            # optional — web search tier 2
REDIS_HOST=localhost
REDIS_PORT=6379
CHROMA_PATH=./data/chroma
```

Run Redis, then:
```bash
python main.py
```

---

## Slash Commands

### Session
| Command | Action |
|---|---|
| `/help` | Command reference |
| `/clear` | Clear console |
| `/clear-session` | Wipe session memory (Redis) |
| `/clear-all` | Wipe all memory (confirm required) |
| `/compact` | Summarize + trim long context |
| `/resume` | List + resume prior sessions |
| `/exit` | Quit |

### Modes
| Command | Action |
|---|---|
| `/socratic` | Toggle Socratic critique (challenge assumptions) |
| `/steelman` | Toggle strongest-possible counter-argument |
| `/genius` | Toggle multi-pass deep reasoning (hypothesis → counters → blind-spot → synthesis) |
| `/auto-approve` | Toggle bypass permission prompts |
| `/plan` | Toggle plan-only mode (no writes or exec) |

### Workspace
| Command | Action |
|---|---|
| `/project <name>` | Create new project |
| `/init` | Generate APEX.md directives for active project |
| `/scan` | Re-map active project files |
| `/map` | Render knowledge graph SVG |
| `/prune` | Show compressed context for current focus |
| `/skills` | List registered skills |
| `/reload-skills` | Reload markdown skills from `~/.apex/skills/` |
| `/todo <task>` | Add todo to active project |
| `/todo done <n>` | Mark todo #n complete |
| `/todos` | List todos |

### Self-Evolution
| Command | Action |
|---|---|
| `/evolve` | Run self-improvement cycle now |
| `/evolve auto` | Run cycle + auto-provision missing skill |
| `/proposals` | Show latest self-improvement proposals |

### Code Intelligence
| Command | Action |
|---|---|
| `/analyze` | Build/refresh token-efficient code map |
| `/analyze <term>` | Symbol search across codebase (compressed) |
| `/map-stats` | Compression ratio + token savings |

### Telemetry
| Command | Action |
|---|---|
| `/cost` | Daily spend |
| `/status` | CPU · RAM · safety mode · MCP servers |
| `/policy [allow\|deny] <cmd>` | Manage execution policy |

### Tools
| Command | Action |
|---|---|
| `! <command>` | Direct shell passthrough |
| `/web <query>` | Web search (Tavily → Brave → DuckDuckGo) |
| `/mcp connect <name> <cmd> [args]` | Connect MCP server |
| `/mcp list` | List connected MCP servers |
| `/mcp tools <server>` | List tools on server |

### Snapshot
| Command | Action |
|---|---|
| `/snapshot` | Export state zip |
| `/restore <path>` | Restore from snapshot |

---

## Self-Evolution Engine

APEX analyzes its own source code when idle (5+ min no input, hardware nominal).

**What it scans:**
- Functions with cyclomatic complexity > 12 branches
- Public functions/methods missing docstrings
- TODO / FIXME / HACK comments

**What it produces:**
- Prioritized improvement proposals (Gemini 2.5 Flash Lite)
- Auto-persisted to `data/self_evolution.json`
- Optional auto-provisioning of missing skills via `/evolve auto`

Cycle fires at most every 30 min. Hardware-gated (skips if CPU critical).

---

## Code Compass (Token-Efficient Analysis)

Compressed AST-based symbol index for the entire codebase.

**Supported languages:** Python · JavaScript · TypeScript · Go · Rust · Java

**How it works:**
- Python: full AST parse → classes, method signatures, 1-line docstrings, imports
- Other langs: regex symbol extraction
- Hash-keyed cache at `.apex/code_compass.json` — unchanged files skip re-parse
- Typical compression: 5–12% of raw source size (**8–20x token savings**)

**Used automatically:** Thinking-path injects compressed symbol map into Gemini context instead of raw files.

---

## Emotional Intelligence

APEX reads your emotional state and adapts its own.

**User state detection:** sentiment (neutral/stressed/excited/frustrated) + cognitive load + flow state

**APEX state:** `ApexState` model — mood · energy · curiosity · confidence · response_style · flavor

**Mirroring logic:**
| Your state | APEX mood | Style |
|---|---|---|
| Stressed | Calm | Terse |
| Frustrated | Concerned | Terse |
| Excited | Excited | Expansive |
| Neutral (low load) | Curious | Socratic |
| Any (high load) | — | Terse override |

**Genius mode** (`/genius`): Multi-pass reasoning before committing to a plan:
1. State strongest hypothesis
2. Generate 2 counter-hypotheses
3. Identify 1 blind spot
4. Surface 1 second-order consequence
5. Synthesize final plan that survives all four

---

## Tool System

### Execution Pipeline
All tool calls go through `ParallelExecutor` which runs DAG steps with `asyncio.TaskGroup` at up to 10 concurrent tasks. Hardware-gated: throttles to 1 concurrent if CPU critical.

### Fallback Recovery
Every tool failure triggers `_fallback_recovery`: first tries Gemini to re-plan the step, then falls back to OpenRouter tertiary.

### Safety
Three modes: `default` (prompt per operation) · `auto-approve` (bypass) · `plan` (no writes/exec).

Policy file at `data/policy.json`. Manage via `/policy allow|deny <command>`.

### MCP (Model Context Protocol)
Connect any MCP server at boot via `.mcp.json` (project) or `~/.apex/mcp.json` (global):
```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@some/mcp-server"],
      "env": {}
    }
  }
}
```

---

## Project Directives

Drop any of these files in your project root — APEX auto-loads them into every model call:
- `APEX.md` (preferred)
- `CLAUDE.md`
- `AGENTS.md`
- `.apex/instructions.md`

Generate a starter template: `/init`

---

## Hooks

Claude Code-style event hooks. Config at `.apex/hooks.json` (project) or `~/.apex/hooks.json` (global):

```json
{
  "SessionStart": [{"command": "echo APEX online"}],
  "PreToolUse": [{"matcher": "shell", "command": "echo about to shell"}],
  "PostToolUse": [{"command": "echo done"}],
  "Stop": [{"command": "echo shutting down"}]
}
```

Events: `SessionStart` · `UserPromptSubmit` · `PreToolUse` · `PostToolUse` · `Stop`

---

## Skills System

Reusable execution patterns stored in ChromaDB. Auto-matched on input.

**Load from markdown:** Drop `SKILL.md` files in `~/.apex/skills/`. Reload with `/reload-skills`.

**Auto-learned:** APEX creates skills from multi-step plans automatically after execution.

**Auto-provisioned:** `/evolve auto` analyzes project gaps and generates new skills via Gemini.

---

## Data Layout

```
data/
  apex.db              — spend tracking (SQLite)
  failures.json        — tool failure log
  self_evolution.json  — self-improvement proposals
  chroma/              — ChromaDB (memories + skills + cache)

.apex/
  knowledge_map.json   — per-project cognitive graph
  knowledge_graph.svg  — rendered visualization
  code_compass.json    — compressed symbol index
  hooks.json           — project hooks

backups/               — /snapshot exports
```

---

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Thinking path + classifier |
| `GROQ_API_KEY` | Yes | Fast path streaming |
| `OPENROUTER_API_KEY` | No | Tertiary fallback |
| `TAVILY_API_KEY` | No | Web search (tier 1) |
| `BRAVE_API_KEY` | No | Web search (tier 2) |
| `REDIS_HOST` | No | Default: localhost |
| `REDIS_PORT` | No | Default: 6379 |
| `CHROMA_PATH` | No | Default: ./data/chroma |
#   A p e x  
 
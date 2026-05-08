# APEX — JARVIS-Tier Ecosystem Roadmap

> Goal: surpass JARVIS (Iron Man). Not a chatbot. Ambient, embodied, sovereign, self-evolving AI OS.

---

## Current State (solid foundation)

| Component | Status | Location |
|---|---|---|
| Multi-model brain (Gemini + Groq + OpenRouter) | ✅ Live | `src/models/` |
| Memory (Redis + ChromaDB + ResponseCache) | ✅ Live | `src/services/memory.py` |
| MCP client + auto-load | ✅ Live | `src/tools/mcp_client.py` |
| Vision / screen capture | ✅ Live | `src/tools/vision.py` |
| Hardware monitor | ✅ Live | `src/tools/hardware.py` |
| Self-evolution engine | ✅ Live | `src/services/self_evolution.py` |
| Knowledge Forge (arxiv + ecosystem watcher) | ✅ Live | `src/services/knowledge_forge/` |
| Proposal applier (bench-gated code-gen) | ✅ Live | `src/services/knowledge_forge/proposal_applier.py` |
| EmotionalCore + ApexState | ✅ Live | `src/services/cognitive.py` |
| Hooks system (SessionStart/Stop/PreTool/PostTool) | ✅ Live | `src/core/hooks.py` |
| CodeCompass (token-efficient AST indexer) | ✅ Live | `src/services/code_compass.py` |
| Proactive briefing (morning digest) | ✅ Live | `src/services/proactive.py` |
| Workspace + multi-project | ✅ Live | `src/tools/workspace.py` |
| Web search (Tavily / Brave / DDG) | ✅ Live | `src/tools/web_search.py` |

---

## Layers to Build

### Layer 1 — Voice & Always-On Audio
**Target: APEX responds to spoken name, speaks back. Hands-free.**

| Component | Tech | Notes |
|---|---|---|
| Wake-word detection | `openwakeword` (local) | Train custom "APEX" wake word |
| Speech-to-text | `faster-whisper` large-v3 (local) | GPU-accelerated, no cloud |
| Text-to-speech | `piper` (local) or ElevenLabs streaming | Piper = free/fast, ElevenLabs = quality |
| Voice activity detection | `silero-vad` | Natural turn-taking, barge-in support |
| Audio I/O | `sounddevice` + `pyaudio` | Low-latency mic + speaker |

New service: `src/services/voice_layer.py`
New slash: `/voice on|off|status`

---

### Layer 2 — Ambient Awareness
**Target: APEX sees what you see, reacts without being asked.**

| Component | Tech | Notes |
|---|---|---|
| Continuous screen capture | Extend `RetinaTool` | 1-2 fps diff-only capture |
| OCR + UI element graph | `pytesseract` + `uiautomation` (Win) | Active window, visible text, buttons |
| Clipboard monitor | `pyperclip` + polling or `win32clipboard` | Cross-app context injection |
| File-system watcher | `watchdog` | React to file saves, new files |
| Active app tracker | `pywin32` `GetForegroundWindow` | Switch context when app changes |

New service: `src/services/ambient.py`
New hook events: `AmbientScreenChange`, `AmbientClipboardChange`, `AmbientFileChange`

---

### Layer 3 — Reliable Embodied Control
**Target: APEX controls desktop + browser like a human operator.**

| Component | Tech | Notes |
|---|---|---|
| Desktop control | `uiautomation` (Win accessibility tree) | Replace pixel-based `pyautogui` for reliability |
| Browser automation | Playwright MCP | Already MCP-ready; add `mcp_playwright` |
| Windows automation | `win32com` + PowerShell subprocess | Excel, Office, system settings |
| Mobile bridge | Webhook receiver + Tasker/Shortcuts | APEX as phone backend |
| IoT control | Home Assistant MCP | Lights, locks, cameras, sensors |

New tool: `src/tools/desktop_control.py`
MCP to add: `playwright`, `home-assistant`

---

### Layer 4 — Predictive & Proactive Intelligence
**Target: APEX anticipates before you ask.**

| Component | Tech | Notes |
|---|---|---|
| Daily pattern learner | SQLite time-series + sklearn | When you code, eat, context-switch |
| Intent prediction | n-gram + embedding similarity | 2 words typed → suggest completion |
| Pre-fetch engine | Extend `BriefingAgent` | Opening project X → preload docs/errors |
| Anomaly detection | Rolling stats on spend/activity | Alert on drift |
| Deadline radar | Already partial in `proactive.py` | Extend to calendar API |

New service: `src/services/predictor.py`
New slash: `/predict`, `/patterns`

---

### Layer 5 — Local Sovereignty (Offline Fallback)
**Target: APEX works with zero internet. Full privacy mode.**

| Component | Tech | Notes |
|---|---|---|
| Local LLM | Ollama + `qwen2.5-coder:32b` or `deepseek-v3` | GPU required (24GB+ VRAM for 32b) |
| Local embedding | `nomic-embed-text` via Ollama | Replace `sentence-transformers` |
| Local image model | `llava` via Ollama | Replace Gemini Vision |
| Fallback router | Extend `SmartRouter` | Cloud down → route to Ollama |
| Air-gap mode | Env flag `APEX_OFFLINE=1` | Block all outbound, local-only |

New env: `APEX_OFFLINE`, `OLLAMA_HOST`
Extend: `src/routers/router.py` fallback chain

---

### Layer 6 — Multi-Agent Swarm
**Target: APEX spawns specialist sub-agents, they debate, best answer wins.**

| Component | Tech | Notes |
|---|---|---|
| Swarm coordinator | Extend `ResearchSwarm` | Generalize beyond research |
| Specialist agents | Coder, Reviewer, Debugger, Designer, Critic | Each has scoped tools |
| Shared blackboard | Redis pub/sub or asyncio queue | Agents post findings, coordinator merges |
| Inter-agent debate | Structured adversarial prompting | Challenger must refute before commit |
| Swarm memory | ChromaDB collection per swarm session | Recall prior swarm conclusions |

New service: `src/services/swarm.py`
New slash: `/swarm <goal>`, `/swarm status`

---

### Layer 7 — Autonomous Operator Mode
**Target: APEX executes long-horizon goals autonomously.**

| Component | Tech | Notes |
|---|---|---|
| Goal decomposer | Tree-of-thought + Gemini 2.5 Pro | Multi-step plan with dependencies |
| Plan executor | Extend existing `ExecutionPlan` model | Tracks step state, retries, rollback |
| Reflection loop | Self-critique after each step | "Did this achieve sub-goal? Adjust." |
| Budget gate | Max spend per autonomous session | Hard stop on runaway usage |
| Irreversible-action guard | Extend `SafetyGuard` | Explicit confirm before any destructive op |
| Progress reporter | Rich Live panel + optional voice readout | Briefing-style updates during long runs |

New slash: `/goal "<long horizon task>"`, `/goal status`, `/goal abort`
Extend: `src/tools/safety.py`

---

### Layer 8 — Real-Time Data Fabric
**Target: APEX knows what's happening right now.**

| Component | Tech | Notes |
|---|---|---|
| WebSocket streams | `websockets` lib | GitHub events, crypto, custom feeds |
| RAG over everything | Extend ChromaDB + `watchdog` | Index code, notes, emails, browser history |
| Time-series store | DuckDB or SQLite WAL | Telemetry, spend, perf metrics |
| Browser history index | `sqlite3` → Chrome/Firefox profile | Local only; privacy-gated |
| News/research stream | Extend `KnowledgeForge` | Add RSS aggregator |

New service: `src/services/datastream.py`
New slash: `/stream add <url>`, `/stream list`

---

### Layer 9 — Web Dashboard (The "HUD")
**Target: Visual nerve center. Live telemetry, knowledge graph, mood ring.**

| Stack | Choice | Notes |
|---|---|---|
| Frontend | Next.js 15 + shadcn/ui + Tailwind | Fast to build, looks sharp |
| Backend WS | FastAPI + WebSocket | APEX streams events to browser |
| Knowledge graph viz | `react-force-graph` | Real-time node updates |
| Telemetry charts | Recharts or tremor | CPU/GPU/spend/bench scores |
| Proposal queue | Table with approve/reject buttons | `/forge` via REST API |
| Voice waveform | Web Audio API | Live mic + TTS visualizer |

New dir: `dashboard/` (separate Next.js app)
New service: `src/services/api_server.py` (FastAPI, port 7437)
New slash: `/dashboard start|stop`

---

### Layer 10 — Advanced Reasoning
**Target: APEX reasons better than any single model.**

| Component | Tech | Notes |
|---|---|---|
| Tool-use RL | Track success/fail per tool, update weights | Prefer winners |
| Symbolic solver | Z3 MCP or `z3-solver` direct | Constraint satisfaction, logic proofs |
| Debate-then-commit | Two Gemini calls: propose + adversarial | Before any irreversible action |
| Uncertainty quantification | Confidence scores on all outputs | Flag low-confidence for human review |
| Meta-cognition | APEX evaluates own reasoning quality | "Was my last answer good? Why?" |

Extend: `src/models/thinking_path.py`
New slash: `/reason <problem>` (explicit deep mode)

---

## Build Order (recommended)

```
Phase 1 (~2 weeks)   Voice + Ambient + Desktop Control
Phase 2 (~2 weeks)   Predictive layer + Local Ollama fallback
Phase 3 (~2 weeks)   Web Dashboard (HUD)
Phase 4 (~2 weeks)   Multi-agent Swarm + Autonomous Operator
Phase 5 (~ongoing)   Real-time Data Fabric + Advanced Reasoning
```

**Rule:** daily-drive each phase for 2 weeks before starting next. Stability > features.

---

## What Makes This Better Than JARVIS

| JARVIS | APEX Edge |
|---|---|
| Fictional — no real code | Real, running, extensible |
| Closed system | Fully open, self-modifying |
| Single AI | Multi-model routing (best model per task) |
| No self-improvement | SelfEvolver + KnowledgeForge (live arxiv) |
| No memory beyond session | ChromaDB persistent semantic memory |
| No benchmark tracking | SelfBenchmark regression detection |
| Cloud-dependent | Ollama fallback = air-gappable |
| No ecosystem watcher | Tracks PyPI/GitHub/HF/HN daily |
| Hardcoded behavior | Hooks system = fully programmable lifecycle |

---

## File Map (target state)

```
realjarvis/
  main.py                         REPL + slash commands
  dashboard/                      Next.js HUD (Phase 3)
  src/
    models/
      fast_path.py                Groq
      thinking_path.py            Gemini
      local_path.py               Ollama (Phase 2)
    services/
      memory.py                   Redis + Chroma + Cache
      learning.py                 Skill registry
      research.py                 ResearchSwarm
      cognitive.py                EmotionalCore + ApexState
      cognitive_graph.py          KnowledgeVisualizer
      proactive.py                BriefingAgent
      self_evolution.py           SelfEvolver
      code_compass.py             AST indexer
      knowledge_forge/            Arxiv + Ecosystem + Applier
      voice_layer.py              STT + TTS + wake-word (Phase 1)
      ambient.py                  Screen + clipboard + FS watcher (Phase 1)
      predictor.py                Pattern learner + intent (Phase 2)
      swarm.py                    Multi-agent coordinator (Phase 4)
      datastream.py               WS feeds + RAG (Phase 5)
      api_server.py               FastAPI for dashboard (Phase 3)
    tools/
      filesystem.py
      shell.py
      git_agent.py
      web_search.py
      workspace.py
      vision.py
      hardware.py
      mcp_client.py
      sandbox.py
      executor.py
      safety.py
      desktop_control.py          uiautomation + Playwright (Phase 1)
    routers/
      router.py                   InputClassifier + SmartRouter + ParallelExecutor
    core/
      models.py                   Pydantic schemas
      agents.py                   Base agent classes
      hooks.py                    HookManager
      telemetry.py                SpendTracker
  docs/
    JARVIS_ROADMAP.md             This file
  data/
    forge/                        Papers, ecosystem, proposals, bench
    chroma/                       Vector DB
```

---

## Dependencies to Add (by phase)

### Phase 1
```
faster-whisper
openwakeword
piper-tts
sounddevice
pyaudio
silero-vad
watchdog
uiautomation
pywin32
```

### Phase 2
```
ollama           # Python client
duckdb
```

### Phase 3
```
fastapi
uvicorn[standard]
websockets
```

### Phase 4
```
# No new deps — swarm uses existing Gemini + Groq
```

### Phase 5
```
z3-solver
websockets       # already added Phase 3
```

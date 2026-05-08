# APEX — Sovereign Agentic AI OS

APEX is a next-generation personal operating system designed for cognitive supremacy. It isn't just a wrapper around an LLM; it is a 24-layer orchestration engine that combines high-reasoning planning, fast edge-inference, specialized agent swarms, and an autonomous self-evolution cycle.

---

## 🏛️ The 24-Layer Sovereign Stack

APEX operates on a multi-tiered architecture designed for reliability, speed, and intelligence.

### Tier 1: Intelligence & Strategy (The Brain)
*   **Intent Normalization & Autonomous Routing**: Classifies queries using Gemini 2.0 Flash and activates **Sovereign Skills** automatically.
*   **Master Orchestrator**: Decomposes complex goals into dependency-ordered Task DAGs (Directed Acyclic Graphs).
*   **Socratic Reasoning Gate**: Forces assumption probing and mental friction for robust decision-making.
*   **Steelman Reasoning**: Generates the strongest possible counter-arguments to prevent cognitive bias.
*   **Emotional Intelligence Core**: Adapts tone and complexity based on detected user sentiment and cognitive load.

### Tier 2: Memory & Context (The Soul)
*   **Hybrid Memory System**: Combines **Short-term Working Memory (Redis)** with **Long-term Semantic Memory (ChromaDB)**.
*   **Relational Cognitive Graph**: Links interaction IDs into a semantic web of past decisions and facts.
*   **Semantic Deduplication Cache**: Bypasses LLM inference for near-identical past queries (sub-100ms latency).
*   **Code Compass**: AST-based symbol indexer providing **8-20x token savings** during code analysis.

### Tier 3: Execution & Validation (The Muscle)
*   **Parallel TaskGroup Dispatcher**: Orchestrates concurrent tool execution with atomic error handling.
*   **Multi-Stage Coding Pipeline**: Architecture Spec → Core Implementation → Automated Validation.
*   **Isolated Sandbox Execution**: Secure, timeout-limited environment for all auto-generated code.
*   **Multi-Agent Research Swarm**: Specialized agents (Web, File, Code) building high-density Knowledge Artifacts.

### Tier 4: Hardware & Environment (The Senses)
*   **Hardware-Native Bridge**: Proactive monitoring of CPU/RAM/Thermal metrics with automatic task throttling.
*   **Visual Context (The Retina)**: Multi-modal screen awareness for debugging and visual assistance.
*   **Telemetry & Spend Analytics**: Real-time USD cost logging and token usage tracking via SQLite.

---

## 🚀 Strategic Roadmap

APEX is evolving through 5 major phases to reach full ambient embodiment.

### Phase 1: Voice & Ambient Awareness (Current Focus)
*   **Wake-word Detection**: Local "APEX" trigger (openwakeword).
*   **Hands-free Speech**: Local STT (faster-whisper) and low-latency TTS (Piper).
*   **Continuous Screen Capture**: APEX sees what you see, reacting without being asked.
*   **Desktop Control**: Reliability via Windows UI Automation tree and Playwright.

### Phase 2: Predictive Intelligence
*   **Daily Pattern Learner**: SQLite time-series analysis to anticipate your needs.
*   **Intent Prediction**: Proactive document pre-loading and context switching.
*   **Local Sovereignty**: Full offline fallback using Ollama + DeepSeek/Qwen.

### Phase 3: The "HUD" (Web Dashboard)
*   **Visual Nerve Center**: Live telemetry, knowledge graph visualization, and proposal queue.
*   **Voice Waveform**: Real-time audio interaction visualization.

### Phase 4: Autonomous Operator Mode
*   **Long-Horizon Goals**: Autonomous execution of multi-step plans with rollback and reflection loops.
*   **Budget Gates**: Hard stops on spend per autonomous session.

---

## 🛠️ Quick Start

### 1. Prerequisites
- **Python 3.10+**
- **Redis** (running locally)
- **Node.js** (for MCP servers)

### 2. Install
```bash
git clone https://github.com/your-repo/realjarvis.git
cd realjarvis
pip install -r requirements.txt
```

### 3. Configure
Create a `.env` file:
```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
REDIS_HOST=localhost
REDIS_PORT=6379
CHROMA_PATH=./data/chroma
```

### 4. Run
```bash
python main.py
```

---

## ⌨️ Primary Slash Commands

- `/analyze`: Build/refresh token-efficient code map.
- `/evolve`: Run self-improvement cycle now.
- `/web <query>`: Deep web research swarm.
- `/genius`: Toggle multi-pass deep reasoning.
- `/project <name>`: Initialize a new agentic workspace.
- `/status`: Show hardware health, spend, and active MCP servers.

---

*“Stability > features. Daily-drive each phase before moving to the next.”*

# APEX — Setup Guide

---

## Prerequisites

| Requirement | Version | Why |
|---|---|---|
| Python | 3.13+ | f-string improvements, asyncio |
| Redis | any recent | session memory (optional — APEX degrades gracefully if absent) |
| Node.js | 18+ | MCP server support (optional) |
| CUDA GPU | optional | faster cv2 video processing |

---

## Installation

```bash
git clone <repo>
cd realjarvis
pip install -r requirements.txt
```

Key packages installed:
- `google-generativeai` — Gemini 2.5 Flash
- `groq` — Groq llama-3.1-8b + Whisper
- `openai` — MiMo v2.5-pro (OpenAI-compatible) + OpenRouter
- `rich` — terminal rendering + animations
- `pyfiglet` — ASCII art banner
- `reportlab` — PDF generation (ResumeTool)
- `python-docx` — DOCX resume parsing
- `pypdf` — PDF resume parsing
- `opencv-python` — video frame extraction
- `chromadb` — long-term semantic memory
- `redis` — short-term session memory
- `pytest-asyncio` — async test support
- `tenacity` — retry logic
- `tiktoken` — token counting

---

## Configuration

Create `.env` in the project root:

```env
# ── Required ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY=your_gemini_key_here

# ── Strongly recommended ───────────────────────────────────────────────────────
GROQ_API_KEY=your_groq_key_here
MIMO_API_KEY=your_mimo_key_here        # https://api.xiaomimimo.com

# ── Optional: tertiary fallback brain ─────────────────────────────────────────
OPENROUTER_API_KEY=your_openrouter_key_here

# ── Optional: architecture-spec brain (CodingPipeline stage 1) ────────────────
MINIMAX_API_KEY=your_minimax_key_here

# ── Optional: enhanced web search ─────────────────────────────────────────────
TAVILY_API_KEY=your_tavily_key_here
BRAVE_API_KEY=your_brave_key_here

# ── Memory ────────────────────────────────────────────────────────────────────
REDIS_HOST=localhost
REDIS_PORT=6379
CHROMA_PATH=./data/chroma

# ── Tuning ────────────────────────────────────────────────────────────────────
APEX_HISTORY_CAP=20                    # messages before summarize-before-drop
```

### What happens without each key

| Missing key | Effect |
|---|---|
| `GEMINI_API_KEY` | DAG planner, GeniusMode, ResumeTool all degrade to offline stubs |
| `GROQ_API_KEY` | Fast path + audio transcription offline; harness falls back further |
| `MIMO_API_KEY` | AgentHarness uses Groq only; CodingPipeline stage 2 offline |
| `REDIS_HOST` | No session memory; APEX still runs, history not persisted |
| `CHROMA_PATH` missing dir | ChromaDB auto-creates it |

---

## Running

```bash
# Normal boot
python main.py

# With UTF-8 encoding (recommended on Windows)
PYTHONIOENCODING=utf-8 python main.py

# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"; python main.py
```

APEX boots with:
1. Matrix rain animation
2. Pulse banner (APEX wordmark)
3. Model badges + tagline
4. Animated module checklist
5. Interactive prompt (`❯`)

---

## Running tests

```bash
# All tests
python -m pytest tests/ -v

# E2E smoke suite only (no network required)
python -m pytest tests/test_e2e_full_apex.py -v

# Specific test
python -m pytest tests/test_e2e_full_apex.py::test_harness_fs_crud_end_to_end -v

# With encoding (Windows)
PYTHONIOENCODING=utf-8 python -m pytest tests/ -v
```

See [TESTING.md](TESTING.md) for full test documentation.

---

## Directory layout after first run

```
realjarvis/
├── .env                    your API keys (never committed)
├── .apex/
│   ├── code_compass.json   AST symbol map (generated on /analyze)
│   └── forge_state.json    KnowledgeForge state
├── data/
│   ├── chroma/             ChromaDB files
│   └── todos.json          todo list
└── backups/                AgentHarness snapshots (auto-created)
```

---

## MCP setup (optional)

APEX can connect to any MCP server. Configure in `.apex/hooks.json`:

```json
{
  "mcp_servers": [
    {
      "name": "filesystem",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/your/path"]
    }
  ]
}
```

Then use `/mcp connect <server_name>` in APEX.

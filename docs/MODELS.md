# APEX — LLM Providers

Every brain in APEX has a specific role. No provider is used for everything — each is chosen for what it does best.

---

## Provider map

| Provider | Model | File | Role |
|---|---|---|---|
| Google Gemini | `gemini-2.5-flash` | `src/models/thinking_path.py` | DAG planner, JSON-forced reasoning, vision, resume rewrite, genius critique |
| Google Gemini | `gemini-2.5-flash-lite` | inline | Input classification, LLM auto-selector tier 2, summarize-before-drop |
| Groq | `llama-3.1-8b` | `src/models/fast_path.py` | Fast path streaming, AgentHarness fallback brain, GeniusMode fallback |
| Groq | `whisper-large-v3` | `src/tools/vision.py` | Audio transcription |
| Xiaomi MiMo | `mimo-v2.5-pro` | `src/models/mimo_path.py` | Code implementation (CodingPipeline), AgentHarness primary brain |
| MiniMax | `minimax-2.5` | `src/models/minimax_path.py` | CodingPipeline stage 1 — architecture spec |
| OpenRouter | `gpt-oss-120b` | `src/models/fallback_path.py` | Tertiary fallback when Gemini + agent retry both fail (DAG planner) |
| OpenRouter | `inclusionai/ring-2.6-1t:free` | `src/models/fallback_path.py` | High-reasoning fallback for ThinkPartner + GeniusMode (1T-param, free) |

---

## Gemini 2.5 Flash (`src/models/thinking_path.py`)

**Used for:** planning, JSON generation, vision, analysis

- `TimeContext.system_prefix()` + `tool_registry.get_prompt_block()` auto-injected into every call
- `genius_mode` flag: multi-pass (hypothesis → counters → blind-spot → synthesis)
- `socratic_mode` flag: assumption-surfacing questions
- `steelman_mode` flag: adversarial pushback
- JSON mime-type forced for structured outputs (GeniusMode, ResumeTool)
- Multimodal: accepts image bytes for vision tasks

**When Gemini is offline:** GeniusMode returns offline stub, ResumeTool returns stub dict, planner returns graceful error.

---

## Groq llama-3.1-8b (`src/models/fast_path.py`)

**Used for:** fast responses, harness fallback

- Streaming by default
- TimeContext injected
- Selected by `SmartRouter` for low-complexity inputs
- AgentHarness falls back here when MiMo is offline

---

## Groq Whisper-large-v3 (`src/tools/vision.py`)

**Used for:** audio transcription in `RetinaTool.transcribe_audio(path)`

- Called via `groq.audio.transcriptions.create()`
- Accepts mp3/wav/flac/ogg/m4a
- Returns raw transcript string

---

## Xiaomi MiMo v2.5-pro (`src/models/mimo_path.py`)

**Used for:** code implementation, agentic tool loop

- OpenAI-compatible API at `https://api.xiaomimimo.com/v1`
- Replaces ChatGPT Codex (removed)
- Env var: `MIMO_API_KEY`
- Three interfaces:
  - `get_completion(prompt, ...)` — sync
  - `aget_completion(prompt, ...)` — async
  - `stream_completion(prompt, ...)` — streaming generator
- `is_online` property — True when key present + client constructed
- `api_key_env` parameter — allows specifying alternate env var name (used in tests to force offline path)
- `thinking=True` parameter — enables extended reasoning mode

**CodingPipeline role:**
```
MiniMax 2.5 (arch spec) → MiMo v2.5-pro (implementation) → Gemini 2.5 Flash (validation)
```

**AgentHarness role:** Primary brain for all tool-calling decisions. Falls back to Groq on error.

---

## MiniMax 2.5 (`src/models/minimax_path.py`)

**Used for:** CodingPipeline stage 1 only — produces architecture specification that MiMo then implements.

---

## OpenRouter (`src/models/fallback_path.py`)

Two clients, two roles:

### `TertiaryReasoningClient` — DAG planner recovery
- Model: `gpt-oss-120b`
- Fires after agent retry + Gemini retry both fail in the planning pipeline
- Env var: `OPENROUTER_API_KEY`

### `HighReasoningClient` — deep thinking fallback
- Model: `inclusionai/ring-2.6-1t:free` — 1 trillion parameter free reasoning model
- Used by: `ThinkPartner._gen()` when Gemini hits rate limits or quota errors
- Used by: `GeniusMode.analyze()` as 4th tier (after Gemini → MiMo → Groq)
- Env var: `OPENROUTER_API_KEY` (same key)

---

## Brain selection logic

```
Simple prompt
  → regex auto-selector → execute directly (no brain needed for tool dispatch)

Moderate prompt
  → LLM auto-selector → Gemini Flash Lite classify → single tool

Complex prompt
  → SmartRouter → thinking_path (Gemini 2.5 Flash) → DAG plan → ParallelExecutor

AgentHarness task
  → MiMo v2.5-pro (primary) → Groq (fallback on error)

GeniusMode critique
  → Gemini 2.5 Flash (JSON-forced) → MiMo → Groq → offline stub

ResumeTool rewrite
  → Gemini 2.5 Flash (JSON-forced) → offline stub dict
```

---

## Adding a new provider

1. Create `src/models/<name>_path.py` — wrap the SDK, inject `TimeContext.system_prefix()`
2. Add offline fallback (return stub, never raise)
3. Wire into relevant service (GeniusMode brain cascade, AgentHarness `_select_brain`, etc.)
4. Add `<NAME>_API_KEY` to `.env.example`

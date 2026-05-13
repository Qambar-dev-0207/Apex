# APEX Documentation Index

> Personal AI OS — documentation for every layer, module, and feature.

---

## Table of Contents

| Document | What it covers |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Full system design, input pipeline, data flow, all layers |
| [SETUP.md](SETUP.md) | Installation, env vars, requirements, running APEX |
| [MODELS.md](MODELS.md) | Every LLM provider — when and why each is used |
| [TOOLS.md](TOOLS.md) | All 17 registered tools + 35 AgentHarness tools |
| [HARNESS.md](HARNESS.md) | AgentHarness deep dive — autonomous tool loop |
| [COMMANDS.md](COMMANDS.md) | Complete slash command reference |
| [GENIUS_MODE.md](GENIUS_MODE.md) | GeniusMode, resume rewriting, critique system |
| [VISION.md](VISION.md) | Image, video, audio understanding (RetinaTool) |
| [ANIMATIONS.md](ANIMATIONS.md) | Terminal animation system |
| [TESTING.md](TESTING.md) | Test suites, coverage, how to run |
| [JARVIS_ROADMAP.md](JARVIS_ROADMAP.md) | What's built and what's next |
| [CHANGELOG.md](CHANGELOG.md) | Release history |

---

## Quick orientation

```
main.py              ← CLI entry point, slash commands, boot sequence
src/
  models/            ← LLM clients (Gemini, Groq, MiMo, OpenRouter, MiniMax)
  services/          ← Higher-level services (ThinkPartner, Swarm, GeniusMode, ResumeTool, ...)
  tools/             ← Tool implementations + registry + auto-selector
  core/              ← Harness, animations, time_context, hooks
  routers/           ← InputClassifier, SmartRouter, ParallelExecutor
tests/               ← All test suites (21+ E2E + 279 unit tests)
docs/                ← This folder
```

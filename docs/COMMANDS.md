# APEX — Slash Command Reference

All commands start with `/`. Type `/help` in APEX for an inline listing.

---

## Session

| Command | Description |
|---|---|
| `/help` | Show all commands |
| `/now` | Show current date, time, weekday |
| `/clear` | Clear current session history |
| `/clear-session` | Clear session (alias) |
| `/clear-all` | Clear all history including ChromaDB + cache |
| `/exit` | Exit APEX |
| `/resume` | Resume a previous session |
| `/compact` | Compact/summarize long context |
| `/status` | Show system status (models, memory, hardware) |
| `/cost` | Show daily token spend |

---

## Workspace

| Command | Description |
|---|---|
| `/init` | Initialize workspace for current project |
| `/scan` | Scan and index project |
| `/map` | Show project knowledge map |
| `/prune` | Remove stale memory entries |
| `/project <name>` | Switch active project |
| `/skills` | List loaded skills |
| `/reload-skills` | Reload skills from disk |

---

## Todos

| Command | Description |
|---|---|
| `/todo <task>` | Add a todo item |
| `/todo done <n>` | Mark todo N as done |
| `/todos` | List all todos |

---

## Reasoning modes (Gemini)

| Command | Description |
|---|---|
| `/socratic` | Toggle Socratic mode (surfaces assumptions) |
| `/steelman` | Toggle steelman mode (strongest opposing view) |
| `/genius` | Toggle genius mode (multi-pass deep critique) |

---

## Routing

| Command | Description |
|---|---|
| `/autothink on\|off` | Auto-route ambiguous prompts to ThinkPartner |
| `/autotool on\|off` | Bypass DAG planner for simple single-tool intents |

---

## Think Partner

| Command | Description |
|---|---|
| `/think <prompt>` | Cross-question mode — surfaces blocking ambiguity |
| `/architect <idea>` | Design + critique |
| `/architect <idea> \| <your-arch>` | Review your architecture |
| `/debate <claim>` | Adversarial pushback (steelman opposing view) |
| `/brainstorm <topic>` | 6 distinct angles via different mental models |
| `/teach <topic>` | Layered: intuition → mechanism → example → misconceptions → self-test |
| `/intent <prompt>` | Structured intent JSON (debug aid) |

---

## GeniusMode

| Command | Description |
|---|---|
| `/genius <prompt>` | Full 5-stage analysis: cross_question/right/wrong/blind_spots/action/one_liner |
| `/critique <prompt>` | Right/wrong only + one-liner — quick sanity check |
| `/blindspot <prompt>` | Blind spots + ranked actions |

---

## Resume

| Command | Description |
|---|---|
| `/resume <path>` | Improve resume, output as PDF |
| `/resume <path> \| <target role>` | Same, with target role for tailored rewrite |

---

## AgentHarness

| Command | Description |
|---|---|
| `/harness <goal>` | Run autonomous agent loop on a goal (MiMo-driven, 35 tools) |

---

## Web & Fetch

| Command | Description |
|---|---|
| `/fetch <url>` | Fetch and strip a URL to plain text |
| `/diff <file_a> <file_b>` | Show unified diff between two files |

---

## Multi-Agent Swarm

| Command | Description |
|---|---|
| `/swarm <goal>` | Spawn specialist agents in parallel |
| `/swarm <goal> \| architect,critic` | Force specific agent roster |
| `/swarm <goal> rounds=2` | Multi-round collaboration |

---

## Knowledge Forge

| Command | Description |
|---|---|
| `/forge` | Full cycle (papers + ecosystem + synthesis + bench) |
| `/forge papers` | Scan arxiv only |
| `/forge ecosystem` | Scan PyPI/GitHub/HF/HN/npm only |
| `/forge synth` | Run capability synthesizer only |
| `/forge bench` | Run self-benchmark only |
| `/forge proposals` | List queued capability proposals |
| `/forge approve <id>` | Approve a proposal |
| `/forge reject <id>` | Reject a proposal |
| `/forge implement <id>` | Apply approved proposal (bench-gated rollback) |
| `/forge implement <id> diff` | Diff mode — safer for large files |
| `/forge backfill <N>` | Catch-up arxiv scan for N days |
| `/forge undo <id>` | Restore last backup for a proposal |
| `/forge log` | Show `~/.apex/forge_log.md` |
| `/forge search <query>` | Semantic search ingested papers |
| `/forge status` | Show forge state |

---

## Code Intel

| Command | Description |
|---|---|
| `/analyze` | Refresh CodeCompass AST map |
| `/analyze <term>` | Symbol search across project |
| `/map-stats` | Show AST map statistics |

---

## Tools

| Command | Description |
|---|---|
| `/tools` | List all registered tools + per-tool telemetry (ok/fail) |

---

## Self-Evolution

| Command | Description |
|---|---|
| `/evolve` | Run improvement cycle now |
| `/evolve auto` | Run cycle + auto-provision missing skill |
| `/proposals` | List improvement proposals |

---

## Shell passthrough

```
! <command>
```

Runs any shell command directly. Example: `! git log --oneline -5`

# APEX — Tool Reference

Two tool surfaces exist in APEX:
1. **Registered tools** (17) — the tool registry used by the DAG planner and auto-selector
2. **Harness tools** (35) — OpenAI function-schema tools used by the AgentHarness autonomous loop

---

## Registered tools (`src/tools/registry.py`)

### `filesystem` (aliases: `fs`, `file`)
File system I/O — read, write, delete, list, search, glob.
- Actions: `read`, `write`, `delete`, `list`, `search`, `glob`
- Backed by: `src/tools/filesystem.py`

### `shell` (aliases: `bash`, `sh`, `run`)
Execute shell commands.
- Actions: `execute`
- Backed by: `src/tools/shell.py`

### `git` (aliases: `vcs`)
Version control operations.
- Actions: `commit`, `status`, `diff`, `add`, `push`, `pull`, `log`, `checkout`
- Backed by: `src/tools/git_agent.py`

### `python_executor` (aliases: `python`, `py`)
Write and run Python code — either code-gen pipeline or direct sandbox execution.
- Actions: `write`, `run`
- Backed by: `src/tools/sandbox.py`, `src/services/coding.py`

### `research_swarm` (aliases: `research`, `rs`)
Multi-agent research across web/file/code sources.
- Actions: `search`
- Backed by: `src/services/swarm.py`

### `web_search` (aliases: `search`, `ws`)
Web search via Tavily (primary), Brave (secondary), or DuckDuckGo (fallback).
- Actions: `search`
- Backed by: `src/tools/web_search.py`

### `web_fetch` (aliases: `fetch`, `url`, `wf`, `get_url`)
Fetch a URL and strip to plain text. Handles HTML/JSON/XML. MAX 1.5MB, truncates to 20K chars.
- Actions: `fetch`
- Backed by: `src/tools/web_fetch.py`

### `workspace` (aliases: `ws2`)
Project workspace context — scan, summarize, directives, list projects.
- Actions: `scan`, `summarize`, `directives`, `list_projects`
- Backed by: `src/tools/workspace.py`

### `mcp` (aliases: `mcp_call`)
Connect to and call external MCP servers.
- Actions: `connect`, `call`
- Backed by: `src/tools/mcp_client.py`

### `vision` (aliases: `retina`)
Screen capture, image description, OCR, video understanding, audio transcription.
- Actions: `capture`, `ocr`, `describe`, `describe_video`, `transcribe_audio`, `understand_media`
- Backed by: `src/tools/vision.py`

### `hardware` (aliases: `hw`, `vitals`)
CPU, RAM, GPU readings and load status.
- Actions: `vitals`, `load`
- Backed by: `src/tools/hardware.py`

### `code_compass` (aliases: `compass`)
Token-efficient AST symbol search and compressed code context.
- Actions: `search`, `stats`, `context`
- Backed by: `src/services/code_compass.py`

### `knowledge_forge` (aliases: `forge`)
Search ingested papers, list proposals, forge status, daily digest.
- Actions: `search_papers`, `list_proposals`, `status`, `digest`
- Backed by: `src/services/knowledge_forge/forge.py`

### `swarm` (aliases: `agents`)
Spawn a multi-agent specialist swarm on a goal.
- Actions: `run`
- Backed by: `src/services/swarm.py`

### `think_partner` (aliases: `think`)
Cognitive collaborator — 6 modes of deep thinking.
- Actions: `cross_question`, `architect`, `debate`, `brainstorm`, `teach`
- Backed by: `src/services/think_partner.py`

### `todo` (aliases: `todos`, `tasks`, `tl`)
Persistent todo list backed by `data/todos.json`.
- Actions: `add`, `list`, `update`, `remove`, `clear_completed`
- Backed by: `src/tools/todo.py`

### `diff` (aliases: `compare`, `patch`)
Unified diff between files or file vs string content.
- Actions: `diff_files`, `diff_content`
- Backed by: `src/tools/diff_tool.py`

---

## Harness tools (`src/core/harness.py` → `TOOL_SCHEMAS`)

These 35 tools are available to the AgentHarness autonomous loop via OpenAI function-calling format.

### File system (10)
| Name | Description |
|---|---|
| `view` | Read file with optional line range |
| `write` | Create or overwrite file (blocked for .env, .git/, id_rsa, .ssh/) |
| `edit` | Replace unique string in file |
| `multi_edit` | Apply multiple replacements atomically |
| `create_dir` | Create directory tree |
| `delete` | Delete file or directory |
| `list_dir` | List directory |
| `tree` | Recursive directory tree |
| `glob` | Find files by glob pattern |
| `grep` | Regex search across files |

### Shell & VCS (3)
| Name | Description |
|---|---|
| `bash` | Run shell command |
| `git` | Run git command |
| `diff_preview` | Unified diff between two files |

### Todos (3)
| Name | Description |
|---|---|
| `todo_add` | Add todo item |
| `todo_list` | List todos |
| `todo_done` | Mark todo done |

### Vision & media (6)
| Name | Description |
|---|---|
| `vision_capture` | Screenshot |
| `vision_describe` | Describe image |
| `vision_ocr` | Extract text from image |
| `video_describe` | Sample + describe video |
| `audio_transcribe` | Transcribe audio (Groq Whisper) |
| `understand_media` | Auto-route by file extension |

### APEX services (12)
| Name | Description |
|---|---|
| `hardware_vitals` | CPU/RAM/GPU readings |
| `code_compass_search` | AST symbol search |
| `code_compass_context` | Compressed code context |
| `knowledge_forge_search` | Search ingested papers |
| `swarm_run` | Run specialist agent swarm |
| `think_partner` | Run a ThinkPartner mode |
| `web_search` | Web search |
| `web_fetch` | Fetch + strip URL |
| `research_swarm` | Multi-agent research |
| `workspace_summarize` | Summarize workspace |
| `mcp_call` | Call MCP server |
| `python_run` | Execute Python in sandbox |

### Termination (1)
| Name | Description |
|---|---|
| `done` | Signal completion with summary |

---

## Auto-selector regex patterns

High-confidence (0.95) patterns that bypass the DAG planner:

| Pattern | Tool | Action |
|---|---|---|
| `git status/log/diff/commit` | git | matched git verb |
| `read/view/open <file>` | filesystem | read |
| `write/create <file>` | filesystem | write |
| `delete/remove <file>` | filesystem | delete |
| `ls/list <dir>` | filesystem | list |
| `grep/search <term>` | filesystem | search |
| `https?://...` | web_fetch | fetch |
| `todos / my tasks` | todo | list |
| `add todo / todo add <task>` | todo | add |
| `vitals / cpu / ram` | hardware | vitals |
| `papers about <topic>` | knowledge_forge | search_papers |
| `screenshot / capture screen` | vision | capture |

Patterns that don't match go to Tier 2 (Gemini Flash Lite LLM classifier) or the full DAG planner.

# AgentHarness — Autonomous Tool Loop

`src/core/harness.py`

---

## What it is

AgentHarness is APEX's autonomous agent runtime. Given a goal, it:
1. Sends the goal + tool schemas to MiMo (or Groq fallback)
2. Receives a tool call decision
3. Executes the tool
4. Feeds the result back
5. Repeats until `done()` is called or max iterations reached

It is the difference between APEX answering questions and APEX *doing things*.

**Slash command:** `/harness <goal>`

---

## Architecture

```
/harness "refactor auth module"
        │
        ▼
AgentHarness.__init__(project_root=cwd)
        │
        ▼
AgentHarness.run(goal, max_iter=20)
        │
        ├── messages = [system_prompt, user_goal]
        │
        └── LOOP (up to max_iter):
              │
              ├── _select_brain() → MiMo or Groq
              │
              ├── brain.chat.completions.create(tools=TOOL_SCHEMAS, ...)
              │
              ├── no tool_call? → break (done)
              │
              ├── tool_call is "done" → break
              │
              └── _dispatch(tool_name, args)
                    │
                    ├── security check (BLOCKED_PATHS)
                    ├── execute tool
                    └── append result → continue loop
```

---

## Brain selection

```python
def _select_brain():
    if mimo.is_online:
        return mimo_client  # MiMo v2.5-pro
    return groq_client      # llama-3.1-8b
```

Both are OpenAI-compatible clients, so tool-calling format is identical.

---

## Security

### Blocked paths
Writes and deletes to these paths are rejected at the harness level:
```python
BLOCKED_PATHS = (".git/", ".env", "id_rsa", ".ssh/")
```

### Auto-snapshot
On the FIRST write to any existing file in a session, the harness snapshots the original to:
```
backups/harness_<timestamp>/relative/path/to/file
```

Call `harness.rollback()` to restore all snapshotted files.

### Atomic multi_edit
`multi_edit` validates ALL edits against the file content before applying any. If edit N fails to find its `old_string`, the file is left unchanged and an error is returned. Never leaves a partially-edited file.

### Ambiguous edit rejection
`edit` rejects any `old_string` that appears more than once in the target file (`"2x"` error). Forces the caller to be more specific.

---

## Tool catalog (35 tools)

### File system
| Tool | Description |
|---|---|
| `view` | Read file contents (optionally with line range) |
| `write` | Create or overwrite file |
| `edit` | Replace exact string in file (single-occurrence guaranteed) |
| `multi_edit` | Apply multiple replacements atomically |
| `create_dir` | Create directory tree |
| `delete` | Delete file or directory (recursive optional) |
| `list_dir` | List directory contents |
| `tree` | Recursive directory tree with depth limit |
| `glob` | Find files matching glob pattern |
| `grep` | Regex search across files |

### Shell & VCS
| Tool | Description |
|---|---|
| `bash` | Execute shell command in project root |
| `git` | Run git command |
| `diff_preview` | Unified diff between two file paths |

### Todos
| Tool | Description |
|---|---|
| `todo_add` | Add a todo item |
| `todo_list` | List all todos with status |
| `todo_done` | Mark a todo as completed |

### Media & vision
| Tool | Description |
|---|---|
| `vision_capture` | Capture screenshot |
| `vision_describe` | Describe an image file via Gemini |
| `vision_ocr` | Extract text from image |
| `video_describe` | Sample video frames + describe via Gemini |
| `audio_transcribe` | Transcribe audio via Groq Whisper |
| `understand_media` | Auto-route by file extension |

### APEX services
| Tool | Description |
|---|---|
| `hardware_vitals` | CPU/RAM/GPU readings |
| `code_compass_search` | AST symbol search |
| `code_compass_context` | Compressed code context for a symbol |
| `knowledge_forge_search` | Semantic search across ingested papers |
| `swarm_run` | Spawn specialist agent swarm on a goal |
| `think_partner` | Run a ThinkPartner mode (cross_question/architect/debate/brainstorm/teach) |
| `web_search` | Web search via Tavily/Brave/DDG |
| `web_fetch` | Fetch and strip a URL |
| `research_swarm` | Multi-agent research swarm |
| `workspace_summarize` | Summarize project workspace |
| `mcp_call` | Call a connected MCP server |
| `python_run` | Execute Python code in sandbox |

### Termination
| Tool | Description |
|---|---|
| `done` | Signal task completion with summary |

---

## Slash command usage

```
/harness <goal>
```

Example:
```
/harness add docstrings to all public functions in src/tools/
/harness find all TODO comments and create todo items for each
/harness refactor the registry to use dataclasses
```

The harness runs fully autonomously until it calls `done()` or hits the iteration cap.

---

## Iteration cap

Default: `max_iter=20`. APEX prints a warning if the cap is hit without `done()`.

Increase for long tasks:
```python
await harness.run(goal, max_iter=40)
```

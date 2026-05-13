# APEX — Testing

---

## Running tests

```bash
# All suites
python -m pytest tests/ -v

# E2E only (no network required)
python -m pytest tests/test_e2e_full_apex.py -v

# Windows with UTF-8
$env:PYTHONIOENCODING="utf-8"; python -m pytest tests/ -v

# Single test
python -m pytest tests/test_e2e_full_apex.py::test_harness_fs_crud_end_to_end -v

# Quiet output
python -m pytest tests/ -q
```

---

## Test suites

| Suite | Tests | Requires network | Coverage |
|---|---|---|---|
| `test_e2e_full_apex.py` | 21 | No | Full APEX E2E smoke |
| `test_knowledge_forge.py` | 93 | No (mocked) | Paper reader, ecosystem, synthesizer, applier, bench |
| `test_memory_system.py` | 37 | No (mocked) | Redis self-heal, async Chroma, cache stats, summarize-before-drop |
| `test_think_partner.py` | 23 | No (mocked) | 6 modes + auto-route |
| `test_swarm.py` | 23 | No (mocked) | Blackboard, agent, coordinator, multi-round |
| `test_time_context.py` | 36 | No | Time-of-day, greetings, relative deltas |
| `test_tool_registry.py` | 23 | No | Registry completeness, alias resolution, telemetry |
| `test_auto_selector.py` | 30 | No | Regex patterns, LLM classifier |
| **Total** | **286+** | | |

---

## E2E suite detail (`test_e2e_full_apex.py`)

All 21 tests designed to pass WITHOUT network keys. Every test either runs fully offline or skips cleanly.

### Registry + auto-selector (4 tests)
| Test | Checks |
|---|---|
| `test_registry_has_required_tools` | 17 must-have tool names present |
| `test_registry_alias_resolution` | 8 alias → canonical mappings |
| `test_registry_prompt_block_renders` | AVAILABLE TOOLS block contains key tool names |
| `test_auto_selector_regex_patterns` | 6 regex cases (git, read, URLs, todos, vitals) |

### Harness FS CRUD (4 tests)
| Test | Checks |
|---|---|
| `test_harness_fs_crud_end_to_end` | Full create_dir → write → view → edit → multi_edit → tree → grep → delete cycle |
| `test_harness_atomic_multi_edit_rollback` | multi_edit with failing edit leaves file unchanged |
| `test_harness_blocks_env_writes` | `.env` write blocked, error contains "blocked" |
| `test_harness_rejects_ambiguous_edit` | Duplicate old_string rejected with "2x" error |

### Vision (1 test)
| Test | Checks |
|---|---|
| `test_vision_understand_media_routes_by_extension` | .png→image, .mp4→video, .mp3→audio, .xyz→unknown (no Gemini call needed) |

### Resume (3 tests)
| Test | Checks |
|---|---|
| `test_resume_load_plain_text` | .txt file read returns content |
| `test_resume_render_pdf_minimum` | PDF created, > 500 bytes |
| `test_resume_offline_fallback_structure` | No Gemini key → returns dict with name/feedback/skills keys |

### GeniusMode (1 test)
| Test | Checks |
|---|---|
| `test_genius_offline_stub_shape` | Forces offline (g.gemini=g.mimo=g.groq=None) → returns all 6 required keys |

### Todo (1 test)
| Test | Checks |
|---|---|
| `test_todo_lifecycle` | Full add → update(in_progress) → update(completed) → clear_completed cycle |

### Diff (2 tests)
| Test | Checks |
|---|---|
| `test_diff_files` | Two different files → success=True, changed=True, added=1, removed=1 |
| `test_diff_content_no_change` | Same content → output=="(no changes)" |

### WebFetch (1 test)
| Test | Checks |
|---|---|
| `test_web_fetch_html_stripper` | Inline HTML → scripts stripped, text preserved, entities decoded |

### Animations (1 test)
| Test | Checks |
|---|---|
| `test_animations_safe_on_non_tty` | All 5 animation functions run without exception on non-tty console |

### Brain clients (2 tests)
| Test | Checks |
|---|---|
| `test_mimo_client_construction` | is_online=False with fake env var; offline response starts with "[MiMo Offline]" |
| `test_groq_client_construct` | Constructs without crash; has `model` attribute |

### Harness tool schemas (1 test)
| Test | Checks |
|---|---|
| `test_harness_tool_schemas_complete` | All 35 expected tool names present in TOOL_SCHEMAS |

---

## pytest configuration (`pytest.ini`)

```ini
[pytest]
asyncio_mode = auto
markers =
    asyncio: mark test as asyncio coroutine
filterwarnings =
    ignore::DeprecationWarning
```

`asyncio_mode = auto` means async test functions run automatically without `@pytest.mark.asyncio` per-test decorators.

---

## Mocking patterns

Unit tests mock at the SDK level:
```python
# Memory tests
from unittest.mock import AsyncMock, patch
with patch("redis.Redis") as mock_redis: ...
with patch("chromadb.PersistentClient") as mock_chroma: ...

# LLM tests
with patch("google.generativeai.Client") as mock_gemini: ...
```

E2E tests avoid mocking — they test real code paths with offline-safe branches (no key → stub response).

---

## Adding tests

1. Create `tests/test_<feature>.py`
2. Import from `src/` (sys.path setup already in conftest or handled per-test via `ROOT` pattern)
3. For async tests: just use `async def test_foo()` — `asyncio_mode=auto` handles it
4. For offline-only tests: use `os.environ.pop("API_KEY", None)` or pass `api_key_env="DOES_NOT_EXIST_XYZ"` to force offline path
5. Run: `python -m pytest tests/test_<feature>.py -v`

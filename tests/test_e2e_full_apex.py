"""
End-to-end smoke suite for APEX. Designed to run WITHOUT network keys —
every test must either pass offline or skip cleanly with a clear reason.

Coverage:
  • Tool registry + alias resolution
  • Auto-selector regex tier
  • Harness FS CRUD + atomic multi_edit rollback + path blocking + snapshot
  • Vision routing (offline, by extension)
  • Resume parsing + PDF render (offline fallback path)
  • GeniusMode offline stub structure
  • Todo persistence
  • Diff tool
  • WebFetch HTML stripper (offline, no network)
  • Animations callable on non-tty (no exceptions)
  • MiMo + Groq client construction (offline)

Run:
    PYTHONIOENCODING=utf-8 python -m pytest tests/test_e2e_full_apex.py -v
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure repo root on sys.path for local pytest runs.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ─────────────────────────────────────────────────────────────────────────────
# Registry + auto-selector
# ─────────────────────────────────────────────────────────────────────────────

def test_registry_has_required_tools():
    from src.tools.registry import REGISTRY, list_tools
    must_have = {
        "filesystem", "shell", "git", "python_executor", "research_swarm",
        "web_search", "web_fetch", "workspace", "mcp", "vision", "hardware",
        "code_compass", "knowledge_forge", "swarm", "think_partner",
        "todo", "diff",
    }
    missing = must_have - set(list_tools())
    assert not missing, f"missing tools: {missing}"
    assert len(REGISTRY) >= len(must_have)


def test_registry_alias_resolution():
    from src.tools.registry import resolve_tool_name
    cases = [
        ("fs", "filesystem"), ("web", "web_search"), ("fetch", "web_fetch"),
        ("hw", "hardware"), ("compass", "code_compass"),
        ("tasks", "todo"), ("compare", "diff"), ("retina", "vision"),
    ]
    for raw, expected in cases:
        assert resolve_tool_name(raw) == expected, raw


def test_registry_prompt_block_renders():
    from src.tools.registry import get_prompt_block
    out = get_prompt_block()
    assert "AVAILABLE TOOLS" in out
    assert "filesystem" in out and "web_fetch" in out and "diff" in out


def test_auto_selector_regex_patterns():
    from src.tools.auto_selector import regex_match
    cases = [
        ("git status", "git", "status"),
        ("read main.py", "filesystem", "read"),
        ("https://example.com", "web_fetch", "fetch"),
        ("todos", "todo", "list"),
        ("todo add wire harness", "todo", "add"),
        ("vitals", "hardware", "vitals"),
    ]
    for prompt, tool, action in cases:
        m = regex_match(prompt)
        assert m is not None, prompt
        assert m["tool"] == tool and m["action"] == action, prompt


# ─────────────────────────────────────────────────────────────────────────────
# Harness — FS CRUD
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_harness_fs_crud_end_to_end():
    from src.core.harness import AgentHarness
    tmp = tempfile.mkdtemp()
    h = AgentHarness(project_root=tmp)

    r = await h._dispatch("create_dir", {"path": "src"})
    assert r["success"]

    r = await h._dispatch("write", {"path": "src/a.py", "content": "x = 1\ny = 2\n"})
    assert r["success"] and "wrote" in r["output"]

    r = await h._dispatch("view", {"path": "src/a.py"})
    assert r["success"] and "x = 1" in r["output"]

    r = await h._dispatch("edit", {"path": "src/a.py", "old_string": "x = 1", "new_string": "x = 42"})
    assert r["success"]

    r = await h._dispatch("multi_edit", {
        "path": "src/a.py",
        "edits": [
            {"old_string": "x = 42", "new_string": "x = 100"},
            {"old_string": "y = 2", "new_string": "y = 200"},
        ],
    })
    assert r["success"]

    r = await h._dispatch("view", {"path": "src/a.py"})
    assert "x = 100" in r["output"] and "y = 200" in r["output"]

    r = await h._dispatch("tree", {"path": ".", "depth": 2})
    assert r["success"] and "src" in r["output"]

    r = await h._dispatch("grep", {"pattern": "x = 100", "path": ".", "file_glob": "*.py"})
    assert r["success"] and "x = 100" in r["output"]

    r = await h._dispatch("delete", {"path": "src", "recursive": True})
    assert r["success"]


@pytest.mark.asyncio
async def test_harness_atomic_multi_edit_rollback():
    from src.core.harness import AgentHarness
    tmp = tempfile.mkdtemp()
    h = AgentHarness(project_root=tmp)
    await h._dispatch("write", {"path": "b.py", "content": "hello\nworld\n"})

    r = await h._dispatch("multi_edit", {
        "path": "b.py",
        "edits": [
            {"old_string": "hello", "new_string": "HI"},
            {"old_string": "MISSING", "new_string": "X"},  # this fails
        ],
    })
    assert not r["success"]
    # File should still contain ORIGINAL content.
    with open(os.path.join(tmp, "b.py"), encoding="utf-8") as f:
        assert f.read() == "hello\nworld\n"


@pytest.mark.asyncio
async def test_harness_blocks_env_writes():
    from src.core.harness import AgentHarness
    tmp = tempfile.mkdtemp()
    h = AgentHarness(project_root=tmp)
    r = await h._dispatch("write", {"path": ".env", "content": "SECRET=oops"})
    assert not r["success"]
    assert "blocked" in r["error"].lower()


@pytest.mark.asyncio
async def test_harness_rejects_ambiguous_edit():
    from src.core.harness import AgentHarness
    tmp = tempfile.mkdtemp()
    h = AgentHarness(project_root=tmp)
    await h._dispatch("write", {"path": "c.py", "content": "x = 1\nx = 1\n"})
    r = await h._dispatch("edit", {"path": "c.py", "old_string": "x = 1", "new_string": "y = 2"})
    assert not r["success"] and "2x" in r["error"]


# ─────────────────────────────────────────────────────────────────────────────
# Vision routing (offline — no Gemini call required for these branches)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_vision_understand_media_routes_by_extension():
    from unittest.mock import patch
    with patch("src.tools.vision.load_dotenv"), patch.dict(os.environ):
        os.environ.pop("GEMINI_API_KEY", None)
        from src.tools.vision import RetinaTool
        r = RetinaTool()
        assert (await r.understand_media("nope.png"))["kind"] == "image"
        assert (await r.understand_media("nope.mp4"))["kind"] == "video"
        assert (await r.understand_media("nope.mp3"))["kind"] == "audio"
        res = await r.understand_media("nope.xyz")
        assert res["kind"] == "unknown" and "unsupported" in res["output"]


# ─────────────────────────────────────────────────────────────────────────────
# Resume tool — offline parsing + render
# ─────────────────────────────────────────────────────────────────────────────

def test_resume_load_plain_text(tmp_path):
    from src.tools.resume_tool import load_resume
    p = tmp_path / "r.txt"
    p.write_text("Jane Doe\nEngineer\n", encoding="utf-8")
    assert "Jane" in load_resume(str(p))


def test_resume_render_pdf_minimum(tmp_path):
    from src.tools.resume_tool import render_pdf, _fallback_parse
    data = _fallback_parse("seed")
    data.update({
        "name": "Jane Doe",
        "headline": "Senior Engineer",
        "contact": {"email": "j@x.com"},
        "experience": [{"role": "Eng", "company": "X", "dates": "2024", "bullets": ["did stuff"]}],
        "skills": {"Languages": ["Python"]},
    })
    out = tmp_path / "out.pdf"
    p = render_pdf(data, str(out))
    assert os.path.exists(p)
    assert os.path.getsize(p) > 500  # has at least some content


@pytest.mark.asyncio
async def test_resume_offline_fallback_structure():
    from unittest.mock import patch
    with patch("src.tools.resume_tool.load_dotenv"), patch.dict(os.environ):
        os.environ.pop("GEMINI_API_KEY", None)
        from src.tools.resume_tool import rewrite_resume
        data = await rewrite_resume("Jane Doe — engineer")
        for k in ("name", "feedback", "skills"):
            assert k in data


# ─────────────────────────────────────────────────────────────────────────────
# GeniusMode — offline stub
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_genius_offline_stub_shape():
    from src.services.genius_mode import GeniusMode
    g = GeniusMode()
    # Force into stub path by passing in dummy disabled brains.
    g.gemini = None
    g.mimo = None
    g.groq = None
    res = await g.analyze("Should I migrate to Postgres?")
    for k in ("cross_question", "right", "wrong", "blind_spots", "action", "one_liner"):
        assert k in res


# ─────────────────────────────────────────────────────────────────────────────
# Todo persistence
# ─────────────────────────────────────────────────────────────────────────────

def test_todo_lifecycle(tmp_path):
    from src.tools.todo import TodoTool
    t = TodoTool(path=str(tmp_path / "todo.json"))
    r = t.add("ship harness")
    assert r["success"]
    tid = r["entry"]["id"]
    r = t.update(tid, "in_progress")
    assert r["success"]
    r = t.list()
    assert "in_progress" in r["output"]
    r = t.update(tid, "completed")
    assert r["success"]
    r = t.clear_completed()
    assert r["success"]
    r = t.list()
    assert r["items"] == []


# ─────────────────────────────────────────────────────────────────────────────
# Diff tool
# ─────────────────────────────────────────────────────────────────────────────

def test_diff_files(tmp_path):
    from src.tools.diff_tool import DiffTool
    a = tmp_path / "a.txt"; a.write_text("alpha\nbeta\n", encoding="utf-8")
    b = tmp_path / "b.txt"; b.write_text("alpha\ngamma\n", encoding="utf-8")
    res = DiffTool().diff_files(str(a), str(b))
    assert res["success"] and res["changed"]
    assert res["added"] == 1 and res["removed"] == 1


def test_diff_content_no_change(tmp_path):
    from src.tools.diff_tool import DiffTool
    a = tmp_path / "a.txt"; a.write_text("alpha\nbeta\n", encoding="utf-8")
    res = DiffTool().diff_content(str(a), "alpha\nbeta\n")
    assert res["output"] == "(no changes)"


# ─────────────────────────────────────────────────────────────────────────────
# WebFetch HTML stripper (pure function, offline)
# ─────────────────────────────────────────────────────────────────────────────

def test_web_fetch_html_stripper():
    from src.tools.web_fetch import WebFetchTool
    html = "<html><body><script>nope()</script><h1>Hi</h1><p>X &amp; Y</p></body></html>"
    out = WebFetchTool._html_to_text(html)
    assert "nope" not in out
    assert "Hi" in out and "X & Y" in out


# ─────────────────────────────────────────────────────────────────────────────
# Animations — must be callable on non-tty without raising
# ─────────────────────────────────────────────────────────────────────────────

def test_animations_safe_on_non_tty(capsys):
    from rich.console import Console
    from src.core.animations import (
        type_text, progress_trail, pulse_banner, sparkle_panel, matrix_rain,
    )
    c = Console(force_terminal=False)
    # Each should run without raising even when stdout is not a tty.
    type_text("hello", console=c, cps=0)
    progress_trail(["step 1", "step 2"], console=c, delay=0.01)
    pulse_banner("APEX", console=c, cycles=1, fps=4)
    sparkle_panel("hello", console=c, cycles=1, fps=4)
    matrix_rain(console=c, duration=0.01)


# ─────────────────────────────────────────────────────────────────────────────
# Brain clients construct without crashing (offline)
# ─────────────────────────────────────────────────────────────────────────────

def test_mimo_client_construction():
    from src.models.mimo_path import MimoClient
    from unittest.mock import patch
    import os
    orig_getenv = os.getenv
    def mock_getenv(key, default=None):
        if key == "NVIDIA_API_KEY":
            return None
        return orig_getenv(key, default)
    with patch("os.getenv", side_effect=mock_getenv):
        c = MimoClient()
        assert c.model == "mimo-v2.5-pro"
        assert hasattr(c, "is_online")
        # Force offline path by passing a non-existent env var.
        c2 = MimoClient(api_key_env="DOES_NOT_EXIST_XYZ_123")
        assert c2.is_online is False
        assert c2.get_completion("hi").startswith("[Client Offline]")


def test_groq_client_construct():
    from src.models.fast_path import GroqClient
    c = GroqClient()
    # Either online (key present) or offline; both must be valid states.
    assert hasattr(c, "model")


# ─────────────────────────────────────────────────────────────────────────────
# Harness tool surface coverage
# ─────────────────────────────────────────────────────────────────────────────

def test_harness_tool_schemas_complete():
    from src.core.harness import TOOL_SCHEMAS
    names = {t["function"]["name"] for t in TOOL_SCHEMAS}
    expected = {
        "view", "write", "edit", "multi_edit", "create_dir", "delete",
        "list_dir", "tree", "glob", "grep", "bash", "git", "diff_preview",
        "todo_add", "todo_list", "todo_done", "vision_capture",
        "vision_describe", "vision_ocr", "video_describe", "audio_transcribe",
        "understand_media", "hardware_vitals", "code_compass_search",
        "code_compass_context", "knowledge_forge_search", "swarm_run",
        "think_partner", "web_search", "web_fetch", "research_swarm",
        "workspace_summarize", "mcp_call", "python_run", "done",
    }
    missing = expected - names
    assert not missing, f"missing harness tools: {missing}"


# ─────────────────────────────────────────────────────────────────────────────
# Harness self-verification and critique tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_harness_auto_verification_detects_syntax_errors():
    from src.core.harness import AgentHarness
    tmp = tempfile.mkdtemp()
    h = AgentHarness(project_root=tmp)

    # 1. Mutate file with valid python content
    r = await h._dispatch("write", {"path": "valid.py", "content": "def test():\n    pass\n"})
    assert r["success"]

    # Run AST check directly via _verify
    vres = await h._verify()
    assert vres["ran"] is True
    assert vres["success"] is True
    assert h._last_verify_failed is False

    # 2. Mutate file with invalid python content (syntax error)
    r = await h._dispatch("write", {"path": "invalid.py", "content": "def test(:\n    pass\n"})
    assert r["success"]

    vres = await h._verify()
    assert vres["ran"] is True
    assert vres["success"] is False
    assert h._last_verify_failed is True


@pytest.mark.asyncio
async def test_harness_done_rejected_when_verify_failed():
    from src.core.harness import AgentHarness
    from unittest.mock import MagicMock
    tmp = tempfile.mkdtemp()
    h = AgentHarness(project_root=tmp)
    await h._dispatch("write", {"path": "broken.py", "content": "def bad(\n"})
    h._last_verify_failed = True

    # Mock brain selection to return a mock client
    mock_client = MagicMock()
    h._select_brain = lambda: (mock_client, "mock-model")

    # Mock client's chat.completions.create response
    mock_choice_1 = MagicMock()
    mock_choice_1.message.content = ""
    tc_done = MagicMock()
    tc_done.id = "tc_1"
    tc_done.function.name = "done"
    tc_done.function.arguments = '{"summary": "completed"}'
    mock_choice_1.message.tool_calls = [tc_done]

    mock_choice_2 = MagicMock()
    mock_choice_2.message.content = "Stopped."
    mock_choice_2.message.tool_calls = []

    mock_response_1 = MagicMock()
    mock_response_1.choices = [mock_choice_1]
    mock_response_2 = MagicMock()
    mock_response_2.choices = [mock_choice_2]

    # Return mock_response_1 first (calls done, gets rejected), then mock_response_2 (finishes)
    mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

    res = await h.run("dummy goal")
    assert res["success"] is True
    # The first response choice was processed, but done was rejected, so we continued.
    # The second response choice had no tool calls, finishing the run.
    assert h.steps_log == []  # No tools logged successfully (done was rejected and skipped)


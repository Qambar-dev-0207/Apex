"""
Tests for AgentHarness self-verification loop, done-rejection guard,
and periodic GeniusMode critique injection.
"""

import os
import json
import tempfile
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from src.core.harness import AgentHarness, _ok, _err
from src.services.genius_mode import GeniusMode


@pytest.mark.asyncio
async def test_harness_mutating_tool_triggers_syntax_verification():
    """Verify that writing invalid Python syntax causes _verify() to fail."""
    tmp = tempfile.mkdtemp()
    h = AgentHarness(project_root=tmp)

    # Valid write -> verify passes
    res = await h._dispatch("write", {"path": "good.py", "content": "def add(a, b):\n    return a + b\n"})
    assert res["success"] is True

    vres = await h._verify()
    assert vres["ran"] is True
    assert vres["success"] is True
    assert h._last_verify_failed is False

    # Broken write (SyntaxError) -> verify fails
    res = await h._dispatch("write", {"path": "bad.py", "content": "def broken(:\n    pass\n"})
    assert res["success"] is True

    vres = await h._verify()
    assert vres["ran"] is True
    assert vres["success"] is False
    assert h._last_verify_failed is True
    assert "SyntaxError" in vres["output"]


@pytest.mark.asyncio
async def test_harness_done_rejection_guard():
    """
    Verify that calling done() while the codebase has syntax errors
    is strictly REJECTED, injecting error feedback and keeping the loop alive.
    """
    tmp = tempfile.mkdtemp()
    h = AgentHarness(project_root=tmp)

    # 1. Create a broken file
    await h._dispatch("write", {"path": "broken_mod.py", "content": "class Foo\n    pass\n"})

    mock_client = MagicMock()
    h._select_brain = lambda: (mock_client, "mock-brain")

    # Step 1: Model tries to call done() prematurely while syntax is broken
    tc_done = MagicMock()
    tc_done.id = "tc_done_1"
    tc_done.function.name = "done"
    tc_done.function.arguments = '{"summary": "I am finished"}'

    choice_1 = MagicMock()
    choice_1.message.content = ""
    choice_1.message.tool_calls = [tc_done]
    resp_1 = MagicMock(choices=[choice_1])

    # Step 2: Model fixes the broken file
    tc_fix = MagicMock()
    tc_fix.id = "tc_fix_2"
    tc_fix.function.name = "write"
    tc_fix.function.arguments = json.dumps({"path": "broken_mod.py", "content": "class Foo:\n    pass\n"})

    choice_2 = MagicMock()
    choice_2.message.content = ""
    choice_2.message.tool_calls = [tc_fix]
    resp_2 = MagicMock(choices=[choice_2])

    # Step 3: Model calls done() again, now clean
    tc_done_2 = MagicMock()
    tc_done_2.id = "tc_done_2"
    tc_done_2.function.name = "done"
    tc_done_2.function.arguments = '{"summary": "Fixed and completed"}'

    choice_3 = MagicMock()
    choice_3.message.content = ""
    choice_3.message.tool_calls = [tc_done_2]
    resp_3 = MagicMock(choices=[choice_3])

    mock_client.chat.completions.create.side_effect = [resp_1, resp_2, resp_3]

    result = await h.run("Fix the broken class definition")

    assert result["success"] is True
    assert result["summary"] == "Fixed and completed"
    assert result["steps_executed"] >= 2
    # Verify done was accepted at end
    done_steps = [s for s in h.steps_log if s["tool"] == "done" and s["result"]["success"]]
    assert len(done_steps) == 1
    assert done_steps[0]["result"]["output"] == "Fixed and completed"


@pytest.mark.asyncio
async def test_harness_periodic_genius_critique_injection():
    """Verify that GeniusMode pre-step critique is injected every verify_every_steps."""
    tmp = tempfile.mkdtemp()
    mock_genius = MagicMock(spec=GeniusMode)
    mock_genius.pre_step_critique = AsyncMock(return_value={
        "wrong": ["Missed edge case for empty input"],
        "blind_spots": ["Locking overhead on concurrent writes"],
        "action": [{"step": "Add check for len == 0", "rationale": "Safety"}]
    })

    h = AgentHarness(project_root=tmp, genius=mock_genius, verify_every_steps=1)

    mock_client = MagicMock()
    h._select_brain = lambda: (mock_client, "mock-brain")

    # Step 1: Model calls view
    tc_view = MagicMock()
    tc_view.id = "tc_view"
    tc_view.function.name = "list_dir"
    tc_view.function.arguments = '{"path": "."}'

    choice_1 = MagicMock()
    choice_1.message.content = ""
    choice_1.message.tool_calls = [tc_view]
    resp_1 = MagicMock(choices=[choice_1])

    # Step 2: Model finishes
    tc_done = MagicMock()
    tc_done.id = "tc_done"
    tc_done.function.name = "done"
    tc_done.function.arguments = '{"summary": "Done after critique"}'

    choice_2 = MagicMock()
    choice_2.message.content = ""
    choice_2.message.tool_calls = [tc_done]
    resp_2 = MagicMock(choices=[choice_2])

    mock_client.chat.completions.create.side_effect = [resp_1, resp_2]

    res = await h.run("Inspect and report")
    assert res["success"] is True
    assert mock_genius.pre_step_critique.called


@pytest.mark.asyncio
async def test_harness_local_ollama_brain_selection():
    """Verify that AgentHarness can select Ollama local brain adapter."""
    mock_ollama = MagicMock()
    mock_openai_adapter = MagicMock()
    mock_ollama.openai_client = mock_openai_adapter
    mock_ollama.llm_model = "qwen2.5-coder:latest"

    h = AgentHarness(ollama=mock_ollama, brain="ollama")
    client, model = h._select_brain()
    assert client is mock_openai_adapter
    assert model == "qwen2.5-coder:latest"

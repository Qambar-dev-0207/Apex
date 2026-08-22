"""
Tests for Local Sovereignty, OllamaClient path, and sovereign routing in SmartRouter.
"""

import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from src.models.local_path import OllamaClient
from src.routers.router import SmartRouter
from src.core.models import ExecutionPlan


def test_ollama_client_init_and_properties():
    """Verify OllamaClient properties, default models, and host normalization."""
    client = OllamaClient(host="http://localhost:11434/", model="llama3.2:latest")
    assert client.host == "http://localhost:11434"
    assert client.llm_model == "llama3.2:latest"
    assert client.model == "llama3.2:latest"
    assert "nomic-embed-text" in client.embed_model


def test_ollama_client_offline_graceful_completion():
    """Verify get_completion returns a graceful message when Ollama is offline."""
    client = OllamaClient(host="http://127.0.0.1:59999")  # Unused port
    res = client.get_completion("Hello from test")
    assert isinstance(res, str)
    assert len(res) > 0


@pytest.mark.asyncio
async def test_ollama_client_generate_plan_mocked():
    """Verify OllamaClient generates an ExecutionPlan DAG."""
    client = OllamaClient()
    mock_async_ollama = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = '{"task_plan": [{"id": 1, "action": "Analyze locally", "description": "Local test", "tool": "python_executor", "input_data": "print(1)", "dependencies": []}], "tools_required": ["python_executor"], "requires_clarification": false, "summary": "Local plan"}'
    mock_resp = MagicMock(message=mock_msg)
    mock_async_ollama.chat = AsyncMock(return_value=mock_resp)
    
    with patch.object(OllamaClient, 'client', new=mock_async_ollama):
        plan = await client.generate_plan("Do something")
        assert isinstance(plan, ExecutionPlan)
        assert len(plan.task_plan) == 1
        assert plan.task_plan[0].action == "Analyze locally"
        assert plan.summary == "Local plan"


def test_smart_router_sovereign_mode_routing():
    """Verify SmartRouter routes to local_path when APEX_SOVEREIGN=1."""
    router = SmartRouter()

    # 1. Standard cloud mode with low complexity -> fast_path
    with patch.dict(os.environ, {"APEX_SOVEREIGN": "0", "APEX_LOCAL": "0", "APEX_OFFLINE": "0", "GEMINI_API_KEY": "test_key", "GROQ_API_KEY": "test_key"}):
        path = router.route({"complexity": "low", "intent": "chat"})
        assert path == "fast_path"

    # 2. Sovereign mode active -> low complexity routes to local_path
    with patch.dict(os.environ, {"APEX_SOVEREIGN": "1", "GEMINI_API_KEY": "test_key", "GROQ_API_KEY": "test_key"}):
        path = router.route({"complexity": "low", "intent": "chat"})
        assert path == "local_path"

    # 3. Explicit local_path in classification -> local_path
    with patch.dict(os.environ, {"APEX_SOVEREIGN": "0", "GEMINI_API_KEY": "test_key", "GROQ_API_KEY": "test_key"}):
        path = router.route({"complexity": "low", "path": "local_path"})
        assert path == "local_path"

    # 4. Zero cloud keys configured -> defaults to sovereign local_path
    with patch.dict(os.environ, {"APEX_SOVEREIGN": "0", "GEMINI_API_KEY": "", "GROQ_API_KEY": ""}):
        path = router.route({"complexity": "low", "intent": "chat"})
        assert path == "local_path"

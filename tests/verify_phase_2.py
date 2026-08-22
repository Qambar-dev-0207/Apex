import os
import sqlite3
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.services.predictor import PredictorService
from src.models.local_path import OllamaClient
from src.core.models import ExecutionPlan

# Force offline mode for testing
os.environ["APEX_OFFLINE"] = "1"

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_predictor.db"
    return str(db_file)

# ── 1. Predictor Service Tests ─────────────────────────────────────────

def test_predictor_db_init(temp_db):
    predictor = PredictorService(db_path=temp_db)
    assert os.path.exists(temp_db)
    
    # Verify tables exist
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    assert "command_history" in tables
    assert "api_spend" in tables
    assert "deadlines" in tables

def test_predictor_record_command(temp_db):
    predictor = PredictorService(db_path=temp_db)
    predictor.record_command("python test.py", "/workspace", 0, 1.25)
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT command, working_dir, exit_code, execution_time FROM command_history")
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == "python test.py"
    assert row[1] == "/workspace"
    assert row[2] == 0
    assert row[3] == 1.25

def test_predictor_next_command_prediction_sparse(temp_db):
    predictor = PredictorService(db_path=temp_db)
    # Sparse data (< 5 entries) should return None
    predictor.record_command("git status", "/workspace", 0, 0.1)
    cmd, conf = predictor.predict_next_command("/workspace")
    assert cmd is None
    assert conf == 0.0

def test_predictor_next_command_prediction_decision_tree(temp_db):
    predictor = PredictorService(db_path=temp_db)
    # Record enough commands to trigger prediction logic (> 5 entries)
    # Create a clear pattern: after "git add", we run "git commit"
    for _ in range(5):
        predictor.record_command("git add", "/workspace", 0, 0.1)
        predictor.record_command("git commit", "/workspace", 0, 0.2)
        predictor.record_command("git push", "/workspace", 0, 0.5)

    cmd, conf = predictor.predict_next_command("/workspace")
    assert cmd is not None
    assert isinstance(conf, float)
    assert conf > 0.0

def test_predictor_completion_suggestions(temp_db):
    predictor = PredictorService(db_path=temp_db)
    predictor.record_command("pytest tests/test_voice.py", "/workspace", 0, 2.0)
    predictor.record_command("git status", "/workspace", 0, 0.1)
    
    suggs = predictor.get_completion_suggestions("pyt")
    assert len(suggs) >= 1
    assert suggs[0] == "pytest tests/test_voice.py"

def test_predictor_budget_anomaly(temp_db):
    predictor = PredictorService(db_path=temp_db)
    # Pre-populate with typical cheap calls
    for _ in range(15):
        predictor.record_spend(0.01, 100, 50, "gpt-3.5")
        
    # Test a small call is NOT an anomaly
    is_anomaly, msg = predictor.check_budget_anomaly(0.01)
    assert not is_anomaly
    
    # Test a massive spike IS an anomaly
    is_anomaly, msg = predictor.check_budget_anomaly(2.50)
    assert is_anomaly
    assert "Anomalous cost detected" in msg

def test_predictor_deadlines(temp_db):
    predictor = PredictorService(db_path=temp_db)
    todos = [
        {"task": "Complete implementation of Phase 2 due 2026-05-24"},
        {"task": "Write docs due: 2026-05-25"},
        {"task": "Refactor codebase without date"},
    ]
    predictor.sync_deadlines(todos)
    import datetime
    real_date = datetime.date
    # Mock date as 2026-05-23
    with patch('src.services.predictor.datetime.date') as mock_date:
        mock_date.today.return_value = real_date(2026, 5, 23)
        upcoming = predictor.get_upcoming_deadlines(days_window=2)
        
        assert len(upcoming) >= 1
        tasks = [u["task"] for u in upcoming]
        assert "Complete implementation of Phase 2 due 2026-05-24" in tasks

# ── 2. Ollama Client Tests ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ollama_client_connection():
    client = OllamaClient()
    mock_async_client = AsyncMock()
    mock_async_client.list = AsyncMock(return_value={"models": []})
    
    with patch.object(OllamaClient, 'client', new_callable=PropertyMock) as mock_prop:
        mock_prop.return_value = mock_async_client
        connected = await client.check_connection()
        assert connected is True
        mock_async_client.list.assert_called_once()

@pytest.mark.asyncio
async def test_ollama_client_generate_plan():
    client = OllamaClient()
    mock_async_client = AsyncMock()
    
    # Mock standard Ollama response
    mock_response = MagicMock()
    mock_response.message.content = """
    {
      "task_plan": [
        {
          "id": 1,
          "action": "Verify offline mode",
          "description": "Ensure Ollama client falls back",
          "tool": "pytest",
          "input_data": "tests/verify_phase_2.py",
          "dependencies": []
        }
      ],
      "tools_required": ["pytest"],
      "requires_clarification": false,
      "summary": "Plan for testing offline path."
    }
    """
    mock_async_client.chat = AsyncMock(return_value=mock_response)
    
    with patch.object(OllamaClient, 'client', new_callable=PropertyMock) as mock_prop:
        mock_prop.return_value = mock_async_client
        plan = await client.generate_plan("Test offline plan generation")
        
        assert isinstance(plan, ExecutionPlan)
        assert len(plan.task_plan) == 1
        assert plan.task_plan[0].action == "Verify offline mode"
        assert plan.tools_required == ["pytest"]

# Helper PropertyMock for unittest.mock
class PropertyMock(MagicMock):
    def __get__(self, obj, objtype=None):
        return self()

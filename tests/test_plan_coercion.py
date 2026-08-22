"""
Tests for plan-schema coercion in src/models/thinking_path.py.

Gemini occasionally emits alternate JSON shapes (plan instead of task_plan,
step instead of action/description, input instead of input_data, etc.).
parse_plan_response + coerce_plan_dict must absorb those drifts.

Run:
    python -m pytest tests/test_plan_coercion.py -v
"""

import json
import pytest

from src.models.thinking_path import parse_plan_response, coerce_plan_dict
from src.core.models import ExecutionPlan


# ── exact bug from screenshot ────────────────────────────────────────────────

def test_drift_plan_step_action_input_keys():
    raw = {"plan": [{"step": "List all files", "tool": "filesystem",
                     "action": "glob", "input": "**/*"}]}
    plan = parse_plan_response(json.dumps(raw))
    assert isinstance(plan, ExecutionPlan)
    assert len(plan.task_plan) == 1
    s = plan.task_plan[0]
    assert s.tool == "filesystem"
    assert s.input_data == "**/*"
    assert s.action == "glob"
    assert s.description == "List all files"
    assert plan.tools_required == ["filesystem"]
    assert plan.requires_clarification is False


# ── shape variants ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("steps_key", ["task_plan", "plan", "steps", "tasks"])
def test_steps_key_aliases(steps_key):
    raw = {steps_key: [{"action": "x", "description": "y", "tool": "git"}]}
    plan = parse_plan_response(json.dumps(raw))
    assert len(plan.task_plan) == 1
    assert plan.task_plan[0].tool == "git"


def test_input_aliases():
    for k in ("input_data", "input", "args", "arg", "payload", "data"):
        raw = {"task_plan": [{"action": "do", "description": "x",
                              "tool": "shell", k: "echo hi"}]}
        plan = parse_plan_response(json.dumps(raw))
        assert plan.task_plan[0].input_data == "echo hi", f"alias {k} failed"


def test_dependencies_aliases():
    for k in ("dependencies", "deps", "depends_on", "after"):
        raw = {"task_plan": [
            {"id": 1, "action": "a", "description": "a"},
            {"id": 2, "action": "b", "description": "b", k: [1]},
        ]}
        plan = parse_plan_response(json.dumps(raw))
        assert plan.task_plan[1].dependencies == [1], f"alias {k} failed"


def test_tool_alias_resolution():
    # "fs" should resolve to canonical "filesystem"
    raw = {"task_plan": [{"action": "read", "description": "r", "tool": "fs"}]}
    plan = parse_plan_response(json.dumps(raw))
    assert plan.task_plan[0].tool == "filesystem"


def test_tool_colon_action_split():
    """Gemini emits combined 'workspace:summarize' as tool; must split."""
    raw = {"task_plan": [{"id": 1, "action": "Summarize workspace",
                          "description": "x", "tool": "workspace:summarize"}]}
    plan = parse_plan_response(json.dumps(raw))
    assert plan.task_plan[0].tool == "workspace"
    # Action verb survives — executor's "summarize" substring checks pass
    assert "summarize" in plan.task_plan[0].action.lower()


def test_tool_colon_action_split_uses_verb_when_action_empty():
    raw = {"task_plan": [{"id": 1, "action": "step 1",
                          "description": "x", "tool": "git:status"}]}
    plan = parse_plan_response(json.dumps(raw))
    assert plan.task_plan[0].tool == "git"
    # Should prefer the verb 'status' over the generic 'step 1' default
    assert plan.task_plan[0].action == "status"


def test_dict_input_data_serialized_to_json_string():
    raw = {"task_plan": [{"action": "call", "description": "c",
                          "tool": "mcp",
                          "input_data": {"server": "x", "tool": "y", "args": {}}}]}
    plan = parse_plan_response(json.dumps(raw))
    # ExecutionPlan input_data is str
    assert isinstance(plan.task_plan[0].input_data, str)
    parsed = json.loads(plan.task_plan[0].input_data)
    assert parsed["server"] == "x"


def test_garbage_id_defaults_to_index():
    raw = {"task_plan": [
        {"action": "a", "description": "a"},
        {"id": "not-an-int", "action": "b", "description": "b"},
    ]}
    plan = parse_plan_response(json.dumps(raw))
    assert plan.task_plan[0].id == 1
    assert plan.task_plan[1].id == 2


def test_garbage_dependencies_dropped():
    raw = {"task_plan": [{"id": 1, "action": "a", "description": "a",
                          "dependencies": [1, "bad", None, 2.5]}]}
    plan = parse_plan_response(json.dumps(raw))
    # 1 stays, "bad" + None drop, 2.5 → 2
    assert plan.task_plan[0].dependencies == [1, 2]


def test_tools_required_derived_when_missing():
    raw = {"task_plan": [
        {"action": "a", "description": "a", "tool": "git"},
        {"action": "b", "description": "b", "tool": "filesystem"},
        {"action": "c", "description": "c"},  # no tool
    ]}
    plan = parse_plan_response(json.dumps(raw))
    assert set(plan.tools_required) == {"git", "filesystem"}


def test_summary_synthesized_when_missing():
    raw = {"task_plan": [{"action": "scan project", "description": "x"}]}
    plan = parse_plan_response(json.dumps(raw))
    assert "scan project" in plan.summary


def test_empty_dict_yields_empty_plan():
    plan = parse_plan_response("{}")
    assert plan.task_plan == []
    assert plan.summary == "Empty plan."


# ── degenerate input ────────────────────────────────────────────────────────

def test_non_json_returns_empty_plan():
    plan = parse_plan_response("this is not JSON at all")
    assert plan.task_plan == []
    assert "non-JSON" in plan.summary


def test_json_string_returns_empty_plan():
    plan = parse_plan_response('"just a quoted string"')
    assert plan.task_plan == []
    assert "non-object" in plan.summary


def test_json_array_returns_empty_plan():
    plan = parse_plan_response('[1,2,3]')
    assert plan.task_plan == []


def test_code_fenced_json_parses():
    fenced = '```json\n' + json.dumps({
        "task_plan": [{"id": 1, "action": "x", "description": "y",
                       "tool": "git", "input_data": None, "dependencies": []}],
        "tools_required": ["git"],
        "requires_clarification": False,
        "summary": "ok"
    }) + '\n```'
    plan = parse_plan_response(fenced)
    assert len(plan.task_plan) == 1
    assert plan.summary == "ok"


# ── strict path still works ─────────────────────────────────────────────────

def test_strict_valid_plan_parses_unchanged():
    raw = {
        "task_plan": [
            {"id": 1, "action": "scan", "description": "scan repo",
             "tool": "filesystem", "input_data": "**/*", "dependencies": []},
        ],
        "tools_required": ["filesystem"],
        "requires_clarification": False,
        "summary": "Scan plan",
        "socratic_insight": "consider .gitignore",
    }
    plan = parse_plan_response(json.dumps(raw))
    assert plan.summary == "Scan plan"
    assert plan.socratic_insight == "consider .gitignore"
    assert plan.task_plan[0].dependencies == []


# ── direct coerce_plan_dict ─────────────────────────────────────────────────

def test_coerce_returns_valid_executionplan_input():
    raw = {"plan": [{"step": "do thing", "tool": "git", "action": "commit"}]}
    coerced = coerce_plan_dict(raw)
    # Should be directly constructible
    plan = ExecutionPlan(**coerced)
    assert plan.task_plan[0].action == "commit"


def test_coerce_handles_non_dict_root():
    coerced = coerce_plan_dict("not a dict")
    plan = ExecutionPlan(**coerced)
    assert plan.task_plan == []

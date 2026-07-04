"""
Smoke tests for auto-spawn dispatch — prefix, keyword, complexity gates.

Verifies:
  - `^^ goal` prefix routes to dispatch_swarm
  - `>> goal` prefix routes to dispatch_harness
  - Reflex classifies "multi-agent" / "spawn agents" prompts as swarm_goal
  - Reflex classifies "do it for me" / "run autonomously" as harness_goal
  - Complexity gate fires swarm when auto_swarm_enabled + high-complexity coding

All collaborators are stubbed. No network. No real LLM.

Run:
    python -m pytest tests/test_auto_spawn.py -v
"""

import asyncio
import re
import pytest

from src.core.reflex import Reflex


# ── Reflex keyword classification ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reflex_classifies_multi_agent_as_swarm():
    r = Reflex()
    d = await r.decide("multi-agent build authentication system")
    assert d.intent == "swarm_goal"
    assert d.path == "swarm"
    assert d.confidence > 0.5


@pytest.mark.asyncio
async def test_reflex_classifies_spawn_agents_as_swarm():
    r = Reflex()
    d = await r.decide("spawn agents to refactor this module")
    assert d.intent == "swarm_goal"
    assert d.confidence > 0.5


@pytest.mark.asyncio
async def test_reflex_classifies_do_it_for_me_as_harness():
    r = Reflex()
    d = await r.decide("do it for me end to end")
    assert d.intent == "harness_goal"
    assert d.path == "harness"
    assert d.confidence > 0.5


# ── Dispatch helpers ─────────────────────────────────────────────────────────

class _FakeMemory:
    def __init__(self):
        self.stored = []
    async def store_interaction(self, sid, q, r, project_name=None, **kwargs):
        self.stored.append((sid, q, r))


class _FakeSwarm:
    def __init__(self):
        self.calls = []
    async def run(self, goal, rounds=1, roster=None):
        self.calls.append({"goal": goal, "rounds": rounds, "roster": roster})
        return {
            "ok": True,
            "artifact": f"## Plan for: {goal}\n\nStep 1: do stuff.",
            "transcript": [
                {"role": "architect", "agent": "alpha", "content": "I propose X."},
                {"role": "critic", "agent": "beta", "content": "X has flaw Y."},
            ],
            "roster": roster or ["architect", "critic"],
        }


class _FakeHarness:
    def __init__(self):
        self.calls = []
        self.max_steps = 10
    async def run(self, goal):
        self.calls.append({"goal": goal, "max_steps": self.max_steps})
        return {
            "success": True,
            "summary": f"Completed: {goal}",
            "touched_files": ["src/foo.py"],
            "snapshot_dir": ".apex/snapshots/abc123",
        }


class _FakeEngine:
    def __init__(self):
        self.swarm = _FakeSwarm()
        self.harness = _FakeHarness()
        self.memory_manager = _FakeMemory()
        self.session_id = "test-session"
        self.auto_swarm_enabled = False
        self.pending_clarification = None
        self.active_project_name = "test-project"


class _SilentConsole:
    """Stand-in for rich.Console that swallows output."""
    def print(self, *a, **kw): pass
    is_terminal = False


@pytest.mark.asyncio
async def test_dispatch_swarm_routes_goal_and_stores_memory():
    from main import dispatch_swarm
    engine = _FakeEngine()
    console = _SilentConsole()
    res = await dispatch_swarm(engine, console, "build a parser",
                               rounds=2, roster=["architect"], trigger="test")
    assert res["ok"] is True
    assert engine.swarm.calls[0]["goal"] == "build a parser"
    assert engine.swarm.calls[0]["rounds"] == 2
    assert engine.swarm.calls[0]["roster"] == ["architect"]
    # Memory stored with trigger tag
    assert any("[auto-swarm:test]" in q for _, q, _ in engine.memory_manager.stored)


@pytest.mark.asyncio
async def test_dispatch_harness_routes_goal_and_stores_memory():
    from main import dispatch_harness
    engine = _FakeEngine()
    console = _SilentConsole()
    res = await dispatch_harness(engine, console, "rename foo to bar",
                                 max_steps=15, trigger="test")
    assert res["success"] is True
    assert engine.harness.calls[0]["goal"] == "rename foo to bar"
    assert engine.harness.calls[0]["max_steps"] == 15
    assert any("[auto-harness:test]" in q for _, q, _ in engine.memory_manager.stored)


@pytest.mark.asyncio
async def test_dispatch_swarm_rejects_empty_goal():
    from main import dispatch_swarm
    engine = _FakeEngine()
    console = _SilentConsole()
    res = await dispatch_swarm(engine, console, "   ", trigger="test")
    assert res["ok"] is False
    assert engine.swarm.calls == []


# ── Prefix parser ────────────────────────────────────────────────────────────

def test_parse_swarm_args_simple():
    from main import _parse_swarm_args
    g, r, ro = _parse_swarm_args("build auth system")
    assert g == "build auth system"
    assert r == 1
    assert ro is None


def test_parse_swarm_args_with_roster():
    from main import _parse_swarm_args
    g, r, ro = _parse_swarm_args("design DB schema | architect, critic")
    assert g == "design DB schema"
    assert ro == ["architect", "critic"]


def test_parse_swarm_args_with_rounds():
    from main import _parse_swarm_args
    g, r, ro = _parse_swarm_args("refactor module rounds=3")
    assert g == "refactor module"
    assert r == 3


def test_parse_swarm_args_full():
    from main import _parse_swarm_args
    g, r, ro = _parse_swarm_args("ship feature X | architect, coder, critic rounds=2")
    assert g == "ship feature X"
    assert r == 2
    assert ro == ["architect", "coder", "critic"]


# ── Complexity gate (logic, not full REPL) ───────────────────────────────────

@pytest.mark.asyncio
async def test_complexity_gate_fires_swarm_when_enabled():
    """
    Mirrors the complexity-gate condition from main.py's input loop.
    """
    from main import dispatch_swarm
    engine = _FakeEngine()
    engine.auto_swarm_enabled = True
    console = _SilentConsole()

    classification = {"complexity": "high", "intent": "coding"}
    # Condition copied verbatim from main.py REPL guard
    should_fire = (
        engine.auto_swarm_enabled
        and not engine.pending_clarification
        and classification.get("complexity") == "high"
        and classification.get("intent") in {"coding", "architect", "skill", "skill_activation"}
    )
    assert should_fire
    if should_fire:
        await dispatch_swarm(engine, console, "build distributed cache layer",
                             trigger="complexity:coding")
    assert engine.swarm.calls[0]["goal"] == "build distributed cache layer"


@pytest.mark.asyncio
async def test_complexity_gate_skips_when_disabled():
    from main import dispatch_swarm
    engine = _FakeEngine()
    engine.auto_swarm_enabled = False
    classification = {"complexity": "high", "intent": "coding"}
    should_fire = (
        engine.auto_swarm_enabled
        and classification.get("complexity") == "high"
        and classification.get("intent") in {"coding", "architect", "skill", "skill_activation"}
    )
    assert not should_fire
    assert engine.swarm.calls == []


@pytest.mark.asyncio
async def test_complexity_gate_skips_low_complexity():
    engine = _FakeEngine()
    engine.auto_swarm_enabled = True
    classification = {"complexity": "low", "intent": "coding"}
    should_fire = (
        engine.auto_swarm_enabled
        and classification.get("complexity") == "high"
        and classification.get("intent") in {"coding", "architect", "skill", "skill_activation"}
    )
    assert not should_fire


# ── Prefix detection (regex extraction matches REPL impl) ────────────────────

def test_prefix_caret_caret_extracts_goal():
    s = "^^ build a multi-agent system | architect, critic rounds=2"
    assert s.startswith("^^")
    goal_str = s[2:].strip()
    from main import _parse_swarm_args
    g, r, ro = _parse_swarm_args(goal_str)
    assert g == "build a multi-agent system"
    assert r == 2
    assert ro == ["architect", "critic"]


def test_prefix_gt_gt_extracts_max_steps():
    s = ">> ship feature X max=15"
    assert s.startswith(">>")
    body = s[2:].strip()
    m = re.search(r"\bmax=(\d+)", body)
    assert m is not None
    max_steps = int(m.group(1))
    body = re.sub(r"\bmax=\d+", "", body).strip()
    assert max_steps == 15
    assert body == "ship feature X"

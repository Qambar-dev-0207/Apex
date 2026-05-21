"""
Smoke tests for src/core/reflex.py — Reflex brain + PrefetchBundle.

No network. No real LLM. All providers stubbed.

Run:
    python -m pytest tests/test_reflex.py -v
"""

import asyncio
import time
import pytest

from src.core.reflex import Reflex, PrefetchBundle, ReflexDecision


# ── Reflex.decide ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_greeting_is_trivial_skip():
    r = Reflex()
    d = await r.decide("hi")
    assert d.intent == "greeting"
    assert d.path == "trivial"
    assert d.needs_llm is False
    assert d.source_kind == "trivial"
    assert d.requires_memory is False
    assert d.prefetch_hint == []


@pytest.mark.asyncio
async def test_identity_question_is_trivial_skip():
    r = Reflex()
    d = await r.decide("what are you")
    assert d.intent == "identity"
    assert d.needs_llm is False


@pytest.mark.asyncio
@pytest.mark.parametrize("phrase", [
    "how is life",
    "HOW IS LIFE?",
    "how are you",
    "how are things",
    "how's it going",
    "what's up",
    "whats up",
    "you good",
    "all good",
    "thanks",
    "thank you",
    "bye",
    "see ya",
])
async def test_casual_chat_is_regex_skip(phrase):
    r = Reflex()
    d = await r.decide(phrase)
    assert d.intent == "conversational", f"expected conversational for '{phrase}', got {d.intent}"
    assert d.needs_llm is False
    assert d.path == "fast_path"
    assert d.requires_memory is False
    assert d.prefetch_hint == []


@pytest.mark.asyncio
async def test_regex_tool_match_skips_gemini():
    r = Reflex()
    d = await r.decide("git status")
    assert d.intent == "git"
    assert d.path == "tool"
    assert d.needs_llm is False
    assert d.source_kind == "regex"
    assert d.tool_pick is not None
    assert d.tool_pick["tool"] == "git"


@pytest.mark.asyncio
async def test_embed_match_always_escalates_to_gemini():
    """Non-regex prompts must always set needs_llm=True regardless of confidence."""
    r = Reflex()
    d = await r.decide("write a function that sorts a list of dicts by key")
    assert d.needs_llm is True
    assert d.source_kind in ("embed", "token")
    assert d.intent in ("coding", "search", "chat", "fs", "exploration")  # plausible buckets


@pytest.mark.asyncio
async def test_prefetch_hint_is_targeted_not_shotgun():
    r = Reflex()
    d = await r.decide("write a function that sorts a list of dicts by key")
    # coding intent → compass+memory, never workspace/skill
    assert set(d.prefetch_hint).issubset({"compass", "memory", "workspace", "skill"})


@pytest.mark.asyncio
async def test_cache_hit_returns_same_decision():
    r = Reflex()
    d1 = await r.decide("git status")
    d2 = await r.decide("git status")
    assert d1.intent == d2.intent
    stats = r.stats()
    assert stats["cache_hits"] >= 1


@pytest.mark.asyncio
async def test_to_classification_carries_reflex_metadata():
    r = Reflex()
    d = await r.decide("git status")
    c = d.to_classification()
    assert "_reflex" in c
    assert c["_reflex"]["source_kind"] == "regex"
    assert c["_reflex"]["needs_llm"] is False


# ── PrefetchBundle ───────────────────────────────────────────────────────────

class _FakeMem:
    def __init__(self, latency=0.1):
        self.latency = latency
    async def get_relevant_context(self, prompt, sid):
        await asyncio.sleep(self.latency)
        return f"MEM[{prompt[:20]}]"


class _FakeCompass:
    index = True
    def __init__(self, latency=0.05):
        self.latency = latency
    def context_for_query(self, q, max_files=5):
        time.sleep(self.latency)
        return f"COMPASS[{q[:20]}]"
    def build(self):
        pass


@pytest.mark.asyncio
async def test_prefetch_runs_in_parallel_with_classifier():
    """Bundle + a 0.4s classifier should finish in ~max(0.4, 0.3)s, not sum."""
    async def fake_classify():
        await asyncio.sleep(0.4)
        return {"intent": "coding", "_reflex": {}}

    bundle = PrefetchBundle(
        hints=["memory", "compass"],
        prompt="benchmark prompt",
        session_id="test",
        memory_manager=_FakeMem(latency=0.25),
        code_compass=_FakeCompass(latency=0.05),
    ).start()

    t0 = time.perf_counter()
    results, classification = await asyncio.gather(
        bundle.await_all(timeout=2.0),
        fake_classify(),
    )
    elapsed = time.perf_counter() - t0

    assert "memory" in results
    assert "compass" in results
    # Strict parallel proof — must be well below the serial sum (0.4 + 0.3 = 0.7s)
    assert elapsed < 0.55, f"expected parallel ~0.4s, got {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_prefetch_cache_hit_zero_cpu(monkeypatch):
    PrefetchBundle._CACHE.clear()
    common = dict(
        hints=["memory"],
        prompt="cache test prompt",
        session_id="cachesess",
        memory_manager=_FakeMem(latency=0.2),
    )
    b1 = PrefetchBundle(**common).start()
    await b1.await_all(timeout=2.0)

    t0 = time.perf_counter()
    b2 = PrefetchBundle(**common).start()
    r2 = await b2.await_all(timeout=2.0)
    elapsed = time.perf_counter() - t0
    assert r2.get("memory") is not None
    # Second hit should be < 50ms (was ~200ms cold).
    assert elapsed < 0.05, f"cache miss penalty — got {elapsed:.3f}s"


@pytest.mark.asyncio
async def test_prefetch_cancel_stops_in_flight():
    """cancel() should stop slow tasks."""
    async def slow_mem():
        await asyncio.sleep(2.0)
        return "should never appear"

    class _SlowMem:
        async def get_relevant_context(self, prompt, sid):
            await asyncio.sleep(2.0)
            return "slow"

    bundle = PrefetchBundle(
        hints=["memory"],
        prompt="slow prompt",
        session_id="cancel_test",
        memory_manager=_SlowMem(),
    ).start()
    bundle.cancel()
    # await_all with short timeout should yield no memory result
    results = await bundle.await_all(timeout=0.1)
    assert results.get("memory") is None


# ── Reflex prefetch telemetry + adaptive disable ─────────────────────────────

@pytest.mark.asyncio
async def test_prefetch_telemetry_records_start_and_used():
    r = Reflex()
    bundle = PrefetchBundle(
        hints=["memory"],
        prompt="telemetry test",
        session_id="t1",
        memory_manager=_FakeMem(latency=0.01),
        reflex=r,
    ).start()
    await bundle.await_all(timeout=1.0)
    bundle.mark_used(bytes_saved=512)

    stats = r.stats()
    assert stats["prefetch_started"] >= 1
    assert stats["prefetch_used"] >= 1
    assert stats["prefetch_bytes_saved"] >= 512


@pytest.mark.asyncio
async def test_adaptive_disable_trips_on_high_waste():
    r = Reflex(adaptive_window=5, adaptive_waste_threshold=0.5)
    for _ in range(5):
        bundle = PrefetchBundle(
            hints=["memory"], prompt=f"x{_}", session_id="s",
            memory_manager=_FakeMem(latency=0.001), reflex=r,
        ).start()
        await bundle.await_all(timeout=1.0)
        bundle.mark_wasted()

    assert r.prefetch_enabled is False
    assert r._auto_disabled is True


@pytest.mark.asyncio
async def test_set_prefetch_enabled_clears_auto_disable():
    r = Reflex(adaptive_window=3, adaptive_waste_threshold=0.5)
    for _ in range(3):
        b = PrefetchBundle(hints=["memory"], prompt=f"y{_}", session_id="z",
                           memory_manager=_FakeMem(0.001), reflex=r).start()
        await b.await_all(timeout=1.0)
        b.mark_wasted()
    assert r.prefetch_enabled is False
    r.set_prefetch_enabled(True)
    assert r.prefetch_enabled is True
    assert r._auto_disabled is False


@pytest.mark.asyncio
async def test_decision_emits_empty_hint_when_prefetch_disabled():
    r = Reflex()
    r.set_prefetch_enabled(False)
    d = await r.decide("write a sort function in python")
    assert d.prefetch_hint == []


# ── Prompt-block injection helper ────────────────────────────────────────────

def test_render_prompt_block_includes_keys():
    bundle = {
        "memory": "remembered foo",
        "compass": "sym A in mod B",
        "skill": "AuditSkill",
    }
    out = PrefetchBundle.render_as_prompt_block(bundle)
    assert "REFLEX PREFETCH BUNDLE" in out
    assert "remembered foo" in out
    assert "sym A in mod B" in out
    assert "AuditSkill" in out


def test_render_prompt_block_empty_returns_empty():
    assert PrefetchBundle.render_as_prompt_block({}) == ""

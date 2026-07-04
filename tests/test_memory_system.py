"""
Tests for src/services/memory.py — fully covers async memory subsystem after
fixes (self-healing Redis, single-round-trip store, summarize-before-drop,
async Chroma ops, response cache stats, pruning).
"""

import asyncio
import json
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))


def run(coro):
    return asyncio.run(coro)


# Patch heavy chromadb / redis at import time so module loads cheap.
_chroma_patcher = patch("chromadb.PersistentClient")
_chroma_mock = _chroma_patcher.start()
_chroma_mock.return_value.get_or_create_collection.return_value = MagicMock()

_ef_patcher = patch("chromadb.utils.embedding_functions.DefaultEmbeddingFunction")
_ef_patcher.start()

from src.services.memory import (  # noqa: E402
    RedisManager, ChromaManager, ResponseCache, MemoryManager, _get_shared_ef,
)
from src.core.models import MemoryEntry, SessionContext  # noqa: E402

_chroma_patcher.stop()
_ef_patcher.stop()


# ════════════════════════════════════════════════════════════════════════════
# RedisManager — self-healing
# ════════════════════════════════════════════════════════════════════════════

class TestRedisManager(unittest.TestCase):

    def _mgr_with_mock(self):
        m = RedisManager()
        m.client = AsyncMock()
        return m

    def test_save_session_success(self):
        m = self._mgr_with_mock()
        ctx = SessionContext(session_id="s1", history=[MemoryEntry(role="user", content="hi")])
        ok = run(m.save_session(ctx))
        self.assertTrue(ok)
        m.client.set.assert_awaited()

    def test_save_session_marks_inactive_on_fail(self):
        m = self._mgr_with_mock()
        m.client.set.side_effect = Exception("connection refused")
        ctx = SessionContext(session_id="s1")
        ok = run(m.save_session(ctx))
        self.assertFalse(ok)
        self.assertFalse(m.is_active)
        self.assertGreater(m._failed_at, 0)

    def test_reactivation_after_cooldown(self):
        m = self._mgr_with_mock()
        m.is_active = False
        m._failed_at = time.time() - (RedisManager.RETRY_AFTER + 1)
        m._maybe_reactivate()
        self.assertTrue(m.is_active)

    def test_no_reactivation_during_cooldown(self):
        m = self._mgr_with_mock()
        m.is_active = False
        m._failed_at = time.time()
        m._maybe_reactivate()
        self.assertFalse(m.is_active)

    def test_load_session_returns_none_when_inactive(self):
        m = self._mgr_with_mock()
        m.is_active = False
        m._failed_at = time.time()
        result = run(m.load_session("anything"))
        self.assertIsNone(result)
        m.client.get.assert_not_awaited()

    def test_load_session_parses_json(self):
        m = self._mgr_with_mock()
        ctx = SessionContext(session_id="s1", history=[MemoryEntry(role="user", content="hi")])
        m.client.get.return_value = ctx.model_dump_json()
        loaded = run(m.load_session("s1"))
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.session_id, "s1")
        self.assertEqual(loaded.history[0].content, "hi")

    def test_delete_session(self):
        m = self._mgr_with_mock()
        ok = run(m.delete_session("s1"))
        self.assertTrue(ok)
        m.client.delete.assert_awaited()

    def test_list_session_ids(self):
        m = self._mgr_with_mock()
        m.client.keys.return_value = ["apex:session:a", "apex:session:b"]
        ids = run(m.list_session_ids())
        self.assertEqual(set(ids), {"a", "b"})


# ════════════════════════════════════════════════════════════════════════════
# ChromaManager — async ops + pruning
# ════════════════════════════════════════════════════════════════════════════

class TestChromaManager(unittest.TestCase):

    def _mgr(self):
        m = ChromaManager()
        m.collection = MagicMock()
        m.client = MagicMock()
        return m

    def test_add_memory_inserts_ts(self):
        m = self._mgr()
        ok = run(m.add_memory("text", {"key": "val"}, "id1"))
        self.assertTrue(ok)
        args, kwargs = m.collection.add.call_args
        meta = kwargs["metadatas"][0]
        self.assertIn("ts_unix", meta)
        self.assertIn("ts", meta)

    def test_add_memory_handles_failure(self):
        m = self._mgr()
        m.collection.add.side_effect = Exception("disk full")
        ok = run(m.add_memory("x", {}, "id"))
        self.assertFalse(ok)

    def test_search_returns_structured_results(self):
        m = self._mgr()
        m.collection.query.return_value = {
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"k": "v"}, {"k": "w"}]],
            "ids": [["id1", "id2"]],
            "distances": [[0.1, 0.3]],
        }
        results = run(m.search_memories("q"))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "id1")
        self.assertEqual(results[0]["distance"], 0.1)

    def test_search_empty_results(self):
        m = self._mgr()
        m.collection.query.return_value = {"documents": [[]]}
        results = run(m.search_memories("q"))
        self.assertEqual(results, [])

    def test_search_handles_failure(self):
        m = self._mgr()
        m.collection.query.side_effect = Exception("chroma down")
        results = run(m.search_memories("q"))
        self.assertEqual(results, [])

    def test_get_by_ids(self):
        m = self._mgr()
        m.collection.get.return_value = {
            "ids": ["a", "b"],
            "documents": ["doc-a", "doc-b"],
            "metadatas": [{}, {}],
        }
        result = run(m.get_by_ids(["a", "b"]))
        self.assertEqual(len(result), 2)

    def test_get_by_ids_empty_input(self):
        m = self._mgr()
        result = run(m.get_by_ids([]))
        self.assertEqual(result, [])
        m.collection.get.assert_not_called()

    def test_prune_older_than(self):
        m = self._mgr()
        m.collection.get.return_value = {"ids": ["old1", "old2"]}
        count = run(m.prune_older_than(days=30))
        self.assertEqual(count, 2)
        m.collection.delete.assert_called_with(ids=["old1", "old2"])

    def test_prune_no_old_entries(self):
        m = self._mgr()
        m.collection.get.return_value = {"ids": []}
        count = run(m.prune_older_than(days=30))
        self.assertEqual(count, 0)
        m.collection.delete.assert_not_called()


# ════════════════════════════════════════════════════════════════════════════
# ResponseCache — semantic dedup + stats
# ════════════════════════════════════════════════════════════════════════════

class TestResponseCache(unittest.TestCase):

    def _cache(self):
        c = ResponseCache()
        c.collection = MagicMock()
        c.client = MagicMock()
        c.is_active = True
        return c

    def test_inactive_returns_none(self):
        c = self._cache()
        c.is_active = False
        result = run(c.get_cached_response("q"))
        self.assertIsNone(result)

    def test_hit_within_threshold(self):
        c = self._cache()
        c.collection.query.return_value = {
            "documents": [["q1"]],
            "metadatas": [[{"response": "answer"}]],
            "distances": [[0.05]],
        }
        result = run(c.get_cached_response("q1", threshold=0.1))
        self.assertEqual(result, "answer")
        self.assertEqual(c.hits, 1)

    def test_miss_above_threshold(self):
        c = self._cache()
        c.collection.query.return_value = {
            "documents": [["q1"]],
            "metadatas": [[{"response": "answer"}]],
            "distances": [[0.5]],
        }
        result = run(c.get_cached_response("q1", threshold=0.1))
        self.assertIsNone(result)
        self.assertEqual(c.misses, 1)

    def test_missing_response_key(self):
        c = self._cache()
        c.collection.query.return_value = {
            "documents": [["q1"]],
            "metadatas": [[{}]],   # no response key
            "distances": [[0.05]],
        }
        result = run(c.get_cached_response("q1"))
        self.assertIsNone(result)
        self.assertEqual(c.misses, 1)

    def test_empty_results(self):
        c = self._cache()
        c.collection.query.return_value = {"documents": [[]]}
        result = run(c.get_cached_response("q"))
        self.assertIsNone(result)

    def test_cache_response_stores(self):
        c = self._cache()
        ok = run(c.cache_response("q", "r"))
        self.assertTrue(ok)
        c.collection.add.assert_called_once()

    def test_stats_hit_rate(self):
        c = self._cache()
        c.hits = 7
        c.misses = 3
        s = c.stats()
        self.assertEqual(s["hit_rate"], 0.7)

    def test_stats_zero_total(self):
        c = self._cache()
        s = c.stats()
        self.assertEqual(s["hit_rate"], 0.0)


# ════════════════════════════════════════════════════════════════════════════
# MemoryManager — integration
# ════════════════════════════════════════════════════════════════════════════

class TestMemoryManager(unittest.TestCase):

    def setUp(self):
        with patch("src.services.memory.RedisManager") as MR, \
             patch("src.services.memory.ChromaManager") as MC, \
             patch("src.services.memory.ResponseCache") as MCh:
            MR.return_value = MagicMock()
            MR.return_value.is_active = True
            MR.return_value.save_session = AsyncMock(return_value=True)
            MR.return_value.load_session = AsyncMock(return_value=None)
            MR.return_value.delete_session = AsyncMock(return_value=True)
            MC.return_value = MagicMock()
            MC.return_value.is_active = True
            MC.return_value.add_memory = AsyncMock(return_value=True)
            MC.return_value.search_memories = AsyncMock(return_value=[])
            MC.return_value.get_by_ids = AsyncMock(return_value=[])
            MC.return_value.prune_older_than = AsyncMock(return_value=0)
            MC.return_value.reset = AsyncMock(return_value=True)
            MCh.return_value = MagicMock()
            MCh.return_value.is_active = True
            MCh.return_value.reset = AsyncMock(return_value=True)
            self.mm = MemoryManager(history_cap=4, summarize_with_gemini=False)
        self.mm._gemini = None  # force fallback summary path

    def test_store_interaction_single_redis_round_trip(self):
        self.mm.redis.load_session = AsyncMock(return_value=None)
        run(self.mm.store_interaction("s1", "hi", "hello"))
        # Should LOAD once, SAVE once — no double round-trip
        self.assertEqual(self.mm.redis.load_session.await_count, 1)
        self.assertEqual(self.mm.redis.save_session.await_count, 1)

    def test_store_interaction_calls_chroma_add(self):
        self.mm.redis.load_session = AsyncMock(return_value=None)
        run(self.mm.store_interaction("s1", "u", "a"))
        self.mm.chroma.add_memory.assert_awaited()

    def test_store_interaction_attaches_related_ids(self):
        self.mm.redis.load_session = AsyncMock(return_value=None)
        self.mm.chroma.search_memories = AsyncMock(return_value=[
            {"id": "rid1", "content": "x", "metadata": {}, "distance": 0.1},
            {"id": "rid2", "content": "y", "metadata": {}, "distance": 0.2},
        ])
        run(self.mm.store_interaction("s1", "u", "a"))
        args, kwargs = self.mm.chroma.add_memory.call_args
        meta = kwargs["metadata"]
        self.assertEqual(meta["related_ids"], "rid1,rid2")

    def test_history_cap_summarizes_old_entries(self):
        # cap=4, summary_keep_recent=6 by default → with cap=4, anything beyond cap triggers summarize
        # but SUMMARY_KEEP_RECENT=6 > cap=4, so all entries become "recent" — let's tune
        self.mm.SUMMARY_KEEP_RECENT = 2
        ctx = SessionContext(session_id="s1", history=[
            MemoryEntry(role="user", content=f"msg{i}") for i in range(8)
        ])
        run(self.mm._enforce_history_cap(ctx))
        # 8 → 1 summary + 2 recent = 3
        self.assertEqual(len(ctx.history), 3)
        self.assertEqual(ctx.history[0].role, "system")
        self.assertIn("SUMMARY", ctx.history[0].content)

    def test_history_cap_no_op_when_under_limit(self):
        ctx = SessionContext(session_id="s1", history=[
            MemoryEntry(role="user", content="a"),
            MemoryEntry(role="assistant", content="b"),
        ])
        before = len(ctx.history)
        run(self.mm._enforce_history_cap(ctx))
        self.assertEqual(len(ctx.history), before)

    def test_get_relevant_context_includes_history(self):
        ctx = SessionContext(session_id="s1", history=[
            MemoryEntry(role="user", content="last question"),
        ])
        self.mm.redis.load_session = AsyncMock(return_value=ctx)
        result = run(self.mm.get_relevant_context("query", "s1"))
        self.assertIn("last question", result)

    def test_get_relevant_context_includes_memories(self):
        self.mm.redis.load_session = AsyncMock(return_value=None)
        self.mm.chroma.search_memories = AsyncMock(return_value=[
            {"id": "abc12345", "content": "important fact", "metadata": {}},
        ])
        result = run(self.mm.get_relevant_context("query", "s1"))
        self.assertIn("important fact", result)

    def test_clear_session_history(self):
        ok = run(self.mm.clear_session_history("s1"))
        self.assertTrue(ok)
        self.mm.redis.delete_session.assert_awaited_with("s1")

    def test_clear_all_history_resets_chroma_and_cache(self):
        self.mm.redis.client = AsyncMock()
        self.mm.redis.client.keys = AsyncMock(return_value=[])
        result = run(self.mm.clear_all_history())
        self.assertTrue(result["chroma"])
        self.assertTrue(result["cache"])
        self.mm.chroma.reset.assert_awaited()
        self.mm.cache.reset.assert_awaited()

    def test_prune_old_memories(self):
        self.mm.chroma.prune_older_than = AsyncMock(return_value=5)
        count = run(self.mm.prune_old_memories(days=30))
        self.assertEqual(count, 5)

    def test_stats_structure(self):
        s = self.mm.stats()
        self.assertIn("redis_active", s)
        self.assertIn("chroma_active", s)
        self.assertIn("cache_stats", s)
        self.assertIn("history_cap", s)

    def test_project_isolation(self):
        # 1. Test store_interaction saves project_name in metadata
        self.mm.redis.load_session = AsyncMock(return_value=None)
        run(self.mm.store_interaction("s1", "u", "a", project_name="my_proj"))
        args, kwargs = self.mm.chroma.add_memory.call_args
        self.assertEqual(kwargs["metadata"]["project_name"], "my_proj")

        # 2. Test get_relevant_context queries with project_name filter
        self.mm.chroma.search_memories = AsyncMock(return_value=[])
        run(self.mm.get_relevant_context("query", "s1", project_name="my_proj"))
        self.mm.chroma.search_memories.assert_awaited_with("query", where={"project_name": "my_proj"})


# ════════════════════════════════════════════════════════════════════════════
# Shared embedding function
# ════════════════════════════════════════════════════════════════════════════

class TestSharedEmbeddingFunction(unittest.TestCase):

    def test_singleton_returns_same_instance(self):
        a = _get_shared_ef()
        b = _get_shared_ef()
        self.assertIs(a, b)


if __name__ == "__main__":
    unittest.main(verbosity=2)

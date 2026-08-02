"""
APEX memory subsystem.

Three layers:
  - RedisManager     short-term session (history, last_plan)
  - ChromaManager    long-term semantic memory
  - ResponseCache    semantic LLM-response cache

Cross-cutting fixes:
  - Reconnect-after-failure (no permanent is_active=False)
  - Single Redis round-trip per interaction (no race)
  - Async-safe Chroma access via asyncio.to_thread
  - Summarize-before-drop when history exceeds cap
  - Shared embedding function (no duplicate model load)
  - Pruning by age (TTL)
  - Stats for observability
"""

import os
import time
import json
import uuid
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

import redis.asyncio as redis
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

from src.core.models import MemoryEntry, SessionContext

try:
    from google import genai
except Exception:
    genai = None

logger = logging.getLogger("apex.memory")

# Shared singleton embedding function — avoids loading sentence-transformer twice.
_SHARED_EF: Optional[Any] = None


def _get_shared_ef():
    global _SHARED_EF
    if _SHARED_EF is None:
        _SHARED_EF = embedding_functions.DefaultEmbeddingFunction()
    return _SHARED_EF


# ── Redis ────────────────────────────────────────────────────────────────────

class RedisManager:
    """
    Short-term session store. Self-healing + Local Disk Fallback.
    If Redis connection fails or is unavailable, seamlessly falls back to
    local JSON persistence so memory context NEVER drops.
    """

    RETRY_AFTER = 30  # seconds before retry after failure

    def __init__(self):
        load_dotenv()
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.is_active = True
        self._failed_at = 0.0
        self._local_sessions: Dict[str, SessionContext] = {}
        self._fallback_path = Path("data/session_history.json")
        self._load_local_fallback()

    def _load_local_fallback(self):
        try:
            if self._fallback_path.exists():
                raw = json.loads(self._fallback_path.read_text(encoding="utf-8"))
                for sid, sdata in raw.items():
                    self._local_sessions[sid] = SessionContext.model_validate(sdata)
        except Exception as e:
            logger.debug(f"Local session fallback load failed: {e}")

    def _save_local_fallback(self):
        try:
            self._fallback_path.parent.mkdir(parents=True, exist_ok=True)
            dump = {sid: ctx.model_dump() for sid, ctx in self._local_sessions.items()}
            self._fallback_path.write_text(json.dumps(dump, indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Local session fallback save failed: {e}")

    def _on_fail(self, op: str, e: Exception):
        self.is_active = False
        self._failed_at = time.time()
        logger.debug(f"Redis {op} failed: {e}; using local fallback (cooldown {self.RETRY_AFTER}s)")

    def _maybe_reactivate(self):
        if not self.is_active and (time.time() - self._failed_at) > self.RETRY_AFTER:
            self.is_active = True
            logger.info("Redis reactivated after cooldown")

    async def save_session(self, context: SessionContext) -> bool:
        self._local_sessions[context.session_id] = context
        self._save_local_fallback()
        self._maybe_reactivate()
        if not self.is_active:
            return False
        try:
            key = f"apex:session:{context.session_id}"
            await self.client.set(key, context.model_dump_json())
            return True
        except Exception as e:
            self._on_fail("save_session", e)
            return False

    async def load_session(self, session_id: str) -> Optional[SessionContext]:
        self._maybe_reactivate()
        if self.is_active:
            try:
                key = f"apex:session:{session_id}"
                data = await self.client.get(key)
                if data:
                    ctx = SessionContext.model_validate_json(data)
                    self._local_sessions[session_id] = ctx
                    return ctx
            except Exception as e:
                self._on_fail("load_session", e)

        return self._local_sessions.get(session_id)

    async def delete_session(self, session_id: str) -> bool:
        if session_id in self._local_sessions:
            del self._local_sessions[session_id]
            self._save_local_fallback()
        self._maybe_reactivate()
        if not self.is_active:
            return False
        try:
            await self.client.delete(f"apex:session:{session_id}")
            return True
        except Exception as e:
            self._on_fail("delete_session", e)
            return False

    async def list_session_ids(self) -> List[str]:
        self._maybe_reactivate()
        if self.is_active:
            try:
                keys = await self.client.keys("apex:session:*")
                r_keys = [k.split(":", 2)[2] for k in keys]
                return list(set(r_keys) | set(self._local_sessions.keys()))
            except Exception as e:
                self._on_fail("list_session_ids", e)
        return list(self._local_sessions.keys())


# ── Chroma ───────────────────────────────────────────────────────────────────

class ChromaManager:
    """
    Long-term semantic memory. All blocking Chroma calls go through
    asyncio.to_thread to avoid blocking the event loop.
    """

    def __init__(self, collection_name: str = "apex_memories"):
        load_dotenv()
        path = os.getenv("CHROMA_PATH", "./data/chroma")
        self.client = chromadb.PersistentClient(path=path)
        self.ef = _get_shared_ef()
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.ef,
        )
        self.is_active = True

    def _on_fail(self, op: str, e: Exception):
        logger.warning(f"Chroma {op} failed: {e}")

    async def add_memory(self, text: str, metadata: Dict[str, Any], doc_id: str) -> bool:
        if not self.is_active:
            return False
        meta = dict(metadata or {})
        meta.setdefault("ts", datetime.now().isoformat())
        meta.setdefault("ts_unix", time.time())
        try:
            await asyncio.to_thread(
                self.collection.add,
                documents=[text], metadatas=[meta], ids=[doc_id],
            )
            return True
        except Exception as e:
            self._on_fail("add_memory", e)
            return False

    async def search_memories(self, query: str, n_results: int = 3,
                              where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.is_active:
            return []
        try:
            kwargs = {"query_texts": [query], "n_results": n_results}
            if where:
                kwargs["where"] = where
            results = await asyncio.to_thread(self.collection.query, **kwargs)
            if where and (not results.get("documents") or not results["documents"][0]):
                kwargs_fallback = {"query_texts": [query], "n_results": n_results}
                results = await asyncio.to_thread(self.collection.query, **kwargs_fallback)
        except Exception as e:
            self._on_fail("search_memories", e)
            return []
        if not results.get("documents") or not results["documents"][0]:
            return []
        out = []
        for i in range(len(results["documents"][0])):
            out.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                "id": results["ids"][0][i],
                "distance": results["distances"][0][i] if results.get("distances") else None,
            })
        return out

    async def get_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        if not self.is_active or not ids:
            return []
        try:
            res = await asyncio.to_thread(self.collection.get, ids=ids)
        except Exception as e:
            self._on_fail("get_by_ids", e)
            return []
        out = []
        for i, did in enumerate(res.get("ids", []) or []):
            out.append({
                "id": did,
                "content": res["documents"][i] if res.get("documents") else "",
                "metadata": res["metadatas"][i] if res.get("metadatas") else {},
            })
        return out

    async def prune_older_than(self, days: int) -> int:
        """Delete memories older than `days`. Returns count removed."""
        if not self.is_active:
            return 0
        cutoff = time.time() - days * 86400
        try:
            res = await asyncio.to_thread(
                self.collection.get,
                where={"ts_unix": {"$lt": cutoff}},
            )
            ids = res.get("ids", []) or []
            if ids:
                await asyncio.to_thread(self.collection.delete, ids=ids)
            return len(ids)
        except Exception as e:
            self._on_fail("prune_older_than", e)
            return 0

    async def reset(self) -> bool:
        try:
            await asyncio.to_thread(self.client.delete_collection, self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name, embedding_function=self.ef,
            )
            return True
        except Exception as e:
            self._on_fail("reset", e)
            return False


# ── Response cache ───────────────────────────────────────────────────────────

class ResponseCache:
    """
    Semantic LLM-response cache. Keyed by query embedding. Returns a hit when
    distance to nearest cached query is below threshold.
    """

    def __init__(self, collection_name: str = "apex_cache",
                 default_threshold: float = 0.15):
        load_dotenv()
        path = os.getenv("CHROMA_PATH", "./data/chroma")
        try:
            self.client = chromadb.PersistentClient(path=path)
            self.ef = _get_shared_ef()
            self.collection = self.client.get_or_create_collection(
                name=collection_name, embedding_function=self.ef,
            )
            self.is_active = True
        except Exception as e:
            logger.warning(f"ResponseCache init failed: {e}")
            self.client = None
            self.collection = None
            self.is_active = False

        self.collection_name = collection_name
        self.default_threshold = default_threshold
        self.hits = 0
        self.misses = 0

    async def get_cached_response(self, query: str,
                                  threshold: Optional[float] = None) -> Optional[str]:
        if not self.is_active or self.collection is None:
            return None
        thr = threshold if threshold is not None else self.default_threshold
        try:
            results = await asyncio.to_thread(
                self.collection.query, query_texts=[query], n_results=1,
            )
        except Exception as e:
            logger.warning(f"ResponseCache query failed: {e}")
            return None
        if not results.get("documents") or not results["documents"][0]:
            self.misses += 1
            return None
        if not results.get("distances") or not results["distances"][0]:
            self.misses += 1
            return None
        if results["distances"][0][0] >= thr:
            self.misses += 1
            return None
        meta = results["metadatas"][0][0] if results.get("metadatas") else {}
        resp = (meta or {}).get("response")
        if not resp:
            self.misses += 1
            return None
        self.hits += 1
        return resp

    async def cache_response(self, query: str, response: str) -> bool:
        if not self.is_active or self.collection is None:
            return False
        try:
            await asyncio.to_thread(
                self.collection.add,
                documents=[query],
                metadatas=[{"response": response, "ts_unix": time.time()}],
                ids=[str(uuid.uuid4())],
            )
            return True
        except Exception as e:
            logger.warning(f"ResponseCache add failed: {e}")
            return False

    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        return {
            "hits": self.hits, "misses": self.misses, "total": total,
            "hit_rate": (self.hits / total) if total else 0.0,
        }

    async def reset(self) -> bool:
        if not self.is_active or self.client is None:
            return False
        try:
            await asyncio.to_thread(self.client.delete_collection, self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name, embedding_function=self.ef,
            )
            self.hits = 0
            self.misses = 0
            return True
        except Exception as e:
            logger.warning(f"ResponseCache reset failed: {e}")
            return False


# ── Unified manager ──────────────────────────────────────────────────────────

class MemoryManager:
    """
    Coordinates Redis (short-term), Chroma (long-term), Cache (semantic dedup).

    Behaviors:
      - store_interaction: single Redis round-trip for both turns (no race)
      - history_cap auto-summarize: when history > cap, oldest pairs collapse
        into one summary entry (Gemini if available, else concatenation)
      - get_relevant_context: drops oldest history first instead of mid-truncation
      - prune_old_memories(days): removes Chroma entries older than threshold
      - clear_all_history: wipes session + memories + cache + (optionally) forge
    """

    DEFAULT_HISTORY_CAP = 20  # entries (10 user/assistant pairs)
    SUMMARY_KEEP_RECENT = 6   # always keep this many newest entries unsummarized

    def __init__(self, history_cap: Optional[int] = None,
                 summarize_with_gemini: bool = True):
        load_dotenv()
        self.redis = RedisManager()
        self.chroma = ChromaManager()
        self.cache = ResponseCache()
        self.history_cap = history_cap or int(
            os.getenv("APEX_HISTORY_CAP", str(self.DEFAULT_HISTORY_CAP))
        )
        self.summarize_with_gemini = summarize_with_gemini and bool(os.getenv("GEMINI_API_KEY"))
        api_key = os.getenv("GEMINI_API_KEY")
        self._gemini = (
            genai.Client(api_key=api_key)
            if (genai and api_key and self.summarize_with_gemini) else None
        )

    # ---- summarization ----

    async def _summarize_old_history(self, entries: List[MemoryEntry]) -> str:
        """Collapse old entries into a single dense summary."""
        if not entries:
            return ""
        if not self._gemini:
            # fallback: concatenated bullet list, still tagged for downstream filters
            bullets = "\n".join(f"- {e.role}: {e.content[:200]}" for e in entries)
            return f"[SUMMARY of {len(entries)} earlier turns — heuristic, no LLM]\n{bullets}"
        joined = "\n".join(f"{e.role}: {e.content[:600]}" for e in entries)
        prompt = (
            f"Summarize this conversation history into a single dense paragraph "
            f"(<=400 chars). Preserve facts, decisions, and unresolved threads. "
            f"Drop pleasantries.\n\n{joined}"
        )
        try:
            res = await asyncio.to_thread(
                self._gemini.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=prompt,
            )
            return f"[SUMMARY of {len(entries)} earlier turns]: {(res.text or '').strip()[:600]}"
        except Exception as e:
            logger.warning(f"summary failed: {e}")
            return "Earlier conversation:\n" + "\n".join(
                f"- {e.role}: {e.content[:200]}" for e in entries
            )

    async def _enforce_history_cap(self, context: SessionContext):
        """If history > cap, summarize oldest entries and replace them."""
        if len(context.history) <= self.history_cap:
            return
        keep = self.SUMMARY_KEEP_RECENT
        old = context.history[: -keep] if keep > 0 else context.history[:]
        recent = context.history[-keep:] if keep > 0 else []
        summary_text = await self._summarize_old_history(old)
        context.history = (
            [MemoryEntry(role="system", content=summary_text)] + recent
        )

    # ---- public ops ----

    async def get_relevant_context(self, query: str, session_id: str,
                                   project_name: Optional[str] = None,
                                   max_tokens: int = 8000) -> str:
        history_str = ""
        context = await self.redis.load_session(session_id)
        if context and context.history:
            history_str = "\n".join(
                f"{e.role}: {e.content}" for e in context.history
            )

        where = {"project_name": project_name} if project_name else None
        memories = await self.chroma.search_memories(query, where=where)
        parts: List[str] = []
        if history_str:
            parts.append(history_str)

        for m in memories:
            parts.append(f"Memory ({m['id'][:8]}): {m['content']}")
            meta = m.get("metadata") or {}
            related_raw = meta.get("related_ids", "") if isinstance(meta, dict) else ""
            related_ids = [r for r in related_raw.split(",") if r] if isinstance(related_raw, str) else []
            if related_ids:
                rels = await self.chroma.get_by_ids(related_ids[:3])
                for r in rels:
                    parts.append(f"Related Fact ({r['id'][:8]}): {r['content'][:400]}")

        full = "\n\n".join(parts)
        char_budget = max_tokens * 4
        if len(full) <= char_budget:
            return full

        # Drop oldest history entries first (preserves structure of newer content)
        if context and context.history:
            trimmed = list(context.history)
            while trimmed and len(full) > char_budget:
                trimmed.pop(0)
                history_str = "\n".join(f"{e.role}: {e.content}" for e in trimmed)
                parts[0] = history_str if history_str else ""
                full = "\n\n".join(p for p in parts if p)

        if len(full) > char_budget:
            full = (
                full[: char_budget // 2]
                + "\n\n[... TRUNCATED — run /compact ...]\n\n"
                + full[-(char_budget // 2):]
            )
        return full

    async def store_interaction(self, session_id: str,
                                user_input: str, assistant_output: str,
                                project_name: Optional[str] = None):
        # Single Redis round-trip — no race between user-add and assistant-add
        context = await self.redis.load_session(session_id) or SessionContext(session_id=session_id)
        context.history.append(MemoryEntry(role="user", content=user_input))
        context.history.append(MemoryEntry(role="assistant", content=assistant_output))
        await self._enforce_history_cap(context)
        await self.redis.save_session(context)

        # Long-term semantic memory
        related_ids: List[str] = []
        where = {"project_name": project_name} if project_name else None
        try:
            recent = await self.chroma.search_memories(user_input, n_results=2, where=where)
            related_ids = [r["id"] for r in recent]
        except Exception as e:
            logger.warning(f"search_memories during store failed: {e}")

        doc_id = str(uuid.uuid4())
        metadata = {
            "session_id": session_id,
            "related_ids": ",".join(related_ids),
        }
        if project_name:
            metadata["project_name"] = project_name

        await self.chroma.add_memory(
            text=f"User: {user_input}\nAssistant: {assistant_output}",
            metadata=metadata,
            doc_id=doc_id,
        )

    async def clear_session_history(self, session_id: str) -> bool:
        return await self.redis.delete_session(session_id)

    async def clear_all_history(self, include_forge: bool = False) -> Dict[str, Any]:
        results = {"redis": False, "chroma": False, "cache": False, "forge": None}
        # Redis
        if self.redis.is_active:
            try:
                keys = await self.redis.client.keys("apex:session:*")
                if keys:
                    await self.redis.client.delete(*keys)
                results["redis"] = True
            except Exception as e:
                self.redis._on_fail("clear_all", e)

        results["chroma"] = await self.chroma.reset()
        results["cache"] = await self.cache.reset()

        if include_forge:
            forge_collections = ["apex_forge_papers"]
            results["forge"] = []
            for name in forge_collections:
                try:
                    await asyncio.to_thread(self.chroma.client.delete_collection, name)
                    results["forge"].append(name)
                except Exception:
                    pass
        return results

    async def prune_old_memories(self, days: int = 60) -> int:
        """Remove Chroma memories older than `days`. Returns count removed."""
        return await self.chroma.prune_older_than(days)

    async def degrade_memories(self, age_hours: float = 24) -> int:
        """
        Scans Chroma for non-legend memories older than `age_hours` and degrades
        them into a lossy, subjective, folklore-style 'legend' (1-2 sentences).
        """
        if not self.chroma.is_active:
            return 0
        cutoff = time.time() - age_hours * 3600
        try:
            res = await asyncio.to_thread(
                self.chroma.collection.get,
                where={"ts_unix": {"$lt": cutoff}}
            )
        except Exception as e:
            logger.warning(f"degrade get failed: {e}")
            return 0

        ids = res.get("ids", []) or []
        documents = res.get("documents", []) or []
        metadatas = res.get("metadatas", []) or []

        degraded_count = 0
        for i, doc_id in enumerate(ids):
            meta = metadatas[i] or {}
            if meta.get("is_legend"):
                continue
            
            raw_text = documents[i]
            legend_text = raw_text
            if self._gemini:
                prompt = f"""
                You are the memory decay daemon of APEX.
                Your task: compress the following precise conversation log into a short, legendary story (1-2 sentences).
                Add a touch of human subjectivity or slightly exaggerated folklore (e.g., 'the time we fought the validation regex bug for hours and triumphed' instead of 'user fixed code regex error at 12:00').
                Keep it brief and memorable.

                CONVERSATION LOG:
                {raw_text}
                """
                try:
                    r = await asyncio.to_thread(
                        self._gemini.models.generate_content,
                        model="gemini-2.5-flash-lite",
                        contents=prompt
                    )
                    legend_text = (r.text or "").strip()
                except Exception as e:
                    logger.warning(f"degrade LLM failed for {doc_id}: {e}")
                    legend_text = f"[Legend fallback]: {raw_text[:100]}..."

            try:
                new_meta = dict(meta)
                new_meta["is_legend"] = True
                new_meta["ts_degraded"] = datetime.now().isoformat()
                await asyncio.to_thread(
                    self.chroma.collection.update,
                    ids=[doc_id],
                    documents=[legend_text],
                    metadatas=[new_meta]
                )
                degraded_count += 1
            except Exception as e:
                logger.warning(f"degrade update failed for {doc_id}: {e}")

        return degraded_count

    async def correct_legend(self, doc_id: str, corrected_text: str) -> bool:
        """
        Manually overwrites the text of a memory legend.
        """
        if not self.chroma.is_active:
            return False
        try:
            res = await asyncio.to_thread(self.chroma.collection.get, ids=[doc_id])
            if not res.get("ids"):
                return False
            meta = (res.get("metadatas", [{}])[0] or {})
            meta["is_legend"] = True
            meta["ts_corrected"] = datetime.now().isoformat()
            await asyncio.to_thread(
                self.chroma.collection.update,
                ids=[doc_id],
                documents=[corrected_text],
                metadatas=[meta]
            )
            return True
        except Exception as e:
            logger.warning(f"correct_legend failed: {e}")
            return False

    def stats(self) -> Dict[str, Any]:
        return {
            "redis_active": self.redis.is_active,
            "chroma_active": self.chroma.is_active,
            "cache_active": self.cache.is_active,
            "cache_stats": self.cache.stats(),
            "history_cap": self.history_cap,
            "summarize_enabled": self.summarize_with_gemini,
        }

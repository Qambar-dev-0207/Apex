import os
import re
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import httpx
from dotenv import load_dotenv

try:
    from google import genai
except Exception:
    genai = None


GH_TRENDING_URL = "https://github.com/trending"
GH_TRENDING_LANG = "https://github.com/trending/{lang}"
PYPI_RSS = "https://pypi.org/rss/updates.xml"
PYPI_NEW_RSS = "https://pypi.org/rss/packages.xml"
HF_TRENDING = "https://huggingface.co/api/models"
HN_ALGOLIA = "https://hn.algolia.com/api/v1/search_by_date"
NPM_REGISTRY_SEARCH = "https://registry.npmjs.org/-/v1/search"

PYPI_VERSION_RE = re.compile(r"\s+\d+(?:\.\d+){0,3}(?:[a-zA-Z0-9.\-+]*)$")


def _strip_pypi_version(title: str) -> str:
    return PYPI_VERSION_RE.sub("", title or "").strip()


class EcosystemWatcher:
    """
    Monitors the Python/JS/AI ecosystem for new libraries, models, and tools.
    Sources:
      - PyPI: new packages + recent releases (RSS)
      - GitHub Trending: scrape (Python + AI langs)
      - HuggingFace: trending models API
      - HackerNews: filtered story stream (Algolia)
      - npm: search-based filter for AI/agent keywords
    Diff against last scan to surface only NEW items. Score relevance for APEX.
    """

    def __init__(self, data_dir: str = "data/forge", console=None,
                 gh_languages: Optional[List[str]] = None,
                 hn_query: str = "AI agent OR LLM OR agentic OR \"open source\" tool",
                 relevance_threshold: float = 0.5):
        load_dotenv()
        self.console = console
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.data_dir / "ecosystem.jsonl"
        self.state_path = self.data_dir / "ecosystem_state.json"

        self.gh_languages = gh_languages or ["python", "rust", "typescript"]
        self.hn_query = hn_query
        self.threshold = relevance_threshold

        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if (genai and api_key) else None
        self.model_id = "gemini-2.5-flash-lite"

    # ---------- helpers ----------

    def _log(self, msg: str, level: str = "info"):
        if not self.console:
            return
        color = {"info": "cyan", "warn": "yellow", "err": "red"}.get(level, "white")
        self.console.print(f"[dim {color}][Ecosystem] {msg}[/dim {color}]")

    def _load_state(self) -> Dict[str, Any]:
        if not self.state_path.exists():
            return {}
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_state(self, state: Dict[str, Any]):
        try:
            self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception as e:
            self._log(f"state save fail: {e}", level="warn")

    def _append_log(self, batch: Dict[str, Any]):
        try:
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(batch, ensure_ascii=False) + "\n")
        except Exception as e:
            self._log(f"log append fail: {e}", level="warn")

    # ---------- sources ----------

    async def fetch_pypi_releases(self, limit: int = 40) -> List[Dict[str, Any]]:
        url = PYPI_RSS
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                r = await client.get(url, headers={"User-Agent": "APEX-Forge/1.0"})
                r.raise_for_status()
        except Exception as e:
            self._log(f"pypi fail: {e}", level="warn")
            return []
        items = re.findall(r"<item>(.*?)</item>", r.text, re.DOTALL)
        out = []
        for it in items[:limit]:
            title = re.search(r"<title>(.*?)</title>", it, re.DOTALL)
            link = re.search(r"<link>(.*?)</link>", it, re.DOTALL)
            desc = re.search(r"<description>(.*?)</description>", it, re.DOTALL)
            pub = re.search(r"<pubDate>(.*?)</pubDate>", it, re.DOTALL)
            t = title.group(1).strip() if title else ""
            pkg = _strip_pypi_version(t)
            out.append({
                "source": "pypi",
                "key": f"pypi:{pkg}",
                "title": t,
                "url": link.group(1).strip() if link else "",
                "summary": (desc.group(1).strip() if desc else "")[:500],
                "published": pub.group(1).strip() if pub else "",
            })
        return out

    async def fetch_pypi_new_packages(self, limit: int = 30) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                r = await client.get(PYPI_NEW_RSS, headers={"User-Agent": "APEX-Forge/1.0"})
                r.raise_for_status()
        except Exception as e:
            self._log(f"pypi-new fail: {e}", level="warn")
            return []
        items = re.findall(r"<item>(.*?)</item>", r.text, re.DOTALL)
        out = []
        for it in items[:limit]:
            title = re.search(r"<title>(.*?)</title>", it, re.DOTALL)
            link = re.search(r"<link>(.*?)</link>", it, re.DOTALL)
            desc = re.search(r"<description>(.*?)</description>", it, re.DOTALL)
            t = title.group(1).strip() if title else ""
            pkg = _strip_pypi_version(t)
            out.append({
                "source": "pypi-new",
                "key": f"pypi-new:{pkg}",
                "title": t,
                "url": link.group(1).strip() if link else "",
                "summary": (desc.group(1).strip() if desc else "")[:500],
                "published": "",
            })
        return out

    async def fetch_github_trending(self, lang: str = "") -> List[Dict[str, Any]]:
        url = GH_TRENDING_LANG.format(lang=lang) if lang else GH_TRENDING_URL
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                r = await client.get(url, headers={"User-Agent": "Mozilla/5.0 APEX-Forge"})
                r.raise_for_status()
        except Exception as e:
            self._log(f"gh-trending {lang} fail: {e}", level="warn")
            return []
        out = []
        repo_pattern = re.compile(
            r'<h2 class="h3 lh-condensed">.*?<a href="/([^"/]+)/([^"]+)"[^>]*>.*?</a>',
            re.DOTALL,
        )
        desc_pattern = re.compile(
            r'<p class="col-9 color-fg-muted my-1 pr-4">\s*([^<]+)</p>',
            re.DOTALL,
        )
        repos = repo_pattern.findall(r.text)
        descs = desc_pattern.findall(r.text)
        for i, (owner, name) in enumerate(repos[:25]):
            desc = (descs[i].strip() if i < len(descs) else "")[:500]
            slug = f"{owner}/{name}"
            out.append({
                "source": f"github-trending-{lang or 'all'}",
                "key": f"gh:{slug}",
                "title": slug,
                "url": f"https://github.com/{slug}",
                "summary": desc,
                "published": "",
            })
        return out

    async def fetch_huggingface_trending(self, limit: int = 25) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(HF_TRENDING, params={"sort": "trendingScore", "direction": "-1", "limit": str(limit)})
                r.raise_for_status()
                data = r.json()
        except Exception as e:
            self._log(f"hf fail: {e}", level="warn")
            return []
        out = []
        for m in data[:limit]:
            mid = m.get("modelId") or m.get("id") or ""
            tags = m.get("tags", []) or []
            out.append({
                "source": "huggingface",
                "key": f"hf:{mid}",
                "title": mid,
                "url": f"https://huggingface.co/{mid}",
                "summary": (m.get("pipeline_tag", "") + " | " + ", ".join(tags[:6]))[:500],
                "published": m.get("lastModified", ""),
            })
        return out

    async def fetch_hackernews(self, limit: int = 25) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(HN_ALGOLIA, params={
                    "query": self.hn_query, "tags": "story",
                    "hitsPerPage": str(limit),
                })
                r.raise_for_status()
                data = r.json()
        except Exception as e:
            self._log(f"hn fail: {e}", level="warn")
            return []
        out = []
        for h in data.get("hits", [])[:limit]:
            t = h.get("title") or h.get("story_title") or ""
            url = h.get("url") or h.get("story_url") or ""
            oid = h.get("objectID", "")
            out.append({
                "source": "hackernews",
                "key": f"hn:{oid}",
                "title": t,
                "url": url,
                "summary": (h.get("story_text") or "")[:500],
                "published": h.get("created_at", ""),
                "points": h.get("points", 0),
            })
        return out

    async def fetch_npm_search(self, query: str = "ai agent llm", limit: int = 20) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(NPM_REGISTRY_SEARCH, params={"text": query, "size": str(limit)})
                r.raise_for_status()
                data = r.json()
        except Exception as e:
            self._log(f"npm fail: {e}", level="warn")
            return []
        out = []
        for obj in data.get("objects", [])[:limit]:
            pkg = obj.get("package", {})
            name = pkg.get("name", "")
            out.append({
                "source": "npm",
                "key": f"npm:{name}",
                "title": name,
                "url": pkg.get("links", {}).get("npm", ""),
                "summary": (pkg.get("description") or "")[:500],
                "published": pkg.get("date", ""),
            })
        return out

    # ---------- score ----------

    async def score_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items or not self.client:
            for it in items:
                it["relevance"] = 0.0
                it["domain"] = "unscored"
                it["why"] = ""
            return items

        compact = [
            {"i": i, "src": it["source"], "title": it["title"][:140], "summary": it.get("summary", "")[:240]}
            for i, it in enumerate(items)
        ]
        prompt = f"""
You triage open-source items for APEX, a Python agentic AI OS.
Score each item for actionable relevance to APEX's stack:
  Python services, agent orchestration, LLM tooling, memory/vector DBs,
  reasoning, MCP, sandboxing, CLI/REPL UI, multi-model routing.
Skip pure web frontends, niche libs, plain news, marketing posts.

Output JSON:
{{"scores":[{{"i":int,"relevance":0.0-1.0,"domain":"agent|llm|vector|tool|infra|reasoning|other","why":"<=80 chars"}}]}}

ITEMS:
{json.dumps(compact, ensure_ascii=False)[:14000]}
""".strip()
        try:
            res = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            data = json.loads(res.text)
        except Exception as e:
            self._log(f"score fail: {e}", level="warn")
            data = {"scores": []}

        by_idx = {s.get("i"): s for s in data.get("scores", []) if isinstance(s, dict)}
        for i, it in enumerate(items):
            s = by_idx.get(i, {})
            it["relevance"] = float(s.get("relevance", 0) or 0)
            it["domain"] = s.get("domain", "other")
            it["why"] = s.get("why", "")
        return items

    # ---------- scan ----------

    async def scan(self) -> Dict[str, Any]:
        state = self._load_state()
        seen_keys = set(state.get("seen_keys", []))

        sources_coros = [
            self.fetch_pypi_releases(40),
            self.fetch_pypi_new_packages(30),
            self.fetch_huggingface_trending(25),
            self.fetch_hackernews(25),
            self.fetch_npm_search("ai agent llm", 20),
        ]
        for lang in self.gh_languages:
            sources_coros.append(self.fetch_github_trending(lang))

        results = await asyncio.gather(*sources_coros, return_exceptions=True)
        all_items: List[Dict[str, Any]] = []
        for r in results:
            if isinstance(r, list):
                all_items.extend(r)

        new_items = [it for it in all_items if it["key"] not in seen_keys]
        new_items = await self.score_batch(new_items[:120])

        for it in new_items:
            seen_keys.add(it["key"])

        applicable = sorted(
            [it for it in new_items if it.get("relevance", 0) >= self.threshold],
            key=lambda x: -x["relevance"],
        )

        batch = {
            "ts": datetime.now().isoformat(),
            "total_seen": len(all_items),
            "new_count": len(new_items),
            "applicable_count": len(applicable),
            "applicable": applicable[:60],
        }
        self._append_log(batch)

        state["seen_keys"] = sorted(list(seen_keys))[-10000:]
        state["last_scan"] = batch["ts"]
        self._save_state(state)

        self._log(
            f"scanned {len(all_items)} | new {len(new_items)} | applicable {len(applicable)}",
            level="info",
        )
        return batch

    def recent_applicable(self, limit: int = 30) -> List[Dict[str, Any]]:
        if not self.log_path.exists():
            return []
        out: List[Dict[str, Any]] = []
        try:
            with self.log_path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
            for ln in reversed(lines):
                try:
                    batch = json.loads(ln)
                    out.extend(batch.get("applicable", []))
                except Exception:
                    continue
                if len(out) >= limit:
                    break
        except Exception:
            pass
        return out[:limit]

import os
import asyncio
import httpx
from typing import Dict, Any, List
from urllib.parse import quote_plus


class WebSearchTool:
    """
    Real web search via DuckDuckGo Instant Answer + Tavily fallback.
    No keys required for DDG; Tavily activates when TAVILY_API_KEY is set.
    """
    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.brave_key = os.getenv("BRAVE_API_KEY")

    async def asearch(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        if self.tavily_key:
            res = await self._tavily(query, max_results)
            if res.get("success"):
                return res
        if self.brave_key:
            res = await self._brave(query, max_results)
            if res.get("success"):
                return res
        return await self._ddg(query, max_results)

    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        try:
            return asyncio.run(self.asearch(query, max_results))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.asearch(query, max_results))
            finally:
                loop.close()

    async def _tavily(self, query: str, max_results: int) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.tavily_key,
                        "query": query,
                        "max_results": max_results,
                        "search_depth": "advanced",
                    },
                )
                r.raise_for_status()
                data = r.json()
                results = [
                    {"title": x.get("title"), "url": x.get("url"), "snippet": x.get("content", "")[:400]}
                    for x in data.get("results", [])
                ]
                return {"success": True, "results": results, "provider": "tavily", "error": None}
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    async def _brave(self, query: str, max_results: int) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": max_results},
                    headers={"X-Subscription-Token": self.brave_key, "Accept": "application/json"},
                )
                r.raise_for_status()
                data = r.json()
                results = [
                    {"title": x.get("title"), "url": x.get("url"), "snippet": x.get("description", "")[:400]}
                    for x in data.get("web", {}).get("results", [])
                ]
                return {"success": True, "results": results, "provider": "brave", "error": None}
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    async def _ddg(self, query: str, max_results: int) -> Dict[str, Any]:
        """
        DuckDuckGo Instant Answer + HTML fallback. No key required.
        """
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                r = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                )
                results: List[Dict[str, str]] = []
                if r.status_code == 200:
                    data = r.json()
                    if data.get("AbstractText"):
                        results.append({
                            "title": data.get("Heading", query),
                            "url": data.get("AbstractURL", ""),
                            "snippet": data.get("AbstractText", "")[:400],
                        })
                    for topic in (data.get("RelatedTopics") or [])[:max_results]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append({
                                "title": topic.get("Text", "")[:80],
                                "url": topic.get("FirstURL", ""),
                                "snippet": topic.get("Text", "")[:400],
                            })

                if not results:
                    html_r = await client.get(
                        f"https://html.duckduckgo.com/html/?q={quote_plus(query)}",
                        headers={"User-Agent": "Mozilla/5.0"},
                    )
                    import re
                    pattern = re.compile(
                        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>.*?<a[^>]+class="result__snippet"[^>]*>([^<]+)</a>',
                        re.DOTALL,
                    )
                    for m in list(pattern.finditer(html_r.text))[:max_results]:
                        results.append({
                            "title": re.sub(r"<[^>]+>", "", m.group(2)).strip(),
                            "url": m.group(1),
                            "snippet": re.sub(r"<[^>]+>", "", m.group(3)).strip()[:400],
                        })

                return {"success": True, "results": results, "provider": "duckduckgo", "error": None}
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

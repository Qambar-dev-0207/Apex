import os
import io
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from xml.etree import ElementTree as ET

import httpx
from dotenv import load_dotenv

try:
    from google import genai
except Exception:
    genai = None

try:
    import pypdf
except Exception:
    pypdf = None

try:
    import chromadb
    from chromadb.utils import embedding_functions
except Exception:
    chromadb = None


ARXIV_NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
ARXIV_API = "https://export.arxiv.org/api/query"

DEFAULT_CATEGORIES = [
    "cs.AI", "cs.CL", "cs.LG", "cs.MA",
    "cs.SE", "cs.PL", "cs.IR",
]


class PaperReader:
    """
    Reads arxiv papers, summarizes via Gemini, stores in ChromaDB for semantic recall.

    Pipeline:
      1. Poll arxiv API by category (recent submissions)
      2. Dedupe by arxiv id (skips already-ingested)
      3. Score abstracts for APEX-applicability
      4. For high-score: download PDF, extract text, chunk, summarize
      5. Persist: data/forge/papers.jsonl + chroma collection apex_forge_papers
    """

    def __init__(self, data_dir: str = "data/forge", console=None,
                 chroma_path: Optional[str] = None,
                 categories: Optional[List[str]] = None,
                 abstract_score_threshold: float = 0.55,
                 max_pdf_chars: int = 60000):
        load_dotenv()
        self.console = console
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.papers_log = self.data_dir / "papers.jsonl"
        self.seen_ids_path = self.data_dir / "papers_seen.json"
        self.categories = categories or DEFAULT_CATEGORIES
        self.threshold = abstract_score_threshold
        self.max_pdf_chars = max_pdf_chars

        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if (genai and api_key) else None
        self.model_id = "gemini-2.5-flash-lite"
        self.deep_model_id = "gemini-3.5-flash"

        self.chroma = None
        self.collection = None
        if chromadb:
            try:
                cpath = chroma_path or os.getenv("CHROMA_PATH", "./data/chroma")
                self.chroma = chromadb.PersistentClient(path=cpath)
                self.ef = embedding_functions.DefaultEmbeddingFunction()
                self.collection = self.chroma.get_or_create_collection(
                    name="apex_forge_papers", embedding_function=self.ef
                )
            except Exception as e:
                self._log(f"[PaperReader] Chroma init failed: {e}", level="warn")

    # ---------- internals ----------

    def _log(self, msg: str, level: str = "info"):
        if not self.console:
            return
        color = {"info": "cyan", "warn": "yellow", "err": "red"}.get(level, "white")
        self.console.print(f"[dim {color}][PaperReader] {msg}[/dim {color}]")

    def _load_seen(self) -> set:
        if not self.seen_ids_path.exists():
            return set()
        try:
            return set(json.loads(self.seen_ids_path.read_text(encoding="utf-8")))
        except Exception:
            return set()

    def _save_seen(self, seen: set):
        try:
            self.seen_ids_path.write_text(json.dumps(sorted(seen)[-5000:]), encoding="utf-8")
        except Exception as e:
            self._log(f"seen save fail: {e}", level="warn")

    def _append_log(self, record: Dict[str, Any]):
        try:
            with self.papers_log.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            self._log(f"log append fail: {e}", level="warn")

    # ---------- arxiv ----------

    def _parse_entries(self, root, category: str) -> List[Dict[str, Any]]:
        out = []
        for entry in root.findall("a:entry", ARXIV_NS):
            id_url = entry.findtext("a:id", "", ARXIV_NS)
            arxiv_id = id_url.rsplit("/", 1)[-1] if id_url else ""
            title = (entry.findtext("a:title", "", ARXIV_NS) or "").strip().replace("\n", " ")
            summary = (entry.findtext("a:summary", "", ARXIV_NS) or "").strip().replace("\n", " ")
            published = entry.findtext("a:published", "", ARXIV_NS)
            authors = [a.findtext("a:name", "", ARXIV_NS) for a in entry.findall("a:author", ARXIV_NS)]
            pdf_url = ""
            for link in entry.findall("a:link", ARXIV_NS):
                if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                    pdf_url = link.get("href", "")
                    break
            out.append({
                "id": arxiv_id,
                "category": category,
                "title": title[:400],
                "abstract": summary[:4000],
                "authors": authors[:6],
                "published": published,
                "pdf_url": pdf_url,
            })
        return out

    async def query_arxiv(self, category: str, max_results: int = 15) -> List[Dict[str, Any]]:
        params = {
            "search_query": f"cat:{category}",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": str(max_results),
        }
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(ARXIV_API, params=params)
                r.raise_for_status()
        except Exception as e:
            self._log(f"arxiv query fail ({category}): {e}", level="err")
            return []
        try:
            root = ET.fromstring(r.text)
        except Exception as e:
            self._log(f"arxiv parse fail: {e}", level="err")
            return []
        return self._parse_entries(root, category)

    async def query_arxiv_date_range(self, category: str, start_dt: datetime,
                                     end_dt: datetime, max_results: int = 20) -> List[Dict[str, Any]]:
        """Query arxiv for papers in a specific date range."""
        s = start_dt.strftime("%Y%m%d%H%M%S")
        e = end_dt.strftime("%Y%m%d%H%M%S")
        params = {
            "search_query": f"cat:{category} AND submittedDate:[{s} TO {e}]",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": str(max_results),
        }
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(ARXIV_API, params=params)
                r.raise_for_status()
        except Exception as e_:
            self._log(f"arxiv date-range fail ({category}): {e_}", level="err")
            return []
        try:
            root = ET.fromstring(r.text)
        except Exception as e_:
            self._log(f"arxiv parse fail: {e_}", level="err")
            return []
        return self._parse_entries(root, category)

    async def fetch_pdf_text(self, pdf_url: str) -> str:
        if not pdf_url or not pypdf:
            return ""
        try:
            async with httpx.AsyncClient(timeout=45, follow_redirects=True) as client:
                r = await client.get(pdf_url)
                r.raise_for_status()
        except Exception as e:
            self._log(f"pdf fetch fail: {e}", level="warn")
            return ""
        try:
            reader = pypdf.PdfReader(io.BytesIO(r.content))
            chunks = []
            total = 0
            for page in reader.pages:
                txt = page.extract_text() or ""
                chunks.append(txt)
                total += len(txt)
                if total >= self.max_pdf_chars:
                    break
            return "\n".join(chunks)[: self.max_pdf_chars]
        except Exception as e:
            self._log(f"pdf parse fail: {e}", level="warn")
            return ""

    # ---------- LLM ----------

    async def _gemini_json(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        if not self.client:
            return {}
        try:
            res = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model or self.model_id,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            return json.loads(res.text)
        except Exception as e:
            self._log(f"gemini fail: {e}", level="warn")
            return {}

    async def score_abstract(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
You triage research papers for APEX, a personal agentic AI OS (Python).
Score this paper for actionable relevance. Be strict — only high score if it
proposes a technique APEX could implement (not pure theory or unrelated domain).

PAPER TITLE: {paper['title']}
CATEGORY: {paper['category']}
ABSTRACT: {paper['abstract']}

Output JSON:
{{
  "applicability": 0.0-1.0,
  "domain": "agents|llm|memory|tools|reasoning|systems|other",
  "actionable_insight": "<=120 chars, concrete take-away",
  "implement_hint": "<=160 chars, where in APEX this could land",
  "skip_reason": "" or short reason
}}
""".strip()
        return await self._gemini_json(prompt)

    async def deep_summarize(self, paper: Dict[str, Any], pdf_text: str) -> Dict[str, Any]:
        body = pdf_text[: self.max_pdf_chars] if pdf_text else paper["abstract"]
        prompt = f"""
You are APEX's research distiller. Produce a high-density summary so APEX can
act on this paper without re-reading.

PAPER: {paper['title']}
ID: {paper['id']}
ABSTRACT: {paper['abstract']}
BODY (truncated): {body}

Output JSON:
{{
  "tldr": "<=240 chars",
  "novel_idea": "<=200 chars, the key contribution",
  "method_outline": ["bullet", "bullet", "..."],
  "results": "<=200 chars",
  "limitations": "<=200 chars",
  "apex_integration": {{
    "target_file_hint": "src/...py or new module",
    "approach": "<=240 chars",
    "risk": "low|medium|high",
    "effort_minutes": int
  }}
}}
""".strip()
        return await self._gemini_json(prompt, model=self.deep_model_id)

    # ---------- ingest ----------

    async def ingest_paper(self, paper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        score = await self.score_abstract(paper)
        applic = float(score.get("applicability", 0) or 0)
        record = {
            "id": paper["id"],
            "title": paper["title"],
            "category": paper["category"],
            "published": paper["published"],
            "pdf_url": paper["pdf_url"],
            "abstract": paper["abstract"],
            "score": score,
            "ingested_at": datetime.now().isoformat(),
        }
        if applic >= self.threshold:
            pdf_text = await self.fetch_pdf_text(paper["pdf_url"])
            deep = await self.deep_summarize(paper, pdf_text)
            record["deep"] = deep
            record["full_text_chars"] = len(pdf_text)
        self._append_log(record)
        if self.collection is not None:
            try:
                doc = (
                    f"{record['title']}\n\n"
                    f"ABSTRACT: {record['abstract'][:2000]}\n\n"
                    f"TLDR: {record.get('deep', {}).get('tldr', '')}\n"
                    f"NOVEL: {record.get('deep', {}).get('novel_idea', '')}"
                )
                meta = {
                    "id": record["id"],
                    "category": record["category"],
                    "applicability": applic,
                    "domain": str(score.get("domain", "")),
                    "published": record["published"],
                }
                self.collection.upsert(documents=[doc], metadatas=[meta], ids=[record["id"]])
            except Exception as e:
                self._log(f"chroma upsert fail: {e}", level="warn")
        return record

    async def scan(self, max_per_category: int = 8, max_total: int = 20,
                   request_interval_sec: float = 3.1) -> Dict[str, Any]:
        seen = self._load_seen()
        total_new: List[Dict[str, Any]] = []
        for idx, cat in enumerate(self.categories):
            if idx > 0:
                # arxiv requests >= 3s apart per their access policy
                await asyncio.sleep(request_interval_sec)
            entries = await self.query_arxiv(cat, max_results=max_per_category)
            fresh = [e for e in entries if e["id"] and e["id"] not in seen]
            for paper in fresh:
                if len(total_new) >= max_total:
                    break
                rec = await self.ingest_paper(paper)
                if rec:
                    total_new.append(rec)
                    seen.add(paper["id"])
            if len(total_new) >= max_total:
                break
        self._save_seen(seen)
        applicable = [r for r in total_new if (r.get("score") or {}).get("applicability", 0) >= self.threshold]
        self._log(f"scanned {len(total_new)} new; {len(applicable)} applicable", level="info")
        return {
            "ts": datetime.now().isoformat(),
            "new_count": len(total_new),
            "applicable_count": len(applicable),
            "applicable": applicable,
            "all": total_new,
        }

    async def scan_backfill(self, days: int = 7, max_per_category: int = 20,
                            max_total: int = 100,
                            request_interval_sec: float = 3.1) -> Dict[str, Any]:
        """Catch-up scan: ingest papers submitted in the last N days."""
        from datetime import timedelta
        seen = self._load_seen()
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        total_new: List[Dict[str, Any]] = []
        for idx, cat in enumerate(self.categories):
            if idx > 0:
                await asyncio.sleep(request_interval_sec)
            entries = await self.query_arxiv_date_range(cat, start_dt, end_dt, max_results=max_per_category)
            fresh = [e for e in entries if e["id"] and e["id"] not in seen]
            for paper in fresh:
                if len(total_new) >= max_total:
                    break
                rec = await self.ingest_paper(paper)
                if rec:
                    total_new.append(rec)
                    seen.add(paper["id"])
            if len(total_new) >= max_total:
                break
        self._save_seen(seen)
        applicable = [r for r in total_new if (r.get("score") or {}).get("applicability", 0) >= self.threshold]
        self._log(f"backfill {days}d: {len(total_new)} new; {len(applicable)} applicable", level="info")
        return {
            "ts": datetime.now().isoformat(),
            "days": days,
            "new_count": len(total_new),
            "applicable_count": len(applicable),
            "applicable": applicable,
            "all": total_new,
        }

    def search_papers(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        if self.collection is None:
            return []
        try:
            res = self.collection.query(query_texts=[query], n_results=n_results)
        except Exception as e:
            self._log(f"chroma query fail: {e}", level="warn")
            return []
        out = []
        if res.get("documents"):
            for i in range(len(res["documents"][0])):
                out.append({
                    "id": res["ids"][0][i],
                    "doc": res["documents"][0][i],
                    "metadata": res["metadatas"][0][i],
                })
        return out

    def recent_records(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.papers_log.exists():
            return []
        out: List[Dict[str, Any]] = []
        try:
            with self.papers_log.open("r", encoding="utf-8") as f:
                lines = f.readlines()[-limit:]
            for ln in lines:
                try:
                    out.append(json.loads(ln))
                except Exception:
                    continue
        except Exception:
            pass
        return out

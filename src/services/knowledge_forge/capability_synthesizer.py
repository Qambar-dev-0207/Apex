import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

try:
    from google import genai
except Exception:
    genai = None


PROPOSAL_SCHEMA = """
{
  "title": "<=80 chars",
  "kind": "integrate_lib|adopt_paper_idea|new_tool|new_skill|refactor|benchmark",
  "source_refs": ["paper_id or eco_key", "..."],
  "target_files": ["src/...py or new module path"],
  "approach": "<=400 chars actionable plan",
  "rationale": "<=240 chars why APEX gains from this",
  "risk": "low|medium|high",
  "priority": 1,
  "estimated_effort_minutes": 30,
  "expected_capability_gain": "<=160 chars, what APEX can do after",
  "rollback_plan": "<=160 chars",
  "depends_on": ["pkg or skill or proposal_title"]
}
""".strip()


class CapabilitySynthesizer:
    """
    Bridges PaperReader + EcosystemWatcher output to actionable APEX patches.
    Always-queue mode: writes proposals to data/forge/proposals.json — never
    auto-applies. The user reviews via /forge proposals and approves manually.
    """

    def __init__(self, data_dir: str = "data/forge", console=None,
                 codebase_root: str = "src",
                 max_proposals_per_cycle: int = 8):
        load_dotenv()
        self.console = console
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.proposals_path = self.data_dir / "proposals.json"
        self.codebase_root = codebase_root
        self.max_per_cycle = max_proposals_per_cycle

        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if (genai and api_key) else None
        self.model_id = "gemini-3.5-flash"

    # ---------- helpers ----------

    def _log(self, msg: str, level: str = "info"):
        if not self.console:
            return
        color = {"info": "magenta", "warn": "yellow", "err": "red"}.get(level, "white")
        self.console.print(f"[dim {color}][Synth] {msg}[/dim {color}]")

    def _load_proposals(self) -> List[Dict[str, Any]]:
        if not self.proposals_path.exists():
            return []
        try:
            return json.loads(self.proposals_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_proposals(self, proposals: List[Dict[str, Any]]):
        try:
            self.proposals_path.write_text(json.dumps(proposals, indent=2), encoding="utf-8")
        except Exception as e:
            self._log(f"persist fail: {e}", level="warn")

    def _load_compass_summary(self) -> Optional[Dict[str, Any]]:
        cp = Path(".apex/code_compass.json")
        if not cp.exists():
            return None
        try:
            data = json.loads(cp.read_text(encoding="utf-8"))
            mods = list(data.get("modules", {}).keys())[:80]
            return {"modules": mods, "stats": data.get("stats", {})}
        except Exception:
            return None

    # ---------- synthesis ----------

    async def synthesize(self,
                         papers: List[Dict[str, Any]],
                         eco_items: List[Dict[str, Any]],
                         existing_modules_hint: Optional[List[str]] = None
                         ) -> List[Dict[str, Any]]:
        if not self.client:
            return self._heuristic(papers, eco_items)

        compass = self._load_compass_summary() or {}
        modules = existing_modules_hint or compass.get("modules", [])

        condensed_papers = [
            {
                "id": p.get("id"),
                "title": p.get("title", "")[:160],
                "tldr": (p.get("deep") or {}).get("tldr", "")[:300],
                "novel": (p.get("deep") or {}).get("novel_idea", "")[:200],
                "approach": (p.get("deep") or {}).get("apex_integration", {}).get("approach", "")[:240],
                "target_hint": (p.get("deep") or {}).get("apex_integration", {}).get("target_file_hint", ""),
                "risk": (p.get("deep") or {}).get("apex_integration", {}).get("risk", "medium"),
                "applicability": (p.get("score") or {}).get("applicability", 0),
            }
            for p in papers
            if (p.get("score") or {}).get("applicability", 0) >= 0.5
        ][:14]

        condensed_eco = [
            {
                "key": it.get("key"),
                "src": it.get("source"),
                "title": it.get("title", "")[:120],
                "summary": it.get("summary", "")[:200],
                "domain": it.get("domain", "other"),
                "relevance": it.get("relevance", 0),
            }
            for it in eco_items
            if it.get("relevance", 0) >= 0.5
        ][:20]

        if not condensed_papers and not condensed_eco:
            return []

        prompt = f"""
You are APEX's chief architect. Convert recent research + ecosystem updates
into concrete, queue-ready capability proposals for the APEX codebase.

APEX EXISTING MODULES (subset):
{json.dumps(modules, ensure_ascii=False)[:3000]}

RECENT APPLICABLE PAPERS:
{json.dumps(condensed_papers, ensure_ascii=False)[:6000]}

RECENT APPLICABLE ECOSYSTEM ITEMS:
{json.dumps(condensed_eco, ensure_ascii=False)[:6000]}

RULES:
- Output {self.max_per_cycle} or fewer proposals, ranked by leverage.
- Each must be CONCRETE (file path, action verb, integration hook).
- Prefer extending existing modules to creating new ones.
- Avoid duplicates of already-pending proposals.
- Reject anything that needs paid services or non-trivial infra.
- If a paper and an ecosystem item solve the same gap, fold them together.
- For "kind=new_tool" use src/tools/<name>.py; for new services src/services/.
- Rollback plan: how to revert if it degrades benchmark scores.

Output JSON list of proposals using this schema per item:
{PROPOSAL_SCHEMA}
""".strip()

        try:
            res = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            raw = json.loads(res.text)
        except Exception as e:
            self._log(f"gemini fail: {e}", level="warn")
            return self._heuristic(papers, eco_items)

        proposals = raw if isinstance(raw, list) else raw.get("proposals", [])
        ts = datetime.now().isoformat()
        for p in proposals:
            p["id"] = self._mk_id(p)
            p["created_at"] = ts
            p["status"] = "queued"
        return proposals[: self.max_per_cycle]

    def _heuristic(self, papers: List[Dict[str, Any]], eco: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for p in papers[:3]:
            deep = p.get("deep") or {}
            integ = deep.get("apex_integration", {})
            out.append({
                "title": f"Adopt: {p.get('title', '')[:60]}",
                "kind": "adopt_paper_idea",
                "source_refs": [p.get("id", "")],
                "target_files": [integ.get("target_file_hint", "src/services/")],
                "approach": integ.get("approach", deep.get("tldr", ""))[:400],
                "rationale": deep.get("novel_idea", "")[:240],
                "risk": integ.get("risk", "medium"),
                "priority": 3,
                "estimated_effort_minutes": int(integ.get("effort_minutes", 60) or 60),
                "expected_capability_gain": deep.get("tldr", "")[:160],
                "rollback_plan": "git revert proposal commit; re-run /forge bench to compare.",
                "depends_on": [],
                "status": "queued",
                "created_at": datetime.now().isoformat(),
            })
            out[-1]["id"] = self._mk_id(out[-1])
        for it in eco[:3]:
            out.append({
                "title": f"Integrate: {it.get('title', '')[:60]}",
                "kind": "integrate_lib",
                "source_refs": [it.get("key", "")],
                "target_files": ["src/tools/" if it.get("source", "").startswith("pypi") else "src/services/"],
                "approach": f"Evaluate {it.get('title', '')} for {it.get('domain', 'other')} use; wire as optional dep.",
                "rationale": it.get("why", "")[:240],
                "risk": "medium",
                "priority": 4,
                "estimated_effort_minutes": 45,
                "expected_capability_gain": it.get("summary", "")[:160],
                "rollback_plan": "Remove dep; revert wiring commit.",
                "depends_on": [],
                "status": "queued",
                "created_at": datetime.now().isoformat(),
            })
            out[-1]["id"] = self._mk_id(out[-1])
        return out[: self.max_per_cycle]

    def _mk_id(self, prop: Dict[str, Any]) -> str:
        import hashlib
        seed = (prop.get("title", "") + "|" + ",".join(prop.get("source_refs", []) or []))
        return "fp_" + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:10]

    # ---------- queue ops ----------

    def enqueue(self, proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        existing = self._load_proposals()
        existing_ids = {p.get("id") for p in existing}
        added = []
        for p in proposals:
            if p.get("id") in existing_ids:
                continue
            existing.append(p)
            added.append(p)
        existing = existing[-200:]
        self._save_proposals(existing)
        return {"added": len(added), "total_queued": len([p for p in existing if p.get("status") == "queued"])}

    def list_queued(self, limit: int = 25) -> List[Dict[str, Any]]:
        return [p for p in self._load_proposals() if p.get("status") == "queued"][-limit:]

    def update_status(self, proposal_id: str, status: str, note: str = "") -> bool:
        proposals = self._load_proposals()
        for p in proposals:
            if p.get("id") == proposal_id:
                p["status"] = status
                p["updated_at"] = datetime.now().isoformat()
                if note:
                    p["note"] = note
                self._save_proposals(proposals)
                return True
        return False

    def find(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        for p in self._load_proposals():
            if p.get("id") == proposal_id:
                return p
        return None

import os
import json
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

from .paper_reader import PaperReader
from .ecosystem_watcher import EcosystemWatcher
from .capability_synthesizer import CapabilitySynthesizer
from .benchmark_self import SelfBenchmark
from .proposal_applier import ProposalApplier


class KnowledgeForge:
    """
    APEX's research+ecosystem learning loop.

    Components:
      - PaperReader: arxiv ingestion + Gemini summarization
      - EcosystemWatcher: PyPI/GitHub/HF/HN/npm scanner
      - CapabilitySynthesizer: turns intake into queued APEX patches
      - SelfBenchmark: tracks coding pass-rate to detect regressions

    Always-queue mode: proposals never auto-apply; user reviews via
    /forge proposals and chooses to act. Background loop runs daily when
    APEX is idle and hardware is not under load.
    """

    def __init__(self, hw_monitor=None, console=None, hooks=None,
                 data_dir: str = "data/forge",
                 codebase_root: str = "src",
                 project_root: str = ".",
                 categories: Optional[List[str]] = None,
                 daily_interval_hours: float = 24.0):
        self.console = console
        self.hw = hw_monitor
        self.hooks = hooks
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # per-project state lives in .apex/ so each workspace has its own cycle clock
        apex_dir = Path(project_root) / ".apex"
        apex_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = apex_dir / "forge_state.json"
        self.forge_log_path = Path.home() / ".apex" / "forge_log.md"
        self.daily_interval = timedelta(hours=daily_interval_hours)
        self.project_root = project_root

        self.paper_reader = PaperReader(data_dir=str(self.data_dir), console=console, categories=categories)
        self.eco_watcher = EcosystemWatcher(data_dir=str(self.data_dir), console=console)
        self.synthesizer = CapabilitySynthesizer(data_dir=str(self.data_dir), console=console,
                                                 codebase_root=codebase_root)
        self.bench = SelfBenchmark(data_dir=str(self.data_dir), console=console)
        self.applier = ProposalApplier(self.synthesizer, self.bench, console=console,
                                       codebase_root=project_root)

        self.last_input_time = time.time()
        self._running = False
        self._missing_key_warned = False
        if not os.getenv("GEMINI_API_KEY"):
            self._log("GEMINI_API_KEY missing — Forge synth/applier will degrade", level="warn")
            self._missing_key_warned = True

    # ---------- helpers ----------

    def _log(self, msg: str, level: str = "info"):
        if not self.console:
            return
        color = {"info": "bright_cyan", "warn": "yellow", "err": "red"}.get(level, "white")
        self.console.print(f"[bold {color}][Forge] {msg}[/bold {color}]")

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

    def mark_input(self):
        self.last_input_time = time.time()

    def _is_idle(self, threshold_sec: int = 600) -> bool:
        return (time.time() - self.last_input_time) > threshold_sec

    def _hw_ok(self) -> bool:
        if not self.hw:
            return True
        try:
            v = self.hw.get_vitals()
            return v.status != "critical"
        except Exception:
            return True

    def _write_forge_log(self, summary: Dict[str, Any]):
        try:
            self.forge_log_path.parent.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            line = (
                f"## {ts}\n"
                f"papers new={summary.get('papers_new', 0)} applicable={summary.get('papers_applicable', 0)} | "
                f"eco new={summary.get('eco_new', 0)} applicable={summary.get('eco_applicable', 0)} | "
                f"proposals added={summary.get('proposals_added', 0)} queued={summary.get('proposals_total_queued', 0)} | "
                f"regression={summary.get('regression', False)}\n\n"
            )
            with self.forge_log_path.open("a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            self._log(f"forge_log write fail: {e}", level="warn")

    def read_forge_log(self, n: int = 30) -> str:
        if not self.forge_log_path.exists():
            return "(no forge log yet — runs after first /forge cycle)"
        try:
            text = self.forge_log_path.read_text(encoding="utf-8")
            # return last n sections (each section ~2 lines)
            lines = text.splitlines()
            return "\n".join(lines[-(n * 3):]).strip() or "(empty log)"
        except Exception as e:
            return f"(log read error: {e})"

    # ---------- public ops ----------

    async def run_backfill(self, days: int = 7) -> Dict[str, Any]:
        res = await self.paper_reader.scan_backfill(days=days)
        for p in res.get("applicable", []):
            await self._fire_hook("ApexPaperFound", {
                "id": p.get("id"), "title": p.get("title"),
                "applicability": (p.get("score") or {}).get("applicability", 0),
            })
        return res

    async def run_papers(self, max_total: int = 12) -> Dict[str, Any]:
        res = await self.paper_reader.scan(max_per_category=6, max_total=max_total)
        for p in res.get("applicable", []):
            await self._fire_hook("ApexPaperFound", {
                "id": p.get("id"), "title": p.get("title"),
                "applicability": (p.get("score") or {}).get("applicability", 0),
            })
        return res

    async def run_ecosystem(self) -> Dict[str, Any]:
        res = await self.eco_watcher.scan()
        if res.get("applicable_count", 0) > 0:
            await self._fire_hook("ApexEcosystemNew", {
                "count": res["applicable_count"],
                "top": [(x.get("title"), x.get("relevance")) for x in res.get("applicable", [])[:5]],
            })
        return res

    async def run_synthesis(self) -> Dict[str, Any]:
        papers = self.paper_reader.recent_records(limit=25)
        eco = self.eco_watcher.recent_applicable(limit=40)
        proposals = await self.synthesizer.synthesize(papers, eco)
        if not proposals:
            return {"added": 0, "total_queued": 0, "proposals": []}
        info = self.synthesizer.enqueue(proposals)
        info["proposals"] = proposals
        if info.get("added", 0) > 0:
            await self._fire_hook("ForgeProposalAdded", {
                "added": info["added"], "total_queued": info.get("total_queued", 0),
                "titles": [p.get("title") for p in proposals[:5]],
            })
        return info

    async def run_bench(self) -> Dict[str, Any]:
        record = await self.bench.run()
        reg = self.bench.regression_check()
        record["regression_check"] = reg
        if reg.get("regression"):
            self._log(f"REGRESSION DETECTED: {reg['details']}", level="err")
        return record

    async def _fire_hook(self, event: str, payload: Dict[str, Any]):
        if not self.hooks:
            return
        try:
            await self.hooks.fire(event, payload)
        except Exception as e:
            self._log(f"hook {event} fail: {e}", level="warn")

    async def run_full_cycle(self, do_bench: bool = True) -> Dict[str, Any]:
        if self._running:
            return {"skipped": "already_running"}
        if not self._hw_ok():
            return {"skipped": "hw_critical"}
        self._running = True
        ts = datetime.now().isoformat()
        await self._fire_hook("ForgeCycleStart", {"ts": ts})
        try:
            self._log("CYCLE START", level="info")

            self._log("step 1/4 — papers", level="info")
            papers_res = await self.run_papers()

            self._log("step 2/4 — ecosystem", level="info")
            eco_res = await self.run_ecosystem()

            self._log("step 3/4 — synthesis", level="info")
            synth_res = await self.run_synthesis()

            bench_res: Dict[str, Any] = {"skipped": "disabled"}
            if do_bench:
                self._log("step 4/4 — benchmark", level="info")
                bench_res = await self.run_bench()

            state = self._load_state()
            state["last_cycle"] = ts
            state["last_summary"] = {
                "papers_new": papers_res.get("new_count", 0),
                "papers_applicable": papers_res.get("applicable_count", 0),
                "eco_new": eco_res.get("new_count", 0),
                "eco_applicable": eco_res.get("applicable_count", 0),
                "proposals_added": synth_res.get("added", 0),
                "proposals_total_queued": synth_res.get("total_queued", 0),
                "bench_summary": bench_res.get("summary", {}),
                "regression": (bench_res.get("regression_check") or {}).get("regression", False),
            }
            self._save_state(state)
            self._log(f"CYCLE DONE: {state['last_summary']}", level="info")
            self._write_forge_log(state["last_summary"])
            await self._fire_hook("ForgeCycleDone", {"ts": ts, "summary": state["last_summary"]})
            return {
                "ts": ts,
                "papers": papers_res,
                "ecosystem": eco_res,
                "synthesis": synth_res,
                "bench": bench_res,
            }
        finally:
            self._running = False

    # ---------- background ----------

    def _due_for_cycle(self) -> bool:
        state = self._load_state()
        last = state.get("last_cycle")
        if not last:
            return True
        try:
            last_dt = datetime.fromisoformat(last)
        except Exception:
            return True
        return datetime.now() - last_dt >= self.daily_interval

    async def background_loop(self, idle_threshold: int = 600, sleep_interval: int = 120):
        """
        Long-running task. Runs full cycle once per `daily_interval_hours`
        when system is idle. Reads `mark_input` to avoid disturbing active sessions.
        """
        while True:
            try:
                await asyncio.sleep(sleep_interval)
                if not self._is_idle(idle_threshold):
                    continue
                if not self._due_for_cycle():
                    continue
                if not self._hw_ok():
                    continue
                self._log("idle + due — running auto cycle", level="info")
                await self.run_full_cycle(do_bench=True)
            except asyncio.CancelledError:
                return
            except Exception as e:
                self._log(f"loop error: {e}", level="err")

    # ---------- queries ----------

    def search_papers(self, query: str, n: int = 5) -> List[Dict[str, Any]]:
        return self.paper_reader.search_papers(query, n_results=n)

    def list_proposals(self, limit: int = 25) -> List[Dict[str, Any]]:
        return self.synthesizer.list_queued(limit=limit)

    def list_approved(self, limit: int = 25) -> List[Dict[str, Any]]:
        return [p for p in self.synthesizer._load_proposals() if p.get("status") == "approved"][-limit:]

    def update_proposal(self, proposal_id: str, status: str, note: str = "") -> bool:
        return self.synthesizer.update_status(proposal_id, status, note)

    async def apply_proposal(self, proposal_id: str, gate_with_bench: bool = True,
                              use_diff: bool = False) -> Dict[str, Any]:
        res = await self.applier.apply(proposal_id, gate_with_bench=gate_with_bench,
                                       use_diff=use_diff)
        if res.get("ok"):
            await self._fire_hook("ForgeApplied", {"id": proposal_id, "files": len(res.get("applied", []))})
        elif res.get("rolled_back"):
            await self._fire_hook("ForgeRolledBack", {"id": proposal_id, "reason": res.get("error", "")})
        return res

    def briefing_digest(self) -> Dict[str, Any]:
        state = self._load_state()
        summary = state.get("last_summary", {})
        approved = self.list_approved(limit=10)
        queued = self.list_proposals(limit=10)
        return {
            "last_cycle": state.get("last_cycle"),
            "papers_applicable": summary.get("papers_applicable", 0),
            "eco_applicable": summary.get("eco_applicable", 0),
            "proposals_queued": len(queued),
            "proposals_approved_pending_apply": len(approved),
            "regression": summary.get("regression", False),
        }

    def status_summary(self) -> Dict[str, Any]:
        state = self._load_state()
        queued = self.list_proposals(limit=200)
        return {
            "last_cycle": state.get("last_cycle"),
            "last_summary": state.get("last_summary", {}),
            "queued_proposals": len(queued),
            "categories": self.paper_reader.categories,
            "gh_languages": self.eco_watcher.gh_languages,
        }

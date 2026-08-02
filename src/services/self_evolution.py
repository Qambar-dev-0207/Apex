import os
import ast
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv

try:
    from google import genai
except Exception:
    genai = None


class SelfEvolver:
    """
    Autonomous self-improvement engine.
    When the system is idle, scans APEX's own codebase for:
      - Functions exceeding complexity thresholds
      - TODO / FIXME comments
      - Missing docstrings on public APIs
      - Skill registry gaps vs project goals
    Then proposes (and optionally auto-applies) improvements.
    """

    def __init__(self, workspace, learning_manager, provisioner, hw_monitor, console=None,
                 forge=None):
        load_dotenv()
        self.workspace = workspace
        self.learning = learning_manager
        self.provisioner = provisioner
        self.hw = hw_monitor
        self.console = console
        self.forge = forge
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if (genai and api_key) else None
        self.model_id = "gemini-3.5-flash"
        self.fallback_models = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-1.5-flash"]

        self.apex_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.last_input_time = time.time()
        self.last_cycle_time = 0.0
        self.cycle_log: List[Dict[str, Any]] = []
        self.proposals_path = Path("data/self_evolution.json")
        self.proposals_path.parent.mkdir(parents=True, exist_ok=True)
        self._running = False

    def mark_input(self):
        """Reset idle timer (called from main loop on every user input)."""
        self.last_input_time = time.time()

    def is_idle(self, threshold_sec: int = 300) -> bool:
        return (time.time() - self.last_input_time) > threshold_sec

    def _scan_python_file(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                src = f.read()
            tree = ast.parse(src, filename=path)
        except Exception as e:
            return {"path": path, "error": str(e)}

        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Cyclomatic complexity proxy: branch-count
                branches = sum(
                    1 for n in ast.walk(node)
                    if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.BoolOp))
                )
                if branches > 12:
                    issues.append({
                        "kind": "complexity",
                        "symbol": node.name,
                        "line": node.lineno,
                        "branches": branches,
                    })
                if not (node.name.startswith("_")) and not ast.get_docstring(node):
                    body_size = sum(1 for _ in ast.walk(node))
                    if body_size > 8:
                        issues.append({
                            "kind": "missing_docstring",
                            "symbol": node.name,
                            "line": node.lineno,
                        })

        # TODO scan
        for i, line in enumerate(src.splitlines(), 1):
            ls = line.strip()
            if "TODO" in ls or "FIXME" in ls or "HACK" in ls:
                issues.append({"kind": "todo", "line": i, "text": ls[:200]})

        return {"path": path, "issues": issues}

    def analyze_self(self, src_root: str = "src") -> Dict[str, Any]:
        """Walk APEX's own src/ directory and produce a compact issue report."""
        if not os.path.isabs(src_root):
            src_root = os.path.join(self.apex_root, src_root)
        report = {"timestamp": datetime.now().isoformat(), "files": [], "totals": {}}
        if not os.path.isdir(src_root):
            return report

        totals = {"complexity": 0, "missing_docstring": 0, "todo": 0}
        for root, _, files in os.walk(src_root):
            if "__pycache__" in root:
                continue
            for f in files:
                if not f.endswith(".py"):
                    continue
                path = os.path.join(root, f)
                file_report = self._scan_python_file(path)
                if file_report.get("issues"):
                    report["files"].append(file_report)
                    for issue in file_report["issues"]:
                        kind = issue.get("kind", "other")
                        totals[kind] = totals.get(kind, 0) + 1
        report["totals"] = totals
        return report

    async def propose_improvements(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ask Gemini for actionable proposals based on the report."""
        if not self.client:
            return self._heuristic_proposals(report)

        condensed = {
            "totals": report["totals"],
            "top_files": [
                {"path": f["path"], "issue_count": len(f["issues"])}
                for f in report["files"][:15]
            ],
            "samples": [f["issues"][:3] for f in report["files"][:5]],
        }
        prompt = f"""
        IDENT: APEX // SELF-EVOLUTION SUBROUTINE
        ROLE: Architect reviewing its own implementation.
        TASK: Generate 3-5 high-leverage improvement proposals based on the static-analysis report below.
        Each proposal must be CONCRETE (file path, action verb, expected gain).

        REPORT:
        {json.dumps(condensed, indent=2)}

        Output JSON list:
        [
          {{
            "title": "...",
            "target_file": "src/path.py",
            "action": "refactor|test|document|provision_skill|provision_mcp",
            "rationale": "why this matters",
            "priority": 1-5,
            "estimated_token_savings": int,
            "estimated_effort_minutes": int
          }}
        ]
        """
        for model_name in self.fallback_models:
            try:
                res = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"},
                )
                if res and res.text:
                    return json.loads(res.text)
            except Exception as e:
                if self.console:
                    self.console.print(f"[dim red][SelfEvolver] Model {model_name} failed: {e}[/dim red]")

        return self._heuristic_proposals(report)

    def _heuristic_proposals(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for fr in report["files"][:5]:
            for issue in fr["issues"][:1]:
                out.append({
                    "title": f"{issue['kind']} in {os.path.basename(fr['path'])}",
                    "target_file": fr["path"],
                    "action": "refactor" if issue["kind"] == "complexity" else "document",
                    "rationale": f"Static analysis flagged {issue['kind']} at line {issue.get('line', '?')}",
                    "priority": 3,
                    "estimated_token_savings": 0,
                    "estimated_effort_minutes": 15,
                })
        return out

    def persist(self, report: Dict[str, Any], proposals: List[Dict[str, Any]]):
        try:
            existing = []
            if self.proposals_path.exists():
                existing = json.loads(self.proposals_path.read_text(encoding="utf-8"))
            existing.append({"report": report, "proposals": proposals, "ts": datetime.now().isoformat()})
            existing = existing[-25:]
            self.proposals_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        except Exception as e:
            if self.console:
                self.console.print(f"[dim red][SelfEvolver] Persist failed: {e}[/dim red]")

    async def run_cycle(self, src_root: str = "src", auto_provision: bool = False) -> Dict[str, Any]:
        """Single evolution pass. Returns the result for inspection."""
        if self._running:
            return {"skipped": "already_running"}
        self._running = True
        self.last_cycle_time = time.time()
        try:
            # Hardware gate: don't evolve if system is busy
            try:
                vitals = self.hw.get_vitals()
                if vitals.status == "critical":
                    return {"skipped": "hw_critical"}
            except Exception:
                pass

            report = self.analyze_self(src_root)
            proposals = await self.propose_improvements(report)

            # Bridge: pull approved-but-not-yet-applied Forge proposals so they
            # surface in /evolve as well.
            if self.forge:
                try:
                    forge_approved = self.forge.list_approved(limit=10)
                    for fp in forge_approved:
                        proposals.append({
                            "title": f"[FORGE] {fp.get('title', '')[:60]}",
                            "target_file": (fp.get("target_files") or [""])[0],
                            "action": "forge_apply",
                            "rationale": fp.get("rationale", "")[:200],
                            "priority": int(fp.get("priority", 3) or 3),
                            "estimated_token_savings": 0,
                            "estimated_effort_minutes": int(fp.get("estimated_effort_minutes", 30) or 30),
                            "forge_id": fp.get("id"),
                        })
                except Exception as e:
                    if self.console:
                        self.console.print(f"[dim red][SelfEvolver] forge bridge fail: {e}[/dim red]")

            self.persist(report, proposals)

            if auto_provision and self.provisioner:
                active = self.workspace.get_active() if self.workspace else None
                if active:
                    try:
                        gaps = await self.provisioner.analyze_project_gaps(active.name)
                        for gap in gaps[:1]:
                            if gap.type == "skill":
                                await self.provisioner.provision_skill(gap)
                    except Exception as e:
                        if self.console:
                            self.console.print(f"[dim red][SelfEvolver] Auto-provision failed: {e}[/dim red]")

            # Queue interrupt for high priority proposals
            high_pri = [p for p in proposals if int(p.get("priority", 3) or 3) >= 4]
            if high_pri and hasattr(self, "engine") and self.engine and self.engine.interrupt_queue:
                top = high_pri[0]
                self.engine.interrupt_queue.put_nowait({
                    "source": "SelfEvolver",
                    "message": f"Critical self-evolution proposal generated: '{top.get('title')}' targeting '{top.get('target_file')}' (Priority {top.get('priority')}). Rationale: {top.get('rationale')}. Should we execute?"
                })

            cycle = {"ts": datetime.now().isoformat(), "totals": report["totals"], "proposals": len(proposals)}
            self.cycle_log.append(cycle)
            self.cycle_log = self.cycle_log[-20:]
            return {"report": report, "proposals": proposals}
        finally:
            self._running = False

    async def background_loop(self, idle_threshold: int = 300, sleep_interval: int = 60):
        """Long-running task. Fires evolution cycle when system is idle."""
        while True:
            try:
                await asyncio.sleep(sleep_interval)
                if not self.is_idle(idle_threshold):
                    continue
                if time.time() - self.last_cycle_time < 1800:  # at most every 30 min
                    continue
                await self.run_cycle()
            except asyncio.CancelledError:
                return
            except Exception:
                pass

    async def apply_proposal(self, proposal: Dict[str, Any], engine=None) -> Dict[str, Any]:
        """Execute a self-evolution proposal against APEX's own system codebase root."""
        target_file = proposal.get("target_file", "")
        action = proposal.get("action", "refactor")
        rationale = proposal.get("rationale", "")
        title = proposal.get("title", proposal.get("action", "evolution"))

        eng = engine or getattr(self, "engine", None)
        if not eng or not hasattr(eng, "harness"):
            return {"success": False, "error": "harness engine not wired to SelfEvolver"}

        harness_goal = f"""APEX SYSTEM SELF-EVOLUTION:
Target APEX System File: {target_file}
Action: {action}
Goal: {title}
Rationale: {rationale}

Execute the necessary refactoring/code update on APEX's internal codebase maintaining full functionality and clean structure."""

        # Ensure harness executes in APEX's own codebase root, not user project root
        orig_root = eng.harness.project_root
        eng.harness.project_root = self.apex_root
        try:
            from main import dispatch_harness
            res = await dispatch_harness(eng, self.console, harness_goal, trigger="self_evolution")
            return res
        finally:
            eng.harness.project_root = orig_root  # background errors are silent

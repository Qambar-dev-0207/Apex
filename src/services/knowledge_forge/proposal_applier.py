import os
import re
import sys
import shutil
import json
import asyncio
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from dotenv import load_dotenv

try:
    from google import genai
except Exception:
    genai = None


CODE_FENCE_RE = re.compile(r"```(?:[\w+-]+)?\s*(.*?)```", re.DOTALL)
# Search-replace block: <<<SEARCH ... ===REPLACE ... >>>
SR_BLOCK_RE = re.compile(
    r"<<<SEARCH\n(.*?)\n===REPLACE\n(.*?)\n>>>",
    re.DOTALL,
)


def _extract_code(text: str) -> str:
    if not text:
        return ""
    m = CODE_FENCE_RE.search(text)
    return (m.group(1) if m else text).strip()


def _apply_sr_blocks(original: str, blocks: List[Tuple[str, str]]) -> Tuple[str, List[str]]:
    result = original
    errors = []
    for i, (search, replace) in enumerate(blocks):
        if search not in result:
            errors.append(f"block {i}: search string not found")
            continue
        result = result.replace(search, replace, 1)
    return result, errors


class PipSandbox:
    """
    Installs dependencies into a temporary venv, validates import, then
    prompts user before installing to the active Python environment.
    """

    def __init__(self, venvs_dir: str = "data/forge/venvs", console=None):
        self.venvs_dir = Path(venvs_dir)
        self.venvs_dir.mkdir(parents=True, exist_ok=True)
        self.console = console

    def _log(self, msg: str, level: str = "info"):
        if not self.console:
            return
        color = {"info": "cyan", "warn": "yellow", "err": "red", "ok": "green"}.get(level, "white")
        self.console.print(f"[dim {color}][PipSandbox] {msg}[/dim {color}]")

    def _venv_python(self, venv_path: Path) -> str:
        if sys.platform == "win32":
            return str(venv_path / "Scripts" / "python.exe")
        return str(venv_path / "bin" / "python")

    async def _run(self, cmd: List[str], timeout: float = 120) -> Tuple[int, str, str]:
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                return proc.returncode, stdout.decode("utf-8", errors="ignore"), stderr.decode("utf-8", errors="ignore")
            except asyncio.TimeoutError:
                proc.kill()
                return -1, "", "TIMEOUT"
        except Exception as e:
            return -2, "", str(e)

    async def test_install(self, packages: List[str], proposal_id: str) -> Dict[str, Any]:
        venv_path = self.venvs_dir / proposal_id
        if venv_path.exists():
            shutil.rmtree(venv_path, ignore_errors=True)

        self._log(f"creating sandbox venv for {proposal_id}", level="info")
        rc, _, err = await self._run([sys.executable, "-m", "venv", str(venv_path)])
        if rc != 0:
            return {"ok": False, "error": f"venv create fail: {err[:400]}"}

        python = self._venv_python(venv_path)
        failed = []
        installed = []
        for pkg in packages:
            self._log(f"sandbox install: {pkg}", level="info")
            rc, out, err = await self._run([python, "-m", "pip", "install", pkg, "--quiet"], timeout=180)
            if rc != 0:
                failed.append({"pkg": pkg, "error": (err or out)[:300]})
            else:
                installed.append(pkg)

        import_results = {}
        for pkg in installed:
            mod = pkg.split("[")[0].replace("-", "_").lower()
            rc, _, _ = await self._run([python, "-c", f"import {mod}"])
            import_results[pkg] = rc == 0

        return {
            "ok": not failed,
            "installed": installed,
            "failed": failed,
            "import_ok": import_results,
            "venv_path": str(venv_path),
        }

    async def install_to_active_env(self, packages: List[str]) -> Dict[str, Any]:
        failed = []
        installed = []
        for pkg in packages:
            self._log(f"installing to active env: {pkg}", level="info")
            rc, out, err = await self._run(
                [sys.executable, "-m", "pip", "install", pkg, "--quiet"], timeout=180
            )
            if rc != 0:
                failed.append({"pkg": pkg, "error": (err or out)[:300]})
            else:
                installed.append(pkg)
        return {"ok": not failed, "installed": installed, "failed": failed}

    def cleanup_venv(self, proposal_id: str):
        venv_path = self.venvs_dir / proposal_id
        if venv_path.exists():
            shutil.rmtree(venv_path, ignore_errors=True)


class ProposalApplier:
    """
    Applies an approved capability proposal to the APEX codebase.

    Two modes:
      - Full rewrite (default): Gemini generates full new file contents.
      - Diff mode: Gemini generates search-replace blocks; safer for large files.

    Both modes:
      - Backup target files before writing.
      - AST-validate Python files before applying.
      - Pre/post benchmark with auto-rollback on regression >= threshold.
      - Sandbox pip-install any new `depends_on` packages before applying.
    """

    def __init__(self, synthesizer, bench, console=None,
                 codebase_root: str = ".", backups_dir: str = "data/forge/backups"):
        load_dotenv()
        self.synth = synthesizer
        self.bench = bench
        self.console = console
        self.codebase_root = Path(codebase_root).resolve()
        self.backups_dir = Path(backups_dir)
        self.backups_dir.mkdir(parents=True, exist_ok=True)

        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if (genai and api_key) else None
        self.model_id = "gemini-2.5-flash"

        venvs_dir = str(Path(backups_dir).parent / "venvs")
        self.pip_sandbox = PipSandbox(venvs_dir=venvs_dir, console=console)

    # ---------- helpers ----------

    def _log(self, msg: str, level: str = "info"):
        if not self.console:
            return
        color = {"info": "magenta", "warn": "yellow", "err": "red", "ok": "green"}.get(level, "white")
        self.console.print(f"[bold {color}][Applier] {msg}[/bold {color}]")

    def _is_safe_path(self, target: Path) -> bool:
        try:
            target_resolved = target.resolve()
        except Exception:
            return False
        try:
            target_resolved.relative_to(self.codebase_root)
        except ValueError:
            return False
        forbidden = {".env", ".env.local", "credentials.json"}
        if target_resolved.name in forbidden:
            return False
        rel_parts = target_resolved.relative_to(self.codebase_root).parts
        if any(part.startswith(".") and part not in {".apex"} for part in rel_parts):
            return False
        return True

    def _backup(self, target: Path, proposal_id: str) -> Optional[Path]:
        if not target.exists():
            return None
        ts = datetime.now().strftime("%Y%m%dT%H%M%S")
        rel = target.resolve().relative_to(self.codebase_root)
        bdir = self.backups_dir / proposal_id / ts
        bdir.mkdir(parents=True, exist_ok=True)
        bpath = bdir / rel.as_posix().replace("/", "__")
        shutil.copy2(target, bpath)
        return bpath

    def _restore(self, target: Path, backup: Optional[Path], created_anew: bool):
        try:
            if created_anew and target.exists():
                target.unlink()
                return
            if backup and backup.exists():
                shutil.copy2(backup, target)
        except Exception as e:
            self._log(f"restore fail {target}: {e}", level="err")

    def prune_old_backups(self, keep_days: int = 14):
        """Remove backup dirs older than keep_days."""
        cutoff = datetime.now().timestamp() - keep_days * 86400
        for proposal_dir in self.backups_dir.iterdir():
            if not proposal_dir.is_dir():
                continue
            for ts_dir in list(proposal_dir.iterdir()):
                if ts_dir.is_dir() and ts_dir.stat().st_mtime < cutoff:
                    shutil.rmtree(ts_dir, ignore_errors=True)

    def list_backups(self, proposal_id: str) -> List[Dict[str, Any]]:
        bdir = self.backups_dir / proposal_id
        if not bdir.exists():
            return []
        out = []
        for ts_dir in sorted(bdir.iterdir(), reverse=True):
            if ts_dir.is_dir():
                files = [f.name for f in ts_dir.iterdir()]
                out.append({"ts": ts_dir.name, "files": files})
        return out

    def restore_backup(self, proposal_id: str, ts: Optional[str] = None) -> Dict[str, Any]:
        bdir = self.backups_dir / proposal_id
        if not bdir.exists():
            return {"ok": False, "error": "no_backups"}
        dirs = sorted(bdir.iterdir(), reverse=True)
        if not dirs:
            return {"ok": False, "error": "no_backup_dirs"}
        target_dir = dirs[0]
        if ts:
            for d in dirs:
                if d.name == ts:
                    target_dir = d
                    break
        restored = []
        for f in target_dir.iterdir():
            rel_path = f.name.replace("__", "/")
            target = self.codebase_root / rel_path
            shutil.copy2(f, target)
            restored.append(str(target))
        return {"ok": True, "restored": restored, "from_ts": target_dir.name}

    # ---------- code generation ----------

    async def _gen_full_file(self, target: Path, proposal: Dict[str, Any], existing: str) -> str:
        if not self.client:
            return ""
        prompt = f"""
You are APEX's code architect. Apply the approved proposal below by producing
the FULL new contents of the target file. Output ONLY the file contents in
ONE fenced code block.

PROPOSAL:
{json.dumps({k: proposal.get(k) for k in [
    'title', 'kind', 'approach', 'rationale', 'expected_capability_gain',
    'risk', 'depends_on', 'source_refs'
]}, indent=2)}

TARGET FILE: {target.as_posix()}
EXISTING CONTENT (truncated to 22000 chars; empty if new file):
{existing[:22000]}

CONSTRAINTS:
- Consistent with existing imports, naming, async patterns.
- Do not delete unrelated functionality already present.
- Do not introduce top-level dependencies not listed in `depends_on`.
- No TODO placeholders.
- Keep file under ~1200 lines.
""".strip()
        try:
            res = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=prompt,
            )
            return _extract_code(res.text or "")
        except Exception as e:
            self._log(f"gemini full-gen fail: {e}", level="err")
            return ""

    async def _gen_diff_blocks(self, target: Path, proposal: Dict[str, Any], existing: str) -> str:
        if not self.client:
            return ""
        prompt = f"""
You are APEX's code architect. Apply the approved proposal as targeted
search-replace edits. Output ONLY the edit blocks using this exact format
(repeat as needed):

<<<SEARCH
<exact original lines to find>
===REPLACE
<replacement lines>
>>>

PROPOSAL:
{json.dumps({k: proposal.get(k) for k in [
    'title', 'kind', 'approach', 'rationale', 'depends_on'
]}, indent=2)}

TARGET FILE: {target.as_posix()}
EXISTING CONTENT (truncated to 22000 chars):
{existing[:22000]}

RULES:
- SEARCH must be an exact substring of the existing content (whitespace-sensitive).
- Each block replaces exactly one occurrence.
- Do not include ```fences``` around the blocks.
- Prefer surgical edits over rewriting whole functions.
""".strip()
        try:
            res = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=prompt,
            )
            return res.text or ""
        except Exception as e:
            self._log(f"gemini diff-gen fail: {e}", level="err")
            return ""

    # ---------- pip sandbox ----------

    async def _handle_depends_on(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        deps = [d for d in (proposal.get("depends_on") or []) if d and not d.startswith("src/")]
        if not deps:
            return {"ok": True, "skipped": True}
        self._log(f"sandbox testing deps: {deps}", level="info")
        pid = proposal.get("id", "unknown")
        sandbox_result = await self.pip_sandbox.test_install(deps, pid)
        if not sandbox_result["ok"]:
            self._log(f"sandbox install failed: {sandbox_result['failed']}", level="err")
            return {"ok": False, "sandbox": sandbox_result}
        all_imports_ok = all(sandbox_result["import_ok"].values())
        if not all_imports_ok:
            bad = [k for k, v in sandbox_result["import_ok"].items() if not v]
            self._log(f"sandbox import fail for: {bad}", level="warn")
            return {"ok": False, "sandbox": sandbox_result, "error": f"import_fail:{bad}"}
        self._log(f"sandbox ok; installing {deps} to active env", level="ok")
        install_result = await self.pip_sandbox.install_to_active_env(deps)
        self.pip_sandbox.cleanup_venv(pid)
        return {"ok": install_result["ok"], "install": install_result, "sandbox": sandbox_result}

    # ---------- apply ----------

    async def apply(self, proposal_id: str, gate_with_bench: bool = True,
                    regression_drop_threshold: float = 0.15,
                    use_diff: bool = False) -> Dict[str, Any]:
        prop = self.synth.find(proposal_id)
        if not prop:
            return {"ok": False, "error": "proposal_not_found", "id": proposal_id}
        if prop.get("status") not in ("approved", "queued"):
            return {"ok": False, "error": f"bad_status:{prop.get('status')}", "id": proposal_id}
        if not self.client:
            return {"ok": False, "error": "no_gemini_key"}

        targets_raw = prop.get("target_files") or []
        targets: List[Path] = []
        for t in targets_raw:
            if not t:
                continue
            p = (self.codebase_root / t).resolve()
            if not self._is_safe_path(p):
                return {"ok": False, "error": f"unsafe_path:{t}"}
            targets.append(p)
        if not targets:
            return {"ok": False, "error": "no_target_files"}

        # Deps sandbox
        deps_result = await self._handle_depends_on(prop)
        if not deps_result.get("ok") and not deps_result.get("skipped"):
            self.synth.update_status(proposal_id, "apply_failed",
                                     note=f"dep_fail:{deps_result.get('error', '')[:200]}")
            return {"ok": False, "error": "dep_install_failed", "deps": deps_result}

        pre_bench: Dict[str, Any] = {}
        if gate_with_bench:
            self._log("pre-apply benchmark...", level="info")
            pre_bench = (await self.bench.run()).get("summary", {})

        applied: List[Dict[str, Any]] = []
        mode_used = "diff" if use_diff else "full"
        try:
            for target in targets:
                target.parent.mkdir(parents=True, exist_ok=True)
                created_anew = not target.exists()
                existing = ""
                backup_path: Optional[Path] = None
                if not created_anew:
                    existing = target.read_text(encoding="utf-8", errors="ignore")
                    backup_path = self._backup(target, proposal_id)

                rel = target.relative_to(self.codebase_root) if target.is_relative_to(self.codebase_root) else target
                self._log(f"generating ({mode_used}) {rel}", level="info")

                if use_diff and existing:
                    raw = await self._gen_diff_blocks(target, prop, existing)
                    blocks = SR_BLOCK_RE.findall(raw)
                    if not blocks:
                        self._log(f"no SR blocks found; falling back to full rewrite for {rel}", level="warn")
                        new_code = await self._gen_full_file(target, prop, existing)
                        mode_used = "full_fallback"
                    else:
                        new_code, sr_errors = _apply_sr_blocks(existing, blocks)
                        if sr_errors:
                            self._log(f"SR errors {sr_errors}; falling back to full rewrite", level="warn")
                            new_code = await self._gen_full_file(target, prop, existing)
                            mode_used = "full_fallback"
                else:
                    new_code = await self._gen_full_file(target, prop, existing)

                if not new_code:
                    raise RuntimeError(f"empty_codegen:{target}")
                if target.suffix == ".py":
                    import ast as _ast
                    try:
                        _ast.parse(new_code)
                    except SyntaxError as se:
                        raise RuntimeError(f"syntax_error:{target.name}:{se}")

                target.write_text(new_code, encoding="utf-8")
                applied.append({
                    "path": str(target),
                    "backup": str(backup_path) if backup_path else None,
                    "created_anew": created_anew,
                    "mode": mode_used,
                })
        except Exception as e:
            self._log(f"apply fail: {e}; rolling back", level="err")
            for a in applied:
                self._restore(Path(a["path"]),
                              Path(a["backup"]) if a["backup"] else None,
                              a["created_anew"])
            self.synth.update_status(proposal_id, "apply_failed", note=str(e)[:240])
            return {"ok": False, "error": str(e)[:240], "rolled_back": True}

        post_bench: Dict[str, Any] = {}
        regressed = False
        if gate_with_bench:
            self._log("post-apply benchmark...", level="info")
            post_bench = (await self.bench.run()).get("summary", {})
            for label, cur in post_bench.items():
                prev = pre_bench.get(label)
                if not prev:
                    continue
                if cur["pass_rate"] - prev["pass_rate"] <= -regression_drop_threshold:
                    regressed = True
                    self._log(f"REGRESSION {label}: {cur['pass_rate'] - prev['pass_rate']:+.3f}", level="err")
                    break

        if regressed:
            for a in applied:
                self._restore(Path(a["path"]),
                              Path(a["backup"]) if a["backup"] else None,
                              a["created_anew"])
            self.synth.update_status(proposal_id, "rolled_back", note="regression_above_threshold")
            return {
                "ok": False, "rolled_back": True, "regression": True,
                "pre_bench": pre_bench, "post_bench": post_bench, "applied": applied,
            }

        self.prune_old_backups(keep_days=14)
        self.synth.update_status(proposal_id, "applied", note=f"{len(applied)} file(s) mode={mode_used}")
        return {
            "ok": True, "applied": applied, "mode": mode_used,
            "pre_bench": pre_bench, "post_bench": post_bench, "regression": False,
            "deps": deps_result,
        }

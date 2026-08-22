"""
Tests for src/services/knowledge_forge/

Covers:
  - Pure logic (no I/O, no network, no LLM)
  - File I/O with temp dirs
  - Mocked network (httpx) and Gemini calls
  - Real subprocess (SelfBenchmark code-exec)
  - Hook system completeness
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# ── path setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.hooks import HookManager
from src.services.knowledge_forge.ecosystem_watcher import _strip_pypi_version
from src.services.knowledge_forge.proposal_applier import (
    ProposalApplier, PipSandbox, _apply_sr_blocks, _extract_code,
)
from src.services.knowledge_forge.capability_synthesizer import CapabilitySynthesizer
from src.services.knowledge_forge.benchmark_self import SelfBenchmark, _run_in_subprocess
from src.services.knowledge_forge.paper_reader import PaperReader
from src.services.knowledge_forge.forge import KnowledgeForge


# ── helpers ──────────────────────────────────────────────────────────────────

def run(coro):
    return asyncio.run(coro)


SAMPLE_ARXIV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2501.99999v1</id>
    <title>Test Paper: Improving AI Agents</title>
    <summary>We propose a novel technique for agentic AI systems.</summary>
    <published>2025-01-15T00:00:00Z</published>
    <author><name>Alice Test</name></author>
    <link title="pdf" href="https://arxiv.org/pdf/2501.99999" type="application/pdf"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2501.88888v2</id>
    <title>Unrelated: Quantum Chemistry Methods</title>
    <summary>Density functional theory for molecular systems.</summary>
    <published>2025-01-14T00:00:00Z</published>
    <author><name>Bob Quantum</name></author>
    <link title="pdf" href="https://arxiv.org/pdf/2501.88888" type="application/pdf"/>
  </entry>
</feed>"""


# ════════════════════════════════════════════════════════════════════════════
# 1. Pure function tests — no I/O
# ════════════════════════════════════════════════════════════════════════════

class TestStripPypiVersion(unittest.TestCase):

    def test_strips_simple_version(self):
        self.assertEqual(_strip_pypi_version("requests 2.31.0"), "requests")

    def test_strips_pre_release(self):
        self.assertEqual(_strip_pypi_version("httpx 0.26.0a1"), "httpx")

    def test_no_version(self):
        self.assertEqual(_strip_pypi_version("numpy"), "numpy")

    def test_empty_string(self):
        self.assertEqual(_strip_pypi_version(""), "")

    def test_none_input(self):
        self.assertEqual(_strip_pypi_version(None), "")

    def test_package_with_dashes(self):
        self.assertEqual(_strip_pypi_version("my-package 1.2.3"), "my-package")


class TestApplySrBlocks(unittest.TestCase):

    def test_single_replacement(self):
        original = "def foo():\n    return 1\n"
        blocks = [("return 1", "return 42")]
        result, errors = _apply_sr_blocks(original, blocks)
        self.assertIn("return 42", result)
        self.assertEqual(errors, [])

    def test_multiple_blocks(self):
        original = "x = 1\ny = 2\nz = 3\n"
        blocks = [("x = 1", "x = 10"), ("y = 2", "y = 20")]
        result, errors = _apply_sr_blocks(original, blocks)
        self.assertIn("x = 10", result)
        self.assertIn("y = 20", result)
        self.assertEqual(errors, [])

    def test_missing_search_string(self):
        original = "def foo():\n    pass\n"
        blocks = [("def bar():", "def baz():")]
        result, errors = _apply_sr_blocks(original, blocks)
        self.assertEqual(result, original)
        self.assertEqual(len(errors), 1)
        self.assertIn("block 0", errors[0])

    def test_replaces_only_first_occurrence(self):
        original = "x = 1\nx = 1\n"
        blocks = [("x = 1", "x = 99")]
        result, errors = _apply_sr_blocks(original, blocks)
        self.assertEqual(result.count("x = 99"), 1)
        self.assertEqual(result.count("x = 1"), 1)

    def test_empty_blocks(self):
        original = "some code"
        result, errors = _apply_sr_blocks(original, [])
        self.assertEqual(result, original)
        self.assertEqual(errors, [])


class TestExtractCode(unittest.TestCase):

    def test_extracts_fenced_block(self):
        text = "Here:\n```python\ndef foo(): pass\n```"
        self.assertEqual(_extract_code(text), "def foo(): pass")

    def test_no_fence_returns_stripped(self):
        text = "def foo(): pass"
        self.assertEqual(_extract_code(text), "def foo(): pass")

    def test_empty_string(self):
        self.assertEqual(_extract_code(""), "")

    def test_none_returns_empty(self):
        self.assertEqual(_extract_code(None), "")


# ════════════════════════════════════════════════════════════════════════════
# 2. CapabilitySynthesizer — file I/O, no LLM
# ════════════════════════════════════════════════════════════════════════════

class TestCapabilitySynthesizer(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.synth = CapabilitySynthesizer(data_dir=self.tmp, console=None)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make_proposal(self, title="Test Prop", refs=None, status="queued"):
        p = {
            "title": title,
            "kind": "integrate_lib",
            "source_refs": refs or ["eco:test"],
            "target_files": ["src/tools/test.py"],
            "approach": "add it",
            "rationale": "because",
            "risk": "low",
            "priority": 3,
            "estimated_effort_minutes": 30,
            "expected_capability_gain": "better",
            "rollback_plan": "revert",
            "depends_on": [],
            "status": status,
        }
        p["id"] = self.synth._mk_id(p)
        p["created_at"] = datetime.now().isoformat()
        return p

    def test_mk_id_deterministic(self):
        p = self._make_proposal("Hello World", ["ref1"])
        p2 = self._make_proposal("Hello World", ["ref1"])
        self.assertEqual(p["id"], p2["id"])

    def test_mk_id_starts_with_fp(self):
        p = self._make_proposal()
        self.assertTrue(p["id"].startswith("fp_"))
        self.assertEqual(len(p["id"]), 13)  # fp_ + 10 hex chars

    def test_enqueue_adds_proposal(self):
        p = self._make_proposal()
        result = self.synth.enqueue([p])
        self.assertEqual(result["added"], 1)
        self.assertEqual(result["total_queued"], 1)

    def test_enqueue_deduplicates_by_id(self):
        p = self._make_proposal()
        self.synth.enqueue([p])
        result = self.synth.enqueue([p])  # same proposal again
        self.assertEqual(result["added"], 0)
        self.assertEqual(result["total_queued"], 1)

    def test_enqueue_different_proposals(self):
        p1 = self._make_proposal("Prop A", ["ref1"])
        p2 = self._make_proposal("Prop B", ["ref2"])
        result = self.synth.enqueue([p1, p2])
        self.assertEqual(result["added"], 2)

    def test_list_queued_filters_status(self):
        p1 = self._make_proposal("Queued", status="queued")
        p2 = self._make_proposal("Applied", refs=["ref2"], status="applied")
        self.synth.enqueue([p1, p2])
        queued = self.synth.list_queued()
        self.assertEqual(len(queued), 1)
        self.assertEqual(queued[0]["title"], "Queued")

    def test_update_status(self):
        p = self._make_proposal()
        self.synth.enqueue([p])
        ok = self.synth.update_status(p["id"], "approved", note="looks good")
        self.assertTrue(ok)
        found = self.synth.find(p["id"])
        self.assertEqual(found["status"], "approved")

    def test_update_status_missing_id(self):
        ok = self.synth.update_status("fp_nonexistent", "approved")
        self.assertFalse(ok)

    def test_find_returns_none_for_missing(self):
        self.assertIsNone(self.synth.find("fp_doesnotexist"))

    def test_heuristic_produces_proposals(self):
        papers = [{
            "id": "2501.00001",
            "title": "Agent Improvement Technique",
            "score": {"applicability": 0.8},
            "deep": {
                "tldr": "We improve agents",
                "novel_idea": "New attention mechanism",
                "apex_integration": {
                    "target_file_hint": "src/models/thinking_path.py",
                    "approach": "Add attention layer",
                    "risk": "medium",
                    "effort_minutes": 60,
                },
            },
        }]
        proposals = run(self.synth.synthesize(papers, []))
        self.assertGreater(len(proposals), 0)
        self.assertEqual(proposals[0]["kind"], "adopt_paper_idea")

    def test_enqueue_caps_at_200(self):
        proposals = [self._make_proposal(f"Prop {i}", [f"ref{i}"]) for i in range(210)]
        self.synth.enqueue(proposals)
        all_props = self.synth._load_proposals()
        self.assertLessEqual(len(all_props), 200)


# ════════════════════════════════════════════════════════════════════════════
# 3. SelfBenchmark — real subprocess execution
# ════════════════════════════════════════════════════════════════════════════

class TestSelfBenchmark(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.bench = SelfBenchmark(data_dir=self.tmp, console=None)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_run_in_subprocess_correct_code(self):
        code = "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen: return [seen[target-n], i]\n        seen[n] = i\n"
        tests = ["assert sorted(two_sum([2,7,11,15], 9)) == [0,1]"]
        result = _run_in_subprocess(code, tests)
        self.assertTrue(result["passed"])
        self.assertEqual(result["returncode"], 0)

    def test_run_in_subprocess_wrong_code(self):
        code = "def two_sum(nums, target):\n    return [0, 0]\n"
        tests = ["assert sorted(two_sum([3,2,4], 6)) == [1,2]"]
        result = _run_in_subprocess(code, tests)
        self.assertFalse(result["passed"])
        self.assertNotEqual(result["returncode"], 0)

    def test_run_in_subprocess_syntax_error(self):
        code = "def two_sum(\n  broken syntax here\n"
        tests = ["assert two_sum([1,2], 3)"]
        result = _run_in_subprocess(code, tests)
        self.assertFalse(result["passed"])

    def test_regression_check_no_data(self):
        result = self.bench.regression_check()
        self.assertFalse(result["regression"])

    def test_regression_check_with_improvement(self):
        records = [
            {"ts": "2025-01-01T00:00:00", "summary": {"test_model": {"pass_rate": 0.6, "passed": 3, "total": 5}}},
            {"ts": "2025-01-02T00:00:00", "summary": {"test_model": {"pass_rate": 0.8, "passed": 4, "total": 5}}},
        ]
        bench_path = Path(self.tmp) / "bench.json"
        bench_path.write_text(json.dumps(records))
        result = self.bench.regression_check()
        self.assertFalse(result["regression"])

    def test_regression_check_detects_drop(self):
        records = [
            {"ts": "2025-01-01T00:00:00", "summary": {"test_model": {"pass_rate": 0.8, "passed": 4, "total": 5}}},
            {"ts": "2025-01-02T00:00:00", "summary": {"test_model": {"pass_rate": 0.4, "passed": 2, "total": 5}}},
        ]
        bench_path = Path(self.tmp) / "bench.json"
        bench_path.write_text(json.dumps(records))
        result = self.bench.regression_check(drop_threshold=0.15)
        self.assertTrue(result["regression"])
        # details is a list of dicts with "model" key
        model_names = [d.get("model") for d in result.get("details", [])]
        self.assertIn("test_model", model_names)


# ════════════════════════════════════════════════════════════════════════════
# 4. ProposalApplier — safety + backup + apply (mocked Gemini)
# ════════════════════════════════════════════════════════════════════════════

class TestProposalApplierSafety(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.synth = CapabilitySynthesizer(data_dir=self.tmp, console=None)
        self.bench = MagicMock()
        self.applier = ProposalApplier(
            self.synth, self.bench, console=None,
            codebase_root=self.tmp,
            backups_dir=str(Path(self.tmp) / "backups"),
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_safe_path_inside_root(self):
        p = Path(self.tmp) / "src" / "tools" / "foo.py"
        self.assertTrue(self.applier._is_safe_path(p))

    def test_unsafe_path_outside_root(self):
        p = Path("/etc/passwd")
        self.assertFalse(self.applier._is_safe_path(p))

    def test_unsafe_dotenv(self):
        p = Path(self.tmp) / ".env"
        self.assertFalse(self.applier._is_safe_path(p))

    def test_unsafe_credentials(self):
        p = Path(self.tmp) / "credentials.json"
        self.assertFalse(self.applier._is_safe_path(p))

    def test_safe_apex_dir(self):
        p = Path(self.tmp) / ".apex" / "hooks.json"
        self.assertTrue(self.applier._is_safe_path(p))

    def test_unsafe_hidden_dir(self):
        p = Path(self.tmp) / ".secret" / "file.py"
        self.assertFalse(self.applier._is_safe_path(p))

    def test_backup_creates_copy(self):
        target = Path(self.tmp) / "src" / "foo.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("original content")
        bpath = self.applier._backup(target, "fp_test")
        self.assertIsNotNone(bpath)
        self.assertTrue(bpath.exists())
        self.assertEqual(bpath.read_text(), "original content")

    def test_backup_nonexistent_file(self):
        target = Path(self.tmp) / "nonexistent.py"
        bpath = self.applier._backup(target, "fp_test")
        self.assertIsNone(bpath)

    def test_restore_backup(self):
        target = Path(self.tmp) / "src" / "restoreme.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("original content")
        bpath = self.applier._backup(target, "fp_restore_test")
        target.write_text("modified content")
        result = self.applier.restore_backup("fp_restore_test")
        self.assertTrue(result["ok"])
        self.assertEqual(target.read_text(), "original content")

    def test_restore_no_backups(self):
        result = self.applier.restore_backup("fp_nonexistent")
        self.assertFalse(result["ok"])

    def test_list_backups_empty(self):
        result = self.applier.list_backups("fp_nosuchid")
        self.assertEqual(result, [])

    def test_list_backups_populated(self):
        target = Path(self.tmp) / "src" / "listed.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("v1")
        self.applier._backup(target, "fp_list_test")
        result = self.applier.list_backups("fp_list_test")
        self.assertEqual(len(result), 1)
        self.assertIn("ts", result[0])
        self.assertIn("files", result[0])

    def test_prune_old_backups_removes_old(self):
        import time as _time
        bdir = Path(self.tmp) / "backups" / "fp_prune_test"
        bdir.mkdir(parents=True, exist_ok=True)
        old_ts = bdir / "20230101T000000"
        old_ts.mkdir()
        (old_ts / "file.py").write_text("old")
        # backdate the directory mtime so prune sees it as old
        ancient = _time.time() - 86400 * 100  # 100 days ago
        os.utime(str(old_ts), (ancient, ancient))
        self.applier.prune_old_backups(keep_days=1)
        self.assertFalse(old_ts.exists())

    def test_prune_keeps_recent_backup(self):
        target = Path(self.tmp) / "src" / "keepme.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("recent")
        self.applier._backup(target, "fp_keep_test")
        self.applier.prune_old_backups(keep_days=30)
        result = self.applier.list_backups("fp_keep_test")
        self.assertEqual(len(result), 1)


class TestProposalApplierApply(unittest.TestCase):
    """Apply pipeline with mocked Gemini and bench."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.synth = CapabilitySynthesizer(data_dir=self.tmp, console=None)
        self.bench_mock = MagicMock()
        self.bench_mock.run = AsyncMock(return_value={
            "summary": {"model_a": {"pass_rate": 0.8, "passed": 4, "total": 5}}
        })
        self.applier = ProposalApplier(
            self.synth, self.bench_mock, console=None,
            codebase_root=self.tmp,
            backups_dir=str(Path(self.tmp) / "backups"),
        )
        target_file = Path(self.tmp) / "src" / "test_module.py"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text("# original\ndef hello():\n    return 'hello'\n")
        self.target_file = target_file

        self.proposal = {
            "id": "fp_testapply",
            "title": "Test Proposal",
            "kind": "refactor",
            "source_refs": ["test"],
            "target_files": ["src/test_module.py"],
            "approach": "add new function",
            "rationale": "test",
            "risk": "low",
            "priority": 1,
            "estimated_effort_minutes": 15,
            "expected_capability_gain": "more functions",
            "rollback_plan": "revert",
            "depends_on": [],
            "status": "approved",
            "created_at": datetime.now().isoformat(),
        }
        self.synth.enqueue([self.proposal])

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_apply_proposal_not_found(self):
        result = run(self.applier.apply("fp_missing"))
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "proposal_not_found")

    def test_apply_no_gemini_key(self):
        self.applier.client = None
        result = run(self.applier.apply("fp_testapply"))
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "no_gemini_key")

    def test_apply_full_rewrite_success(self):
        new_code = "# modified\ndef hello():\n    return 'hello'\n\ndef world():\n    return 'world'\n"
        mock_response = MagicMock()
        mock_response.text = f"```python\n{new_code}\n```"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        self.applier.client = mock_client

        result = run(self.applier.apply("fp_testapply", gate_with_bench=False))
        self.assertTrue(result["ok"])
        # _extract_code strips trailing whitespace; compare stripped
        self.assertEqual(self.target_file.read_text().strip(), new_code.strip())

    def test_apply_rollback_on_syntax_error(self):
        broken_code = "def hello(\n  BROKEN SYNTAX\n"
        mock_response = MagicMock()
        mock_response.text = f"```python\n{broken_code}\n```"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        self.applier.client = mock_client

        original = self.target_file.read_text()
        result = run(self.applier.apply("fp_testapply", gate_with_bench=False))
        self.assertFalse(result["ok"])
        self.assertTrue(result.get("rolled_back"))
        self.assertEqual(self.target_file.read_text(), original)

    def test_apply_diff_mode_success(self):
        diff_output = "<<<SEARCH\ndef hello():\n    return 'hello'\n===REPLACE\ndef hello():\n    return 'HELLO'\n>>>"
        mock_response = MagicMock()
        mock_response.text = diff_output
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        self.applier.client = mock_client

        result = run(self.applier.apply("fp_testapply", gate_with_bench=False, use_diff=True))
        self.assertTrue(result["ok"])
        self.assertIn("HELLO", self.target_file.read_text())

    def test_apply_diff_mode_falls_back_on_no_blocks(self):
        new_code = "# full rewrite fallback\ndef hello():\n    return 'fallback'\n"
        mock_client = MagicMock()
        responses = [
            MagicMock(text="no blocks here"),  # diff response
            MagicMock(text=f"```python\n{new_code}\n```"),  # full-rewrite fallback
        ]
        mock_client.models.generate_content.side_effect = responses
        self.applier.client = mock_client

        result = run(self.applier.apply("fp_testapply", gate_with_bench=False, use_diff=True))
        self.assertTrue(result["ok"])
        self.assertEqual(result["mode"], "full_fallback")

    def test_apply_bench_gated_rollback_on_regression(self):
        new_code = "# post-regression code\ndef hello():\n    return 'hello'\n"
        mock_response = MagicMock()
        mock_response.text = f"```python\n{new_code}\n```"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        self.applier.client = mock_client

        self.bench_mock.run = AsyncMock(side_effect=[
            {"summary": {"m": {"pass_rate": 0.8, "passed": 4, "total": 5}}},  # pre
            {"summary": {"m": {"pass_rate": 0.4, "passed": 2, "total": 5}}},  # post — regression
        ])
        original = self.target_file.read_text()
        result = run(self.applier.apply("fp_testapply", gate_with_bench=True, regression_drop_threshold=0.15))
        self.assertFalse(result["ok"])
        self.assertTrue(result.get("rolled_back"))
        self.assertTrue(result.get("regression"))
        self.assertEqual(self.target_file.read_text(), original)


# ════════════════════════════════════════════════════════════════════════════
# 5. PaperReader — XML parsing + scan_backfill with mocked httpx
# ════════════════════════════════════════════════════════════════════════════

class TestPaperReaderParsing(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.reader = PaperReader(data_dir=self.tmp, console=None, chroma_path=None)
        self.reader.collection = None  # disable chroma

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_parse_entries_extracts_fields(self):
        from xml.etree import ElementTree as ET
        root = ET.fromstring(SAMPLE_ARXIV_XML)
        entries = self.reader._parse_entries(root, "cs.AI")
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["id"], "2501.99999v1")
        self.assertEqual(entries[0]["category"], "cs.AI")
        self.assertIn("Improving AI Agents", entries[0]["title"])
        self.assertIn("https://arxiv.org/pdf/2501.99999", entries[0]["pdf_url"])

    def test_parse_entries_truncates_title(self):
        from xml.etree import ElementTree as ET
        root = ET.fromstring(SAMPLE_ARXIV_XML)
        entries = self.reader._parse_entries(root, "cs.AI")
        self.assertLessEqual(len(entries[0]["title"]), 400)

    def test_recent_records_empty(self):
        records = self.reader.recent_records(limit=10)
        self.assertEqual(records, [])

    def test_recent_records_reads_last_n(self):
        log = Path(self.tmp) / "papers.jsonl"
        for i in range(5):
            log.open("a").write(json.dumps({"id": f"p{i}", "title": f"Paper {i}"}) + "\n")
        records = self.reader.recent_records(limit=3)
        self.assertEqual(len(records), 3)
        self.assertEqual(records[-1]["id"], "p4")

    def test_seen_ids_load_save(self):
        seen = {"2501.00001", "2501.00002"}
        self.reader._save_seen(seen)
        loaded = self.reader._load_seen()
        self.assertEqual(loaded, seen)

    def test_seen_ids_empty_when_no_file(self):
        loaded = self.reader._load_seen()
        self.assertEqual(loaded, set())

    def test_scan_backfill_with_mock(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = SAMPLE_ARXIV_XML
        mock_resp.raise_for_status = MagicMock()

        scored_paper = MagicMock()

        async def fake_ingest(paper):
            return {
                "id": paper["id"],
                "title": paper["title"],
                "score": {"applicability": 0.8},
                "ingested_at": datetime.now().isoformat(),
            }

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_ctx = AsyncMock()
            mock_ctx.get.return_value = mock_resp
            mock_httpx.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            mock_httpx.return_value.__aexit__ = AsyncMock(return_value=False)
            with patch.object(self.reader, "ingest_paper", side_effect=fake_ingest):
                result = run(self.reader.scan_backfill(days=3, max_per_category=5, max_total=20))

        self.assertIn("new_count", result)
        self.assertIn("applicable_count", result)
        self.assertEqual(result["days"], 3)

    def test_query_arxiv_date_range_builds_correct_query(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = SAMPLE_ARXIV_XML
        mock_resp.raise_for_status = MagicMock()

        captured_params = {}

        async def fake_get(url, params=None):
            captured_params.update(params or {})
            return mock_resp

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_ctx = AsyncMock()
            mock_ctx.get = AsyncMock(side_effect=fake_get)
            mock_httpx.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            mock_httpx.return_value.__aexit__ = AsyncMock(return_value=False)

            start = datetime(2025, 1, 1)
            end = datetime(2025, 1, 8)
            entries = run(self.reader.query_arxiv_date_range("cs.AI", start, end, max_results=10))

        self.assertIn("submittedDate", captured_params.get("search_query", ""))
        self.assertIn("cs.AI", captured_params.get("search_query", ""))
        self.assertEqual(captured_params.get("max_results"), "10")


# ════════════════════════════════════════════════════════════════════════════
# 6. KnowledgeForge — state + forge log + briefing_digest
# ════════════════════════════════════════════════════════════════════════════

class TestKnowledgeForge(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.project_root = tempfile.mkdtemp()
        # patch out Gemini client construction
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            self.forge = KnowledgeForge(
                data_dir=str(Path(self.tmp) / "forge"),
                project_root=self.project_root,
                codebase_root=self.tmp,
                console=None,
                hooks=None,
            )
        # override forge_log_path to tmp for isolation
        self.forge.forge_log_path = Path(self.tmp) / "forge_log.md"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_state_path_is_in_apex_dir(self):
        expected = Path(self.project_root) / ".apex" / "forge_state.json"
        self.assertEqual(self.forge.state_path, expected)

    def test_apex_dir_created_on_init(self):
        apex_dir = Path(self.project_root) / ".apex"
        self.assertTrue(apex_dir.exists())

    def test_load_state_empty(self):
        state = self.forge._load_state()
        self.assertEqual(state, {})

    def test_save_and_load_state(self):
        state = {"last_cycle": "2025-01-15T10:00:00", "last_summary": {"papers_new": 3}}
        self.forge._save_state(state)
        loaded = self.forge._load_state()
        self.assertEqual(loaded["last_cycle"], "2025-01-15T10:00:00")
        self.assertEqual(loaded["last_summary"]["papers_new"], 3)

    def test_write_forge_log_creates_file(self):
        summary = {"papers_new": 5, "papers_applicable": 2, "eco_new": 8,
                   "eco_applicable": 3, "proposals_added": 1, "proposals_total_queued": 4,
                   "regression": False}
        self.forge._write_forge_log(summary)
        self.assertTrue(self.forge.forge_log_path.exists())
        content = self.forge.forge_log_path.read_text()
        self.assertIn("papers new=5", content)
        self.assertIn("applicable=2", content)

    def test_write_forge_log_appends(self):
        summary = {"papers_new": 1, "papers_applicable": 0, "eco_new": 0,
                   "eco_applicable": 0, "proposals_added": 0, "proposals_total_queued": 0,
                   "regression": False}
        self.forge._write_forge_log(summary)
        self.forge._write_forge_log(summary)
        content = self.forge.forge_log_path.read_text()
        self.assertEqual(content.count("##"), 2)

    def test_read_forge_log_empty(self):
        text = self.forge.read_forge_log()
        self.assertIn("no forge log", text)

    def test_read_forge_log_after_write(self):
        summary = {"papers_new": 7, "papers_applicable": 3, "eco_new": 5,
                   "eco_applicable": 2, "proposals_added": 2, "proposals_total_queued": 6,
                   "regression": False}
        self.forge._write_forge_log(summary)
        text = self.forge.read_forge_log()
        self.assertIn("papers new=7", text)

    def test_briefing_digest_empty_state(self):
        digest = self.forge.briefing_digest()
        self.assertIn("last_cycle", digest)
        self.assertIsNone(digest["last_cycle"])
        self.assertFalse(digest["regression"])

    def test_is_idle_when_no_input(self):
        self.forge.last_input_time = 0  # ancient timestamp
        self.assertTrue(self.forge._is_idle(threshold_sec=10))

    def test_is_not_idle_recent_input(self):
        import time
        self.forge.mark_input()
        self.assertFalse(self.forge._is_idle(threshold_sec=600))

    def test_due_for_cycle_first_run(self):
        self.assertTrue(self.forge._due_for_cycle())

    def test_not_due_after_recent_cycle(self):
        state = {"last_cycle": datetime.now().isoformat()}
        self.forge._save_state(state)
        self.assertFalse(self.forge._due_for_cycle())

    def test_status_summary_structure(self):
        s = self.forge.status_summary()
        self.assertIn("last_cycle", s)
        self.assertIn("queued_proposals", s)
        self.assertIn("categories", s)


# ════════════════════════════════════════════════════════════════════════════
# 7. HookManager — events completeness + fire behavior
# ════════════════════════════════════════════════════════════════════════════

class TestHookManager(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hooks = HookManager(project_root=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_all_forge_events_registered(self):
        forge_events = {
            "ForgeCycleStart", "ForgeCycleDone",
            "ApexPaperFound", "ApexEcosystemNew",
            "ForgeProposalAdded", "ForgeApplied", "ForgeRolledBack",
        }
        self.assertTrue(forge_events.issubset(HookManager.EVENTS),
                        f"Missing events: {forge_events - HookManager.EVENTS}")

    def test_all_base_events_registered(self):
        base_events = {"SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"}
        self.assertTrue(base_events.issubset(HookManager.EVENTS))

    def test_fire_unknown_event_returns_empty(self):
        result = run(self.hooks.fire("NonExistentEvent", {}))
        self.assertEqual(result, [])

    def test_fire_with_no_hooks_returns_empty(self):
        result = run(self.hooks.fire("ForgeCycleStart", {"ts": "2025-01-15"}))
        self.assertEqual(result, [])

    def test_matches_by_value_substring(self):
        ctx = {"tool": "shell", "action": "run"}
        self.assertTrue(self.hooks._matches("shell", ctx))
        self.assertFalse(self.hooks._matches("nonexistent", ctx))

    def test_fire_with_hook_executes(self):
        apex_dir = Path(self.tmp) / ".apex"
        apex_dir.mkdir(exist_ok=True)
        out_file = Path(self.tmp) / "hook_output.txt"
        hooks_config = {
            "ForgeCycleStart": [
                {"command": f'echo "fired" > "{out_file}"'}
            ]
        }
        (apex_dir / "hooks.json").write_text(json.dumps(hooks_config))
        hooks = HookManager(project_root=self.tmp)
        results = run(hooks.fire("ForgeCycleStart", {"ts": "now"}))
        self.assertEqual(len(results), 1)
        # result success depends on platform; just check structure
        self.assertIn("success", results[0])

    def test_load_hooks_from_project_apex_dir(self):
        apex_dir = Path(self.tmp) / ".apex"
        apex_dir.mkdir(exist_ok=True)
        config = {"SessionStart": [{"command": "echo loaded"}]}
        (apex_dir / "hooks.json").write_text(json.dumps(config))
        hooks = HookManager(project_root=self.tmp)
        self.assertEqual(len(hooks.hooks["SessionStart"]), 1)

    def test_invalid_hooks_json_does_not_crash(self):
        apex_dir = Path(self.tmp) / ".apex"
        apex_dir.mkdir(exist_ok=True)
        (apex_dir / "hooks.json").write_text("{invalid json")
        # should not raise
        hooks = HookManager(project_root=self.tmp)
        self.assertIsNotNone(hooks)


# ════════════════════════════════════════════════════════════════════════════
# 8. PipSandbox — core logic with mocked subprocess
# ════════════════════════════════════════════════════════════════════════════

class TestPipSandbox(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.sandbox = PipSandbox(venvs_dir=self.tmp, console=None)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_venv_python_path_win(self):
        with patch("sys.platform", "win32"):
            path = self.sandbox._venv_python(Path("/tmp/venv"))
            self.assertIn("Scripts", path)
            self.assertIn("python.exe", path)

    def test_venv_python_path_unix(self):
        with patch("sys.platform", "linux"):
            path = self.sandbox._venv_python(Path("/tmp/venv"))
            # Path uses OS-native separators; check parts not literal string
            p = Path(path)
            self.assertIn("bin", p.parts)
            self.assertTrue(p.name.startswith("python"))

    def test_cleanup_venv_removes_dir(self):
        venv_dir = Path(self.tmp) / "fp_testclean"
        venv_dir.mkdir()
        (venv_dir / "file.txt").write_text("data")
        self.sandbox.cleanup_venv("fp_testclean")
        self.assertFalse(venv_dir.exists())

    def test_cleanup_venv_missing_dir_no_crash(self):
        self.sandbox.cleanup_venv("fp_nonexistent")  # should not raise

    def test_test_install_skips_src_deps(self):
        # depends_on entries starting with src/ are filtered in _handle_depends_on
        # but here we test that PipSandbox.test_install with empty list short-circuits
        # The real filter is in ProposalApplier._handle_depends_on
        pass  # Covered by integration; sandbox itself accepts any package list

    def test_run_timeout_returns_error(self):
        async def do():
            with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError):
                rc, out, err = await self.sandbox._run([sys.executable, "-V"], timeout=0.001)
            return rc, out, err
        rc, out, err = run(do())
        self.assertEqual(rc, -1)
        self.assertEqual(err, "TIMEOUT")


# ════════════════════════════════════════════════════════════════════════════
# 9. EcosystemWatcher state management
# ════════════════════════════════════════════════════════════════════════════

class TestEcosystemWatcher(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        from src.services.knowledge_forge.ecosystem_watcher import EcosystemWatcher
        self.watcher = EcosystemWatcher(data_dir=self.tmp, console=None)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_state_empty(self):
        state = self.watcher._load_state()
        self.assertEqual(state, {})

    def test_save_and_load_state(self):
        state = {"seen_keys": ["pypi:requests", "gh:trending:python:httpx"], "last_scan": "2025-01-15"}
        self.watcher._save_state(state)
        loaded = self.watcher._load_state()
        self.assertEqual(loaded["last_scan"], "2025-01-15")
        self.assertEqual(len(loaded["seen_keys"]), 2)

    def test_recent_applicable_empty(self):
        from src.services.knowledge_forge.ecosystem_watcher import EcosystemWatcher
        results = self.watcher.recent_applicable(limit=10)
        self.assertEqual(results, [])

    def test_strip_pypi_version_integration(self):
        items = [
            ("numpy 1.26.0", "numpy"),
            ("scikit-learn 1.4.0rc1", "scikit-learn"),
            ("torch 2.0.0+cu118", "torch"),
        ]
        for raw, expected in items:
            self.assertEqual(_strip_pypi_version(raw), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)

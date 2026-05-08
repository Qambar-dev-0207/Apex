"""
Tests for src/tools/auto_selector.py — regex tier + LLM classifier.
"""

import asyncio
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.auto_selector import AutoToolSelector, regex_match


def run(coro):
    return asyncio.run(coro)


# ════════════════════════════════════════════════════════════════════════════
# Tier 1 — regex patterns
# ════════════════════════════════════════════════════════════════════════════

class TestRegexMatch(unittest.TestCase):

    def test_git_status(self):
        r = regex_match("git status")
        self.assertEqual(r["tool"], "git")
        self.assertEqual(r["action"], "status")
        self.assertEqual(r["confidence"], 0.95)

    def test_git_diff_no_arg(self):
        r = regex_match("git diff")
        self.assertEqual(r["tool"], "git")
        self.assertEqual(r["action"], "diff")

    def test_git_diff_with_arg(self):
        r = regex_match("git diff src/foo.py")
        self.assertEqual(r["tool"], "git")
        self.assertEqual(r["action"], "diff")
        self.assertEqual(r["input_data"], "src/foo.py")

    def test_git_commit(self):
        r = regex_match("git commit -m 'fix bug'")
        self.assertEqual(r["tool"], "git")
        self.assertEqual(r["action"], "commit")
        self.assertIn("fix bug", r["input_data"])

    def test_git_push_pull(self):
        self.assertEqual(regex_match("git push")["action"], "push")
        self.assertEqual(regex_match("git pull")["action"], "pull")

    def test_filesystem_read(self):
        r = regex_match("read src/main.py")
        self.assertEqual(r["tool"], "filesystem")
        self.assertEqual(r["action"], "read")
        self.assertEqual(r["input_data"], "src/main.py")

    def test_filesystem_cat(self):
        r = regex_match("cat config.json")
        self.assertEqual(r["tool"], "filesystem")
        self.assertEqual(r["action"], "read")

    def test_filesystem_list(self):
        r = regex_match("ls src")
        self.assertEqual(r["tool"], "filesystem")
        self.assertEqual(r["action"], "list")
        self.assertEqual(r["input_data"], "src")

    def test_grep_search(self):
        r = regex_match("grep MemoryManager")
        self.assertEqual(r["tool"], "filesystem")
        self.assertEqual(r["action"], "search")
        self.assertEqual(r["input_data"], "MemoryManager")

    def test_search_for(self):
        r = regex_match("search for async def")
        self.assertEqual(r["action"], "search")
        self.assertEqual(r["input_data"], "async def")

    def test_glob(self):
        r = regex_match("glob **/*.py")
        self.assertEqual(r["action"], "glob")
        self.assertEqual(r["input_data"], "**/*.py")

    def test_hardware_vitals(self):
        for q in ["vitals", "hw status", "hardware", "cpu usage", "ram"]:
            r = regex_match(q)
            self.assertEqual(r["tool"], "hardware", f"failed: {q}")
            self.assertEqual(r["action"], "vitals")

    def test_vision_capture(self):
        for q in ["screenshot", "capture screen", "see my screen", "what's on my screen"]:
            r = regex_match(q)
            self.assertEqual(r["tool"], "vision", f"failed: {q}")

    def test_web_search(self):
        r = regex_match("google fastapi tutorial")
        self.assertEqual(r["tool"], "web_search")
        self.assertEqual(r["input_data"], "fastapi tutorial")

    def test_workspace_summarize(self):
        r = regex_match("project summary")
        self.assertEqual(r["tool"], "workspace")
        self.assertEqual(r["action"], "summarize")

    def test_code_compass_find_symbol(self):
        r = regex_match("find class MemoryManager")
        self.assertEqual(r["tool"], "code_compass")
        self.assertEqual(r["action"], "search")
        self.assertEqual(r["input_data"], "MemoryManager")

    def test_knowledge_forge_papers(self):
        r = regex_match("papers about transformers")
        self.assertEqual(r["tool"], "knowledge_forge")
        self.assertEqual(r["action"], "search_papers")
        self.assertEqual(r["input_data"], "transformers")

    def test_shell_run(self):
        r = regex_match("run pytest")
        self.assertEqual(r["tool"], "shell")
        self.assertEqual(r["input_data"], "pytest")

    def test_no_match_returns_none(self):
        # conversational / multi-step prompts shouldn't match
        self.assertIsNone(regex_match("can you help me design a billing system"))
        self.assertIsNone(regex_match("hello"))
        self.assertIsNone(regex_match(""))

    def test_case_insensitive(self):
        r = regex_match("GIT STATUS")
        self.assertEqual(r["action"], "status")

    def test_whitespace_tolerant(self):
        r = regex_match("   git status   ")
        self.assertEqual(r["action"], "status")


# ════════════════════════════════════════════════════════════════════════════
# Tier 2 — LLM classifier
# ════════════════════════════════════════════════════════════════════════════

class TestAutoToolSelector(unittest.TestCase):

    def test_classify_no_client_returns_empty(self):
        s = AutoToolSelector()
        s.client = None
        result = run(s.classify("ambiguous prompt nothing matches"))
        self.assertEqual(result, [])

    def test_classify_uses_regex_first(self):
        s = AutoToolSelector()
        # Even with a mock client, regex should hit first
        result = run(s.classify("git status"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source"], "regex")

    def test_classify_llm_path(self):
        json_response = json.dumps({
            "candidates": [
                {"tool": "filesystem", "action": "read",
                 "input_data": "src/main.py", "confidence": 0.9,
                 "rationale": "user wants to read code"},
            ],
            "needs_planning": False,
        })
        mock_resp = MagicMock()
        mock_resp.text = json_response
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp

        s = AutoToolSelector()
        s.client = mock_client
        result = run(s.classify("show me what main.py does"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["tool"], "filesystem")
        self.assertEqual(result[0]["source"], "llm")

    def test_classify_filters_invalid_tool_names(self):
        json_response = json.dumps({
            "candidates": [
                {"tool": "imaginary_tool", "action": "go", "input_data": "",
                 "confidence": 0.99, "rationale": "x"},
                {"tool": "fs", "action": "read", "input_data": "x",
                 "confidence": 0.8, "rationale": "y"},
            ],
            "needs_planning": False,
        })
        mock_resp = MagicMock()
        mock_resp.text = json_response
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp

        s = AutoToolSelector()
        s.client = mock_client
        result = run(s.classify("read x"))
        # imaginary_tool dropped; fs aliased to filesystem
        # but regex catches "read x" first → only regex returned
        # so let's use a non-regex prompt
        result = run(s.classify("perform some non-regex matchable action"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["tool"], "filesystem")  # fs alias resolved

    def test_classify_sorts_by_confidence(self):
        json_response = json.dumps({
            "candidates": [
                {"tool": "filesystem", "action": "read", "input_data": "",
                 "confidence": 0.5, "rationale": ""},
                {"tool": "shell", "action": "execute", "input_data": "",
                 "confidence": 0.9, "rationale": ""},
            ],
            "needs_planning": False,
        })
        mock_resp = MagicMock()
        mock_resp.text = json_response
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp

        s = AutoToolSelector()
        s.client = mock_client
        result = run(s.classify("a non-regex prompt"))
        self.assertEqual(result[0]["tool"], "shell")  # highest confidence first

    def test_pick_best_above_threshold(self):
        s = AutoToolSelector()
        # regex tier guarantees confidence 0.95 — above default 0.85
        result = run(s.pick_best("git status"))
        self.assertIsNotNone(result)
        self.assertEqual(result["tool"], "git")

    def test_pick_best_below_threshold_returns_none(self):
        json_response = json.dumps({
            "candidates": [{"tool": "filesystem", "action": "read",
                            "input_data": "", "confidence": 0.4,
                            "rationale": ""}],
            "needs_planning": False,
        })
        mock_resp = MagicMock()
        mock_resp.text = json_response
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp

        s = AutoToolSelector()
        s.client = mock_client
        result = run(s.pick_best("vague request"))
        self.assertIsNone(result)

    def test_pick_best_skips_when_needs_planning(self):
        json_response = json.dumps({
            "candidates": [{"tool": "filesystem", "action": "read",
                            "input_data": "x", "confidence": 0.95,
                            "rationale": "x"}],
            "needs_planning": True,
        })
        mock_resp = MagicMock()
        mock_resp.text = json_response
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp

        s = AutoToolSelector()
        s.client = mock_client
        result = run(s.pick_best("multi-step goal"))
        self.assertIsNone(result)

    def test_classify_handles_malformed_json(self):
        mock_resp = MagicMock()
        mock_resp.text = "{ malformed"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp

        s = AutoToolSelector()
        s.client = mock_client
        result = run(s.classify("non-regex prompt"))
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

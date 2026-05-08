"""
Tests for src/tools/registry.py — alias resolution, prompt block generation,
telemetry, completeness check.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.registry import (
    REGISTRY, ToolTelemetry, resolve_tool_name, list_tools, get_spec,
    get_prompt_block,
)


class TestRegistryCompleteness(unittest.TestCase):

    def test_all_required_tools_registered(self):
        required = {
            "filesystem", "shell", "git", "python_executor",
            "research_swarm", "web_search", "workspace", "mcp",
            "vision", "hardware", "code_compass", "knowledge_forge",
            "swarm", "think_partner",
        }
        self.assertEqual(set(REGISTRY.keys()), required)

    def test_all_tools_have_actions(self):
        for name, spec in REGISTRY.items():
            self.assertGreater(len(spec.actions), 0, f"{name} has no actions")

    def test_all_tools_have_when_to_use(self):
        for name, spec in REGISTRY.items():
            self.assertGreater(len(spec.when_to_use), 0, f"{name} missing when_to_use")


class TestAliasResolution(unittest.TestCase):

    def test_canonical_name_resolves(self):
        self.assertEqual(resolve_tool_name("filesystem"), "filesystem")

    def test_known_aliases(self):
        self.assertEqual(resolve_tool_name("fs"), "filesystem")
        self.assertEqual(resolve_tool_name("files"), "filesystem")
        self.assertEqual(resolve_tool_name("web"), "web_search")
        self.assertEqual(resolve_tool_name("hw"), "hardware")
        self.assertEqual(resolve_tool_name("compass"), "code_compass")
        self.assertEqual(resolve_tool_name("forge"), "knowledge_forge")

    def test_case_insensitive(self):
        self.assertEqual(resolve_tool_name("FS"), "filesystem")
        self.assertEqual(resolve_tool_name("FileSystem"), "filesystem")
        self.assertEqual(resolve_tool_name("Web"), "web_search")

    def test_strips_whitespace(self):
        self.assertEqual(resolve_tool_name("  fs  "), "filesystem")

    def test_unknown_returns_none(self):
        self.assertIsNone(resolve_tool_name("nonexistent"))
        self.assertIsNone(resolve_tool_name(""))
        self.assertIsNone(resolve_tool_name(None))


class TestGetSpec(unittest.TestCase):

    def test_canonical_lookup(self):
        spec = get_spec("filesystem")
        self.assertIsNotNone(spec)
        self.assertEqual(spec.name, "filesystem")

    def test_alias_lookup(self):
        spec = get_spec("fs")
        self.assertIsNotNone(spec)
        self.assertEqual(spec.name, "filesystem")

    def test_unknown_returns_none(self):
        self.assertIsNone(get_spec("doesnotexist"))


class TestPromptBlock(unittest.TestCase):

    def test_block_lists_all_tools(self):
        block = get_prompt_block()
        for name in REGISTRY:
            self.assertIn(name, block)

    def test_block_includes_actions(self):
        block = get_prompt_block()
        self.assertIn("read", block)
        self.assertIn("write", block)
        self.assertIn("commit", block)

    def test_block_starts_with_header(self):
        block = get_prompt_block()
        self.assertTrue(block.startswith("AVAILABLE TOOLS"))


class TestListTools(unittest.TestCase):

    def test_returns_sorted(self):
        tools = list_tools()
        self.assertEqual(tools, sorted(tools))

    def test_count_matches_registry(self):
        self.assertEqual(len(list_tools()), len(REGISTRY))


class TestToolTelemetry(unittest.TestCase):

    def test_initial_empty(self):
        t = ToolTelemetry()
        self.assertEqual(t.summary(), {})

    def test_record_success(self):
        t = ToolTelemetry()
        t.record("filesystem", True)
        self.assertEqual(t.calls["filesystem"]["ok"], 1)
        self.assertEqual(t.calls["filesystem"]["fail"], 0)

    def test_record_failure_stores_error(self):
        t = ToolTelemetry()
        t.record("shell", False, "permission denied")
        self.assertEqual(t.calls["shell"]["fail"], 1)
        self.assertIn("permission denied", t.calls["shell"]["last_error"])

    def test_record_uses_canonical_name(self):
        t = ToolTelemetry()
        t.record("fs", True)  # alias
        # should be stored under "filesystem"
        self.assertIn("filesystem", t.calls)
        self.assertNotIn("fs", t.calls)

    def test_record_unknown_tool_falls_through(self):
        t = ToolTelemetry()
        t.record("totally-unknown", False, "what")
        # records under raw name when unresolvable
        self.assertIn("totally-unknown", t.calls)

    def test_long_error_truncated(self):
        t = ToolTelemetry()
        big = "x" * 500
        t.record("shell", False, big)
        self.assertLessEqual(len(t.calls["shell"]["last_error"]), 200)

    def test_reset(self):
        t = ToolTelemetry()
        t.record("git", True)
        t.reset()
        self.assertEqual(t.summary(), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)

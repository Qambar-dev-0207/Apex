"""
Tests for src/services/swarm.py
"""

import asyncio
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.swarm import Agent, Blackboard, Swarm, SPECIALIST_PROMPTS


def run(coro):
    return asyncio.run(coro)


# ════════════════════════════════════════════════════════════════════════════
# Blackboard
# ════════════════════════════════════════════════════════════════════════════

class TestBlackboard(unittest.TestCase):

    def test_empty_render(self):
        bb = Blackboard()
        self.assertIn("empty", bb.render_for_agent())

    def test_post_and_read(self):
        bb = Blackboard()
        run(bb.post("agent1", "coder", "wrote function foo()"))
        posts = bb.read_all()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["agent"], "agent1")
        self.assertEqual(posts[0]["role"], "coder")

    def test_render_excludes_self(self):
        bb = Blackboard()
        run(bb.post("a1", "coder", "my-content"))
        run(bb.post("a2", "critic", "their-content"))
        rendered = bb.render_for_agent(exclude_agent="a1")
        self.assertNotIn("my-content", rendered)
        self.assertIn("their-content", rendered)

    def test_render_truncates_long_content(self):
        bb = Blackboard()
        long = "x" * 2000
        run(bb.post("a1", "coder", long))
        rendered = bb.render_for_agent(exclude_agent="other")
        # should cap at 600 chars per post
        self.assertLess(len(rendered), 1000)

    def test_concurrent_posts(self):
        bb = Blackboard()

        async def many_posts():
            await asyncio.gather(*[
                bb.post(f"a{i}", "coder", f"content{i}") for i in range(10)
            ])

        run(many_posts())
        self.assertEqual(len(bb.read_all()), 10)


# ════════════════════════════════════════════════════════════════════════════
# Agent
# ════════════════════════════════════════════════════════════════════════════

class TestAgent(unittest.TestCase):

    def test_init_uses_role_prompt(self):
        agent = Agent(name="a1", role="coder")
        self.assertIn("CODER", agent.system_prompt)

    def test_unknown_role_uses_generic_prompt(self):
        agent = Agent(name="a1", role="weirdrole")
        self.assertIn("WEIRDROLE", agent.system_prompt)

    def test_custom_system_prompt_override(self):
        agent = Agent(name="a1", role="coder", system_prompt_override="custom")
        self.assertEqual(agent.system_prompt, "custom")

    def test_think_no_client_returns_offline_msg(self):
        agent = Agent(name="a1", role="coder", client=None)
        bb = Blackboard()
        result = run(agent.think("goal", bb))
        self.assertIn("offline", result)

    def test_think_calls_gemini(self):
        mock_resp = MagicMock()
        mock_resp.text = "## My contribution\nUse FastAPI."
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp

        agent = Agent(name="coder-1", role="coder", client=mock_client)
        bb = Blackboard()
        result = run(agent.think("build a CRM", bb))

        self.assertIn("FastAPI", result)
        # blackboard should have the post
        self.assertEqual(len(bb.read_all()), 1)
        self.assertEqual(bb.read_all()[0]["agent"], "coder-1")

    def test_think_records_to_memory(self):
        mock_resp = MagicMock()
        mock_resp.text = "output1"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp

        agent = Agent(name="a1", role="coder", client=mock_client)
        bb = Blackboard()
        run(agent.think("g", bb))
        run(agent.think("g", bb))
        self.assertEqual(len(agent.memory), 2)

    def test_think_excludes_own_posts_from_context(self):
        captured_prompts = []

        def fake_gen(*args, **kwargs):
            captured_prompts.append(kwargs.get("contents", ""))
            r = MagicMock()
            r.text = f"output{len(captured_prompts)}"
            return r

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = fake_gen

        agent = Agent(name="me", role="coder", client=mock_client)
        bb = Blackboard()
        run(bb.post("other", "critic", "external-note"))
        run(agent.think("goal", bb))
        # should see other-note in second call's context
        self.assertIn("external-note", captured_prompts[0])

    def test_think_handles_gemini_exception(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("api down")
        agent = Agent(name="a1", role="coder", client=mock_client)
        bb = Blackboard()
        result = run(agent.think("g", bb))
        self.assertIn("error", result)


# ════════════════════════════════════════════════════════════════════════════
# Swarm
# ════════════════════════════════════════════════════════════════════════════

class TestSwarm(unittest.TestCase):

    def test_default_roster_constant(self):
        self.assertEqual(set(Swarm.DEFAULT_ROSTER), {"architect", "coder", "critic"})

    def test_run_no_client_returns_error(self):
        s = Swarm(console=None)
        s.client = None
        result = run(s.run("build a CRM"))
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "no_gemini_client")

    def test_decompose_returns_default_on_no_client(self):
        s = Swarm(console=None)
        s.client = None
        # _decompose short-circuits when client is None
        result = run(s._decompose("goal"))
        self.assertEqual(result, Swarm.DEFAULT_ROSTER)

    def test_decompose_picks_from_available(self):
        s = Swarm(console=None)
        mock_resp = MagicMock()
        mock_resp.text = json.dumps({"roster": ["coder", "critic"]})
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        s.client = mock_client
        result = run(s._decompose("write Python code"))
        self.assertEqual(result, ["coder", "critic"])

    def test_decompose_filters_invalid_roles(self):
        s = Swarm(console=None)
        mock_resp = MagicMock()
        mock_resp.text = json.dumps({"roster": ["coder", "wizard", "critic"]})
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        s.client = mock_client
        result = run(s._decompose("goal"))
        self.assertNotIn("wizard", result)
        self.assertIn("coder", result)

    def test_decompose_caps_at_4(self):
        s = Swarm(console=None)
        mock_resp = MagicMock()
        mock_resp.text = json.dumps({
            "roster": ["architect", "coder", "critic", "researcher", "planner"]
        })
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        s.client = mock_client
        result = run(s._decompose("goal"))
        self.assertLessEqual(len(result), 4)

    def test_run_full_flow_with_explicit_roster(self):
        mock_client = MagicMock()
        # Each call returns same canned response
        responses = []
        for i in range(20):
            r = MagicMock()
            r.text = f"agent-output-{i}"
            responses.append(r)
        mock_client.models.generate_content.side_effect = responses

        s = Swarm(console=None)
        s.client = mock_client

        result = run(s.run("build chat app", rounds=1, roster=["coder", "critic"]))
        self.assertTrue(result["ok"])
        self.assertEqual(result["roster"], ["coder", "critic"])
        # 2 agents × 1 round + 1 synthesis = 3 calls minimum
        self.assertGreaterEqual(mock_client.models.generate_content.call_count, 3)
        # transcript should have 2 entries (2 agents thought once)
        self.assertEqual(len(result["transcript"]), 2)

    def test_run_multiple_rounds_produces_more_transcript(self):
        mock_client = MagicMock()
        r = MagicMock()
        r.text = "output"
        mock_client.models.generate_content.return_value = r

        s = Swarm(console=None)
        s.client = mock_client
        result = run(s.run("goal", rounds=2, roster=["coder"]))
        # 1 agent × 2 rounds = 2 transcript entries
        self.assertEqual(len(result["transcript"]), 2)

    def test_synthesize_falls_back_when_client_fails(self):
        s = Swarm(console=None)
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("boom")
        s.client = mock_client
        bb = Blackboard()
        run(bb.post("a1", "coder", "stuff"))
        result = run(s._synthesize("goal", bb))
        # fallback returns blackboard rendering
        self.assertIn("stuff", result)

    def test_specialist_prompts_complete(self):
        for role in ["architect", "coder", "critic", "researcher", "planner"]:
            self.assertIn(role, SPECIALIST_PROMPTS)
            self.assertIn(role.upper(), SPECIALIST_PROMPTS[role])


if __name__ == "__main__":
    unittest.main(verbosity=2)

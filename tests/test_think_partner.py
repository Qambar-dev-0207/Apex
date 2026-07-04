"""
Tests for src/services/think_partner.py

Covers:
  - Pattern triggers (regex heuristic for auto-routing)
  - Each of the 6 capabilities with mocked Gemini
  - JSON parsing fallbacks for malformed responses
"""

import asyncio
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.think_partner import ThinkPartner, detect_think_mode, should_extract_intent


def run(coro):
    return asyncio.run(coro)


# ════════════════════════════════════════════════════════════════════════════
# 1. Pattern detection — pure regex
# ════════════════════════════════════════════════════════════════════════════

class TestDetectThinkMode(unittest.TestCase):

    def test_architect_build(self):
        self.assertEqual(detect_think_mode("I want to build a Slack clone"), "architect")
        self.assertEqual(detect_think_mode("design a recommendation system"), "architect")
        self.assertEqual(detect_think_mode("How should I build a REST API?"), "architect")
        self.assertEqual(detect_think_mode("Architect a microservice for billing"), "architect")

    def test_debate_decision(self):
        self.assertEqual(detect_think_mode("Should I use Postgres or MongoDB?"), "debate")
        self.assertEqual(detect_think_mode("Which is better, Redis or memcached?"), "debate")
        self.assertEqual(detect_think_mode("What are the trade-offs of GraphQL?"), "debate")
        self.assertEqual(detect_think_mode("Is it worth migrating to TypeScript?"), "debate")

    def test_brainstorm(self):
        self.assertEqual(detect_think_mode("brainstorm ideas for a hackathon"), "brainstorm")
        self.assertEqual(detect_think_mode("ideas for reducing API latency"), "brainstorm")
        self.assertEqual(detect_think_mode("alternatives to webpack"), "brainstorm")
        self.assertEqual(detect_think_mode("what if we cached everything?"), "brainstorm")

    def test_teach(self):
        self.assertEqual(detect_think_mode("explain how transformers work"), "teach")
        self.assertEqual(detect_think_mode("teach me about CRDTs"), "teach")
        self.assertEqual(detect_think_mode("what is a B-tree?"), "teach")
        self.assertEqual(detect_think_mode("help me understand event sourcing"), "teach")

    def test_no_match_returns_none(self):
        self.assertIsNone(detect_think_mode("write a function to parse JSON"))
        self.assertIsNone(detect_think_mode("git status"))
        self.assertIsNone(detect_think_mode("delete the temp file"))

    def test_priority_order(self):
        # "build" should win over "what if" in same prompt
        self.assertEqual(detect_think_mode("I want to build a system. What if it scales?"), "architect")

    def test_expanded_decide_patterns(self):
        self.assertEqual(detect_think_mode("compare Postgres and MySQL"), "debate")
        self.assertEqual(detect_think_mode("Postgres vs MySQL"), "debate")
        self.assertEqual(detect_think_mode("convince me to use Rust"), "debate")

    def test_expanded_architect_patterns(self):
        self.assertEqual(detect_think_mode("review my architecture"), "architect")
        self.assertEqual(detect_think_mode("feedback on my design"), "architect")
        self.assertEqual(detect_think_mode("how do I get started with this?"), "architect")
        self.assertEqual(detect_think_mode("considering building a CRM"), "architect")
        self.assertEqual(detect_think_mode("planning to build an SaaS"), "architect")

    def test_expanded_help_patterns(self):
        self.assertEqual(detect_think_mode("stuck on a perf issue"), "cross_question")
        self.assertEqual(detect_think_mode("having trouble with auth"), "cross_question")
        self.assertEqual(detect_think_mode("can't figure out how to scale"), "cross_question")

    def test_expanded_teach_patterns(self):
        self.assertEqual(detect_think_mode("walk me through OAuth"), "teach")
        self.assertEqual(detect_think_mode("break down how kafka works"), "teach")


# ════════════════════════════════════════════════════════════════════════════
# 1b. should_extract_intent gate
# ════════════════════════════════════════════════════════════════════════════

class TestShouldExtractIntent(unittest.TestCase):

    def test_short_text_skipped(self):
        self.assertFalse(should_extract_intent("hi"))
        self.assertFalse(should_extract_intent("git status"))

    def test_command_like_skipped(self):
        self.assertFalse(should_extract_intent("delete the old config files now"))
        self.assertFalse(should_extract_intent("git push origin main"))
        self.assertFalse(should_extract_intent("npm install all the dependencies"))
        self.assertFalse(should_extract_intent("rename foo.py to bar.py please"))

    def test_few_words_skipped(self):
        self.assertFalse(should_extract_intent("looks good now ok"))

    def test_substantive_prompt_extracted(self):
        self.assertTrue(should_extract_intent("I'd like to discuss the trade-offs of various caching strategies"))
        self.assertTrue(should_extract_intent("can you help me think through this database choice for my new project"))


# ════════════════════════════════════════════════════════════════════════════
# 1c. auto_route — combines regex + LLM + ambiguity gate
# ════════════════════════════════════════════════════════════════════════════

class TestAutoRoute(unittest.TestCase):

    def setUp(self):
        self.tp = ThinkPartner(console=None)

    def test_regex_match_returns_immediately(self):
        # No client needed — regex tier 1 short-circuits before LLM call
        self.tp.client = None
        result = run(self.tp.auto_route("I want to build a Slack clone"))
        self.assertEqual(result["mode"], "architect")
        self.assertEqual(result["source"], "regex")

    def test_skip_for_short_prompts(self):
        result = run(self.tp.auto_route("hi"))
        self.assertEqual(result["mode"], "execute")
        self.assertEqual(result["source"], "skip")

    def test_skip_for_command_like(self):
        result = run(self.tp.auto_route("git push origin main"))
        self.assertEqual(result["mode"], "execute")
        self.assertEqual(result["source"], "skip")

    def test_intent_extraction_used_for_substantive(self):
        intent_response = json.dumps({
            "primary_intent": "build",
            "explicit_goal": "make a chat app",
            "implicit_goal": "real-time messaging",
            "ambiguity_score": 0.3,
            "needs_clarification": False,
            "blocking_questions": [],
            "sub_tasks": [],
            "recommended_mode": "architect",
        })
        mock_resp = MagicMock()
        mock_resp.text = intent_response
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        self.tp.client = mock_client

        # phrasing avoids regex matchers ("set up", no "build", no "compare", etc.)
        result = run(self.tp.auto_route("kindly set up a small messaging service for my team chat needs"))
        self.assertEqual(result["mode"], "architect")
        self.assertEqual(result["source"], "intent")

    def test_high_ambiguity_overrides_to_cross_question(self):
        intent_response = json.dumps({
            "primary_intent": "build",
            "explicit_goal": "do something",
            "implicit_goal": "unclear",
            "ambiguity_score": 0.9,
            "needs_clarification": True,
            "blocking_questions": ["What scale?", "Who's the user?"],
            "sub_tasks": [],
            "recommended_mode": "execute",  # intent says execute but ambiguity should override
        })
        mock_resp = MagicMock()
        mock_resp.text = intent_response
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        self.tp.client = mock_client

        result = run(self.tp.auto_route("please go ahead and do the thing for the people now"))
        self.assertEqual(result["mode"], "cross_question")
        self.assertEqual(result["source"], "ambiguity")
        self.assertEqual(len(result["blocking_questions"]), 2)

    def test_low_ambiguity_concrete_returns_execute(self):
        intent_response = json.dumps({
            "primary_intent": "automate",
            "explicit_goal": "rename test files",
            "implicit_goal": "rename test files",
            "ambiguity_score": 0.1,
            "needs_clarification": False,
            "blocking_questions": [],
            "sub_tasks": [{"task": "rename", "depends_on": [], "tool_hint": "filesystem", "effort": "S"}],
            "recommended_mode": "execute",
        })
        mock_resp = MagicMock()
        mock_resp.text = intent_response
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        self.tp.client = mock_client

        result = run(self.tp.auto_route("rename all the test_*.py files to spec_*.py recursively"))
        self.assertEqual(result["mode"], "execute")


# ════════════════════════════════════════════════════════════════════════════
# 2. ThinkPartner methods — mocked Gemini
# ════════════════════════════════════════════════════════════════════════════

class TestThinkPartnerCrossQuestion(unittest.TestCase):

    def setUp(self):
        self.tp = ThinkPartner(console=None)

    def test_no_client_returns_safe_default(self):
        self.tp.client = None
        result = run(self.tp.cross_question("ambiguous prompt"))
        self.assertEqual(result["mode"], "cross_question")
        self.assertEqual(result["questions"], [])

    def test_returns_questions_when_ambiguous(self):
        json_response = json.dumps({
            "ambiguity_score": 0.8,
            "interpretation": "build a chat app",
            "questions": [
                {"q": "Real-time or polling?", "why_it_matters": "stack choice", "default_assumption": "real-time"},
                {"q": "Auth required?", "why_it_matters": "scope", "default_assumption": "yes"},
            ],
            "ready_to_proceed_without_answers": False,
            "minimal_must_answer": ["Real-time or polling?"],
        })
        mock_resp = MagicMock()
        mock_resp.text = json_response
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        self.tp.client = mock_client

        result = run(self.tp.cross_question("build a chat thing"))
        self.assertEqual(len(result["questions"]), 2)
        self.assertEqual(result["ambiguity_score"], 0.8)
        self.assertIn("Real-time or polling?", result["must_answer"])

    def test_handles_malformed_json(self):
        mock_resp = MagicMock()
        mock_resp.text = "not valid json {"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        self.tp.client = mock_client

        result = run(self.tp.cross_question("anything"))
        self.assertEqual(result["mode"], "cross_question")
        self.assertEqual(result["questions"], [])


class TestThinkPartnerArchitect(unittest.TestCase):

    def setUp(self):
        self.tp = ThinkPartner(console=None)

    def test_no_client_returns_message(self):
        self.tp.client = None
        result = run(self.tp.architect("build a CRM"))
        self.assertEqual(result["mode"], "architect")
        self.assertIn("Gemini key", result["output"])

    def test_returns_markdown_output(self):
        markdown_response = """
## 1. Optimal Architecture
- FastAPI + Postgres + Redis

## 2. Critique
- Skip — no user arch

## 3. Synthesis
- Mine wins
""".strip()
        mock_resp = MagicMock()
        mock_resp.text = markdown_response
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        self.tp.client = mock_client

        result = run(self.tp.architect("build a CRM"))
        self.assertEqual(result["mode"], "architect")
        self.assertIn("Optimal Architecture", result["output"])

    def test_includes_user_arch_in_prompt(self):
        captured = {}

        def fake_gen(*args, **kwargs):
            captured["prompt"] = kwargs.get("contents", "")
            r = MagicMock()
            r.text = "## response"
            return r

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = fake_gen
        self.tp.client = mock_client

        run(self.tp.architect("build a chat", user_architecture="React + Firebase"))
        self.assertIn("React + Firebase", captured["prompt"])


class TestThinkPartnerDebate(unittest.TestCase):

    def setUp(self):
        self.tp = ThinkPartner(console=None)

    def test_no_client_returns_message(self):
        self.tp.client = None
        result = run(self.tp.debate("microservices are always better"))
        self.assertEqual(result["mode"], "debate")
        self.assertIn("Gemini key", result["output"])

    def test_returns_steelman_output(self):
        mock_resp = MagicMock()
        mock_resp.text = "## Strongest Counter-Argument\n- Monoliths win at small scale"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        self.tp.client = mock_client

        result = run(self.tp.debate("microservices are always better"))
        self.assertIn("Counter-Argument", result["output"])


class TestThinkPartnerBrainstorm(unittest.TestCase):

    def setUp(self):
        self.tp = ThinkPartner(console=None)

    def test_returns_brainstorm_output(self):
        mock_resp = MagicMock()
        mock_resp.text = "1. **Lens**: First principles\n   - Idea: foo\n   - Why win: x\n   - Why fail: y"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        self.tp.client = mock_client

        result = run(self.tp.brainstorm("reduce latency"))
        self.assertEqual(result["mode"], "brainstorm")
        self.assertIn("Lens", result["output"])

    def test_n_param_in_prompt(self):
        captured = {}

        def fake_gen(*args, **kwargs):
            captured["prompt"] = kwargs.get("contents", "")
            r = MagicMock()
            r.text = "ideas"
            return r

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = fake_gen
        self.tp.client = mock_client

        run(self.tp.brainstorm("topic", n=4))
        self.assertIn("4", captured["prompt"])


class TestThinkPartnerTeach(unittest.TestCase):

    def setUp(self):
        self.tp = ThinkPartner(console=None)

    def test_returns_layered_explanation(self):
        mock_resp = MagicMock()
        mock_resp.text = "## Intuition\nMetaphor.\n## Mechanism\nDetails."
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        self.tp.client = mock_client

        result = run(self.tp.teach("event sourcing"))
        self.assertEqual(result["mode"], "teach")
        self.assertIn("Intuition", result["output"])


class TestThinkPartnerExtractIntent(unittest.TestCase):

    def setUp(self):
        self.tp = ThinkPartner(console=None)

    def test_no_client_returns_default(self):
        self.tp.client = None
        result = run(self.tp.extract_intent("do the thing"))
        self.assertEqual(result["mode"], "extract_intent")
        self.assertEqual(result["recommended_mode"], "execute")

    def test_returns_structured_intent(self):
        json_response = json.dumps({
            "primary_intent": "build",
            "explicit_goal": "make a chat app",
            "implicit_goal": "real-time messaging POC",
            "ambiguity_score": 0.7,
            "needs_clarification": True,
            "blocking_questions": ["websockets or polling?"],
            "sub_tasks": [
                {"task": "scaffold backend", "depends_on": [], "tool_hint": "filesystem", "effort": "M"},
            ],
            "recommended_mode": "architect",
        })
        mock_resp = MagicMock()
        mock_resp.text = json_response
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        self.tp.client = mock_client

        result = run(self.tp.extract_intent("make a chat app"))
        self.assertEqual(result["primary_intent"], "build")
        self.assertEqual(result["recommended_mode"], "architect")
        self.assertEqual(len(result["sub_tasks"]), 1)

    def test_malformed_json_returns_safe_default(self):
        mock_resp = MagicMock()
        mock_resp.text = "{ malformed"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_resp
        self.tp.client = mock_client

        result = run(self.tp.extract_intent("something"))
        self.assertEqual(result["mode"], "extract_intent")
        self.assertEqual(result["recommended_mode"], "execute")
        self.assertEqual(result["sub_tasks"], [])


# ════════════════════════════════════════════════════════════════════════════
# 3. Construction smoke
# ════════════════════════════════════════════════════════════════════════════

class TestThinkPartnerConstruction(unittest.TestCase):

    def test_init_without_api_key(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}, clear=False):
            # explicit clear
            import os
            os.environ.pop("GEMINI_API_KEY", None)
            tp = ThinkPartner(console=None)
            # client may be None if no key — that's the safe path
            self.assertEqual(tp.model_id, "gemini-3.5-flash")

    def test_default_model_ids(self):
        tp = ThinkPartner(console=None)
        self.assertEqual(tp.model_id, "gemini-3.5-flash")
        self.assertEqual(tp.deep_model_id, "gemini-2.5-pro")

    def test_custom_model_ids(self):
        tp = ThinkPartner(console=None, model_id="custom-fast", deep_model_id="custom-deep")
        self.assertEqual(tp.model_id, "custom-fast")
        self.assertEqual(tp.deep_model_id, "custom-deep")


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""
Tests for EmotionalCore fixes, WeatherTool, ApiConnectorTool, and ParallelExecutor integration.
"""

import asyncio
import os
import unittest
from pathlib import Path

from src.services.cognitive import EmotionalCore
from src.tools.weather_tool import WeatherTool
from src.tools.api_connector import ApiConnectorTool, mask_key, save_key_to_env
from src.tools.auto_selector import regex_match
from src.tools.registry import resolve_tool_name, get_spec
from src.routers.router import ParallelExecutor


def run(coro):
    return asyncio.run(coro)


class TestEmotionalCore(unittest.TestCase):
    def setUp(self):
        self.core = EmotionalCore()

    def test_analyze_input_returns_emotional_state(self):
        query = "connect to a free weather api to fetch the latest so next time ask you ,you should be able to fetch it for me"
        state = self.core.analyze_input(query)
        self.assertIsNotNone(state)
        self.assertIn(state.sentiment, ["neutral", "stressed", "excited", "frustrated"])
        self.assertIn(state.cognitive_load, ["low", "medium", "high"])

    def test_analyze_input_stressed_heuristic(self):
        state = self.core.analyze_input("urgent! critical bug in production, hurry up!")
        self.assertEqual(state.sentiment, "stressed")
        self.assertEqual(state.cognitive_load, "high")

    def test_analyze_input_excited_heuristic(self):
        state = self.core.analyze_input("wow awesome work, this is amazing! let's go!")
        self.assertEqual(state.sentiment, "excited")

    def test_get_system_personality_prompt(self):
        self.core.analyze_input("hello apex")
        prompt = self.core.get_system_personality_prompt()
        self.assertIsInstance(prompt, str)
        self.assertIn("[APEX_STATE]", prompt)
        self.assertIn("[TONE_DIRECTIVE]", prompt)


class TestWeatherTool(unittest.TestCase):
    def setUp(self):
        self.weather = WeatherTool()

    def test_tool_registered(self):
        self.assertEqual(resolve_tool_name("weather"), "weather")
        self.assertEqual(resolve_tool_name("meteo"), "weather")
        spec = get_spec("weather")
        self.assertIsNotNone(spec)
        self.assertIn("current", spec.actions)
        self.assertIn("forecast", spec.actions)
        self.assertIn("connect", spec.actions)

    def test_weather_connect(self):
        res = run(self.weather.execute("connect", ""))
        self.assertTrue(res["success"])
        self.assertIn("WEATHER API CONNECTED", res["output"])

    def test_weather_current_london(self):
        res = run(self.weather.execute("current", "London"))
        self.assertTrue(res["success"])
        self.assertIn("London", res["output"])
        self.assertIn("Temperature:", res["output"])

    def test_weather_forecast_tokyo(self):
        res = run(self.weather.execute("forecast", {"location": "Tokyo", "days": 3}))
        self.assertTrue(res["success"])
        self.assertIn("Tokyo", res["output"])
        self.assertIn("Forecast", res["output"])


class TestApiConnector(unittest.TestCase):
    def setUp(self):
        self.api = ApiConnectorTool()

    def test_tool_registered(self):
        self.assertEqual(resolve_tool_name("api_connector"), "api_connector")
        self.assertEqual(resolve_tool_name("api"), "api_connector")
        self.assertEqual(resolve_tool_name("credentials"), "api_connector")

    def test_mask_key(self):
        self.assertEqual(mask_key("sk-1234567890abcdef"), "sk-...cdef")
        self.assertEqual(mask_key("short"), "*****")

    def test_request_key(self):
        res = run(self.api.execute("request_key", {"service": "WeatherAPI", "key_name": "WEATHER_API_KEY"}))
        self.assertTrue(res["success"])
        self.assertIn("WEATHER_API_KEY", res["output"])

    def test_save_key(self):
        test_env = os.path.join(os.getcwd(), "tests", "test_temp.env")
        try:
            ok = save_key_to_env("TEST_APEX_KEY", "dummy_val_1234", env_path=test_env)
            self.assertTrue(ok)
            self.assertEqual(os.getenv("TEST_APEX_KEY"), "dummy_val_1234")
        finally:
            if os.path.exists(test_env):
                os.remove(test_env)


class TestAutoSelectorWeather(unittest.TestCase):
    def test_connect_weather_api_pattern(self):
        match = regex_match("connect to a free weather api to fetch the latest so next time ask you ,you should be able to fetch it for me")
        self.assertIsNotNone(match)
        self.assertEqual(match["tool"], "weather")
        self.assertEqual(match["action"], "connect")

    def test_weather_in_city_pattern(self):
        match = regex_match("what is the weather in London")
        self.assertIsNotNone(match)
        self.assertEqual(match["tool"], "weather")
        self.assertEqual(match["action"], "current")
        self.assertEqual(match["input_data"], "London")

    def test_temperature_in_city_pattern(self):
        match = regex_match("temperature in Tokyo?")
        self.assertIsNotNone(match)
        self.assertEqual(match["tool"], "weather")
        self.assertEqual(match["action"], "current")
        self.assertEqual(match["input_data"], "Tokyo")

    def test_save_api_key_pattern(self):
        match = regex_match("save api key WEATHER_API_KEY xyz_sample_token")
        self.assertIsNotNone(match)
        self.assertEqual(match["tool"], "api_connector")
        self.assertEqual(match["action"], "save_key")


class TestParallelExecutorIntegration(unittest.TestCase):
    def setUp(self):
        self.executor = ParallelExecutor()

    def test_execute_weather_step(self):
        step = {
            "id": 1,
            "tool": "weather",
            "action": "current",
            "input_data": "Paris",
            "dependencies": [],
        }
        res = run(self.executor.execute_step(step))
        self.assertTrue(res["success"])
        self.assertIn("Paris", res["output"])


if __name__ == "__main__":
    unittest.main()

"""
Tests for src/core/time_context.py

Pure logic — no I/O, no LLM. Fast.
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.time_context import TimeContext


# Helper: freeze datetime.now() for deterministic tests
def freeze(year, month, day, hour=12, minute=0):
    fake = datetime(year, month, day, hour, minute)

    class _DT(datetime):
        @classmethod
        def now(cls, tz=None):
            return fake
    return patch("src.core.time_context.datetime", _DT)


class TestTimeOfDay(unittest.TestCase):

    def test_morning(self):
        with freeze(2026, 5, 8, 7):
            self.assertEqual(TimeContext.time_of_day(), "morning")

    def test_afternoon(self):
        with freeze(2026, 5, 8, 14):
            self.assertEqual(TimeContext.time_of_day(), "afternoon")

    def test_evening(self):
        with freeze(2026, 5, 8, 19):
            self.assertEqual(TimeContext.time_of_day(), "evening")

    def test_night(self):
        with freeze(2026, 5, 8, 23):
            self.assertEqual(TimeContext.time_of_day(), "night")

    def test_dawn_edge(self):
        # 5:00 → morning
        with freeze(2026, 5, 8, 5, 0):
            self.assertEqual(TimeContext.time_of_day(), "morning")
        # 4:59 → night
        with freeze(2026, 5, 8, 4, 59):
            self.assertEqual(TimeContext.time_of_day(), "night")


class TestGreeting(unittest.TestCase):

    def test_morning_greeting(self):
        with freeze(2026, 5, 8, 9):
            self.assertEqual(TimeContext.greeting(), "Good morning")

    def test_night_falls_back_to_hello(self):
        with freeze(2026, 5, 8, 23):
            self.assertEqual(TimeContext.greeting(), "Hello")


class TestWeekend(unittest.TestCase):

    def test_saturday_is_weekend(self):
        # 2026-05-09 is Saturday
        with freeze(2026, 5, 9, 12):
            self.assertTrue(TimeContext.is_weekend())

    def test_monday_is_weekday(self):
        # 2026-05-11 is Monday
        with freeze(2026, 5, 11, 12):
            self.assertFalse(TimeContext.is_weekend())


class TestLateNight(unittest.TestCase):

    def test_2am_is_late(self):
        with freeze(2026, 5, 8, 2):
            self.assertTrue(TimeContext.is_late_night())

    def test_11pm_is_late(self):
        with freeze(2026, 5, 8, 23):
            self.assertTrue(TimeContext.is_late_night())

    def test_10pm_not_late(self):
        with freeze(2026, 5, 8, 22):
            self.assertFalse(TimeContext.is_late_night())

    def test_5am_not_late(self):
        with freeze(2026, 5, 8, 5):
            self.assertFalse(TimeContext.is_late_night())


class TestRelative(unittest.TestCase):

    def test_just_now(self):
        with freeze(2026, 5, 8, 12, 0):
            self.assertEqual(
                TimeContext.relative(datetime(2026, 5, 8, 12, 0, 0)),
                "just now",
            )

    def test_minutes_ago(self):
        with freeze(2026, 5, 8, 12, 30):
            self.assertEqual(
                TimeContext.relative(datetime(2026, 5, 8, 12, 25)),
                "5 min ago",
            )

    def test_hours_ago(self):
        with freeze(2026, 5, 8, 12, 0):
            self.assertEqual(
                TimeContext.relative(datetime(2026, 5, 8, 9, 0)),
                "3 hours ago",
            )

    def test_yesterday(self):
        with freeze(2026, 5, 8, 12, 0):
            self.assertEqual(
                TimeContext.relative(datetime(2026, 5, 7, 10, 0)),
                "yesterday",
            )

    def test_days_ago(self):
        with freeze(2026, 5, 8, 12, 0):
            result = TimeContext.relative(datetime(2026, 5, 5, 12, 0))
            self.assertIn("days ago", result)

    def test_iso_string_input(self):
        with freeze(2026, 5, 8, 12, 0):
            result = TimeContext.relative("2026-05-08T11:30:00")
            self.assertEqual(result, "30 min ago")

    def test_unix_timestamp_input(self):
        with freeze(2026, 5, 8, 12, 0):
            ts = datetime(2026, 5, 8, 11, 0).timestamp()
            result = TimeContext.relative(ts)
            self.assertIn("hour", result.lower())

    def test_future_timestamp(self):
        with freeze(2026, 5, 8, 12, 0):
            result = TimeContext.relative(datetime(2026, 5, 9, 12, 0))
            self.assertEqual(result, "in the future")

    def test_none_input(self):
        self.assertEqual(TimeContext.relative(None), "unknown")

    def test_garbage_string(self):
        result = TimeContext.relative("not-a-date")
        self.assertEqual(result, "not-a-date")


class TestSystemPrefix(unittest.TestCase):

    def test_contains_time(self):
        with freeze(2026, 5, 8, 14, 30):
            prefix = TimeContext.system_prefix()
            self.assertIn("TIME:", prefix)
            self.assertIn("2026", prefix)
            self.assertIn("14:30", prefix)
            self.assertIn("afternoon", prefix)

    def test_marks_weekend(self):
        with freeze(2026, 5, 9, 12, 0):  # Saturday
            self.assertIn("weekend", TimeContext.system_prefix())

    def test_marks_late_night(self):
        with freeze(2026, 5, 8, 2, 0):
            self.assertIn("late-night", TimeContext.system_prefix())


class TestIsGreeting(unittest.TestCase):

    def test_simple_greetings(self):
        for g in ["hi", "hello", "hey", "yo", "sup", "howdy", "greetings"]:
            self.assertTrue(TimeContext.is_greeting(g), f"failed: {g}")

    def test_with_punctuation(self):
        self.assertTrue(TimeContext.is_greeting("hi!"))
        self.assertTrue(TimeContext.is_greeting("hello."))
        self.assertTrue(TimeContext.is_greeting("hey?"))

    def test_compound_greetings(self):
        self.assertTrue(TimeContext.is_greeting("good morning"))
        self.assertTrue(TimeContext.is_greeting("Good Evening"))
        self.assertTrue(TimeContext.is_greeting("what's up"))
        self.assertTrue(TimeContext.is_greeting("hi apex"))

    def test_not_greeting_when_has_request(self):
        self.assertFalse(TimeContext.is_greeting("hi can you help me with code"))
        self.assertFalse(TimeContext.is_greeting("hello world program"))

    def test_empty_input(self):
        self.assertFalse(TimeContext.is_greeting(""))
        self.assertFalse(TimeContext.is_greeting("   "))

    def test_too_long_input(self):
        long = "hi " * 30
        self.assertFalse(TimeContext.is_greeting(long))


class TestCraftGreetingResponse(unittest.TestCase):

    def test_morning_response(self):
        with freeze(2026, 5, 11, 9, 0):  # Monday morning
            r = TimeContext.craft_greeting_response()
            self.assertIn("Monday", r)
            self.assertIn("morning", r.lower())

    def test_late_night_response(self):
        with freeze(2026, 5, 8, 2, 0):
            r = TimeContext.craft_greeting_response()
            self.assertIn("late", r.lower())

    def test_response_is_string(self):
        with freeze(2026, 5, 8, 14, 0):
            r = TimeContext.craft_greeting_response()
            self.assertIsInstance(r, str)
            self.assertGreater(len(r), 0)


class TestNowHuman(unittest.TestCase):

    def test_format(self):
        with freeze(2026, 5, 8, 14, 30):
            r = TimeContext.now_human()
            self.assertIn("2026", r)
            self.assertIn("May", r)
            self.assertIn("Friday", r)


if __name__ == "__main__":
    unittest.main(verbosity=2)

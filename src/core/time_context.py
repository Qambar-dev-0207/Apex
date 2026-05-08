"""
TimeContext — APEX's awareness of current time and date.

Single source of truth. Injected into every LLM system prompt via
`system_prefix()` so models always know wall-clock time without the user
having to mention it.

Provides:
  - now()/now_iso/now_human          formatted current time
  - time_of_day()                    morning/afternoon/evening/night
  - greeting()                       "Good morning" etc — for human-feel greetings
  - weekday()/is_weekend/is_late_night
  - relative(ts)                     human delta — "3 hours ago", "yesterday"
  - system_prefix()                  one-line block to prepend to LLM prompts
  - is_greeting(text)                cheap regex for inbound greeting detection
"""

import re
from datetime import datetime, timedelta
from typing import Union


_GREETING_RE = re.compile(
    r"^\s*("
    r"hi|hello|hey|yo|sup|"
    r"good\s*(?:morning|afternoon|evening|night)|"
    r"morning|evening|"
    r"what'?s up|whats up|wassup|"
    r"howdy|greetings|"
    r"hi apex|hey apex|hello apex"
    r")[\s!.?,]*$",
    re.IGNORECASE,
)


class TimeContext:
    """Static helpers — no state. Reads current clock on each call."""

    @staticmethod
    def now() -> datetime:
        return datetime.now()

    @staticmethod
    def now_iso() -> str:
        return datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def now_human() -> str:
        """e.g. 'Wednesday, 8 May 2026, 03:42 PM'"""
        return datetime.now().strftime("%A, %d %B %Y, %I:%M %p")

    @staticmethod
    def time_of_day() -> str:
        h = datetime.now().hour
        if 5 <= h < 12:
            return "morning"
        if 12 <= h < 17:
            return "afternoon"
        if 17 <= h < 21:
            return "evening"
        return "night"

    @staticmethod
    def greeting() -> str:
        """'Good morning/afternoon/evening' — 'Good night' rare, replaced with 'Hello' after 21h."""
        tod = TimeContext.time_of_day()
        if tod == "night":
            # 'good night' is a farewell, not a greeting — use neutral
            return "Hello"
        return f"Good {tod}"

    @staticmethod
    def weekday() -> str:
        return datetime.now().strftime("%A")

    @staticmethod
    def is_weekend() -> bool:
        return datetime.now().weekday() >= 5

    @staticmethod
    def is_late_night() -> bool:
        h = datetime.now().hour
        return h >= 23 or h < 5

    @staticmethod
    def relative(ts: Union[str, int, float, datetime, None]) -> str:
        """Human-readable delta from now. Handles ISO str, unix ts, datetime."""
        # Re-import datetime locally so isinstance() check survives test patches
        # that replace module-level `datetime` with a subclass.
        from datetime import datetime as _dt
        if ts is None:
            return "unknown"
        dt: _dt
        if isinstance(ts, _dt):
            dt = ts
        elif isinstance(ts, (int, float)):
            try:
                dt = _dt.fromtimestamp(ts)
            except Exception:
                return str(ts)
        elif isinstance(ts, str):
            try:
                dt = _dt.fromisoformat(ts.replace("Z", "+00:00"))
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
            except Exception:
                return ts
        else:
            return str(ts)

        delta = datetime.now() - dt
        secs = delta.total_seconds()
        if secs < 0:
            return "in the future"
        if secs < 30:
            return "just now"
        if secs < 60:
            return f"{int(secs)}s ago"
        if secs < 3600:
            return f"{int(secs / 60)} min ago"
        if secs < 7200:
            return "an hour ago"
        if secs < 86400:
            return f"{int(secs / 3600)} hours ago"
        if secs < 172800:
            return "yesterday"
        if secs < 604800:
            return f"{int(secs / 86400)} days ago"
        if secs < 1209600:
            return "last week"
        if secs < 2592000:
            return f"{int(secs / 604800)} weeks ago"
        if secs < 5184000:
            return "last month"
        if secs < 31536000:
            return f"{int(secs / 2592000)} months ago"
        return f"{int(secs / 31536000)} year(s) ago"

    @staticmethod
    def system_prefix() -> str:
        """
        Block prepended to every LLM system prompt. Compact — one line —
        so it doesn't bloat context but model always knows wall time.
        """
        now = datetime.now()
        return (
            f"[TIME: {now.strftime('%a %d %b %Y, %H:%M')} "
            f"({TimeContext.time_of_day()}, "
            f"{'weekend' if TimeContext.is_weekend() else 'weekday'}"
            f"{', late-night' if TimeContext.is_late_night() else ''})]"
        )

    @staticmethod
    def is_greeting(text: str) -> bool:
        """True if input is a bare greeting (short, salutation-only)."""
        if not text or len(text.strip()) > 40:
            return False
        return bool(_GREETING_RE.match(text))

    @staticmethod
    def craft_greeting_response(user_name: str = "") -> str:
        """Generate a context-aware greeting reply."""
        tod = TimeContext.time_of_day()
        weekday = TimeContext.weekday()
        late = TimeContext.is_late_night()

        if late:
            base = "Up late — what's the mission?"
        elif tod == "morning":
            base = f"Good morning. {weekday} — what's first?"
        elif tod == "afternoon":
            base = f"Good {tod}. What are we working on?"
        elif tod == "evening":
            base = "Good evening. What's the play?"
        else:
            base = "Hello. What do you need?"

        if user_name:
            base = base.replace("Good ", f"Good ", 1)  # placeholder for future name use
        return base

"""
API Security — centralized key management, error sanitization, and threat detection.

Responsibilities:
  - Mask API keys in error messages so they never appear in logs or UI
  - Detect leaked/revoked keys and surface an actionable warning
  - Validate key format at startup so bad configs fail fast
  - Backoff helper for rate-limited (429) requests
"""

import re
import asyncio
import os
from enum import Enum
from typing import Optional, Tuple


# ── key masking ───────────────────────────────────────────────────────────────

# Patterns that look like API keys in error strings
_KEY_PATTERNS = [
    re.compile(r"\bAIza[A-Za-z0-9_\-]{30,}\b"),          # Google/Gemini
    re.compile(r"\bgsk_[A-Za-z0-9]{20,}\b"),              # Groq
    re.compile(r"\bsk-or-[A-Za-z0-9_\-]{20,}\b"),        # OpenRouter
    re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"),           # OpenAI-style
    re.compile(r"\b[A-Za-z0-9]{32,64}\b"),                # Generic long token (last resort)
]


def mask_key(key: str) -> str:
    """Return a safe display version: first 4 + *** + last 4."""
    if not key or len(key) < 12:
        return "***"
    return f"{key[:4]}***{key[-4:]}"


def sanitize_error(exc: BaseException) -> str:
    """
    Convert an exception to a safe string with API keys redacted.
    Never let raw API errors reach the UI with key material in them.
    """
    raw = str(exc)
    result = raw
    for pattern in _KEY_PATTERNS[:-1]:  # skip generic last-resort in normal pass
        result = pattern.sub("[REDACTED]", result)
    # Only apply generic pattern if result is long and still looks like it has a token
    if len(result) > 80:
        result = _KEY_PATTERNS[-1].sub(
            lambda m: "[REDACTED]" if len(m.group()) > 40 else m.group(), result
        )
    return result


# ── key format validation ─────────────────────────────────────────────────────

# Minimum accepted key lengths per provider
_KEY_MIN_LEN = {
    "GEMINI_API_KEY": 30,
    "GROQ_API_KEY": 20,
    "OPENROUTER_API_KEY": 20,
    "MIMO_API_KEY": 10,
    "MINIMAX_API_KEY": 10,
    "TAVILY_API_KEY": 10,
    "BRAVE_API_KEY": 10,
}

# Known placeholder / test values that should not be used
_PLACEHOLDER_VALUES = frozenset({
    "your_key_here", "your_api_key_here", "your_gemini_api_key_here",
    "your_groq_key_here", "your_openrouter_key_here", "your_mimo_key_here",
    "changeme", "test", "placeholder", "xxx", "none", "null", "",
})


def validate_key(env_var: str, value: Optional[str]) -> Tuple[bool, str]:
    """
    Returns (is_valid, reason). Checks format without making a network call.
    """
    if not value:
        return False, f"{env_var} not set"
    stripped = value.strip()
    if stripped.lower() in _PLACEHOLDER_VALUES:
        return False, f"{env_var} contains placeholder value"
    min_len = _KEY_MIN_LEN.get(env_var, 8)
    if len(stripped) < min_len:
        return False, f"{env_var} too short (min {min_len} chars)"
    return True, "ok"


def validate_all_keys() -> list[Tuple[str, bool, str]]:
    """
    Validate all known API keys from environment.
    Returns list of (env_var, is_valid, reason).
    """
    results = []
    for var in _KEY_MIN_LEN:
        val = os.getenv(var)
        if val is None:
            continue  # not set at all — not an error, just offline
        ok, reason = validate_key(var, val)
        results.append((var, ok, reason))
    return results


# ── threat detection ──────────────────────────────────────────────────────────

class KeyThreat(Enum):
    NONE = "none"
    LEAKED = "leaked"       # key was reported as leaked/compromised
    REVOKED = "revoked"     # key was disabled/revoked by provider
    INVALID = "invalid"     # wrong key, bad format at API level
    RATE_LIMITED = "rate_limited"
    QUOTA = "quota"         # quota exhausted (not a security threat)


_THREAT_PATTERNS = [
    (KeyThreat.LEAKED,   re.compile(r"reported as leaked|key.*leaked|compromised", re.I)),
    (KeyThreat.LEAKED,   re.compile(r"api key has been disabled|key disabled", re.I)),
    (KeyThreat.REVOKED,  re.compile(r"api key.*revoked|revoked.*api key", re.I)),
    (KeyThreat.INVALID,  re.compile(r"invalid api key|api_key_invalid|incorrect api key", re.I)),
    (KeyThreat.RATE_LIMITED, re.compile(r"rate.limit|too.many.requests|429", re.I)),
    (KeyThreat.QUOTA,    re.compile(r"quota.*exceeded|resource.exhausted|billing", re.I)),
]

# Provider dashboard URLs for key rotation guidance
_ROTATE_URLS = {
    "gemini": "https://aistudio.google.com/app/apikey",
    "groq":   "https://console.groq.com/keys",
    "openrouter": "https://openrouter.ai/settings/keys",
    "mimo":   "https://api.xiaomimimo.com",
}


def detect_threat(error_str: str) -> KeyThreat:
    """Classify the security threat level from an API error string."""
    for threat, pattern in _THREAT_PATTERNS:
        if pattern.search(error_str):
            return threat
    return KeyThreat.NONE


def leaked_key_warning(provider: str, rich: bool = True) -> str:
    """
    Return a warning message for a leaked key.
    `rich=True`  → Rich markup (for console.print)
    `rich=False` → plain text (for string returns)
    """
    url = _ROTATE_URLS.get(provider.lower(), "your provider's dashboard")
    if rich:
        return (
            f"\n[bold red]⚠  SECURITY ALERT — {provider.upper()} KEY LEAKED[/bold red]\n"
            f"[red]Your API key was reported as compromised. Rotate it immediately:[/red]\n"
            f"[yellow]{url}[/yellow]\n"
            f"[dim]Generate a new key, update .env, and restart APEX.[/dim]\n"
        )
    return (
        f"SECURITY ALERT: {provider.upper()} key leaked — rotate immediately at {url}. "
        "Update .env and restart APEX."
    )


# ── rate-limit backoff ────────────────────────────────────────────────────────

async def backoff_retry(coro_factory, max_retries: int = 2, base_delay: float = 2.0):
    """
    Call `coro_factory()` (returns a coroutine) up to `max_retries` times on
    rate-limit errors. Uses exponential backoff: base_delay * 2^attempt.

    Returns the result or raises the last exception.
    """
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            return await coro_factory()
        except Exception as e:
            threat = detect_threat(str(e))
            if threat in (KeyThreat.RATE_LIMITED, KeyThreat.QUOTA) and attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
                last_exc = e
                continue
            raise
    raise last_exc

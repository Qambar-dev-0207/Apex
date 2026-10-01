"""
GeniusMode (Backward Compatibility Wrapper).

Re-exports Raphael (Lord of Wisdom) as GeniusMode so existing imports
and legacy integrations continue to work seamlessly.
"""

from src.services.raphael import Raphael, GeniusMode, SYSTEM_PROMPT, _safe_json_parse

__all__ = ["Raphael", "GeniusMode", "SYSTEM_PROMPT", "_safe_json_parse"]

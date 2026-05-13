"""
WebFetch — pull a specific URL's content and return clean text.

Distinct from `web_search` (which returns ranked SERP results):
  - web_search:  "find me pages about X"
  - web_fetch:   "give me the content of https://..."

Security:
  - SSRF protection: blocks private/loopback/link-local/metadata IPs
  - Scheme whitelist: only http/https
  - Body size cap: 1.5 MB max
  - Output cap: 20 000 chars
"""

import re
import ipaddress
import asyncio
from typing import Dict, Any, Optional
from urllib.parse import urlparse

import httpx


# RFC 1918 + loopback + link-local + cloud metadata ranges that must never be fetched
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # loopback
    ipaddress.ip_network("::1/128"),           # IPv6 loopback
    ipaddress.ip_network("10.0.0.0/8"),        # private
    ipaddress.ip_network("172.16.0.0/12"),     # private
    ipaddress.ip_network("192.168.0.0/16"),    # private
    ipaddress.ip_network("169.254.0.0/16"),    # link-local / AWS IMDS
    ipaddress.ip_network("fd00::/8"),          # IPv6 ULA
    ipaddress.ip_network("fe80::/10"),         # IPv6 link-local
    ipaddress.ip_network("0.0.0.0/8"),         # "this" network
    ipaddress.ip_network("100.64.0.0/10"),     # carrier-grade NAT
]

_BLOCKED_HOSTNAMES = frozenset({
    "localhost", "metadata.google.internal",
    "169.254.169.254",                         # AWS / GCP IMDS
    "metadata", "instance-data",
})


def _is_ssrf_target(hostname: str) -> bool:
    """Return True if the hostname resolves to a private/internal address."""
    h = hostname.lower().split(":")[0]
    if h in _BLOCKED_HOSTNAMES:
        return True
    try:
        addr = ipaddress.ip_address(h)
        return any(addr in net for net in _BLOCKED_NETWORKS)
    except ValueError:
        pass
    return False


class WebFetchTool:
    DEFAULT_TIMEOUT = 20.0
    MAX_BYTES = 1_500_000       # ~1.5 MB hard cap
    MAX_OUTPUT_CHARS = 20_000

    USER_AGENT = (
        "Mozilla/5.0 (compatible; APEX-WebFetch/1.0; "
        "+https://apex-os.local)"
    )

    async def afetch(
        self, url: str, max_chars: Optional[int] = None
    ) -> Dict[str, Any]:
        if not url or not url.strip():
            return {"success": False, "error": "empty url", "output": ""}
        url = url.strip()
        if not re.match(r"^https?://", url, re.I):
            url = "https://" + url
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return {"success": False, "error": f"unsupported scheme: {parsed.scheme}"}
            hostname = parsed.hostname or ""
            if not hostname:
                return {"success": False, "error": "missing hostname"}
            if _is_ssrf_target(hostname):
                return {"success": False, "error": "request to private/internal address blocked"}
        except Exception as e:
            return {"success": False, "error": f"bad url: {e}"}

        try:
            async with httpx.AsyncClient(
                timeout=self.DEFAULT_TIMEOUT,
                follow_redirects=True,
                headers={"User-Agent": self.USER_AGENT},
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                ctype = resp.headers.get("content-type", "").lower()
                raw = resp.content[: self.MAX_BYTES]
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

        # binary types we won't try to decode
        if any(
            t in ctype
            for t in ("image/", "audio/", "video/", "application/octet-stream")
        ):
            return {
                "success": True,
                "output": f"[binary content, type={ctype}, bytes={len(raw)}] {url}",
                "url": url,
                "content_type": ctype,
            }

        text = raw.decode("utf-8", errors="ignore")

        # Markdown / json / plain — keep as-is
        if "html" not in ctype and "xml" not in ctype:
            cap = max_chars or self.MAX_OUTPUT_CHARS
            return {
                "success": True,
                "output": text[:cap],
                "url": url,
                "content_type": ctype,
            }

        cleaned = self._html_to_text(text)
        cap = max_chars or self.MAX_OUTPUT_CHARS
        return {
            "success": True,
            "output": cleaned[:cap],
            "url": url,
            "content_type": ctype,
            "truncated": len(cleaned) > cap,
        }

    def fetch(self, url: str, max_chars: Optional[int] = None) -> Dict[str, Any]:
        try:
            return asyncio.run(self.afetch(url, max_chars))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.afetch(url, max_chars))
            finally:
                loop.close()

    @staticmethod
    def _html_to_text(html: str) -> str:
        # Strip scripts/styles entirely (incl. content)
        html = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
        html = re.sub(r"<style\b[^>]*>.*?</style>", " ", html, flags=re.I | re.S)
        # Replace block elements with newlines so structure survives
        html = re.sub(
            r"</(p|div|li|h[1-6]|tr|br|article|section)>",
            "\n", html, flags=re.I,
        )
        html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
        # Drop all remaining tags
        text = re.sub(r"<[^>]+>", " ", html)
        # Decode common entities
        for k, v in {
            "&nbsp;": " ", "&amp;": "&", "&lt;": "<",
            "&gt;": ">", "&quot;": '"', "&#39;": "'", "&apos;": "'",
        }.items():
            text = text.replace(k, v)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

import re
import asyncio
from typing import Dict, Any, Optional
from rich.console import Console

from src.tools.safety import SafetyGuard

# Hard deny — never run regardless of policy or mode
_HARD_DENY_PATTERNS = [
    re.compile(r"\brm\s+-[a-z]*f[a-z]*\s+/", re.I),          # rm -rf /
    re.compile(r"\bdd\b.*\bof=/dev/", re.I),                   # dd to device
    re.compile(r"\bformat\s+[a-z]:", re.I),                    # Windows format
    re.compile(r"\bmkfs\b", re.I),                             # mkfs
    re.compile(r">\s*/dev/s[dh][a-z]", re.I),                  # write to raw disk
    re.compile(r"\bchmod\s+[0-7]*7[0-7][0-7]\s+/", re.I),     # chmod 777 /
    re.compile(r"\bchown\s+.*\s+/\s*$", re.I),                 # chown /
    re.compile(r"curl\s+.*\|\s*(ba)?sh\b", re.I),              # curl | bash
    re.compile(r"wget\s+.*\|\s*(ba)?sh\b", re.I),              # wget | bash
    re.compile(r"curl\s+.*\|\s*python", re.I),                 # curl | python
    re.compile(r":\(\)\s*\{.*\}\s*;", re.I),                   # fork bomb
    re.compile(r"\bpkill\s+-9\s+-f\b", re.I),                  # kill all processes
    re.compile(r"\bsudo\s+rm\s+-rf\s+/", re.I),               # sudo rm -rf /
    re.compile(r"\bsudo\s+dd\b", re.I),                        # sudo dd
]

MAX_OUTPUT_BYTES = 512 * 1024  # 512 KB stdout cap


class ShellAgent:
    """
    Executes shell commands with hard-deny patterns, policy checks, and output size caps.
    """

    def __init__(self, console=None, safety: Optional[SafetyGuard] = None):
        self.console = console or Console()
        self.safety = safety or SafetyGuard(console=self.console)

    @staticmethod
    def _hard_denied(command: str) -> bool:
        return any(p.search(command) for p in _HARD_DENY_PATTERNS)

    async def execute(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        command = command.strip()

        # Hard deny — no user override possible
        if self._hard_denied(command):
            return {"success": False, "error": f"command blocked by security policy"}

        authorized = await self.safety.check_command(command)
        if not authorized:
            return {"success": False, "error": "execution denied by policy or user"}

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                return {"success": False, "error": f"command timed out after {timeout}s"}

            out = stdout[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
            err = stderr[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")

            if proc.returncode == 0:
                return {"success": True, "output": out}
            return {
                "success": False,
                "error": err or f"exit code {proc.returncode}",
                "output": out,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

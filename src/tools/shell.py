import asyncio
from typing import Dict, Any, Optional
from rich.console import Console

from src.tools.safety import SafetyGuard

class ShellAgent:
    """
    Executes shell commands with built-in permission gates and policy checks.
    """
    def __init__(self, console=None, safety: Optional[SafetyGuard] = None):
        self.console = console or Console()
        self.safety = safety or SafetyGuard(console=self.console)

    async def execute(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        authorized = await self.safety.check_command(command)
        if not authorized:
            return {"success": False, "error": "Execution denied by policy or user."}

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                proc.kill()
                return {"success": False, "error": f"Command timed out after {timeout}s"}

            out = stdout.decode("utf-8", errors="replace")
            err = stderr.decode("utf-8", errors="replace")
            if proc.returncode == 0:
                return {"success": True, "output": out}
            return {"success": False, "error": err or f"Exit code {proc.returncode}", "output": out}
        except Exception as e:
            return {"success": False, "error": str(e)}

import subprocess
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.prompt import Confirm

class GitAgent:
    """
    Automates advanced git operations with permission gates.
    """
    def __init__(self, working_dir: str = ".", console: Optional[Console] = None):
        self.working_dir = working_dir
        self.console = console or Console()

    def _run(self, args: List[str]) -> Dict[str, Any]:
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            return {
                "success": res.returncode == 0,
                "output": res.stdout,
                "error": res.stderr
            }
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}

    def status(self) -> Dict[str, Any]:
        return self._run(["status"])

    def diff(self, cached: bool = False) -> Dict[str, Any]:
        args = ["diff"]
        if cached: args.append("--cached")
        return self._run(args)

    def add(self, files: str = ".") -> Dict[str, Any]:
        return self._run(["add", files])

    def commit(self, message: str) -> Dict[str, Any]:
        self.console.print(f"\n[bold yellow]APEX wants to COMMIT changes:[/bold yellow]")
        self.console.print(f"[cyan]Message: {message}[/cyan]")
        if not Confirm.ask("[bold red]Do you authorize this commit?[/bold red]"):
            return {"success": False, "error": "Permission denied by user."}
        return self._run(["commit", "-m", message])

    def push(self, remote: str = "origin", branch: str = "main") -> Dict[str, Any]:
        self.console.print(f"\n[bold yellow]APEX wants to PUSH to {remote}/{branch}[/bold yellow]")
        if not Confirm.ask("[bold red]Do you authorize this push?[/bold red]"):
            return {"success": False, "error": "Permission denied by user."}
        return self._run(["push", remote, branch])

    def pull(self, remote: str = "origin", branch: str = "main") -> Dict[str, Any]:
        return self._run(["pull", remote, branch])

    def log(self, n: int = 5) -> Dict[str, Any]:
        return self._run(["log", "-n", str(n), "--oneline"])

    def checkout(self, branch: str, create: bool = False) -> Dict[str, Any]:
        args = ["checkout"]
        if create: args.append("-b")
        args.append(branch)
        return self._run(args)

import re
import os
import json
from typing import Dict, Any, List, Optional
from rich.prompt import Confirm
from rich.console import Console

class PolicyManager:
    """
    Manages execution policies for APEX, similar to Gemini CLI.
    """
    def __init__(self, policy_path: str = "data/policy.json"):
        self.policy_path = policy_path
        os.makedirs(os.path.dirname(self.policy_path), exist_ok=True)
        self.policy = self._load()

    def _load(self) -> Dict[str, List[str]]:
        if os.path.exists(self.policy_path):
            with open(self.policy_path, "r") as f:
                try:
                    return json.load(f)
                except:
                    pass
        return {
            "allowed_commands": ["git status", "ls", "dir", "pwd", "whoami"],
            "denied_commands": ["rm -rf /", "format c:", "mkfs"],
            "always_ask": ["*"]
        }

    def save(self):
        with open(self.policy_path, "w") as f:
            json.dump(self.policy, f, indent=2)

    def check(self, command: str) -> str:
        """Returns 'allow', 'deny', or 'ask'."""
        command = command.strip()

        for c in self.policy.get("denied_commands", []):
            if c == "*":
                return "deny"
            if command.startswith(c):
                return "deny"

        for c in self.policy.get("allowed_commands", []):
            if c == "*":
                return "allow"
            if command.startswith(c):
                return "allow"

        always_ask = self.policy.get("always_ask", [])
        if "*" in always_ask:
            return "ask"

        return "ask"

class SafetyGuard:
    """
    Scans code and commands for potentially destructive operations.
    Modes: 'default' (ask), 'auto-approve' (bypass prompts), 'plan' (deny all writes).
    """
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.policy = PolicyManager()
        self.mode = "default"  # default | auto-approve | plan
        self.destructive_patterns = [
            (r"os\.remove\b", "File deletion"),
            (r"os\.rmdir\b", "Directory deletion"),
            (r"shutil\.rmtree\b", "Recursive directory deletion"),
            (r"open\(.*['\"]w['\"]\)", "File overwrite"),
            (r"open\(.*['\"]a['\"]\)", "File append"),
            (r"subprocess\.run\(.*rm\s", "System-level removal"),
            (r"subprocess\.(?:run|call|Popen)\(.*shell=True", "Shell injection risk"),
            (r"sys\.exit\b", "Process termination"),
            (r"os\.system\b", "OS command execution"),
            (r"eval\s*\(", "Dynamic code evaluation"),
            (r"exec\s*\(", "Dynamic code execution"),
            (r"__import__\s*\(", "Dynamic import"),
            (r"pickle\.loads?\b", "Unsafe deserialization"),
            (r"yaml\.load\s*\([^,)]+\)", "Unsafe YAML load (use safe_load)"),
        ]

    def set_mode(self, mode: str):
        if mode in ("default", "auto-approve", "plan"):
            self.mode = mode
            self.console.print(f"[bold cyan]Safety mode → {mode}[/bold cyan]")

    def scan(self, code: str) -> List[str]:
        findings = []
        for pattern, label in self.destructive_patterns:
            if re.search(pattern, code):
                findings.append(label)
        return findings

    async def check_command(self, command: str) -> bool:
        """
        Consults policy and potentially asks user for permission.
        """
        if self.mode == "plan":
            self.console.print(f"[bold magenta]PLAN MODE: would run → {command}[/bold magenta]")
            return False
        status = self.policy.check(command)

        if status == "allow":
            return True
        if status == "deny":
            self.console.print(f"[bold red]POLICY DENIED: {command}[/bold red]")
            return False

        if self.mode == "auto-approve":
            self.console.print(f"[dim cyan]AUTO-APPROVED: {command}[/dim cyan]")
            return True

        self.console.print(f"\n[bold yellow]PERMISSION REQUESTED:[/bold yellow]")
        self.console.print(f"[cyan]> {command}[/cyan]")
        return Confirm.ask("[bold red]Do you authorize this execution?[/bold red]")

    async def check_filesystem(self, action: str, path: str, content: Optional[str] = None) -> bool:
        """
        Consults policy and asks user for permission for file operations.
        """
        if self.mode == "plan" and action in ("write", "delete"):
            self.console.print(f"[bold magenta]PLAN MODE: would {action} {path}[/bold magenta]")
            return False
        if self.mode == "auto-approve":
            self.console.print(f"[dim cyan]AUTO-APPROVED ({action}): {path}[/dim cyan]")
            return True

        self.console.print(f"\n[bold yellow]FILE OPERATION REQUESTED ({action}):[/bold yellow]")
        self.console.print(f"[cyan]Path: {path}[/cyan]")
        if content:
            self.console.print(f"[dim]{content[:200]}{'...' if len(content) > 200 else ''}[/dim]")

        return Confirm.ask(f"[bold red]Do you authorize this {action}?[/bold red]")

    async def async_confirm(self, findings: List[str], console=None) -> bool:
        """
        Request user confirmation if destructive patterns are found.
        """
        if not findings:
            return True
            
        target_console = console or self.console
        if target_console:
            target_console.print(f"[bold red]WARNING: Destructive patterns detected: {', '.join(findings)}[/bold red]")
            return Confirm.ask("[bold yellow]Do you want to proceed with execution?[/bold yellow]")
            
        return False # Fail safe if no console

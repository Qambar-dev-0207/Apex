from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.markdown import Markdown
from rich.text import Text
from rich.align import Align
from typing import Dict, Any, List, Optional
from src.core.models import ExecutionPlan, ValidationResult, ProjectManifest, SystemVitals

class ResponseAssembler:
    """
    Supercomputer-grade UI Assembly.
    """
    def __init__(self, console: Console):
        self.console = console

    def render_plan(self, plan: ExecutionPlan) -> Tree:
        tree = Tree(f"[bold gold1]LOGIC DAG:[/bold gold1] {plan.summary}")
        for step in plan.task_plan:
            tool_str = f" [cyan]// TOOL:{step.tool}[/cyan]" if step.tool else ""
            tree.add(f"[bold]NODE_{step.id}[/bold]: {step.description}{tool_str}")
        return tree

    def render_workspace_info(self, project: Optional[ProjectManifest], vitals: Optional[SystemVitals] = None):
        info = Text()
        if project:
            info.append("PROJECT ", style="bold magenta")
            info.append(f"[{project.name}] ", style="white")
            info.append("GOALS ", style="bold magenta")
            info.append(f"{len(project.goals)} ", style="white")

        if vitals:
            color = "green" if vitals.status == "nominal" else "yellow" if vitals.status == "warning" else "red"
            info.append("| CORE_LOAD ", style="bold yellow")
            info.append(f"{vitals.cpu_percent}% ", style=color)
            info.append("| RAM ", style="bold yellow")
            info.append(f"{vitals.ram_percent}% ", style=color)
            if vitals.temperature:
                info.append(f"| TEMP {vitals.temperature}°C ", style=color)

        if not info.plain.strip():
            info.append("OFFLINE — no project, no telemetry", style="dim")

        return Panel(Align.center(info), title="[bold cyan]SYSCFG // TELEMETRY[/bold cyan]", border_style="cyan")

    def render_final_response(self, query: str, assistant_output: str, plan: Optional[ExecutionPlan] = None, results: Optional[List[Dict[str, Any]]] = None, project: Optional[ProjectManifest] = None, vitals: Optional[SystemVitals] = None):
        self.console.print("\n" + "═"*80)
        
        # 1. Telemetry
        self.console.print(self.render_workspace_info(project, vitals))
            
        # 2. Reasoning Artifacts
        if plan and plan.socratic_insight:
            self.console.print(Panel(f"[italic cyan]{plan.socratic_insight}[/italic cyan]", title="[bold white]JARVIS // SOCRATIC CRITIQUE[/bold white]", border_style="bright_black"))

        if plan:
            self.console.print(Panel(self.render_plan(plan), title="[bold gold1]ARCHITECTURAL SCHEMATIC[/bold gold1]", border_style="yellow"))
        
        # 3. Execution Data
        if results:
            table = Table(title="COMPUTE SEQUENCE LOGS", border_style="dim", box=None)
            table.add_column("NODE", style="cyan")
            table.add_column("RESULT", ratio=1)
            for i, res in enumerate(results):
                status = "[green]SUCCESS[/green]" if res["success"] else "[red]FAILURE[/red]"
                out = res.get("output") or res.get("error") or ""
                out_preview = out[:70] + ("..." if len(out) > 70 else "")
                table.add_row(f"0x0{i+1}", f"{status} | {out_preview}")
            self.console.print(table)
            
        # 4. Final Output
        import random
        footers = [
            "Always happy to help, even when your logic is flawed.",
            "Shall I order a coffee, or are we going to stay this inefficient?",
            "Architectural supremacy established. You're welcome.",
            "Data synthesized. Try not to break it this time.",
            "I've optimized the response. Unfortunately, I can't optimize your typing speed."
        ]
        
        self.console.print(Panel(Markdown(assistant_output), title="[bold blue]APEX // INTELLECTUAL SYNTHESIS[/bold blue]", subtitle=f"[italic]{random.choice(footers)}[/italic]", border_style="blue", padding=(1, 2)))
        self.console.print("═"*80 + "\n")

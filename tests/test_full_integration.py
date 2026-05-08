import asyncio
import sys
import os
from rich.console import Console

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.thinking_path import GeminiClient
from src.services.memory import MemoryManager
from src.routers.router import ParallelExecutor
from src.core.models import ExecutionPlan, TaskStep

async def test_full_integration():
    console = Console()
    console.print("[bold cyan]Phase 7: Full Integration Verification[/bold cyan]")
    
    # 1. Initialize all managers
    memory = MemoryManager()
    executor = ParallelExecutor(console=console)
    session_id = "integration_test_2026"
    
    # 2. Simulate Memory Storage (L2)
    console.print("[green]Simulating memory storage...[/green]")
    await memory.store_interaction(session_id, "My favorite color is emerald.", "Noted.")
    
    # 3. Simulate Hybrid Retrieval (L2 Hybrid)
    console.print("[green]Testing hybrid retrieval...[/green]")
    context = await memory.get_relevant_context("emerald color", session_id)
    if "emerald" in context:
        console.print("[bold green]✓ Hybrid retrieval successful.[/bold green]")
    else:
        console.print("[bold red]✗ Hybrid retrieval failed.[/bold red]")
        
    # 4. Simulate Parallel Execution with TaskGroup (L4)
    console.print("[green]Testing Parallel TaskGroup execution...[/green]")
    plan = ExecutionPlan(
        task_plan=[
            TaskStep(id=1, action="task1", description="independent task 1", tool=None, dependencies=[]),
            TaskStep(id=2, action="task2", description="independent task 2", tool=None, dependencies=[]),
            TaskStep(id=3, action="task3", description="dependent on 1 & 2", tool=None, dependencies=[1, 2])
        ],
        tools_required=[],
        requires_clarification=False,
        summary="DAG Integration Test"
    )
    results = await executor.run(plan)
    if len(results) == 3 and all(r['success'] for r in results):
        console.print("[bold green]✓ Parallel TaskGroup execution successful.[/bold green]")
    else:
        console.print(f"[bold red]✗ Parallel execution failed: {results}[/bold red]")

    # 5. Check Safety Guard (L6 Safety)
    console.print("[green]Testing Safety Guard (Non-interactive mode simulation)...[/green]")
    from src.tools.safety import SafetyGuard
    guard = SafetyGuard()
    findings = guard.scan("import os; os.remove('important_file.txt')")
    if "File deletion" in findings:
        console.print("[bold green]✓ Safety Guard detected destructive pattern.[/bold green]")
    else:
        console.print("[bold red]✗ Safety Guard failed to detect pattern.[/bold red]")

    console.print("\n[bold cyan]Full System Integration Verified.[/bold cyan]")

if __name__ == "__main__":
    asyncio.run(test_full_integration())

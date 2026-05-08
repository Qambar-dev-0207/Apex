import asyncio
import sys
import os
from rich.console import Console

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.thinking_path import GeminiClient
from src.services.memory import MemoryManager

async def verify_upgrades():
    console = Console()
    console.print("[bold cyan]Verifying Phase 4 Upgrades: New SDK + Async Redis[/bold cyan]")
    
    # 1. Test MemoryManager (Async)
    memory = MemoryManager()
    session_id = "upgrade_test"
    
    console.print("[green]Testing Async Redis Interaction...[/green]")
    await memory.store_interaction(session_id, "Hello from the new SDK!", "Upgrade successful.")
    context = await memory.get_relevant_context("What did I just say?", session_id)
    
    if "Hello from the new SDK" in context:
        console.print("[bold green]✓ Async Redis working correctly.[/bold green]")
    else:
        console.print("[bold red]✗ Async Redis retrieval failed (Check if redis-server is running).[/bold red]")

    # 2. Test GeminiClient (New SDK)
    if os.getenv("GEMINI_API_KEY"):
        console.print("[green]Testing Gemini 2.0 Flash (New SDK)...[/green]")
        client = GeminiClient()
        plan = await client.generate_plan("Calculate 2+2 and search for Gemini 2.0 features.", session_id)
        
        if plan.task_plan:
            console.print(f"[bold green]✓ Gemini 2.0 Flash plan generated: {plan.summary}[/bold green]")
        else:
            console.print(f"[bold red]✗ Gemini 2.0 Flash plan generation failed: {plan.summary}[/bold red]")
    else:
        console.print("[yellow]! GEMINI_API_KEY missing, skipping SDK test.[/yellow]")

    console.print("\n[bold cyan]Upgrade Verification Complete.[/bold cyan]")

if __name__ == "__main__":
    asyncio.run(verify_upgrades())

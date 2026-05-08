import sys
import os
import asyncio
from rich.console import Console

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.memory import MemoryManager
from src.core.models import MemoryEntry

async def test_memory_system():
    console = Console()
    console.print("[bold cyan]Phase 3 Verification: Memory System[/bold cyan]")
    
    manager = MemoryManager()
    session_id = "test_session_123"
    
    # 1. Test Redis (Short-term)
    if manager.redis:
        console.print("[green]Testing Redis...[/green]")
        await manager.store_interaction(session_id, "What is my name?", "Your name is APEX Test User.")
        context = await manager.get_relevant_context("What is my name?", session_id)
        if "APEX Test User" in context:
            console.print("[bold green]✓ Redis history retrieval successful.[/bold green]")
        else:
            console.print("[bold red]✗ Redis history retrieval failed.[/bold red]")
    else:
        console.print("[yellow]! Redis not available, skipping short-term test.[/yellow]")

    # 2. Test ChromaDB (Long-term)
    if manager.chroma:
        console.print("[green]Testing ChromaDB...[/green]")
        await manager.store_interaction(session_id, "I love pizza.", "Noted, you love pizza.")
        context = await manager.get_relevant_context("What do I like to eat?", session_id)
        if "pizza" in context.lower():
            console.print("[bold green]✓ ChromaDB semantic retrieval successful.[/bold green]")
        else:
            console.print("[bold red]✗ ChromaDB semantic retrieval failed.[/bold red]")
    else:
        console.print("[yellow]! ChromaDB not available, skipping long-term test.[/yellow]")

    console.print("\n[bold cyan]Verification Complete.[/bold cyan]")

if __name__ == "__main__":
    asyncio.run(test_memory_system())

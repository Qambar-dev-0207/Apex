import asyncio
import sys
import os

from main import APEXEngine

async def main():
    engine = APEXEngine()
    print("Booting APEXEngine...")
    await engine.load_system()
    engine.parallel_executor.safety_guard.mode = "autonomous"
    engine.shell.safety.mode = "autonomous"
    engine.auto_approve_enabled = True
    
    # We test two things:
    # 1. Shell passthrough (ensure shell access works)
    print("\n--- Testing Shell Passthrough ---")
    await engine.handle_user_turn("! echo Shell Test Works > apex_shell_test.txt")
    
    # 2. Autonomous Agent action (ensure APEX natural language parsing and file creation works)
    print("\n--- Testing Autonomous Action ---")
    await engine.handle_user_turn(">> (groq) create a file called apex_autonomous_test.txt with the content 'APEX AI Agent works perfectly'")
    
    print("\nDone. Exiting.")

if __name__ == "__main__":
    asyncio.run(main())

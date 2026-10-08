import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import APEXEngine


async def main():
    engine = APEXEngine()
    print("Booting APEXEngine...")
    await engine.load_system()
    engine.parallel_executor.safety_guard.mode = "autonomous"
    engine.shell.safety.mode = "autonomous"
    engine.auto_approve_enabled = True
    
    try:
        # 1. Shell passthrough (ensure shell access works)
        print("\n--- Testing Shell Passthrough ---")
        await engine.handle_user_turn("! echo Shell Test Works > test_shell.tmp")
        
        # 2. Autonomous Agent action (ensure APEX natural language parsing and file creation works)
        print("\n--- Testing Autonomous Action ---")
        await engine.handle_user_turn(">> (groq) create a file called test_auto.tmp with the content 'APEX AI Agent works perfectly'")
        
        print("\nDone. Exiting.")
    finally:
        for tmp_file in ["test_shell.tmp", "test_auto.tmp", "apex_shell_test.txt", "apex_autonomous_test.txt"]:
            if os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                except Exception:
                    pass

if __name__ == "__main__":
    asyncio.run(main())


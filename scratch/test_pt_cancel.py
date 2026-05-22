import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML

async def main():
    session = PromptSession()
    print("Starting cancel test in 2 seconds...")
    
    async def cancel_after_2s():
        await asyncio.sleep(2.0)
        print("\n[Timer] Cancelling prompt now...")
        prompt_task.cancel()

    prompt_task = asyncio.create_task(session.prompt_async(HTML("<b>Test Prompt❯ </b>")))
    cancel_task = asyncio.create_task(cancel_after_2s())
    
    try:
        res = await prompt_task
        print(f"Result: {res}")
    except asyncio.CancelledError:
        print("Prompt successfully cancelled cleanly!")
    finally:
        await cancel_task

if __name__ == "__main__":
    asyncio.run(main())

import os
from src.core.models import ExecutionPlan, TaskStep
from src.models.thinking_path import GeminiClient
from dotenv import load_dotenv

def test_models():
    step = TaskStep(id=1, action="test", description="test desc")
    plan = ExecutionPlan(
        task_plan=[step],
        tools_required=[],
        requires_clarification=False,
        summary="Test Plan"
    )
    assert len(plan.task_plan) == 1
    assert plan.summary == "Test Plan"
    print("Models test passed!")

def test_gemini_integration():
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("Skipping Gemini integration test (No API Key)")
        return
        
    client = GeminiClient()
    query = "Write a python script to calculate the first 10 fibonacci numbers and print them."
    plan = client.generate_plan(query)
    
    assert isinstance(plan, ExecutionPlan)
    assert len(plan.task_plan) > 0
    assert any(step.tool == "python_executor" for step in plan.task_plan)
    print("Gemini integration test passed!")
    print(f"Summary: {plan.summary}")

if __name__ == "__main__":
    try:
        test_models()
        test_gemini_integration()
        print("\nAll Phase 2 Verification Tests Passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

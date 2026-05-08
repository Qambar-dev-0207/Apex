from src.routers.router import InputClassifier, SmartRouter
from src.tools.executor import PythonExecutor

def test_classifier():
    classifier = InputClassifier()
    
    # Test simple chat
    res1 = classifier.classify("Hello, how are you?")
    assert res1["intent"] == "chat", f"Expected intent 'chat', got {res1['intent']}"
    assert res1["complexity"] == "low", f"Expected complexity 'low', got {res1['complexity']}"
    
    # Test coding intent
    res2 = classifier.classify("Write a python script to calculate the area of a circle.")
    assert res2["intent"] == "coding", f"Expected intent 'coding', got {res2['intent']}"
    assert res2["complexity"] == "high", f"Expected complexity 'high', got {res2['complexity']}"
    
    print("Classifier tests passed!")

def test_router():
    router = SmartRouter()
    
    res1 = router.route({"complexity": "low"})
    assert res1 == "fast_path"
    
    res2 = router.route({"complexity": "high"})
    assert res2 == "thinking_path"
    
    print("Router tests passed!")

def test_executor():
    executor = PythonExecutor()
    
    code = "print(2 + 2)"
    res = executor.execute(code)
    assert res["success"] is True
    assert res["output"].strip() == "4"
    
    code_fail = "print(1/0)"
    res_fail = executor.execute(code_fail)
    assert res_fail["success"] is False
    assert "division by zero" in res_fail["error"]
    
    print("Executor tests passed!")

if __name__ == "__main__":
    try:
        test_classifier()
        test_router()
        test_executor()
        print("\nAll Phase 1 Verification Tests Passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

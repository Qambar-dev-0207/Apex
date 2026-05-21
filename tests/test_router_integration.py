import asyncio
from src.routers.router import InputClassifier, SmartRouter

def test_smart_router_integration():
    classifier = InputClassifier()
    router = SmartRouter()
    
    async def run():
        # Complex input should trigger thinking_path
        complex_input = "Write a complete python script to scrape a website and save the results to a structured CSV file, handling errors and rate limiting."
        classification = await classifier.classify(complex_input)
        path = router.route(classification)
        
        assert classification["complexity"] == "high", f"Expected 'high', got {classification['complexity']}"
        assert path == "thinking_path", f"Expected 'thinking_path', got {path}"
        
        # Simple input should trigger fast_path
        simple_input = "Hi there"
        classification_simple = await classifier.classify(simple_input)
        path_simple = router.route(classification_simple)
        
        assert classification_simple["complexity"] == "low"
        assert path_simple == "fast_path"
        
        print("Smart Router Integration Test Passed!")

    asyncio.run(run())

if __name__ == "__main__":
    test_smart_router_integration()

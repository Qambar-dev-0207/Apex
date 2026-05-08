import os
import json
import asyncio
from google import genai
from typing import Dict, Any, List, Optional
from src.core.models import CodeSpec, ValidationResult
from src.tools.sandbox import SandboxExecutor
from dotenv import load_dotenv

class CodeValidator:
    """
    Validates generated code by creating and running automated tests.
    """
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = model_name
        self.sandbox = SandboxExecutor()

    async def validate(self, code: str, spec: CodeSpec) -> ValidationResult:
        """
        Generates and runs tests for the provided code based on the spec.
        """
        # 1. Generate unit tests based on the spec and code
        test_prompt = f"""
        Generate a Python unittest script for the following code.
        
        CODE TO TEST:
        {code}
        
        SPECIFICATION:
        Architecture: {spec.architecture_notes}
        Scenarios: {spec.test_scenarios}
        
        RULES:
        1. Output ONLY the Python test code. 
        2. Use the 'unittest' library.
        3. Ensure the test code includes an entry point: if __name__ == '__main__': unittest.main()
        4. Mock any external dependencies if necessary.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=test_prompt
            )
            test_code = response.text.replace("```python", "").replace("```", "").strip()
            
            # 2. Combine code and tests into a single script for execution
            # In a real pipeline, we'd save them as separate files.
            execution_script = f"{code}\n\n{test_code}"
            
            # 3. Run in sandbox
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.sandbox.execute, execution_script)
            
            success = result["success"]
            # Basic validation: check if 'OK' is in the test output (standard unittest output)
            if success and "OK" not in result["output"] and "Ran" in result["output"]:
                 success = False # Tests ran but maybe some failed
            
            return ValidationResult(
                success=success,
                test_output=result["output"],
                errors=[result["error"]] if result["error"] else [],
                generated_code=code
            )
            
        except Exception as e:
            return ValidationResult(
                success=False,
                test_output="",
                errors=[str(e)],
                generated_code=code
            )

import sys
import io
from typing import Dict, Any

class PythonExecutor:
    """
    A basic tool for executing Python code strings and capturing output.
    """
    def execute(self, code: str) -> Dict[str, Any]:
        # Capture stdout
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        
        success = True
        error = None
        
        try:
            # Note: exec is used for Phase 1. Docker sandboxing is planned for Layer 6.
            exec(code, {})
        except Exception as e:
            success = False
            error = str(e)
        finally:
            sys.stdout = old_stdout
            
        return {
            "success": success,
            "output": redirected_output.getvalue(),
            "error": error
        }

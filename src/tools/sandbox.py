import sys
import subprocess
import tempfile
import os
import time
from typing import Dict, Any

class SandboxExecutor:
    """
    An isolated environment for executing Python code safely.
    Uses subprocess to run code in a separate process with a timeout.
    """
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def execute(self, code: str) -> Dict[str, Any]:
        """
        Executes the provided Python code and captures output/errors.
        """
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        success = True
        output = ""
        error = None
        
        try:
            # Run the code in a separate process
            # Note: For true isolation, this should ideally run in a Docker container
            # or with resource limits (prlimit on Linux).
            process = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            output = process.stdout
            if process.returncode != 0:
                success = False
                error = process.stderr
                
        except subprocess.TimeoutExpired:
            success = False
            error = f"Execution timed out after {self.timeout} seconds."
        except Exception as e:
            success = False
            error = str(e)
        finally:
            # Clean up the temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
        return {
            "success": success,
            "output": output,
            "error": error
        }

import subprocess
import tempfile
import time
import os

def run_code(code, config):
    """Execute Python code with timing and memory tracking"""
    start_time = time.time()
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
        temp_file.write(code)
        temp_file.flush()
        
        try:
            timeout = config.get('timeout_seconds', 5)
            result = subprocess.run(["python3", temp_file.name],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    timeout=timeout)
            
            execution_time = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else "",
                "execution_time": execution_time,
                "memory_used": 0,  # Will implement proper tracking later
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "output": "",
                "error": "[Python] Execution timed out.",
                "execution_time": execution_time,
                "memory_used": 0,
                "exit_code": -1
            }
        finally:
            # Clean up temp file
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)

import subprocess
import tempfile

def run_python_code(code):
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
        temp_file.write(code)
        temp_file.flush()
        try:
            result = subprocess.run(["python3", temp_file.name],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    timeout=5)
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else ""
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "[Python] Execution timed out."
            }

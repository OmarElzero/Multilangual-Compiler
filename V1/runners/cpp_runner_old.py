import subprocess
import tempfile
import os
import time

def run_code(code, config):
    """Compile and execute C++ code with timing and memory tracking"""
    start_time = time.time()
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.cpp', delete=False) as src_file:
        src_file.write(code)
        src_file.flush()
        exe_file = src_file.name.replace('.cpp', '')
        
        try:
            # Compilation step
            compile_result = subprocess.run(["g++", src_file.name, "-o", exe_file],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True)
            if compile_result.returncode != 0:
                execution_time = time.time() - start_time
                return {
                    "success": False,
                    "output": "",
                    "error": "[C++] Compile Error:\n" + compile_result.stderr,
                    "execution_time": execution_time,
                    "memory_used": 0,
                    "exit_code": compile_result.returncode
                }
            
            # Execution step
            timeout = config.get('timeout_seconds', 5)
            run_result = subprocess.run([exe_file],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True,
                                        timeout=timeout)
            
            execution_time = time.time() - start_time
            
            return {
                "success": run_result.returncode == 0,
                "output": run_result.stdout,
                "error": run_result.stderr if run_result.returncode != 0 else "",
                "execution_time": execution_time,
                "memory_used": 0,  # Will implement proper tracking later
                "exit_code": run_result.returncode
            }
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "output": "",
                "error": "[C++] Execution timed out.",
                "execution_time": execution_time,
                "memory_used": 0,
                "exit_code": -1
            }
        finally:
            # Clean up files
            if os.path.exists(exe_file):
                os.remove(exe_file)
            if os.path.exists(src_file.name):
                os.remove(src_file.name)

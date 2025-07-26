import subprocess
import tempfile
import os

def run_cpp_code(code):
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.cpp', delete=False) as src_file:
        src_file.write(code)
        src_file.flush()
        exe_file = src_file.name.replace('.cpp', '')
        try:
            compile_result = subprocess.run(["g++", src_file.name, "-o", exe_file],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True)
            if compile_result.returncode != 0:
                return {
                    "success": False,
                    "output": "",
                    "error": "[C++] Compile Error:\\n" + compile_result.stderr
                }
            run_result = subprocess.run([exe_file],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True,
                                        timeout=5)
            return {
                "success": run_result.returncode == 0,
                "output": run_result.stdout,
                "error": run_result.stderr if run_result.returncode != 0 else ""
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "[C++] Execution timed out."
            }
        finally:
            if os.path.exists(exe_file):
                os.remove(exe_file)

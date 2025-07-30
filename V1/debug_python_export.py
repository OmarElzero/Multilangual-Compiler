#!/usr/bin/env python3

import sys
import os
sys.path.append('/root/Multilangual Compilor/V1')

from runners.python_runner import PythonRunner

# Test code with export
test_code = '''
message = "Hello from Python"
numbers = [1, 2, 3, 4, 5]
print(f"Python: Created message='{message}' and numbers={numbers}")
'''

export_vars = ['message', 'numbers']

runner = PythonRunner()
enhanced_code = runner._prepare_code(test_code, None, export_vars)

print("=== ENHANCED PYTHON CODE ===")
print(enhanced_code)
print("\n=== EXECUTION RESULT ===")

result = runner.run(test_code, None, export_vars)
print("Result:", result)

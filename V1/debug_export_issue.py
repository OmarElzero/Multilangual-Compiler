#!/usr/bin/env python3

import sys
import os
import tempfile
sys.path.append('/root/Multilangual Compilor/V1')

from runners.python_runner import PythonRunner

# Test code with export - same as in mix file
test_code = '''message = "Hello from Python!"
numbers = [1, 2, 3, 4, 5]
print(f"Python: Created message='{message}' and numbers={numbers}")'''

export_vars = ['message', 'numbers']

print("=== Testing Python Runner Export ===")
runner = PythonRunner()

# Test the enhanced code generation
enhanced_code = runner._prepare_code(test_code, None, export_vars)
print("Enhanced code:")
print(enhanced_code)
print("\n" + "="*50)

# Test the actual execution
result = runner.run(test_code, None, export_vars)
print("Execution result:")
print(f"Return code: {result['return_code']}")
print(f"Output: {result['output']}")
print(f"Error: {result['error']}")
print(f"Exported data: {result['exported_data']}")

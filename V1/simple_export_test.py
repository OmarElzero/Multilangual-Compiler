#!/usr/bin/env python3

import sys
import os
sys.path.append('/root/Multilangual Compilor/V1')

from runners.python_runner import PythonRunner

# Test code with export
test_code = '''message = "Hello"
numbers = [1, 2, 3]
print("Variables created")'''

export_vars = ['message', 'numbers']

runner = PythonRunner()
result = runner.run(test_code, None, export_vars)
print("Export result:", result['exported_data'])
print("Return code:", result['return_code'])
print("Output:", result['output'])
if result['error']:
    print("Error:", result['error'])

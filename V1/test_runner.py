#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/root/Multilangual Compilor/V1')

# Test Python runner functionality
from runners.base_runner import BaseRunner
from runners.python_runner import PythonRunner

print("Testing Python runner data export...")
runner = PythonRunner()
result = runner.run('x = 42\nprint("Value:", x)', export_vars=['x'])
print("Result:", result)
print("Exported data:", result.get('exported_data', {}))

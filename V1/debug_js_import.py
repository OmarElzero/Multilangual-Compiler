#!/usr/bin/env python3

import sys
import os
sys.path.append('/root/Multilangual Compilor/V1')

from runners.javascript_runner import JavaScriptRunner

# Test code with import
test_code = '''console.log("JavaScript received message:", message);
console.log("JavaScript received numbers:", numbers);
let sum = numbers.reduce((a, b) => a + b, 0);
console.log("JavaScript: Sum =", sum);'''

import_data = {'message': 'Hello from Python!', 'numbers': [1, 2, 3, 4, 5]}

runner = JavaScriptRunner()
enhanced_code = runner._prepare_code(test_code, import_data, [])

print("=== ENHANCED JAVASCRIPT CODE ===")
print(enhanced_code)
print("\n=== EXECUTION RESULT ===")

result = runner.run(test_code, import_data, [])
print("Result:", result)

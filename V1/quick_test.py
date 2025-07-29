#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing PolyRun components...")

# Test 1: Import test
try:
    from runners.python_runner import run_code as run_python
    from runners.cpp_runner import run_code as run_cpp
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Python runner
try:
    config = {"timeout_seconds": 5}
    result = run_python('print("Hello Python")', config)
    print(f"✅ Python runner: {result['success']}, Output: {result['output'].strip()}")
except Exception as e:
    print(f"❌ Python runner failed: {e}")

# Test 3: C++ runner  
try:
    cpp_code = '''#include <iostream>
using namespace std;
int main() {
    cout << "Hello C++" << endl;
    return 0;
}'''
    result = run_cpp(cpp_code, config)
    print(f"✅ C++ runner: {result['success']}, Output: {result['output'].strip()}")
except Exception as e:
    print(f"❌ C++ runner failed: {e}")

print("Test completed!")

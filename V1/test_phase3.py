#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Phase 3 Security Features...")

# Test 1: Import security manager
try:
    from security.manager import SecurityManager
    print("✅ Security manager imported successfully")
except Exception as e:
    print(f"❌ Security manager import failed: {e}")

# Test 2: Test code validation
try:
    config = {"docker_security_policies": {}}
    sm = SecurityManager(config)
    
    # Test safe code
    safe_python = 'print("Hello World")'
    is_safe, msg = sm.validate_code_safety(safe_python, 'python')
    print(f"✅ Safe Python code validation: {is_safe} - {msg}")
    
    # Test dangerous code
    dangerous_python = 'import os; os.system("rm -rf /")'
    is_safe, msg = sm.validate_code_safety(dangerous_python, 'python')
    print(f"🚫 Dangerous Python code validation: {is_safe} - {msg}")
    
except Exception as e:
    print(f"❌ Security validation test failed: {e}")

# Test 3: Docker runner import
try:
    from runners.docker_runner import DockerRunner
    print("✅ Docker runner imported successfully")
    
    config = {"docker_enabled": True}
    docker_runner = DockerRunner(config)
    status = docker_runner.get_docker_status()
    print(f"🐳 Docker status: Available={status['available']}")
    
except Exception as e:
    print(f"❌ Docker runner test failed: {e}")

print("Phase 3 testing complete!")

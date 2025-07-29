import unittest
import sys
import os
import tempfile

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import load_config, get_runner
from parser import parse_mix_file, validate_mix_file

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete PolyRun system"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_mix_content = '''#lang:python
print("Hello from Python!")

#lang:cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Hello from C++!" << endl;
    return 0;
}
'''
    
    def test_full_execution_flow(self):
        """Test complete execution from CLI"""
        # Create temporary mix file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mix', delete=False) as f:
            f.write(self.test_mix_content)
            temp_file = f.name
        
        try:
            # Run the main script
            result = subprocess.run([
                'python3', 'main.py', temp_file
            ], capture_output=True, text=True, timeout=30)
            
            # Check execution was successful
            self.assertEqual(result.returncode, 0, f"Execution failed: {result.stderr}")
            
            # Check output contains expected results
            self.assertIn("Hello from Python!", result.stderr)  # Logging goes to stderr
            self.assertIn("Hello from C++!", result.stderr)
            self.assertIn("completed successfully", result.stderr)
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_invalid_file_handling(self):
        """Test handling of non-existent files"""
        result = subprocess.run([
            'python3', 'main.py', 'nonexistent.mix'
        ], capture_output=True, text=True)
        
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr)
    
    def test_unsupported_language(self):
        """Test handling of unsupported languages"""
        unsupported_content = '''#lang:javascript
console.log("This should fail");
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mix', delete=False) as f:
            f.write(unsupported_content)
            temp_file = f.name
        
        try:
            result = subprocess.run([
                'python3', 'main.py', temp_file
            ], capture_output=True, text=True, timeout=10)
            
            # Should exit with error but not crash
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not supported", result.stderr)
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == '__main__':
    unittest.main()

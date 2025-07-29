import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parse_mix_file, validate_mix_file

class TestParser(unittest.TestCase):
    def test_simple_parsing(self):
        """Test parsing of existing sample file"""
        blocks = parse_mix_file("samples/hello_world.mix")
        self.assertGreater(len(blocks), 0)
        self.assertIn("language", blocks[0])
        self.assertIn("code", blocks[0])
        
        # Check specific languages are found
        languages = [block["language"] for block in blocks]
        self.assertIn("cpp", languages)
        self.assertIn("python", languages)
    
    def test_validation_valid_blocks(self):
        """Test validation with valid blocks"""
        valid_blocks = [
            {"language": "python", "code": "print('hello')"},
            {"language": "cpp", "code": "#include <iostream>\nint main() { return 0; }"}
        ]
        errors = validate_mix_file(valid_blocks)
        self.assertEqual(len(errors), 0)
    
    def test_validation_invalid_blocks(self):
        """Test validation with invalid blocks"""
        invalid_blocks = [
            {"language": "", "code": "print('hello')"},  # Missing language
            {"language": "python", "code": "   "}        # Empty code
        ]
        errors = validate_mix_file(invalid_blocks)
        self.assertGreater(len(errors), 0)
        self.assertIn("Missing language specification", errors[0])
        self.assertIn("Empty code block", errors[1])

if __name__ == '__main__':
    unittest.main()
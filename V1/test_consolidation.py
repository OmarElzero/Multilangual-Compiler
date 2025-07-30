#!/usr/bin/env python3
"""
Test header consolidation feature
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parse_mix_file, consolidate_language_blocks

def test_header_consolidation():
    print("🧪 Testing Header Consolidation Feature...")
    
    # Test data that simulates your desired format
    test_blocks = [
        {
            "language": "cpp",
            "code": """#include <iostream>
using namespace std;

int main() {
    cout << "Hello from C++\\n";
    return 0;
}""",
            "start_line": 1
        },
        {
            "language": "python", 
            "code": 'print("Hello from Python!")',
            "start_line": 8
        },
        {
            "language": "cpp",
            "code": """cout << "Hello again from C++\\n";""",
            "start_line": 12
        }
    ]
    
    print(f"📋 Original blocks: {len(test_blocks)}")
    for i, block in enumerate(test_blocks):
        print(f"  Block {i+1} ({block['language']}): {len(block['code'].splitlines())} lines")
    
    # Test consolidation
    consolidated = consolidate_language_blocks(test_blocks)
    
    print(f"\n🔧 Consolidated blocks: {len(consolidated)}")
    for i, block in enumerate(consolidated):
        print(f"  Block {i+1} ({block['language']}): {len(block['code'].splitlines())} lines")
        if block.get('consolidated'):
            print(f"    ✅ Consolidated from multiple blocks")
        
        print(f"    Preview:")
        lines = block['code'].split('\n')
        for j, line in enumerate(lines[:8]):  # Show first 8 lines
            print(f"      {j+1}: {line}")
        if len(lines) > 8:
            print(f"      ... ({len(lines)-8} more lines)")
        print()

if __name__ == '__main__':
    test_header_consolidation()

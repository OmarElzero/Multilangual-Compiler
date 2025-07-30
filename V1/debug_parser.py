#!/usr/bin/env python3

import sys
sys.path.append('/root/Multilangual Compilor/V1')

from parser import parse_mix_file

# Test parsing the mix file
print("=== Testing Parser ===")
blocks = parse_mix_file('test_data_passing.mix')

for i, block in enumerate(blocks):
    print(f"\nBlock {i+1}:")
    print(f"  Language: {block['language']}")
    print(f"  Imports: {block.get('imports', [])}")
    print(f"  Exports: {block.get('exports', [])}")
    print(f"  Code: {repr(block['code'][:100])}...")

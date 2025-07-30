#!/usr/bin/env python3

from parser import parse_mix_file, consolidate_language_blocks

# Parse the test file
blocks = parse_mix_file('samples/cpp_headers_test.mix')
print('=== ORIGINAL BLOCKS ===')
for i, block in enumerate(blocks):
    print(f'Block {i+1} ({block["language"]}):')
    print(block['code'])
    print('---')

# Consolidate blocks
consolidated = consolidate_language_blocks(blocks)
print('\n=== CONSOLIDATED ===')
for i, block in enumerate(consolidated):
    print(f'Block {i+1} ({block["language"]}):')
    print(repr(block['code']))  # Use repr to see exact formatting
    print('--- ACTUAL CODE ---')
    print(block['code'])
    print('==================')

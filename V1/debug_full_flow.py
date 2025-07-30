#!/usr/bin/env python3

import sys
import os
sys.path.append('/root/Multilangual Compilor/V1')

from parser import parse_mix_file
from runners.plugin_manager import PluginManager

# Parse the test file
blocks = parse_mix_file('test_data_passing.mix')

print("=== PARSED BLOCKS ===")
for i, block in enumerate(blocks):
    print(f"Block {i+1}:")
    print(f"  Language: {block['language']}")
    print(f"  Imports: {block.get('imports', [])}")
    print(f"  Exports: {block.get('exports', [])}")
    print(f"  Code: {block['code'][:50]}...")
    print()

# Test data passing manually
plugin_manager = PluginManager()
shared_data = {}

print("=== EXECUTION SIMULATION ===")
for i, block in enumerate(blocks):
    lang = block['language']
    code = block['code']
    import_vars = block.get('imports', [])
    export_vars = block.get('exports', [])
    
    print(f"\n--- Block {i+1} [{lang}] ---")
    print(f"Import vars: {import_vars}")
    print(f"Export vars: {export_vars}")
    
    # Prepare import data
    import_data = {}
    for var_name in import_vars:
        if var_name in shared_data:
            import_data[var_name] = shared_data[var_name]
            print(f"📥 Importing {var_name} = {shared_data[var_name]}")
        else:
            print(f"⚠️  Variable {var_name} not found in shared data")
    
    # Execute
    result = plugin_manager.run_code(lang, code, import_data, export_vars)
    print(f"Return code: {result.get('return_code', 'N/A')}")
    print(f"Output: {result.get('output', '')}")
    print(f"Error: {result.get('error', '')}")
    print(f"Exported data: {result.get('exported_data', {})}")
    
    # Handle exported data
    if result.get('exported_data'):
        print(f"Export vars check: {export_vars}")
        for var_name, value in result['exported_data'].items():
            if var_name in export_vars:
                shared_data[var_name] = value
                print(f"📤 Exported {var_name} = {value}")
            else:
                print(f"⚠️  Variable {var_name} not in export list")
    
    print(f"Shared data after block: {shared_data}")

# C++ Runner for PolyRun
import subprocess
import tempfile
import os
import time
import json
from .base_runner import BaseRunner

class CppRunner(BaseRunner):
    """
    C++ code runner with data import/export capabilities
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        self.language = "cpp"
        self.file_extension = ".cpp"
        
    def run(self, code, import_data=None, export_vars=None):
        """
        Execute C++ code with optional data import/export
        
        Args:
            code: C++ code to execute
            import_data: Dict of variables to import (limited support)
            export_vars: List of variable names to export (limited support)
            
        Returns:
            Dict with output, error, return_code, exported_data
        """
        start_time = time.time()
        
        # Prepare code with import/export handling
        enhanced_code = self._prepare_code(code, import_data, export_vars)
        
        # Debug: Print the enhanced code to see what's being generated
        print("=== DEBUG: Enhanced C++ Code ===")
        print(enhanced_code)
        print("=== END DEBUG ===")
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix=self.file_extension, delete=False) as f:
            f.write(enhanced_code)
            cpp_file = f.name
        
        exe_file = cpp_file.replace('.cpp', '')
        
        try:
            # Compilation step
            compile_result = subprocess.run(
                ['g++', '-std=c++17', cpp_file, '-o', exe_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if compile_result.returncode != 0:
                execution_time = time.time() - start_time
                return {
                    'output': '',
                    'error': '[C++] Compile Error:\n' + compile_result.stderr,
                    'return_code': compile_result.returncode,
                    'exported_data': {},
                    'execution_time': execution_time
                }
            
            # Execution step
            exec_result = subprocess.run(
                [exe_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            execution_time = time.time() - start_time
            
            # Read exported data if available
            exported_data = self._read_exported_data(cpp_file)
            
            return {
                'output': exec_result.stdout,
                'error': exec_result.stderr,
                'return_code': exec_result.returncode,
                'exported_data': exported_data,
                'execution_time': execution_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                'output': '',
                'error': f'C++ execution timed out after {self.timeout} seconds',
                'return_code': 124,
                'exported_data': {},
                'execution_time': self.timeout
            }
        finally:
            # Clean up
            self._cleanup_temp_files(cpp_file, exe_file)
    
    def _prepare_code(self, code, import_data=None, export_vars=None):
        """Prepare C++ code with import/export functionality"""
        enhanced_code = []
        
        # Add necessary headers
        if import_data or export_vars:
            enhanced_code.append("#include <iostream>")
            enhanced_code.append("#include <fstream>")
            enhanced_code.append("#include <string>")
            enhanced_code.append("#include <vector>")
            enhanced_code.append("#include <map>")
            enhanced_code.append("#include <sstream>")
            enhanced_code.append("")
        
        # Check if original code has its own headers
        code_lines = code.split('\n')
        has_includes = any(line.strip().startswith('#include') for line in code_lines)
        has_main = 'int main(' in code
        
        if not has_includes:
            enhanced_code.append("#include <iostream>")
            enhanced_code.append("#include <vector>")
            enhanced_code.append("")
        
        # Add import data as constants with proper types
        if import_data:
            enhanced_code.append("// Imported data from previous blocks")
            for var_name, value in import_data.items():
                print(f"DEBUG: Processing {var_name} = {value} (type: {type(value)})")
                
                if isinstance(value, str):
                    # Escape quotes in strings
                    escaped_value = value.replace('"', '\\"')
                    enhanced_code.append(f'const std::string {var_name} = "{escaped_value}";')
                elif isinstance(value, int):
                    enhanced_code.append(f'const int {var_name} = {value};')
                elif isinstance(value, float):
                    enhanced_code.append(f'const double {var_name} = {value};')
                elif isinstance(value, bool):
                    enhanced_code.append(f'const bool {var_name} = {str(value).lower()};')
                elif isinstance(value, list):
                    print(f"DEBUG: Processing list {var_name} with values: {value}")
                    # Handle different types of lists
                    if not value:  # Empty list
                        enhanced_code.append(f'const std::vector<int> {var_name} = {{}};')
                    else:
                        # Check what types we have in the list
                        first_item = value[0]
                        if all(isinstance(x, int) for x in value):
                            # Integer vector
                            values_str = ', '.join(map(str, value))
                            enhanced_code.append(f'const std::vector<int> {var_name} = {{{values_str}}};')
                            print(f"DEBUG: Created int vector: const std::vector<int> {var_name} = {{{values_str}}};")
                        elif all(isinstance(x, (int, float)) for x in value):
                            # Mixed numbers - use double vector
                            values_str = ', '.join(map(str, value))
                            enhanced_code.append(f'const std::vector<double> {var_name} = {{{values_str}}};')
                            print(f"DEBUG: Created double vector: const std::vector<double> {var_name} = {{{values_str}}};")
                        elif all(isinstance(x, str) for x in value):
                            # String vector
                            values_str = ', '.join(f'"{item.replace(chr(34), chr(92)+chr(34))}"' for item in value)
                            enhanced_code.append(f'const std::vector<std::string> {var_name} = {{{values_str}}};')
                            print(f"DEBUG: Created string vector: const std::vector<std::string> {var_name} = {{{values_str}}};")
                        else:
                            # Mixed types - convert all to strings
                            values_str = ', '.join(f'"{str(item).replace(chr(34), chr(92)+chr(34))}"' for item in value)
                            enhanced_code.append(f'const std::vector<std::string> {var_name} = {{{values_str}}};')
                            print(f"DEBUG: Created mixed string vector: const std::vector<std::string> {var_name} = {{{values_str}}};")
                else:
                    # Try to convert to string as fallback
                    escaped_value = str(value).replace('"', '\\"')
                    enhanced_code.append(f'const std::string {var_name} = "{escaped_value}";')
                    print(f"DEBUG: Created string fallback: const std::string {var_name} = \"{escaped_value}\";")
            enhanced_code.append("")
        
        if has_main:
            # Insert the original code directly
            enhanced_code.extend(code_lines)
            
            # Add export functionality before the return statement if needed
            if export_vars:
                # Add export functionality with better vector support
                export_code = []
                export_code.append("    // Export data for next blocks")
                export_code.append("    std::ofstream export_file(\"__export__.json\");")
                export_code.append("    export_file << \"{\" << std::endl;")
                
                for i, var_name in enumerate(export_vars):
                    comma = "," if i < len(export_vars) - 1 else ""
                    # Try to detect if it's a vector and handle accordingly
                    export_code.append(f"    // Export {var_name}")
                    export_code.append(f"    export_file << \"\\\"{var_name}\\\": \";")
                    export_code.append(f"    // Check if {var_name} is a vector (simplified)")
                    export_code.append(f"    export_file << \"\\\"\" << {var_name} << \"\\\"{comma}\" << std::endl;")
                
                export_code.append("    export_file << \"}\" << std::endl;")
                export_code.append("    export_file.close();")
                
                # Insert before the last return statement
                modified_lines = []
                for line in enhanced_code:
                    if 'return 0;' in line:
                        modified_lines.extend(export_code)
                    modified_lines.append(line)
                enhanced_code = modified_lines
        else:
            # No main function, wrap in main
            enhanced_code.append("int main() {")
            enhanced_code.extend(['    ' + line for line in code_lines])
            
            if export_vars:
                enhanced_code.append("    // Export data for next blocks")
                enhanced_code.append("    std::ofstream export_file(\"__export__.json\");")
                enhanced_code.append("    export_file << \"{\" << std::endl;")
                
                for i, var_name in enumerate(export_vars):
                    comma = "," if i < len(export_vars) - 1 else ""
                    # Add a simple export that works for basic types
                    enhanced_code.append(f"    export_file << \"\\\"{var_name}\\\": \\\"\" << {var_name} << \"\\\"{comma}\" << std::endl;")
                
                enhanced_code.append("    export_file << \"}\" << std::endl;")
                enhanced_code.append("    export_file.close();")
            
            enhanced_code.append("    return 0;")
            enhanced_code.append("}")
        
        return '\n'.join(enhanced_code)
    
    def _read_exported_data(self, cpp_file):
        """Read exported data from JSON file"""
        export_file = os.path.join(os.path.dirname(cpp_file), "__export__.json")
        if os.path.exists(export_file):
            try:
                with open(export_file, 'r') as f:
                    data = json.load(f)
                os.remove(export_file)
                return data
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _cleanup_temp_files(self, cpp_file, exe_file=None):
        """Clean up temporary files"""
        try:
            if os.path.exists(cpp_file):
                os.remove(cpp_file)
            if exe_file and os.path.exists(exe_file):
                os.remove(exe_file)
            export_file = os.path.join(os.path.dirname(cpp_file), "__export__.json")
            if os.path.exists(export_file):
                os.remove(export_file)
        except OSError:
            pass


# Legacy function for backward compatibility
def run_code(code, config):
    """Legacy function - compile and execute C++ code"""
    runner = CppRunner(config)
    result = runner.run(code)
    
    return {
        "success": result['return_code'] == 0,
        "output": result['output'],
        "error": result['error'] if result['return_code'] != 0 else "",
        "execution_time": result.get('execution_time', 0),
        "memory_used": 0,  # Will implement proper tracking later
        "exit_code": result['return_code']
    }

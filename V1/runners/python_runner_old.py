# Python Runner for PolyRun
import subprocess
import tempfile
import time
import os
import json
import pickle
import base64
from .base_runner import BaseRunner

class PythonRunner(BaseRunner):
    """
    Python code runner with data import/export capabilities
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        self.language = "python"
        self.file_extension = ".py"
        
    def run(self, code, import_data=None, export_vars=None):
        """
        Execute Python code with optional data import/export
        
        Args:
            code: Python code to execute
            import_data: Dict of variables to import
            export_vars: List of variable names to export
            
        Returns:
            Dict with output, error, return_code, exported_data
        """
        start_time = time.time()
        
        # Prepare code with import/export handling
        enhanced_code = self._prepare_code(code, import_data, export_vars)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=self.file_extension, delete=False) as f:
            f.write(enhanced_code)
            temp_file = f.name
        
        try:
            # Execute the Python code
            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            execution_time = time.time() - start_time
            
            # Read exported data if available
            exported_data = self._read_exported_data(temp_file)
            
            return {
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode,
                'exported_data': exported_data,
                'execution_time': execution_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                'output': '',
                'error': f'Python execution timed out after {self.timeout} seconds',
                'return_code': 124,
                'exported_data': {},
                'execution_time': self.timeout
            }
        finally:
            # Clean up
            self._cleanup_temp_files(temp_file)
    
    def _prepare_code(self, code, import_data=None, export_vars=None):
        """Prepare Python code with import/export functionality"""
        enhanced_code = []
        
        # Add import data at the beginning
        if import_data:
            enhanced_code.append("# Imported data from previous blocks")
            enhanced_code.append("import json")
            enhanced_code.append("import pickle")
            enhanced_code.append("import base64")
            enhanced_code.append("")
            
            for var_name, value in import_data.items():
                if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    enhanced_code.append(f'{var_name} = {repr(value)}')
                else:
                    # For complex objects, use pickle
                    try:
                        pickled = base64.b64encode(pickle.dumps(value)).decode('ascii')
                        enhanced_code.append(f'{var_name} = pickle.loads(base64.b64decode("{pickled}"))')
                    except:
                        enhanced_code.append(f'{var_name} = {repr(str(value))}')
            enhanced_code.append("")
        
        # Add the main code
        enhanced_code.append("# User code")
        enhanced_code.append(code)
        
        # Add export functionality
        if export_vars:
            enhanced_code.append("")
            enhanced_code.append("# Export data for next blocks")
            enhanced_code.append("import json")
            enhanced_code.append("import pickle")
            enhanced_code.append("import base64")
            enhanced_code.append("")
            enhanced_code.append("_export_data = {}")
            
            for var_name in export_vars:
                enhanced_code.append(f"try:")
                enhanced_code.append(f"    if '{var_name}' in locals() or '{var_name}' in globals():")
                enhanced_code.append(f"        _val = {var_name}")
                enhanced_code.append(f"        if isinstance(_val, (str, int, float, bool, list, dict, type(None))):")
                enhanced_code.append(f"            _export_data['{var_name}'] = _val")
                enhanced_code.append(f"        else:")
                enhanced_code.append(f"            # Use pickle for complex objects")
                enhanced_code.append(f"            try:")
                enhanced_code.append(f"                _pickled = base64.b64encode(pickle.dumps(_val)).decode('ascii')")
                enhanced_code.append(f"                _export_data['{var_name}'] = {{'__pickle__': _pickled}}")
                enhanced_code.append(f"            except:")
                enhanced_code.append(f"                _export_data['{var_name}'] = str(_val)")
                enhanced_code.append(f"    else:")
                enhanced_code.append(f"        _export_data['{var_name}'] = None")
                enhanced_code.append(f"except:")
                enhanced_code.append(f"    _export_data['{var_name}'] = None")
                enhanced_code.append("")
            
            enhanced_code.append("with open('__export__.json', 'w') as _f:")
            enhanced_code.append("    json.dump(_export_data, _f)")
        
        return '\n'.join(enhanced_code)
    
    def _read_exported_data(self, temp_file):
        """Read exported data from JSON file"""
        export_file = os.path.join(os.path.dirname(temp_file), "__export__.json")
        if os.path.exists(export_file):
            try:
                with open(export_file, 'r') as f:
                    data = json.load(f)
                os.remove(export_file)
                
                # Deserialize pickled objects
                for key, value in data.items():
                    if isinstance(value, dict) and '__pickle__' in value:
                        try:
                            data[key] = pickle.loads(base64.b64decode(value['__pickle__']))
                        except:
                            data[key] = str(value)
                
                return data
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _cleanup_temp_files(self, temp_file):
        """Clean up temporary files"""
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            export_file = os.path.join(os.path.dirname(temp_file), "__export__.json")
            if os.path.exists(export_file):
                os.remove(export_file)
        except OSError:
            pass


# Legacy function for backward compatibility
def run_code(code, config):
    """Legacy function - execute Python code with timing and memory tracking"""
    runner = PythonRunner(config)
    result = runner.run(code)
    
    return {
        "success": result['return_code'] == 0,
        "output": result['output'],
        "error": result['error'] if result['return_code'] != 0 else "",
        "execution_time": result.get('execution_time', 0),
        "memory_used": 0,  # Will implement proper tracking later
        "exit_code": result['return_code']
    }
            }
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "output": "",
                "error": "[Python] Execution timed out.",
                "execution_time": execution_time,
                "memory_used": 0,
                "exit_code": -1
            }
        finally:
            # Clean up temp file
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)

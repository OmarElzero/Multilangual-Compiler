# Bash Runner for PolyRun
import subprocess
import tempfile
import os
import json
from .base_runner import BaseRunner

class BashRunner(BaseRunner):
    """
    Bash script runner with environment variable data passing
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        self.language = "bash"
        self.file_extension = ".sh"
        
    def run(self, code, import_data=None, export_vars=None):
        """
        Execute Bash script with optional data import/export
        
        Args:
            code: Bash script to execute
            import_data: Dict of variables to import as environment variables
            export_vars: List of variable names to export
            
        Returns:
            Dict with output, error, return_code, exported_data
        """
        # Check if bash is available
        try:
            subprocess.run(['bash', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {
                'output': '',
                'error': 'Bash not found. Please install bash to run shell scripts.',
                'return_code': 127,
                'exported_data': {}
            }
        
        # Prepare code with import/export handling
        enhanced_code = self._prepare_code(code, import_data, export_vars)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=self.file_extension, delete=False) as f:
            f.write(enhanced_code)
            temp_file = f.name
        
        # Make script executable
        os.chmod(temp_file, 0o755)
        
        # Prepare environment with imported data
        env = os.environ.copy()
        if import_data:
            for key, value in import_data.items():
                env[f'IMPORT_{key.upper()}'] = str(value)
        
        try:
            # Execute the bash script
            result = subprocess.run(
                ['bash', temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env
            )
            
            # Read exported data if available
            exported_data = self._read_exported_data(temp_file)
            
            return {
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode,
                'exported_data': exported_data
            }
            
        except subprocess.TimeoutExpired:
            return {
                'output': '',
                'error': f'Bash execution timed out after {self.timeout} seconds',
                'return_code': 124,
                'exported_data': {}
            }
        finally:
            # Clean up
            self._cleanup_temp_files(temp_file)
    
    def _prepare_code(self, code, import_data=None, export_vars=None):
        """Prepare Bash script with import/export functionality"""
        enhanced_code = ["#!/bin/bash"]
        enhanced_code.append("set -e  # Exit on error")
        enhanced_code.append("")
        
        # Add import data as variables
        if import_data:
            enhanced_code.append("# Imported data from previous blocks")
            for var_name, value in import_data.items():
                # Import as regular variables from environment
                enhanced_code.append(f'{var_name}="$IMPORT_{var_name.upper()}"')
            enhanced_code.append("")
        
        # Add the main code
        enhanced_code.append("# User code")
        enhanced_code.append(code)
        
        # Add export functionality
        if export_vars:
            enhanced_code.append("")
            enhanced_code.append("# Export data for next blocks")
            enhanced_code.append('EXPORT_FILE="$(dirname "$0")/__export__.json"')
            enhanced_code.append("cat > \"$EXPORT_FILE\" << EOF")
            enhanced_code.append("{")
            for i, var_name in enumerate(export_vars):
                comma = "," if i < len(export_vars) - 1 else ""
                enhanced_code.append(f'  "{var_name}": "${{{var_name}:-null}}"{comma}')
            enhanced_code.append("}")
            enhanced_code.append("EOF")
        
        return '\n'.join(enhanced_code)
    
    def _read_exported_data(self, temp_file):
        """Read exported data from JSON file"""
        export_file = os.path.join(os.path.dirname(temp_file), "__export__.json")
        if os.path.exists(export_file):
            try:
                with open(export_file, 'r') as f:
                    data = json.load(f)
                os.remove(export_file)
                # Convert string "null" to actual None
                for key, value in data.items():
                    if value == "null":
                        data[key] = None
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

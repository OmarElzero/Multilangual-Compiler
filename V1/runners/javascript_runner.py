# JavaScript Runner for PolyRun
import subprocess
import tempfile
import os
import json
from .base_runner import BaseRunner

class JavaScriptRunner(BaseRunner):
    """
    JavaScript code runner using Node.js
    Supports data import/export through JSON files
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        self.language = "javascript"
        self.file_extension = ".js"
        
    def run(self, code, import_data=None, export_vars=None):
        """
        Execute JavaScript code with optional data import/export
        
        Args:
            code: JavaScript code to execute
            import_data: Dict of variables to import
            export_vars: List of variable names to export
            
        Returns:
            Dict with output, error, return_code, exported_data
        """
        # Check if Node.js is available (try multiple common paths)
        node_paths = ['/usr/bin/node', 'node', '/usr/local/bin/node']
        node_cmd = None
        
        for path in node_paths:
            try:
                subprocess.run([path, '--version'], capture_output=True, check=True)
                node_cmd = path
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if not node_cmd:
            return {
                'output': '',
                'error': 'Node.js not found. Please install Node.js to run JavaScript code.',
                'return_code': 127,
                'exported_data': {}
            }
        
        # Prepare code with import/export handling
        enhanced_code = self._prepare_code(code, import_data, export_vars)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=self.file_extension, delete=False) as f:
            f.write(enhanced_code)
            temp_file = f.name
        
        try:
            # Execute the JavaScript code
            result = subprocess.run(
                [node_cmd, temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
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
                'error': f'JavaScript execution timed out after {self.timeout} seconds',
                'return_code': 124,
                'exported_data': {}
            }
        finally:
            # Clean up
            self._cleanup_temp_files(temp_file)
    
    def _prepare_code(self, code, import_data=None, export_vars=None):
        """Prepare JavaScript code with import/export functionality"""
        enhanced_code = []
        
        # Add import data at the beginning
        if import_data:
            enhanced_code.append("// Imported data from previous blocks")
            for var_name, value in import_data.items():
                if isinstance(value, str):
                    enhanced_code.append(f'const {var_name} = "{value}";')
                elif isinstance(value, (int, float)):
                    enhanced_code.append(f'const {var_name} = {value};')
                elif isinstance(value, (list, dict)):
                    enhanced_code.append(f'const {var_name} = {json.dumps(value)};')
                else:
                    enhanced_code.append(f'const {var_name} = {json.dumps(str(value))};')
            enhanced_code.append("")
        
        # Add the main code
        enhanced_code.append("// User code")
        enhanced_code.append(code)
        
        # Add export functionality
        if export_vars:
            enhanced_code.append("")
            enhanced_code.append("// Export data for next blocks")
            enhanced_code.append("const fs = require('fs');")
            enhanced_code.append("const path = require('path');")
            export_obj = {}
            for var_name in export_vars:
                export_obj[var_name] = f"typeof {var_name} !== 'undefined' ? {var_name} : null"
            
            export_code = f"const exportData = {{"
            for var_name in export_vars:
                export_code += f'"{var_name}": typeof {var_name} !== "undefined" ? {var_name} : null, '
            export_code = export_code.rstrip(', ') + "};"
            
            enhanced_code.append(export_code)
            enhanced_code.append('const exportFile = path.join(__dirname, "__export__.json");')
            enhanced_code.append('fs.writeFileSync(exportFile, JSON.stringify(exportData));')
        
        return '\n'.join(enhanced_code)
    
    def _read_exported_data(self, temp_file):
        """Read exported data from JSON file"""
        export_file = os.path.join(os.path.dirname(temp_file), "__export__.json")
        if os.path.exists(export_file):
            try:
                with open(export_file, 'r') as f:
                    data = json.load(f)
                os.remove(export_file)
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

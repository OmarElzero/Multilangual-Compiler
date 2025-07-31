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
        node_paths = [
            'nodejs',                  # Ubuntu common name (try first)
            '/usr/bin/nodejs',         # Ubuntu alternative name (try second)
            'node',                    # System PATH
            '/usr/bin/node',           # Standard Ubuntu location
            '/usr/local/bin/node',     # Local install
            '/opt/node/bin/node',      # Custom install
            '/app/node_modules/.bin/node',  # NPM local
            '/bin/node',               # Basic system location
        ]
        node_cmd = None
        tried_paths = []
        
        # Try to install Node.js first
        try:
            print("🔧 Attempting to install Node.js...")
            # Try quick installation methods
            install_commands = [
                ['apt-get', 'update'],
                ['apt-get', 'install', '-y', 'nodejs', 'npm']
            ]
            
            for cmd in install_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True, timeout=30)
                    print(f"✅ Executed: {' '.join(cmd)}")
                except:
                    pass
            
            # Create symlink if nodejs exists but node doesn't
            try:
                subprocess.run(['ln', '-sf', '/usr/bin/nodejs', '/usr/bin/node'], capture_output=True)
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ Installation attempt failed: {e}")
        
        for path in node_paths:
            try:
                result = subprocess.run([path, '--version'], capture_output=True, check=True, text=True)
                node_cmd = path
                print(f"Found Node.js at {path}: {result.stdout.strip()}")
                break
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                tried_paths.append(f"{path}: {str(e)}")
                continue
        
        # If not found, try to find it using 'which' command
        if not node_cmd:
            # Try different which commands
            for cmd in ['node', 'nodejs']:
                try:
                    which_result = subprocess.run(['which', cmd], capture_output=True, check=True, text=True)
                    potential_path = which_result.stdout.strip()
                    if potential_path:
                        try:
                            subprocess.run([potential_path, '--version'], capture_output=True, check=True)
                            node_cmd = potential_path
                            print(f"Found Node.js via 'which {cmd}': {potential_path}")
                            break
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            pass
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
        
        # If still not found, try some diagnostics
        if not node_cmd:
            try:
                # Check what's actually in /usr/bin/
                ls_result = subprocess.run(['ls', '/usr/bin/'], capture_output=True, text=True)
                node_files = [f for f in ls_result.stdout.split() if 'node' in f.lower()]
                print(f"Node-related files in /usr/bin/: {node_files}")
                
                # Check if we can find anything with 'node' anywhere
                find_result = subprocess.run(['find', '/usr', '-name', '*node*', '-type', 'f'], 
                                           capture_output=True, text=True, timeout=5)
                if find_result.stdout:
                    print(f"Found Node.js related files: {find_result.stdout.strip()}")
            except Exception as e:
                print(f"Diagnostic error: {e}")
        
        if not node_cmd:
            error_msg = f'Node.js not found. Tried paths: {", ".join(tried_paths)}'
            return {
                'output': '',
                'error': error_msg,
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

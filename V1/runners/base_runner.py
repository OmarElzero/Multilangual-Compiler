# Base Runner Class for PolyRun
import os
import tempfile
from abc import ABC, abstractmethod

class BaseRunner(ABC):
    """
    Abstract base class for all language runners
    Provides common functionality and interface
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.timeout = self.config.get('timeout', 30)
        self.memory_limit = self.config.get('memory_limit', '512m')
        self.language = None
        self.file_extension = None
        
    @abstractmethod
    def run(self, code, import_data=None, export_vars=None):
        """
        Execute code with optional data import/export
        
        Args:
            code: Source code to execute
            import_data: Dict of variables to import from previous blocks
            export_vars: List of variable names to export to next blocks
            
        Returns:
            Dict with keys: output, error, return_code, exported_data
        """
        pass
    
    def get_temp_file(self, code, suffix=None):
        """Create a temporary file with the given code"""
        suffix = suffix or self.file_extension
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(code)
            return f.name
    
    def cleanup_temp_file(self, file_path):
        """Remove temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass
    
    def validate_code(self, code):
        """Basic code validation - can be overridden by subclasses"""
        if not code or not code.strip():
            return False, "Empty code block"
        return True, ""
    
    def get_runner_info(self):
        """Get information about this runner"""
        return {
            'language': self.language,
            'file_extension': self.file_extension,
            'timeout': self.timeout,
            'memory_limit': self.memory_limit
        }

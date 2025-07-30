# Plugin Manager for PolyRun Language Runners
import importlib
import os
from typing import Dict, List, Optional, Any
from .base_runner import BaseRunner

class PluginManager:
    """
    Manages dynamic loading and discovery of language runners
    Supports plugin architecture for extensibility
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.runners: Dict[str, BaseRunner] = {}
        self.runner_cache: Dict[str, Any] = {}
        self._load_built_in_runners()
        self._discover_external_plugins()
    
    def _load_built_in_runners(self):
        """Load built-in language runners"""
        built_in_runners = {
            'python': 'python_runner.PythonRunner',
            'cpp': 'cpp_runner.CppRunner',
            'c++': 'cpp_runner.CppRunner',
            'c': 'cpp_runner.CppRunner',
            'javascript': 'javascript_runner.JavaScriptRunner',
            'js': 'javascript_runner.JavaScriptRunner',
            'bash': 'bash_runner.BashRunner',
            'sh': 'bash_runner.BashRunner',
            'shell': 'bash_runner.BashRunner'
        }
        
        for language, runner_path in built_in_runners.items():
            try:
                self._load_runner(language, runner_path)
            except Exception as e:
                print(f"Warning: Failed to load {language} runner: {e}")
    
    def _discover_external_plugins(self):
        """Discover external plugins in the plugins directory"""
        plugins_dir = os.path.join(os.path.dirname(__file__), '..', 'plugins')
        if not os.path.exists(plugins_dir):
            return
        
        for filename in os.listdir(plugins_dir):
            if filename.endswith('_runner.py'):
                try:
                    language = filename.replace('_runner.py', '')
                    module_path = f'plugins.{filename[:-3]}'
                    self._load_runner(language, f'{module_path}.{language.title()}Runner')
                except Exception as e:
                    print(f"Warning: Failed to load plugin {filename}: {e}")
    
    def _load_runner(self, language: str, runner_path: str):
        """Load a specific runner"""
        try:
            module_name, class_name = runner_path.rsplit('.', 1)
            
            # Handle relative imports for built-in runners
            if not module_name.startswith('.') and '.' not in module_name:
                module_name = f'runners.{module_name}'
            
            module = importlib.import_module(module_name, package='runners')
            runner_class = getattr(module, class_name)
            
            if issubclass(runner_class, BaseRunner):
                self.runner_cache[language.lower()] = runner_class
            else:
                print(f"Warning: {class_name} is not a BaseRunner subclass")
                
        except Exception as e:
            print(f"Failed to load {language} runner: {e}")
    
    def get_runner(self, language: str) -> Optional[BaseRunner]:
        """Get a runner instance for the specified language"""
        language = language.lower()
        
        if language in self.runners:
            return self.runners[language]
        
        if language in self.runner_cache:
            try:
                runner_class = self.runner_cache[language]
                runner = runner_class(self.config)
                self.runners[language] = runner
                return runner
            except Exception as e:
                print(f"Failed to instantiate {language} runner: {e}")
                return None
        
        return None
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.runner_cache.keys())
    
    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported"""
        return language.lower() in self.runner_cache
    
    def get_runner_info(self, language: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific runner"""
        runner = self.get_runner(language)
        if runner:
            return runner.get_runner_info()
        return None
    
    def reload_plugins(self):
        """Reload all plugins (useful for development)"""
        self.runners.clear()
        self.runner_cache.clear()
        self._load_built_in_runners()
        self._discover_external_plugins()
    
    def add_custom_runner(self, language: str, runner_class: type):
        """Add a custom runner programmatically"""
        if issubclass(runner_class, BaseRunner):
            self.runner_cache[language.lower()] = runner_class
        else:
            raise ValueError(f"Runner class must inherit from BaseRunner")
    
    def run_code(self, language: str, code: str, import_data=None, export_vars=None):
        """
        Convenient method to run code in any supported language
        
        Args:
            language: Programming language
            code: Source code to execute
            import_data: Data to import from previous blocks
            export_vars: Variables to export to next blocks
            
        Returns:
            Execution result dictionary
        """
        runner = self.get_runner(language)
        if not runner:
            return {
                'output': '',
                'error': f'Unsupported language: {language}',
                'return_code': 1,
                'exported_data': {}
            }
        
        return runner.run(code, import_data, export_vars)

"""
Security Manager for PolyRun
Handles security policies, resource limits, and code validation
"""

import re
import logging

class SecurityManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load security policies
        self.policies = config.get('docker_security_policies', {})
        self.resource_limits = config.get('docker_resource_limits', {})
        
    def validate_code_safety(self, code, language):
        """
        Perform static analysis to detect potentially dangerous patterns
        Returns: (is_safe: bool, message: str)
        """
        dangerous_patterns = {
            'python': [
                r'os\.system\s*\(',
                r'subprocess\.',
                r'eval\s*\(',
                r'exec\s*\(',
                r'__import__\s*\(',
                r'open\s*\([^)]*["\'][rwa]',  # File operations
                r'import\s+socket',
                r'import\s+urllib',
                r'import\s+requests',
            ],
            'cpp': [
                r'system\s*\(',
                r'fork\s*\(',
                r'exec[lv]*\s*\(',
                r'#include\s*<sys/',
                r'#include\s*<unistd\.h>',
                r'fopen\s*\(',
                r'popen\s*\(',
            ]
        }
        
        patterns = dangerous_patterns.get(language.lower(), [])
        
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Potentially dangerous pattern detected: {pattern}"
        
        # Check for excessive resource usage patterns
        if language.lower() == 'python':
            if 'while True:' in code and 'time.sleep' not in code:
                return False, "Potential infinite loop detected without sleep"
            
        elif language.lower() == 'cpp':
            if re.search(r'while\s*\(\s*true\s*\)', code, re.IGNORECASE):
                return False, "Potential infinite loop detected"
        
        return True, "Code passed safety validation"
    
    def get_container_security_opts(self):
        """Generate Docker security options"""
        opts = []
        
        # Basic security options
        opts.extend([
            '--security-opt=no-new-privileges',
            '--cap-drop=ALL',
            '--read-only',
            '--tmpfs=/tmp:rw,noexec,nosuid,size=100m',
        ])
        
        # Network restrictions
        if not self.policies.get('allow_network', False):
            opts.append('--network=none')
        
        # Additional restrictions based on policies
        if not self.policies.get('allow_privileged', False):
            opts.append('--user=1000:1000')
            
        return opts
    
    def get_resource_limits(self):
        """Get resource limits for containers"""
        return {
            'mem_limit': self.resource_limits.get('memory', '512m'),
            'cpu_quota': int(self.resource_limits.get('cpu', '0.5') * 100000),  # Convert to microseconds
            'cpu_period': 100000,  # 100ms
            'pids_limit': 50,
            'ulimits': [
                {'Name': 'nofile', 'Soft': 64, 'Hard': 64},  # File handles
                {'Name': 'nproc', 'Soft': 16, 'Hard': 16},   # Processes
            ]
        }
    
    def validate_execution_time(self, execution_time, timeout):
        """Check if execution time is within acceptable limits"""
        if execution_time > timeout * 1.1:  # 10% tolerance
            self.logger.warning(f"Execution took {execution_time:.2f}s, timeout was {timeout}s")
            return False
        return True
    
    def log_security_event(self, event_type, language, details):
        """Log security-related events"""
        self.logger.info(f"Security Event: {event_type} | Language: {language} | Details: {details}")

"""
Docker-based secure code runner for PolyRun
Executes code in isolated containers with resource limits
"""

import docker
import tempfile
import time
import os
import logging
from security.manager import SecurityManager

class DockerRunner:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.security_manager = SecurityManager(config)
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            self.docker_available = True
            self.logger.info("Docker client initialized successfully")
        except Exception as e:
            self.logger.warning(f"Docker not available: {e}")
            self.docker_available = False
    
    def run_code(self, code, language, config):
        """
        Execute code in a secure Docker container
        Falls back to local execution if Docker is unavailable
        """
        # Validate code safety first
        is_safe, safety_message = self.security_manager.validate_code_safety(code, language)
        if not is_safe:
            self.security_manager.log_security_event("UNSAFE_CODE_BLOCKED", language, safety_message)
            return {
                "success": False,
                "output": "",
                "error": f"Security check failed: {safety_message}",
                "execution_time": 0,
                "memory_used": 0,
                "exit_code": -1,
                "security_blocked": True
            }
        
        if self.docker_available:
            return self._run_in_docker(code, language, config)
        else:
            self.logger.warning("Docker unavailable, falling back to local execution")
            return self._run_locally(code, language, config)
    
    def _run_in_docker(self, code, language, config):
        """Execute code in Docker container"""
        start_time = time.time()
        
        # Get language-specific settings
        image_name = f"polyrun-{language}:latest"
        file_extension = self._get_file_extension(language)
        run_command = self._get_run_command(language)
        
        # Create temporary directory for code
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write code to file
            code_file = os.path.join(temp_dir, f"code{file_extension}")
            with open(code_file, 'w') as f:
                f.write(code)
            
            try:
                # Get security options and resource limits
                security_opts = self.security_manager.get_container_security_opts()
                resource_limits = self.security_manager.get_resource_limits()
                
                # Run container
                container = self.docker_client.containers.run(
                    image=image_name,
                    command=run_command,
                    volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}},
                    working_dir='/app',
                    mem_limit=resource_limits['mem_limit'],
                    cpu_quota=resource_limits['cpu_quota'],
                    cpu_period=resource_limits['cpu_period'],
                    pids_limit=resource_limits['pids_limit'],
                    network_mode='none',
                    user='runner',
                    detach=True,
                    remove=True,
                    security_opt=['no-new-privileges'],
                    cap_drop=['ALL'],
                    read_only=True,
                    tmpfs={'/tmp': 'rw,noexec,nosuid,size=100m'}
                )
                
                # Wait for completion with timeout
                timeout = config.get('timeout_seconds', 30)
                try:
                    result = container.wait(timeout=timeout)
                    logs = container.logs().decode('utf-8')
                    
                    execution_time = time.time() - start_time
                    
                    # Log security event
                    self.security_manager.log_security_event(
                        "CONTAINER_EXECUTION", 
                        language, 
                        f"Exit code: {result['StatusCode']}, Time: {execution_time:.2f}s"
                    )
                    
                    return {
                        "success": result['StatusCode'] == 0,
                        "output": logs,
                        "error": logs if result['StatusCode'] != 0 else "",
                        "execution_time": execution_time,
                        "memory_used": 0,  # Would need container stats for actual memory
                        "exit_code": result['StatusCode'],
                        "container_used": True
                    }
                    
                except docker.errors.ContainerError as e:
                    execution_time = time.time() - start_time
                    error_msg = f"Container execution failed: {e}"
                    self.security_manager.log_security_event("CONTAINER_ERROR", language, error_msg)
                    
                    return {
                        "success": False,
                        "output": "",
                        "error": error_msg,
                        "execution_time": execution_time,
                        "memory_used": 0,
                        "exit_code": -1,
                        "container_used": True
                    }
                    
            except docker.errors.ImageNotFound:
                self.logger.error(f"Docker image {image_name} not found. Run build_containers.sh first.")
                return {
                    "success": False,
                    "output": "",
                    "error": f"Docker image {image_name} not found. Please build containers first.",
                    "execution_time": 0,
                    "memory_used": 0,
                    "exit_code": -1,
                    "container_used": False
                }
            except Exception as e:
                execution_time = time.time() - start_time
                error_msg = f"Docker execution failed: {e}"
                self.logger.error(error_msg)
                
                return {
                    "success": False,
                    "output": "",
                    "error": error_msg,
                    "execution_time": execution_time,
                    "memory_used": 0,
                    "exit_code": -1,
                    "container_used": False
                }
    
    def _run_locally(self, code, language, config):
        """Fallback to local execution when Docker is unavailable"""
        # Import the original runners
        try:
            if language == 'python':
                from runners.python_runner import run_code
            elif language == 'cpp':
                from runners.cpp_runner import run_code
            else:
                return {
                    "success": False,
                    "output": "",
                    "error": f"No local runner available for {language}",
                    "execution_time": 0,
                    "memory_used": 0,
                    "exit_code": -1,
                    "container_used": False
                }
            
            result = run_code(code, config)
            result['container_used'] = False
            return result
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Local execution failed: {e}",
                "execution_time": 0,
                "memory_used": 0,
                "exit_code": -1,
                "container_used": False
            }
    
    def _get_file_extension(self, language):
        """Get file extension for language"""
        extensions = {
            'python': '.py',
            'cpp': '.cpp',
            'javascript': '.js',
            'bash': '.sh'
        }
        return extensions.get(language.lower(), '.txt')
    
    def _get_run_command(self, language):
        """Get execution command for language"""
        commands = {
            'python': ['python3', '/app/code.py'],
            'cpp': ['sh', '-c', 'g++ /app/code.cpp -o /tmp/code && /tmp/code'],
            'javascript': ['node', '/app/code.js'],
            'bash': ['bash', '/app/code.sh']
        }
        return commands.get(language.lower(), ['cat', '/app/code.txt'])
    
    def cleanup_containers(self):
        """Clean up stopped containers and unused images"""
        if not self.docker_available:
            return
            
        try:
            # Remove stopped containers
            self.docker_client.containers.prune()
            
            # Remove dangling images if enabled
            if self.config.get('docker_cleanup', True):
                self.docker_client.images.prune(filters={'dangling': True})
                
            self.logger.info("Container cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"Container cleanup failed: {e}")
    
    def get_docker_status(self):
        """Get Docker availability status"""
        return {
            "available": self.docker_available,
            "client_version": docker.__version__ if self.docker_available else None,
            "server_info": self.docker_client.info() if self.docker_available else None
        }

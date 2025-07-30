import os
import sys
from parser import parse_mix_file, validate_mix_file, consolidate_language_blocks
from datetime import datetime
import json
import argparse
import importlib
import logging
import time
import psutil
from runners.plugin_manager import PluginManager

def load_config(path='config.json'):
    with open(path, 'r') as f:
        return json.load(f)

def get_runner(language, use_docker=False, config=None):
    """Get appropriate runner based on Docker availability and config"""
    # Initialize plugin manager
    plugin_manager = PluginManager(config)
    
    if use_docker and config and config.get('docker_enabled', False):
        try:
            from runners.docker_runner import DockerRunner
            docker_runner = DockerRunner(config)
            
            # Return a lambda that calls the docker runner with the right signature
            return lambda code, cfg: docker_runner.run_code(code, language, cfg)
        except ImportError as e:
            logging.warning(f"Docker runner not available: {e}, falling back to local execution")
    
    # Use plugin manager to get runner
    runner = plugin_manager.get_runner(language)
    if runner:
        return lambda code, cfg, import_data=None, export_vars=None: runner.run(code, import_data, export_vars)
    
    # Fallback to legacy runners for compatibility
    try:
        runner_module = importlib.import_module(f"runners.{language}_runner")
        return runner_module.run_code
    except ImportError:
        return None

def setup_logging(config, timestamp):
    """Setup structured logging"""
    log_level = config.get('log_level', 'INFO')
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'output/run_{timestamp}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Execute mixed-language .mix files')
    parser.add_argument('input_file', help='Path to .mix file to execute')
    parser.add_argument('-c', '--config', default='config.json', help='Config file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--docker', action='store_true', help='Force Docker execution (if available)')
    parser.add_argument('--no-docker', action='store_true', help='Disable Docker execution')
    parser.add_argument('--no-consolidate', action='store_true', help='Disable header consolidation for C/C++')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Docker execution preference
    use_docker = args.docker or (config.get('docker_enabled', False) and not args.no_docker)
    use_consolidation = not args.no_consolidate
    
    # Setup logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = setup_logging(config, timestamp)
    
    # Log execution mode
    if use_docker:
        logger.info("🐳 Docker execution mode enabled")
    else:
        logger.info("🖥️  Local execution mode")
    
    # Validate input file exists
    if not os.path.exists(args.input_file):
        logger.error(f"File {args.input_file} not found")
        sys.exit(1)
    
    logger.info(f"Starting execution of {args.input_file}")
    
    # Parse the mix file
    try:
        blocks = parse_mix_file(args.input_file)
        logger.info(f"Parsed {len(blocks)} code blocks")
        
        # Consolidate blocks if enabled
        if use_consolidation:
            original_count = len(blocks)
            blocks = consolidate_language_blocks(blocks)
            if len(blocks) < original_count:
                logger.info(f"🔧 Consolidated {original_count} blocks into {len(blocks)} blocks (headers merged)")
            
    except Exception as e:
        logger.error(f"Failed to parse file: {e}")
        sys.exit(1)
    
    # Validate the parsed blocks
    validation_errors = validate_mix_file(blocks)
    if validation_errors:
        logger.error("Validation errors found:")
        for error in validation_errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    # Initialize Docker runner if needed
    docker_runner = None
    if use_docker:
        try:
            from runners.docker_runner import DockerRunner
            docker_runner = DockerRunner(config)
            docker_status = docker_runner.get_docker_status()
            
            if docker_status["available"]:
                logger.info("✅ Docker runtime ready for secure execution")
            else:
                logger.warning("❌ Docker not available, falling back to local execution")
                use_docker = False
        except ImportError:
            logger.warning("Docker runner module not available")
            use_docker = False
    
    # Execute each block
    total_start_time = time.time()
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Initialize data store for inter-block communication
    shared_data = {}
    plugin_manager = PluginManager(config)
    
    for i, block in enumerate(blocks):
        lang = block['language']
        code = block['code']
        import_vars = block.get('imports', [])
        export_vars = block.get('exports', [])
        
        logger.info(f"Running block {i+1} [{lang}]")
        logger.debug(f"Block imports: {import_vars}")
        logger.debug(f"Block exports: {export_vars}")
        logger.debug(f"Current shared_data: {shared_data}")
        
        # Prepare import data from previous blocks
        import_data = {}
        for var_name in import_vars:
            if var_name in shared_data:
                import_data[var_name] = shared_data[var_name]
                logger.info(f"📥 Importing {var_name} = {shared_data[var_name]}")
            else:
                logger.warning(f"⚠️  Variable {var_name} not found in shared data")
        
        logger.debug(f"Import vars: {import_vars}, Export vars: {export_vars}")
        logger.debug(f"Shared data: {shared_data}")
        logger.debug(f"Import data: {import_data}")
        
        # Check if language is supported
        if not plugin_manager.is_language_supported(lang):
            logger.error(f"Language {lang} not supported")
            result = {
                "success": False, 
                "error": f"Language {lang} not supported",
                "execution_time": 0,
                "memory_used": 0
            }
        else:
            # Use plugin manager directly
            try:
                block_start_memory = process.memory_info().rss
                result = plugin_manager.run_code(lang, code, import_data, export_vars)
                logger.debug(f"Plugin manager result: {result}")
                block_end_memory = process.memory_info().rss
                result['memory_used'] = block_end_memory - block_start_memory
                
                # Handle exported data
                if result.get('exported_data'):
                    logger.debug(f"Got exported data: {result['exported_data']}")
                    logger.debug(f"Export vars to check: {export_vars}")
                    for var_name, value in result['exported_data'].items():
                        if var_name in export_vars:
                            shared_data[var_name] = value
                            logger.info(f"📤 Exported {var_name} = {value}")
                        else:
                            logger.debug(f"Skipping {var_name} (not in export list)")
                else:
                    logger.debug("No exported data found")
                
            except Exception as e:
                logger.error(f"Runner failed: {e}")
                result = {
                    "success": False,
                    "error": f"Runner failed: {e}",
                    "execution_time": 0,
                    "memory_used": 0
                }
        
        # Log results with security information
        if result.get('success', result.get('return_code') == 0):
            container_info = " (🐳 Docker)" if result.get('container_used', False) else " (🖥️ Local)"
            security_info = " [🔒 Security Validated]" if result.get('security_blocked') is False else ""
            logger.info(f"Block {i+1} completed successfully in {result.get('execution_time', 0):.3f}s{container_info}{security_info}")
            if result.get('output'):
                logger.info(f"Output:\n{result['output']}")
        else:
            if result.get('security_blocked'):
                logger.error(f"🚫 Block {i+1} BLOCKED for security: {result.get('error', 'Security violation')}")
            else:
                logger.error(f"Block {i+1} failed: {result.get('error', 'Unknown error')}")
        
        # Display memory usage if available
        if result.get('memory_used', 0) > 0:
            logger.info(f"Memory used: {result['memory_used']/1024:.1f}KB")
    
    # Cleanup containers if Docker was used
    if use_docker and docker_runner:
        docker_runner.cleanup_containers()
    
    # Final summary
    total_time = time.time() - total_start_time
    final_memory = process.memory_info().rss
    total_memory = final_memory - initial_memory
    
    logger.info(f"Execution completed in {total_time:.3f}s")
    logger.info(f"Total memory change: {total_memory/1024:.1f}KB")

if __name__ == "__main__":
    main()

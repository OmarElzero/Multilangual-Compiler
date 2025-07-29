import os
import sys
from parser import parse_mix_file, validate_mix_file
from datetime import datetime
import json
import argparse
import importlib
import logging
import time
import psutil

def load_config(path='config.json'):
    with open(path, 'r') as f:
        return json.load(f)

def get_runner(language):
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
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Setup logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = setup_logging(config, timestamp)
    
    # Validate input file exists
    if not os.path.exists(args.input_file):
        logger.error(f"File {args.input_file} not found")
        sys.exit(1)
    
    logger.info(f"Starting execution of {args.input_file}")
    
    # Parse the mix file
    try:
        blocks = parse_mix_file(args.input_file)
        logger.info(f"Parsed {len(blocks)} code blocks")
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
    
    # Execute each block
    total_start_time = time.time()
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    for i, block in enumerate(blocks):
        lang = block['language']
        code = block['code']
        
        logger.info(f"Running block {i+1} [{lang}]")
        
        # Check if language is supported
        if lang not in config.get('supported_languages', []):
            logger.error(f"Language {lang} not supported")
            result = {
                "success": False, 
                "error": f"Language {lang} not supported",
                "execution_time": 0,
                "memory_used": 0
            }
        else:
            # Get and execute runner
            runner = get_runner(lang)
            if runner:
                try:
                    block_start_memory = process.memory_info().rss
                    result = runner(code, config)
                    block_end_memory = process.memory_info().rss
                    result['memory_used'] = block_end_memory - block_start_memory
                except Exception as e:
                    logger.error(f"Runner failed: {e}")
                    result = {
                        "success": False,
                        "error": f"Runner failed: {e}",
                        "execution_time": 0,
                        "memory_used": 0
                    }
            else:
                logger.error(f"No runner found for {lang}")
                result = {
                    "success": False, 
                    "error": f"No runner for {lang}",
                    "execution_time": 0,
                    "memory_used": 0
                }
        
        # Log results
        if result['success']:
            logger.info(f"Block {i+1} completed successfully in {result.get('execution_time', 0):.3f}s")
            if result.get('output'):
                logger.info(f"Output:\n{result['output']}")
        else:
            logger.error(f"Block {i+1} failed: {result['error']}")
        
        # Display memory usage if available
        if result.get('memory_used', 0) > 0:
            logger.info(f"Memory used: {result['memory_used']/1024:.1f}KB")
    
    # Final summary
    total_time = time.time() - total_start_time
    final_memory = process.memory_info().rss
    total_memory = final_memory - initial_memory
    
    logger.info(f"Execution completed in {total_time:.3f}s")
    logger.info(f"Total memory change: {total_memory/1024:.1f}KB")

if __name__ == "__main__":
    main()

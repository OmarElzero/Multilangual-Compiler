# FastAPI Backend for PolyRun Web Interface
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import sys
import os
import asyncio
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from parser import parse_mix_file, validate_mix_file, consolidate_language_blocks
from runners.plugin_manager import PluginManager
from security.manager import SecurityManager

app = FastAPI(title="PolyRun API", description="Multi-language code execution API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global managers
plugin_manager = None
security_manager = None
config = {}

# Data models
class CodeExecutionRequest(BaseModel):
    code: str
    language: Optional[str] = None
    consolidate: bool = True
    docker_enabled: bool = False

class ExecutionResult(BaseModel):
    success: bool
    output: str
    error: str
    execution_time: float
    memory_used: int
    blocks_executed: int
    blocks_consolidated: int

class LanguageInfo(BaseModel):
    name: str
    supported: bool
    runner_info: Optional[Dict[str, Any]] = None

class SystemStatus(BaseModel):
    status: str
    languages_supported: List[str]
    docker_available: bool
    security_enabled: bool
    version: str

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass  # Connection might be closed

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    global plugin_manager, security_manager, config
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {
            "supported_languages": ["python", "cpp", "javascript", "bash"],
            "timeout_seconds": 30,
            "docker_enabled": False,
            "security_enabled": True
        }
    
    # Initialize managers
    plugin_manager = PluginManager(config)
    security_manager = SecurityManager(config)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("PolyRun API server started")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main web interface"""
    html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    try:
        with open(html_path, 'r') as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>PolyRun Web Interface</h1><p>Frontend not found. Please build the frontend first.</p>")

@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status and capabilities"""
    docker_available = False
    try:
        import docker
        docker_client = docker.from_env()
        docker_available = True
    except:
        pass
    
    return SystemStatus(
        status="running",
        languages_supported=plugin_manager.get_supported_languages(),
        docker_available=docker_available,
        security_enabled=config.get("security_enabled", True),
        version="1.0.0"
    )

@app.get("/api/languages", response_model=List[LanguageInfo])
async def get_supported_languages():
    """Get list of supported languages with details"""
    languages = []
    for lang in plugin_manager.get_supported_languages():
        runner_info = plugin_manager.get_runner_info(lang)
        languages.append(LanguageInfo(
            name=lang,
            supported=True,
            runner_info=runner_info
        ))
    return languages

@app.post("/api/execute", response_model=ExecutionResult)
async def execute_code(request: CodeExecutionRequest):
    """Execute multi-language code"""
    try:
        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mix', delete=False) as f:
            f.write(request.code)
            temp_file = f.name
        
        try:
            # Parse the code
            blocks = parse_mix_file(temp_file)
            original_count = len(blocks)
            
            # Validate
            validation_errors = validate_mix_file(blocks)
            if validation_errors:
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Validation errors: {'; '.join(validation_errors)}",
                    execution_time=0.0,
                    memory_used=0,
                    blocks_executed=0,
                    blocks_consolidated=0
                )
            
            # Consolidate if requested
            if request.consolidate:
                blocks = consolidate_language_blocks(blocks)
            
            # Execute blocks
            total_output = []
            total_errors = []
            total_time = 0.0
            total_memory = 0
            shared_data = {}
            
            for i, block in enumerate(blocks):
                lang = block['language']
                code = block['code']
                imports = block.get('imports', [])
                exports = block.get('exports', [])
                
                # Prepare import data
                import_data = {}
                for var_name in imports:
                    if var_name in shared_data:
                        import_data[var_name] = shared_data[var_name]
                
                # Execute block
                result = plugin_manager.run_code(lang, code, import_data, exports)
                
                total_time += result.get('execution_time', 0)
                total_memory += result.get('memory_used', 0)
                
                if result['return_code'] == 0:
                    total_output.append(f"[{lang}] {result['output']}")
                    
                    # Update shared data with exports
                    if result.get('exported_data'):
                        shared_data.update(result['exported_data'])
                else:
                    total_errors.append(f"[{lang}] {result['error']}")
                    if not config.get('continue_on_error', False):
                        break
            
            return ExecutionResult(
                success=len(total_errors) == 0,
                output="\n".join(total_output),
                error="\n".join(total_errors),
                execution_time=total_time,
                memory_used=total_memory,
                blocks_executed=len(blocks),
                blocks_consolidated=original_count - len(blocks) if request.consolidate else 0
            )
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
            
    except Exception as e:
        logging.error(f"Execution error: {e}")
        return ExecutionResult(
            success=False,
            output="",
            error=f"Internal error: {str(e)}",
            execution_time=0.0,
            memory_used=0,
            blocks_executed=0,
            blocks_consolidated=0
        )

@app.websocket("/api/ws/execute")
async def websocket_execute(websocket: WebSocket):
    """WebSocket endpoint for real-time code execution"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive execution request
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # Send start message
            await manager.send_personal_message(
                json.dumps({"type": "start", "message": "Execution started"}), 
                websocket
            )
            
            # Execute code (similar to POST endpoint but with progress updates)
            try:
                code = request_data.get("code", "")
                consolidate = request_data.get("consolidate", True)
                
                # Create temp file and parse
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.mix', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                
                blocks = parse_mix_file(temp_file)
                if consolidate:
                    original_count = len(blocks)
                    blocks = consolidate_language_blocks(blocks)
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "consolidation", 
                            "message": f"Consolidated {original_count} blocks into {len(blocks)} blocks"
                        }), 
                        websocket
                    )
                
                shared_data = {}
                for i, block in enumerate(blocks):
                    lang = block['language']
                    code_block = block['code']
                    
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "block_start", 
                            "block": i + 1, 
                            "language": lang
                        }), 
                        websocket
                    )
                    
                    # Execute block
                    imports = block.get('imports', [])
                    exports = block.get('exports', [])
                    import_data = {var: shared_data.get(var) for var in imports if var in shared_data}
                    
                    result = plugin_manager.run_code(lang, code_block, import_data, exports)
                    
                    # Send result
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "block_result",
                            "block": i + 1,
                            "language": lang,
                            "success": result['return_code'] == 0,
                            "output": result['output'],
                            "error": result['error'],
                            "execution_time": result.get('execution_time', 0)
                        }), 
                        websocket
                    )
                    
                    # Update shared data
                    if result.get('exported_data'):
                        shared_data.update(result['exported_data'])
                
                # Send completion
                await manager.send_personal_message(
                    json.dumps({"type": "complete", "message": "Execution completed"}), 
                    websocket
                )
                
                os.unlink(temp_file)
                
            except Exception as e:
                await manager.send_personal_message(
                    json.dumps({
                        "type": "error", 
                        "message": f"Execution error: {str(e)}"
                    }), 
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Serve static files (if directory exists)
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

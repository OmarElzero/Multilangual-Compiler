# Modern FastAPI Backend for PolyRun Web Interface
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sys
import os
import json
import logging
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

app = FastAPI(title="PolyRun API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str
    consolidate: bool = True

@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve the modern web interface"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PolyRun</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .status-indicator {
            background: #4ade80;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: white;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .examples-bar {
            background: rgba(255, 255, 255, 0.1);
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .examples-label {
            color: white;
            font-weight: 500;
        }
        
        .example-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.875rem;
        }
        
        .example-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-1px);
        }
        
        .checkbox-container {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-left: auto;
        }
        
        .checkbox {
            width: 1rem;
            height: 1rem;
        }
        
        .checkbox-label {
            color: white;
            font-size: 0.875rem;
        }
        
        .main-container {
            display: flex;
            height: calc(100vh - 140px);
        }
        
        .editor-panel {
            flex: 1;
            background: white;
            margin: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
        }
        
        .panel-header {
            padding: 1rem;
            border-bottom: 1px solid #e5e7eb;
            font-weight: 600;
            color: #374151;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .editor {
            flex: 1;
            border: none;
            outline: none;
            padding: 1rem;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
            line-height: 1.5;
            resize: none;
            background: #1e1e1e;
            color: #d4d4d4;
            border-bottom-left-radius: 0.5rem;
            border-bottom-right-radius: 0.5rem;
        }
        
        .output-panel {
            flex: 1;
            background: white;
            margin: 1rem 1rem 1rem 0;
            border-radius: 0.5rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
        }
        
        .output {
            flex: 1;
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 1rem;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
            line-height: 1.5;
            overflow-y: auto;
            white-space: pre-wrap;
            margin: 0;
            border-bottom-left-radius: 0.5rem;
            border-bottom-right-radius: 0.5rem;
        }
        
        .controls {
            background: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: center;
            gap: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 0.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
        }
        
        .btn-primary {
            background: #3b82f6;
            color: white;
        }
        
        .btn-primary:hover {
            background: #2563eb;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        
        .btn-secondary {
            background: #6b7280;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #4b5563;
        }
        
        .btn-success {
            background: #10b981;
            color: white;
        }
        
        .btn-success:hover {
            background: #059669;
        }
        
        .btn-warning {
            background: #f59e0b;
            color: white;
        }
        
        .btn-warning:hover {
            background: #d97706;
        }
        
        .btn-info {
            background: #8b5cf6;
            color: white;
        }
        
        .btn-info:hover {
            background: #7c3aed;
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        
        .clear-btn {
            background: transparent;
            border: 1px solid #d1d5db;
            color: #6b7280;
            padding: 0.5rem;
            border-radius: 0.25rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .clear-btn:hover {
            background: #f3f4f6;
            border-color: #9ca3af;
        }
        
        .status-message {
            position: fixed;
            top: 1rem;
            right: 1rem;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            color: white;
            font-weight: 500;
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        
        .status-message.show {
            transform: translateX(0);
        }
        
        .status-success {
            background: #10b981;
        }
        
        .status-error {
            background: #ef4444;
        }
        
        @media (max-width: 768px) {
            .main-container {
                flex-direction: column;
                height: auto;
            }
            
            .editor-panel, .output-panel {
                margin: 0.5rem;
            }
            
            .controls {
                padding: 1rem;
            }
            
            .btn {
                padding: 0.5rem 1rem;
                font-size: 0.8rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <nav class="nav">
            <div class="logo">
                🏃‍♂️ PolyRun
            </div>
            <div class="status-indicator">
                <div class="status-dot"></div>
                <span>Online</span>
                <span>|</span>
                <span>9 languages</span>
            </div>
        </nav>
    </div>
    
    <div class="examples-bar">
        <span class="examples-label">Examples:</span>
        <button class="example-btn" onclick="loadExample('hello')">Hello World</button>
        <button class="example-btn" onclick="loadExample('datapass')">Data Passing Demo</button>
        <button class="example-btn" onclick="loadExample('cpp')">C++ Demo</button>
        
        <div class="checkbox-container">
            <input type="checkbox" id="consolidateCheck" class="checkbox" checked>
            <label for="consolidateCheck" class="checkbox-label">Consolidate blocks</label>
        </div>
    </div>
    
    <div class="main-container">
        <div class="editor-panel">
            <div class="panel-header">
                Code Editor (.mix file)
            </div>
            <textarea id="codeEditor" class="editor" placeholder="Write your multi-language code here..."></textarea>
        </div>
        
        <div class="output-panel">
            <div class="panel-header">
                Output
                <button class="clear-btn" onclick="clearOutput()">Clear</button>
            </div>
            <div id="output" class="output">Ready to execute your multi-language code...</div>
        </div>
    </div>
    
    <div class="controls">
        <button class="btn btn-primary" onclick="executeCode()" id="runBtn">
            ▶️ Run Code
        </button>
        <button class="btn btn-secondary" onclick="clearOutput()">
            🗑️ Clear Output
        </button>
        <button class="btn btn-success" onclick="loadExamples()">
            📚 Examples
        </button>
        <button class="btn btn-warning" onclick="saveProject()">
            💾 Save Project
        </button>
        <button class="btn btn-warning" onclick="loadProject()">
            📁 Load Project
        </button>
        <button class="btn btn-info" onclick="shareProject()">
            🔗 Share
        </button>
    </div>
    
    <div id="statusMessage" class="status-message"></div>
    
    <script>
        const examples = {
            hello: `#lang: python
print("Hello from Python! 🐍")

#lang: javascript
console.log("Hello from JavaScript! 🚀");`,
            
            datapass: `#lang: python
#export: message, numbers
message = "Data from Python"
numbers = [1, 2, 3, 4, 5]
print(f"Python: Created {message}")
print(f"Numbers: {numbers}")

#lang: javascript
#import: message, numbers
console.log("JavaScript received:", message);
console.log("Numbers:", numbers);
let sum = numbers.reduce((a, b) => a + b, 0);
console.log("Sum:", sum);`,
            
            cpp: `#lang: cpp
#include <iostream>
#include <vector>

int main() {
    std::cout << "Hello from C++! ⚡" << std::endl;
    
    std::vector<int> nums = {1, 2, 3, 4, 5};
    int sum = 0;
    for(int n : nums) sum += n;
    
    std::cout << "Sum: " << sum << std::endl;
    return 0;
}`
        };

        function loadExample(type) {
            document.getElementById('codeEditor').value = examples[type];
            showStatus('Example loaded!', 'success');
        }

        function showStatus(message, type) {
            const statusEl = document.getElementById('statusMessage');
            statusEl.textContent = message;
            statusEl.className = `status-message status-${type} show`;
            
            setTimeout(() => {
                statusEl.classList.remove('show');
            }, 3000);
        }

        async function executeCode() {
            const code = document.getElementById('codeEditor').value.trim();
            const runBtn = document.getElementById('runBtn');
            const output = document.getElementById('output');
            const consolidate = document.getElementById('consolidateCheck').checked;

            if (!code) {
                showStatus('Please enter some code', 'error');
                return;
            }

            runBtn.disabled = true;
            runBtn.innerHTML = '⏳ Running...';
            output.textContent = 'Executing...';

            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        code: code,
                        consolidate: consolidate 
                    })
                });

                const result = await response.json();

                if (result.success) {
                    let displayOutput = result.output || 'Code executed successfully';
                    
                    // Use the full output directly since it's now properly formatted
                    if (result.output) {
                        displayOutput = result.output.trim();
                    }
                    
                    output.textContent = displayOutput;
                    showStatus('Execution completed!', 'success');
                } else {
                    output.textContent = result.error || result.output || 'Execution failed';
                    showStatus('Execution failed', 'error');
                }
            } catch (error) {
                output.textContent = `Error: ${error.message}`;
                showStatus('Network error', 'error');
            } finally {
                runBtn.disabled = false;
                runBtn.innerHTML = '▶️ Run Code';
            }
        }

        function clearOutput() {
            document.getElementById('output').textContent = 'Ready to execute your multi-language code...';
            showStatus('Output cleared', 'success');
        }

        function loadExamples() {
            showStatus('Choose an example from the Examples bar above', 'success');
        }

        function saveProject() {
            // TODO: Implement project saving
            showStatus('Save functionality coming soon!', 'success');
        }

        function loadProject() {
            // TODO: Implement project loading  
            showStatus('Load functionality coming soon!', 'success');
        }

        function shareProject() {
            // TODO: Implement project sharing
            showStatus('Share functionality coming soon!', 'success');
        }

        // Load hello example by default
        document.addEventListener('DOMContentLoaded', function() {
            loadExample('hello');
        });
        
        // Handle keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                executeCode();
            }
        });
    </script>
</body>
</html>
    """

@app.post("/execute")
async def execute_code(request: CodeRequest):
    """Execute multi-language code with cloud platform compatibility"""
    try:
        # Import necessary modules
        import io
        import contextlib
        
        # Create temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mix', delete=False) as f:
            f.write(request.code)
            temp_file = f.name
        
        # Capture output
        output_buffer = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(output_buffer):
                with contextlib.redirect_stderr(output_buffer):
                    # Execute the code by calling the execution function directly
                    from parser import parse_mix_file, consolidate_language_blocks
                    from runners.plugin_manager import PluginManager
                    
                    # Load config
                    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Parse the mix file
                    blocks = parse_mix_file(temp_file)
                    print(f"📂 Parsed {len(blocks)} code blocks")
                    
                    # Apply consolidation if requested
                    if request.consolidate:
                        blocks = consolidate_language_blocks(blocks)
                        print(f"🔄 Consolidated to {len(blocks)} blocks")
                    
                    # Initialize plugin manager and execute blocks
                    plugin_manager = PluginManager(config)
                    export_data = {}
                    
                    for i, block in enumerate(blocks):
                        language = block['language']
                        code = block['code']
                        imports = block.get('imports', [])
                        exports = block.get('exports', [])
                        
                        print(f"\n🚀 Running block {i+1}: {language}")
                        
                        # Prepare import data
                        import_data = {}
                        for var in imports:
                            if var in export_data:
                                import_data[var] = export_data[var]
                                print(f"📥 Importing {var}: {import_data[var]}")
                        
                        # Get runner and execute
                        runner = plugin_manager.get_runner(language)
                        if runner:
                            result = runner.run(code, import_data, exports)
                            
                            # Print the actual code output first
                            output_displayed = False
                            if isinstance(result, dict):
                                if result.get('output'):
                                    print(result['output'].strip())
                                    output_displayed = True
                                if result.get('error'):
                                    print(f"Error: {result['error'].strip()}")
                            elif hasattr(result, 'output') and result.output:
                                print(result.output.strip())
                                output_displayed = True
                            elif isinstance(result, str):
                                print(result.strip())
                                output_displayed = True
                            
                            # Handle exports - check if result is dict and has exported_data
                            if exports and isinstance(result, dict) and 'exported_data' in result:
                                for var, value in result['exported_data'].items():
                                    if var in exports:
                                        export_data[var] = value
                                        print(f"📤 Exported {var}: {value}")
                            
                            if not output_displayed:
                                print(f"✅ Block completed successfully")
                        else:
                            print(f"❌ No runner found for language: {language}")
                            
            captured_output = output_buffer.getvalue()
            
            return {
                "success": True,
                "output": captured_output,
                "full_log": captured_output
            }
            
        except Exception as e:
            error_output = output_buffer.getvalue()
            return {
                "success": False,
                "error": str(e),
                "output": error_output,
                "full_log": error_output
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Server error: {str(e)}"
        }
        
    finally:
        # Clean up temp file
        if 'temp_file' in locals():
            try:
                os.unlink(temp_file)
            except:
                pass

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # Install Node.js at startup if not available
    print("🚀 Starting PolyRun server...")
    try:
        from nodejs_installer import install_nodejs
        install_nodejs()
    except Exception as e:
        print(f"⚠️ Node.js installation failed: {e}")
        print("JavaScript functionality may be limited")
    
    parser = argparse.ArgumentParser(description='PolyRun Web Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=int(os.getenv('PORT', 8000)), help='Port to bind to')
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port)

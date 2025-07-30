# Simple FastAPI Backend for PolyRun Web Interface
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
    use_docker: bool = False

@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve the web interface"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>PolyRun - Multi-Language Code Executor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #333; text-align: center; }
        .editor-container { display: flex; gap: 20px; margin: 20px 0; }
        .editor-panel, .output-panel { flex: 1; }
        textarea { width: 100%; height: 400px; font-family: monospace; padding: 10px; border: 1px solid #ddd; }
        .output { height: 400px; background: #1e1e1e; color: #fff; padding: 10px; font-family: monospace; overflow-y: auto; white-space: pre-wrap; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; text-align: center; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .examples { margin: 20px 0; }
        .example { display: inline-block; margin: 5px; padding: 5px 10px; background: #e9ecef; border-radius: 4px; cursor: pointer; }
        .example:hover { background: #dee2e6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 PolyRun - Multi-Language Code Executor</h1>
        
        <div class="examples">
            <strong>Examples:</strong>
            <span class="example" onclick="loadExample('hello')">Hello World</span>
            <span class="example" onclick="loadExample('math')">Data Passing Demo</span>
            <span class="example" onclick="loadExample('cpp')">C++ Demo</span>
        </div>
        
        <div class="editor-container">
            <div class="editor-panel">
                <h3>Code Editor (.mix file)</h3>
                <textarea id="codeEditor" placeholder="Enter your .mix code here..."></textarea>
            </div>
            <div class="output-panel">
                <h3>Output</h3>
                <div id="output" class="output">Ready to execute code...</div>
            </div>
        </div>
        
        <div style="text-align: center;">
            <button onclick="executeCode()" id="runBtn">▶️ Run Code</button>
            <button onclick="clearOutput()">Clear Output</button>
        </div>
        
        <div id="status" style="display: none;"></div>
    </div>

    <script>
        const examples = {
            hello: `#lang: python
print("Hello from Python! 🐍")

#lang: javascript
console.log("Hello from JavaScript! 🚀");`,
            
            math: `#lang: python
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
int main() {
    std::cout << "Hello from C++! ⚡" << std::endl;
    return 0;
}`
        };

        function loadExample(type) {
            document.getElementById('codeEditor').value = examples[type];
        }

        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `status ${type}`;
            status.style.display = 'block';
        }

        async function executeCode() {
            const code = document.getElementById('codeEditor').value.trim();
            const runBtn = document.getElementById('runBtn');
            const output = document.getElementById('output');

            if (!code) {
                showStatus('Please enter some code', 'error');
                return;
            }

            runBtn.disabled = true;
            runBtn.textContent = '⏳ Running...';
            output.textContent = 'Executing...';

            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code })
                });

                const result = await response.json();

                if (result.success) {
                    // Display the output, handling both formatted and full output
                    let displayOutput = result.output || result.full_log || 'Code executed successfully';
                    
                    // If output is empty but we have logs, extract the useful parts
                    if (!result.output && result.full_log) {
                        const lines = result.full_log.split('\n');
                        const outputLines = [];
                        let collectingOutput = false;
                        
                        for (let line of lines) {
                            if (line.includes('Output:')) {
                                collectingOutput = true;
                                continue;
                            }
                            if (line.includes('INFO - Running block') || line.includes('INFO - Block') || line.includes('INFO - Execution completed')) {
                                collectingOutput = false;
                                continue;
                            }
                            if (collectingOutput && line.trim() && !line.includes('INFO -')) {
                                outputLines.push(line.trim());
                            }
                            // Also collect export/import messages
                            if (line.includes('📤 Exported') || line.includes('📥 Importing')) {
                                outputLines.push(line.substring(line.indexOf('📤') !== -1 ? line.indexOf('📤') : line.indexOf('📥')));
                            }
                        }
                        
                        if (outputLines.length > 0) {
                            displayOutput = outputLines.join('\n');
                        }
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
                runBtn.textContent = '▶️ Run Code';
            }
        }

        function clearOutput() {
            document.getElementById('output').textContent = 'Ready to execute code...';
            document.getElementById('status').style.display = 'none';
        }

        // Load hello example by default
        loadExample('hello');
    </script>
</body>
</html>
    """

@app.post("/execute")
async def execute_code(request: CodeRequest):
    """Execute mixed-language code"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mix', delete=False) as f:
            f.write(request.code)
            temp_file = f.name
        
        try:
            # Import here to avoid issues
            from parser import parse_mix_file
            from main import main as execute_main
            
            # Parse blocks
            blocks = parse_mix_file(temp_file)
            if not blocks:
                return {"success": False, "error": "No code blocks found", "output": ""}
            
            # Execute using main function (simplified)
            import subprocess
            import sys
            
            result = subprocess.run([
                sys.executable, 'main.py', temp_file, '--no-docker'
            ], capture_output=True, text=True, cwd='/root/Multilangual Compilor/V1')
            
            if result.returncode == 0:
                # Extract just the execution output, not the logging
                output_lines = []
                for line in result.stdout.split('\n'):
                    if 'Output:' in line:
                        # Start collecting output after "Output:" lines
                        continue
                    elif 'INFO - Running block' in line or 'INFO - Block' in line:
                        # Skip info lines but extract actual code output
                        continue
                    elif 'INFO - Output:' in line:
                        continue
                    elif not line.strip().startswith('2025-') and line.strip():
                        # This is actual code output
                        output_lines.append(line)
                
                # If no specific output found, use full stdout
                if not output_lines:
                    formatted_output = result.stdout
                else:
                    formatted_output = '\n'.join(output_lines)
                
                return {
                    "success": True,
                    "output": formatted_output,
                    "error": "",
                    "full_log": result.stdout  # Include full log for debugging
                }
            else:
                return {
                    "success": False,
                    "output": result.stdout,
                    "error": result.stderr
                }
                
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Server error: {str(e)}",
            "output": ""
        }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

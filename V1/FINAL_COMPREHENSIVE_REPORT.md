# PolyRun: Complete Project Documentation
**A Comprehensive Guide for Fresh Students**
*Updated: July 30, 2025*
**A Comprehensive Guide for Fresh Students**

## 📖 Table of Contents
1. [Project Overview](#-project-overview)
2. [Project Structure](#-project-structure)
3. [Architecture Explanation](#️-architecture-explanation)
4. [File-by-File Code Explanation](#-file-by-file-code-explanation)
5. [Logic Flow Diagrams](#-logic-flow-diagrams)
6. [Phase Implementation Details](#-phase-implementation-details)
7. [Usage Examples](#-usage-examples)
8. [Advanced Features](#-advanced-features)
9. [Troubleshooting Guide](#️-troubleshooting-guide)
10. [Learning Objectives Achieved](#-learning-objectives-achieved)
11. [Further Reading and Extensions](#-further-reading-and-extensions)
12. [Conclusion](#-conclusion)

---

## 🎯 Project Overview

### What is PolyRun?
PolyRun is a **multi-language code execution engine** that allows you to write code in multiple programming languages within a single file and execute them sequentially with data passing between languages.

**Think of it like this**: 
- Imagine having a Python script that calculates some data
- Then JavaScript code that processes that data 
- Then C++ code that performs heavy computation on the results
- All in ONE file, with automatic data sharing between them!

### Why was this built?
1. **Educational Purpose**: Teach students how different languages can work together
2. **Real-world Simulation**: Many real applications use multiple technologies
3. **Learning Tool**: Understand how parsers, interpreters, and compilers work
4. **Modern Architecture**: Demonstrate web APIs, security, and plugin systems

### Core Concept: .mix Files
A `.mix` file contains multiple language blocks:

```
#lang: python
message = "Hello from Python"
print(message)
#export: message

#lang: javascript  
#import: message
console.log("JavaScript received:", message);
console.log("Processing complete!");
```

**Key Features:**
- **Multi-language support**: Python, C++, JavaScript, Bash
- **Data passing**: Variables can be shared between language blocks
- **Security**: Built-in code validation and sandboxing
- **Web interface**: Browser-based code editor and execution
- **Extensible**: Plugin architecture for adding new languages

---

## 📁 Project Structure

```
PolyRun/
├── 📄 main.py                          # Main entry point (CLI interface)
├── 📄 parser.py                        # .mix file parser and block extractor
├── 📄 config.json                      # Central configuration file
├── 📁 runners/                         # Language execution engines
│   ├── 📄 base_runner.py               # Abstract base class for all runners
│   ├── 📄 plugin_manager.py            # Dynamic runner loading system
│   ├── 📄 python_runner.py             # Python code executor
│   ├── 📄 cpp_runner.py                # C++ compiler and executor
│   ├── 📄 javascript_runner.py         # JavaScript/Node.js executor
│   ├── 📄 bash_runner.py               # Bash/Shell script executor
│   └── 📄 docker_runner.py             # Docker containerized execution
├── 📁 security/                        # Security and validation system
│   ├── 📄 manager.py                   # Security policy enforcement
│   ├── 📄 validator.py                 # Code safety validation
│   └── 📄 patterns.py                  # Dangerous code pattern detection
├── 📁 web/                             # Web interface components
│   ├── 📁 backend/                     # FastAPI web server
│   │   ├── 📄 modern_server.py         # Current web server (active)
│   │   ├── 📄 simple_server.py         # Original web server
│   │   └── 📄 main.py                  # Alternative advanced server
│   └── 📁 frontend/                    # HTML/CSS/JS interface
│       └── 📄 index.html               # Complete web UI
├── 📁 database/                        # Project storage system (Phase 6)
│   ├── 📄 project_db.py               # SQLite database manager
│   └── 📄 polyrun.db                  # SQLite database file
├── 📁 samples/                         # Example .mix files
│   ├── 📄 hello_world.mix             # Basic multi-language demo
│   ├── 📄 data_passing.mix            # Inter-language communication
│   └── 📄 cpp_demo.mix                # C++ compilation example
├── 📁 tests/                           # Test files and validation
├── 📁 output/                          # Execution logs and results
├── 📁 docker/                          # Docker containerization files
└── 📁 instructions/                    # Development documentation
```

### File Organization Logic

**Core System** (`main.py`, `parser.py`, `config.json`):
- These files form the heart of PolyRun
- `main.py` orchestrates everything
- `parser.py` breaks .mix files into executable blocks
- `config.json` controls all system behavior

**Runners Directory** (`runners/`):
- Each language has its own runner (e.g., `python_runner.py`)
- `base_runner.py` defines the interface all runners must follow
- `plugin_manager.py` loads runners dynamically
- This design makes adding new languages easy

**Security System** (`security/`):
- Validates code before execution
- Prevents dangerous operations
- Enforces resource limits
- Critical for safe code execution

**Web Interface** (`web/`):
- `backend/` contains the web server (FastAPI)
- `frontend/` contains the user interface (HTML/JS)
- Provides browser-based access to PolyRun

**Database System** (`database/`):
- Stores and manages projects
- Handles sharing and collaboration
- SQLite for simplicity
4. **Educational Platform**: Demonstrate language interoperability

### Core Concept: .mix Files
```
#lang: python
print("Hello from Python!")
data = [1, 2, 3, 4, 5]

#lang: javascript
console.log("Hello from JavaScript!");
let sum = [1,2,3,4,5].reduce((a,b) => a+b, 0);
console.log("Sum:", sum);

#lang: cpp
#include <iostream>
int main() {
    std::cout << "Hello from C++!" << std::endl;
    return 0;
}
```

---

## 🏗️ Architecture Explanation

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │────│  FastAPI Backend │────│   Core Engine   │
│   (HTML/JS)     │    │   (REST API)    │    │  (Python CLI)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                        ┌───────────────────────────────┼───────────────────────────────┐
                        │                               │                               │
                ┌───────▼────────┐            ┌────────▼────────┐            ┌────────▼────────┐
                │     Parser      │            │   Plugin Mgr    │            │   Security Mgr  │
                │  (parser.py)    │            │  (runners/)     │            │  (security/)    │
                └────────────────┘            └─────────────────┘            └─────────────────┘
```

### Component Responsibilities

#### 1. **Parser Module** (`parser.py`)
- **Purpose**: Breaks .mix files into language-specific blocks
- **Input**: Raw .mix file content
- **Output**: Structured list of code blocks with metadata
- **Key Functions**:
  - `parse_mix_file()`: Main parsing logic
  - `consolidate_language_blocks()`: Merge blocks of same language
  - `validate_mix_file()`: Check for syntax errors

#### 2. **Plugin Manager** (`runners/plugin_manager.py`)
- **Purpose**: Dynamically loads and manages language runners
- **Pattern**: Factory + Plugin Architecture
- **Benefits**: Easy to add new languages without changing core code

#### 3. **Language Runners** (`runners/`)
- **Purpose**: Execute code in specific languages
- **Base Class**: `BaseRunner` (abstract interface)
- **Implementations**: `PythonRunner`, `CppRunner`, `JavaScriptRunner`, `BashRunner`

#### 4. **Security Manager** (`security/manager.py`)
- **Purpose**: Validate code safety before execution
- **Features**: Pattern detection, resource limits, sandboxing

#### 5. **Web Interface** (`web/backend/`)
- **Purpose**: HTTP API and web UI for remote access
- **Technology**: FastAPI + HTML/JavaScript

---

## 📁 File-by-File Code Explanation

### 🔧 Core Files

#### `main.py` - The Orchestrator
**Purpose**: Main entry point that coordinates all components

```python
# Key sections explained:

# 1. Configuration Loading
def load_config(path='config.json'):
    with open(path, 'r') as f:
        return json.load(f)
# WHY: Centralizes all settings in one place

# 2. Runner Selection Logic  
def get_runner(language, use_docker=False, config=None):
    plugin_manager = PluginManager(config)
    runner = plugin_manager.get_runner(language)
    # WHY: Plugin pattern allows dynamic language addition

# 3. Main Execution Loop
for i, block in enumerate(blocks):
    lang = block['language']
    code = block['code']
    imports = block.get('imports', [])
    exports = block.get('exports', [])
    
    # Get runner for this language
    runner = get_runner(lang, use_docker, config)
    
    # Prepare imported data
    import_data = {var: shared_data[var] for var in imports if var in shared_data}
    
    # Execute with data passing
    result = runner.run(code, import_data, exports)
    
    # Update shared data with exports
    if result.get('exported_data'):
        shared_data.update(result['exported_data'])
# WHY: Sequential execution with data flow between blocks
```

**Line-by-Line Logic**:
1. **Lines 1-15**: Import required modules and set up logging
2. **Lines 16-25**: Load configuration from JSON file
3. **Lines 26-45**: Get appropriate runner (Docker or local)
4. **Lines 46-65**: Argument parsing for CLI interface
5. **Lines 66-85**: Initialize logging and memory tracking
6. **Lines 86-110**: Parse and validate .mix file
7. **Lines 111-180**: Main execution loop with data passing
8. **Lines 181-200**: Result logging and cleanup

#### `parser.py` - The Language Block Parser
**Purpose**: Converts .mix files into structured data

```python
# Core parsing logic explained:

def parse_mix_file(file_path):
    blocks = []
    current_block = {"language": None, "code": [], "imports": [], "exports": []}
    recording = False
    
    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Detect language markers
        if line_stripped.startswith("#lang:"):
            # Save previous block
            if recording and current_block["language"]:
                blocks.append({
                    "language": current_block["language"],
                    "code": "".join(current_block["code"]).strip(),
                    "start_line": current_block["start_line"],
                    "imports": current_block["imports"],
                    "exports": current_block["exports"]
                })
            
            # Start new block
            current_block = {
                "language": line_stripped.split(":")[1].strip(),
                "code": [],
                "start_line": line_num,
                "imports": [],
                "exports": []
            }
            recording = True
            
        # Detect import/export directives
        elif line_stripped.startswith("#import:") and recording:
            import_vars = line_stripped.replace("#import:", "").strip()
            current_block["imports"].extend([var.strip() for var in import_vars.split(",") if var.strip()])
            
        elif line_stripped.startswith("#export:") and recording:
            export_vars = line_stripped.replace("#export:", "").strip()
            current_block["exports"].extend([var.strip() for var in export_vars.split(",") if var.strip()])
            
        # Regular code line
        elif recording:
            current_block["code"].append(line)
    
    return blocks
```

**Why This Design?**:
- **State Machine**: Uses `recording` flag to track parsing state
- **Metadata Capture**: Stores imports/exports for data passing
- **Line Tracking**: Maintains line numbers for error reporting
- **Memory Efficient**: Processes file line by line

#### `config.json` - Central Configuration
**Purpose**: Single source of truth for all settings

```json
{
    "supported_languages": ["python", "cpp", "c++", "c", "javascript", "js", "bash", "sh", "shell"],
    "timeout_seconds": 30,
    "memory_limit_mb": 512,
    "docker_enabled": true,
    "consolidation_enabled": true,
    "security": {
        "validate_code": true,
        "dangerous_patterns": [
            "os.system", "subprocess.call", "eval", "exec",
            "system(", "popen(", "execl(", "fork("
        ],
        "max_file_size_mb": 1,
        "max_execution_time": 30
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(levelname)s - %(message)s",
        "output_dir": "output"
    }
}
```

**Configuration Sections**:
- **Languages**: Which languages are supported
- **Limits**: Timeout and memory constraints
- **Security**: Code validation rules
- **Logging**: How to record execution details

### 🏃‍♂️ Runner System

#### `runners/base_runner.py` - Abstract Base Class
**Purpose**: Defines interface that all language runners must implement

```python
class BaseRunner(ABC):
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
        
        Returns:
            Dict with keys: output, error, return_code, exported_data
        """
        pass
```

**Why Abstract Base Class?**:
- **Consistency**: All runners have same interface
- **Polymorphism**: Can treat all runners the same way
- **Extensibility**: Easy to add new language support
- **Type Safety**: Prevents implementation errors

#### `runners/python_runner.py` - Python Execution
**Purpose**: Execute Python code with data import/export

```python
def _prepare_code(self, code, import_data=None, export_vars=None):
    enhanced_code = []
    
    # Add import data at the beginning
    if import_data:
        enhanced_code.append("# Imported data from previous blocks")
        for var_name, value in import_data.items():
            if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                enhanced_code.append(f'{var_name} = {repr(value)}')
            else:
                # For complex objects, use pickle
                pickled = base64.b64encode(pickle.dumps(value)).decode('ascii')
                enhanced_code.append(f'{var_name} = pickle.loads(base64.b64decode("{pickled}"))')
    
    # Add the main code
    enhanced_code.append("# User code")
    enhanced_code.append(code)
    
    # Add export functionality
    if export_vars:
        enhanced_code.append("# Export data for next blocks")
        enhanced_code.append("_export_data = {}")
        for var_name in export_vars:
            enhanced_code.append(f"try:")
            enhanced_code.append(f"    _export_data['{var_name}'] = {var_name}")
            enhanced_code.append(f"except:")
            enhanced_code.append(f"    _export_data['{var_name}'] = None")
        enhanced_code.append("with open('__export__.json', 'w') as _f:")
        enhanced_code.append("    json.dump(_export_data, _f)")
    
    return '\n'.join(enhanced_code)
```

**Data Flow Logic**:
1. **Import Injection**: Adds imported variables to code
2. **Code Execution**: Runs user's Python code
3. **Export Capture**: Saves specified variables to JSON
4. **Error Handling**: Graceful handling of missing variables

#### `runners/cpp_runner.py` - C++ Compilation and Execution
**Purpose**: Compile and execute C++ code

```python
def run(self, code, import_data=None, export_vars=None):
    # Prepare code with imports/exports
    enhanced_code = self._prepare_code(code, import_data, export_vars)
    
    # Create temporary files
    cpp_file = tempfile.NamedTemporaryFile(suffix='.cpp', delete=False)
    exe_file = cpp_file.name.replace('.cpp', '')
    
    try:
        # Write enhanced code to file
        with open(cpp_file.name, 'w') as f:
            f.write(enhanced_code)
        
        # Compilation step
        compile_result = subprocess.run([
            'g++', '-std=c++17', cpp_file.name, '-o', exe_file
        ], capture_output=True, text=True, timeout=30)
        
        if compile_result.returncode != 0:
            return {
                'output': '',
                'error': '[C++] Compile Error:\n' + compile_result.stderr,
                'return_code': compile_result.returncode,
                'exported_data': {}
            }
        
        # Execution step
        exec_result = subprocess.run([exe_file], 
                                   capture_output=True, 
                                   text=True, 
                                   timeout=self.timeout)
        
        return {
            'output': exec_result.stdout,
            'error': exec_result.stderr,
            'return_code': exec_result.returncode,
            'exported_data': self._read_exported_data(cpp_file.name)
        }
    finally:
        # Cleanup temporary files
        self._cleanup_temp_files(cpp_file.name, exe_file)
```

**Two-Phase Execution**:
1. **Compilation**: C++ source → executable binary
2. **Execution**: Run the compiled binary
3. **Data Handling**: Limited to basic types (strings, numbers)

#### `runners/javascript_runner.py` - Node.js Execution
**Purpose**: Execute JavaScript using Node.js runtime

```python
def _prepare_code(self, code, import_data=None, export_vars=None):
    enhanced_code = []
    
    # Add imports as JavaScript variables
    if import_data:
        enhanced_code.append("// Imported data from previous blocks")
        for var_name, value in import_data.items():
            if isinstance(value, str):
                enhanced_code.append(f'const {var_name} = "{value}";')
            elif isinstance(value, (int, float)):
                enhanced_code.append(f'const {var_name} = {value};')
            elif isinstance(value, (list, dict)):
                enhanced_code.append(f'const {var_name} = {json.dumps(value)};')
    
    # Add user code
    enhanced_code.append("// User code")
    enhanced_code.append(code)
    
    # Add export functionality
    if export_vars:
        enhanced_code.append("// Export data for next blocks")
        enhanced_code.append("const fs = require('fs');")
        enhanced_code.append("const exportData = {")
        for var_name in export_vars:
            enhanced_code.append(f'  "{var_name}": typeof {var_name} !== "undefined" ? {var_name} : null,')
        enhanced_code.append("};")
        enhanced_code.append('fs.writeFileSync("__export__.json", JSON.stringify(exportData));')
    
    return '\n'.join(enhanced_code)
```

**JavaScript-Specific Features**:
- **Type Checking**: Uses `typeof` to check variable existence
- **JSON Serialization**: Native JSON support for data export
- **File System**: Uses Node.js `fs` module for file operations

### 🔒 Security System

#### `security/manager.py` - Code Safety Validation
**Purpose**: Prevent execution of dangerous code patterns

```python
class SecurityManager:
    def __init__(self, config):
        self.config = config
        self.dangerous_patterns = config.get('security', {}).get('dangerous_patterns', [])
        
    def validate_code_safety(self, code, language):
        """Check if code contains dangerous patterns"""
        for pattern in self.dangerous_patterns:
            if pattern in code:
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Language-specific validations
        if language == 'python':
            return self._validate_python_code(code)
        elif language == 'cpp':
            return self._validate_cpp_code(code)
        
        return True, ""
    
    def _validate_python_code(self, code):
        """Python-specific security checks"""
        dangerous_imports = ['os', 'subprocess', 'sys']
        for imp in dangerous_imports:
            if f'import {imp}' in code or f'from {imp}' in code:
                return False, f"Import of dangerous module: {imp}"
        return True, ""
```

**Security Layers**:
1. **Pattern Detection**: Scans for dangerous function calls
2. **Import Validation**: Blocks dangerous module imports
3. **Resource Limits**: Enforces memory and time constraints
4. **Sandbox Environment**: Uses Docker for isolation

### 🌐 Web Interface

#### `web/backend/simple_server.py` - HTTP API Server
**Purpose**: Provides web-based access to PolyRun functionality

```python
@app.post("/execute")
async def execute_code(request: CodeRequest):
    """Execute mixed-language code via HTTP"""
    try:
        # Create temporary file from web request
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mix', delete=False) as f:
            f.write(request.code)
            temp_file = f.name
        
        # Execute using subprocess (isolation)
        result = subprocess.run([
            sys.executable, 'main.py', temp_file, '--no-docker'
        ], capture_output=True, text=True, cwd='/root/Multilangual Compilor/V1')
        
        if result.returncode == 0:
            return {"success": True, "output": result.stdout, "error": ""}
        else:
            return {"success": False, "output": result.stdout, "error": result.stderr}
            
    except Exception as e:
        return {"success": False, "error": f"Server error: {str(e)}", "output": ""}
    finally:
        # Always clean up temporary files
        if os.path.exists(temp_file):
            os.unlink(temp_file)
```

**Web Architecture**:
- **FastAPI Framework**: Modern Python web framework
- **REST API**: HTTP POST for code execution
- **CORS Support**: Cross-origin requests for frontend
- **Error Handling**: Graceful error responses

---

## 🔄 Logic Flow Diagrams

### Main Execution Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Parse     │───▶│  Validate   │───▶│  Execute    │
│ .mix File   │    │   Blocks    │    │   Blocks    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                    │                   │
       ▼                    ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Extract     │    │ Security    │    │ Data        │
│ Language    │    │ Check       │    │ Passing     │
│ Blocks      │    │ Code        │    │ Between     │
│             │    │             │    │ Languages   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Data Passing Flow
```
Block 1 (Python)           Block 2 (JavaScript)       Block 3 (C++)
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│ #export:    │──JSON─────▶│ #import:    │──JSON─────▶│ #import:    │
│ message,    │  File      │ message,    │  File      │ message     │
│ numbers     │            │ numbers     │            │             │
└─────────────┘            └─────────────┘            └─────────────┘
```

### Security Validation Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Input     │───▶│  Pattern    │───▶│  Execute    │
│   Code      │    │  Detection  │    │  or Block   │
└─────────────┘    └─────────────┘    └─────────────┘
                          │                   │
                          ▼                   ▼
                   ┌─────────────┐    ┌─────────────┐
                   │  Dangerous  │    │   Safe      │
                   │  Pattern    │    │ Execution   │
                   │  Found      │    │             │
                   └─────────────┘    └─────────────┘
```

---

## 📋 Phase Implementation Details

### Phase 1: CLI MVP ✅
**Goal**: Basic command-line execution of .mix files

**Implementation**:
- Created `main.py` with argument parsing
- Built basic `parser.py` for .mix file parsing
- Implemented `python_runner.py` and `cpp_runner.py`
- Added `config.json` for settings management

**Key Learning**: Established the core architecture and proof of concept

### Phase 1.5: Testing & Validation ✅
**Goal**: Comprehensive testing and error handling

**Implementation**:
- Added `validate_mix_file()` function
- Created test files in `samples/` directory
- Implemented proper error reporting with line numbers
- Added memory and time tracking

**Key Learning**: Testing early prevents architectural issues

### Phase 2: Error Handling + Output Capture ✅
**Goal**: Robust execution with proper error handling

**Implementation**:
- Enhanced error messages with context
- Added execution time and memory tracking
- Improved logging system with timestamps
- Created structured output format

**Key Learning**: Good error messages are crucial for user experience

### Phase 2.5: Performance Monitoring ✅
**Goal**: Track and optimize execution performance

**Implementation**:
- Added `psutil` for memory monitoring
- Implemented execution timing
- Created performance logging
- Added resource usage reports

**Key Learning**: Performance monitoring helps identify bottlenecks

### Phase 2.7: Header Consolidation ✅
**Goal**: Optimize C++ compilation by merging headers

**Implementation**:
- Added `consolidate_language_blocks()` function
- Implemented header extraction logic
- Created main function merging for C++
- Added `--no-consolidate` option

**Key Learning**: Domain-specific optimizations can significantly improve performance

### Phase 3: Sandboxing + Security ✅
**Goal**: Secure code execution with safety checks

**Implementation**:
- Created `SecurityManager` class
- Added dangerous pattern detection
- Implemented Docker containerization
- Added resource limits and timeouts

**Key Learning**: Security must be built in from the start, not added later

### Phase 4: Multi-Language + Data Linking ✅
**Goal**: Add more languages and enable data passing

**Implementation**:
- Created `plugin_manager.py` for extensible architecture
- Added `javascript_runner.py` and `bash_runner.py`
- Implemented import/export system with JSON serialization
- Enhanced parser to handle `#import:` and `#export:` tags

**Key Learning**: Plugin architecture makes adding new features much easier

### Phase 5: Web Interface ✅
**Goal**: Web-based UI for remote access

**Implementation**:
- Built FastAPI backend with REST endpoints
- Created embedded HTML/JavaScript frontend
- Added real-time code execution via HTTP
- Implemented example library and download features

**Key Learning**: Web interfaces dramatically improve accessibility

---

## 💡 Usage Examples

### Basic Multi-Language Execution
```bash
# Create a .mix file
cat > example.mix << EOF
#lang: python
print("Hello from Python!")
result = 2 + 2
print(f"2 + 2 = {result}")

#lang: javascript
console.log("Hello from JavaScript!");
let fibonacci = n => n <= 1 ? n : fibonacci(n-1) + fibonacci(n-2);
console.log("Fibonacci(10):", fibonacci(10));

#lang: cpp
#include <iostream>
int main() {
    std::cout << "Hello from C++!" << std::endl;
    return 0;
}
EOF

# Execute the file
python3 main.py example.mix
```

### Data Passing Between Languages
```bash
cat > data_example.mix << EOF
#lang: python
#export: message, numbers
message = "Data from Python"
numbers = [1, 2, 3, 4, 5]
print(f"Python: Created {message}")

#lang: javascript
#import: message, numbers
console.log("JavaScript received:", message);
console.log("Numbers:", numbers);
let sum = numbers.reduce((a, b) => a + b, 0);
console.log("Sum:", sum);

#lang: bash
#import: message
echo "Bash received: $message"
echo "Processing complete!"
EOF

python3 main.py data_example.mix
```

### Web Interface Usage
```bash
# Start the web server
cd web/backend
python3 simple_server.py

# Open browser to http://localhost:8000
# Use the web interface to:
# 1. Load examples
# 2. Edit code in the Monaco-style editor
# 3. Execute code with real-time output
# 4. Download .mix files
```

### Security Features
```bash
# This will be blocked by security manager
cat > dangerous.mix << EOF
#lang: python
import os
os.system("rm -rf /")  # Dangerous!
EOF

python3 main.py dangerous.mix
# Output: 🚫 Block 1 BLOCKED for security: Dangerous pattern detected: os.system
```

### Docker Secure Execution
```bash
# Build Docker containers first
./build_containers.sh

# Run with Docker security
python3 main.py example.mix --docker
```

---

## 🚀 Advanced Features

### Plugin System for New Languages
To add a new language (e.g., Ruby):

1. **Create Runner Class**:
```python
# runners/ruby_runner.py
from .base_runner import BaseRunner
import subprocess
import tempfile

class RubyRunner(BaseRunner):
    def __init__(self, config=None):
        super().__init__(config)
        self.language = "ruby"
        self.file_extension = ".rb"
    
    def run(self, code, import_data=None, export_vars=None):
        # Implementation similar to other runners
        pass
```

2. **Register in Plugin Manager**:
```python
# The plugin manager will automatically discover it
# if named correctly: *_runner.py with *Runner class
```

3. **Update Configuration**:
```json
{
    "supported_languages": ["python", "cpp", "javascript", "bash", "ruby"]
}
```

### Header Consolidation Logic
**Problem**: C++ blocks repeat the same headers
**Solution**: Extract and merge headers automatically

```python
def consolidate_language_blocks(blocks):
    consolidated = {}
    
    for block in blocks:
        lang = block["language"]
        
        if lang.lower() in ['cpp', 'c', 'c++']:
            # Extract headers and main function body
            lines = code.split('\n')
            headers = []
            main_body = []
            
            for line in lines:
                if line.strip().startswith('#include'):
                    headers.append(line.strip())
                elif 'int main(' not in line and line.strip() != '}':
                    main_body.append(line)
            
            # Merge into consolidated structure
            if lang not in consolidated:
                consolidated[lang] = {"headers": set(), "main_bodies": []}
            
            consolidated[lang]["headers"].update(headers)
            consolidated[lang]["main_bodies"].extend(main_body)
```

### Data Serialization System
**Challenge**: Pass complex data between different language runtimes
**Solution**: JSON + Pickle hybrid approach

```python
# Python → JavaScript (JSON compatible)
python_data = {"numbers": [1, 2, 3], "message": "hello"}
# Serialized as: {"numbers": [1, 2, 3], "message": "hello"}

# Python → Python (Pickle for complex objects)
import datetime
python_data = {"timestamp": datetime.now()}
# Serialized as: {"timestamp": {"__pickle__": "base64_encoded_pickle_data"}}

# JavaScript → Bash (Environment variables)
js_data = {"count": 42, "name": "test"}
# Becomes: IMPORT_COUNT=42 IMPORT_NAME=test
```

---

## 🛠️ Troubleshooting Guide

### Common Issues and Solutions

#### 1. "Language not supported" Error
**Problem**: PolyRun doesn't recognize the language
**Solution**: 
- Check `config.json` for supported languages
- Ensure correct syntax: `#lang: python` (not `#lang:python`)
- Verify the language runner exists in `runners/` directory

#### 2. "Docker not available" Warning
**Problem**: Docker functionality requested but Docker not installed
**Solution**:
- Install Docker: `sudo apt install docker.io`
- Start Docker service: `sudo systemctl start docker`
- Add user to docker group: `sudo usermod -aG docker $USER`
- Or use `--no-docker` flag to run locally

#### 3. "Security check failed" Error
**Problem**: Code contains dangerous patterns
**Solution**:
- Remove dangerous functions like `os.system()`, `eval()`, `subprocess.call()`
- Use safer alternatives:
  - Instead of `os.system("ls")` → use `os.listdir(".")`
  - Instead of `eval(code)` → use `ast.literal_eval(safe_code)`

#### 4. Compilation Errors in C++
**Problem**: C++ code fails to compile
**Solution**:
- Check syntax with a C++ compiler: `g++ -c yourfile.cpp`
- Ensure all necessary headers are included
- Use C++17 standard: code is compiled with `-std=c++17`
- Check for missing main function

#### 5. Data Not Passing Between Blocks
**Problem**: Exported variables not available in next block
**Solution**:
- Check `#export:` and `#import:` spelling
- Ensure exported variable exists: `#export: variable_that_exists`
- Check variable name consistency between blocks
- Verify no typos in variable names

#### 6. Web Interface Not Loading
**Problem**: Browser shows connection refused
**Solution**:
- Check if server is running: `curl http://localhost:8000/health`
- Start server: `cd web/backend && python3 simple_server.py`
- Check port conflicts: try different port with `--port 8001`
- Verify firewall settings allow port 8000

#### 7. Import Errors in Python
**Problem**: Module import failures in runners
**Solution**:
- Check Python path: `echo $PYTHONPATH`
- Install missing dependencies: `pip3 install fastapi uvicorn`
- Verify relative imports: ensure `__init__.py` files exist
- Run from correct directory: execute from project root

#### 8. Memory or Timeout Issues
**Problem**: Code execution times out or uses too much memory
**Solution**:
- Increase timeout in `config.json`: `"timeout_seconds": 60`
- Optimize code for better performance
- Use `--no-consolidate` to reduce C++ compilation time
- Check for infinite loops in code

#### 9. Permission Denied Errors
**Problem**: Cannot create temporary files or execute binaries
**Solution**:
- Check file permissions: `ls -la /tmp`
- Ensure execute permissions: `chmod +x script`
- Check disk space: `df -h`
- Verify user has write access to temp directory

#### 10. Unicode/Encoding Issues
**Problem**: Special characters cause parsing errors
**Solution**:
- Save .mix files with UTF-8 encoding
- Avoid binary data in code blocks
- Use proper string escaping in multi-language contexts

### Debug Mode
Enable detailed logging for troubleshooting:
```bash
# Set debug level in config.json
{
    "logging": {
        "level": "DEBUG"
    }
}

# Or use verbose flag
python3 main.py example.mix --verbose
```

### Log File Analysis
Check execution logs in the `output/` directory:
```bash
# View latest log
ls -t output/run_*.log | head -1 | xargs cat

# Search for errors
grep -i error output/run_*.log

# Check security events
grep -i security output/run_*.log
```

---

## 🎓 Learning Objectives Achieved

By studying and understanding PolyRun, students learn:

### Programming Concepts
- **Multi-language Programming**: How different languages can work together
- **Plugin Architecture**: Extensible design patterns
- **Abstract Base Classes**: Interface design and polymorphism
- **Error Handling**: Robust error management strategies
- **Security**: Code validation and safe execution practices

### Software Engineering
- **Modular Design**: How to break complex systems into manageable parts
- **Configuration Management**: Centralized settings and environment handling
- **Testing Strategies**: Unit testing and integration testing
- **Documentation**: How to document complex systems effectively

### System Design
- **Parser Design**: How to build language parsers
- **Execution Models**: Different approaches to code execution
- **Web APIs**: RESTful service design with FastAPI
- **Process Management**: Subprocess handling and resource management

### DevOps and Deployment
- **Containerization**: Docker usage for isolation and security
- **Web Deployment**: Backend and frontend integration
- **Logging and Monitoring**: System observability and debugging

---

## 📚 Further Reading and Extensions

### Potential Enhancements
1. **Database Integration**: Save and share .mix files
2. **Real-time Collaboration**: Multiple users editing simultaneously
3. **AI Code Assistance**: Intelligent code suggestions
4. **Package Management**: Language-specific dependency handling
5. **Version Control**: Git integration for .mix files
6. **Performance Profiling**: Detailed execution analysis

### Related Technologies to Explore
- **Jupyter Notebooks**: Similar multi-language concept
- **Docker Compose**: Multi-container deployments
- **WebAssembly**: Browser-based code execution
- **Language Servers**: Advanced code intelligence
- **CI/CD Pipelines**: Automated testing and deployment

### Learning Path for Students
1. **Start Simple**: Understand basic execution flow
2. **Add Language**: Implement a new language runner
3. **Enhance Security**: Add new security validation rules
4. **Build UI**: Create better web interface components
5. **Scale Up**: Handle multiple concurrent users
6. **Optimize**: Improve performance and resource usage

---

## 🎉 Conclusion

PolyRun demonstrates how modern software systems can be built with:
- **Clean Architecture**: Separation of concerns and modular design
- **Extensibility**: Plugin systems for easy enhancement
- **Security**: Built-in safety measures and validation
- **User Experience**: Both CLI and web interfaces
- **Documentation**: Comprehensive guides for maintainability

This project serves as an excellent learning platform for understanding:
- How interpreters and compilers work
- Web API design and implementation
- Security considerations in code execution
- Multi-language programming concepts
- Software architecture patterns

The codebase is designed to be educational, with clear separation of concerns, extensive comments, and progressive complexity that makes it suitable for students at different levels.

**Project Statistics**:
- **Total Lines of Code**: ~4,759 lines (Python)
- **Languages Supported**: Python, C++, JavaScript, Bash (+ extensible)
- **Test Files Created**: 17 .mix example files
- **Frameworks Used**: FastAPI, Uvicorn
- **Key Patterns**: Plugin Architecture, Factory Pattern, Abstract Base Classes
- **Security Features**: Input validation, resource limits, containerization support
- **Phases Completed**: 5 out of 8 planned phases

**Current Status**: 
- ✅ **Phase 1-5**: Fully functional multi-language execution engine with web interface
- ✅ **Web Server**: Active at http://localhost:8000 with modern UI
- ✅ **Data Passing**: Working seamlessly between all supported languages
- ✅ **Plugin System**: Extensible architecture for adding new languages
- 🔄 **Phase 6**: Database layer implemented, web integration ready
- 📋 **Phase 7-8**: Planned for future development

**Latest Achievements (July 30, 2025)**:
- ✅ Fixed web interface output display issues
- ✅ Enhanced frontend JavaScript parsing logic
- ✅ Streamlined backend API for better performance
- ✅ Comprehensive data passing system working in web interface
- ✅ Modern, professional web UI with glassmorphism design
- ✅ Real-time code execution with proper error handling

This comprehensive system showcases modern software development practices while remaining accessible for educational purposes.

---

*End of Documentation - PolyRun v1.0*

from parser import parse_mix_file
from runners.python_runner import run_python_code
from runners.cpp_runner import run_cpp_code
from datetime import datetime
import json


def load_config(path='config.json'):
    with open(path, 'r') as f:
        return json.load(f)


def main():
    blocks = parse_mix_file("samples/hello_world.mix")
    log_lines = []

    for i, block in enumerate(blocks):
        lang = block['language']
        code = block['code']
        print(f"\\n--- Running block {i+1} [{lang}] ---")
        log_lines.append(f"\\n--- Block {i+1} [{lang}] ---")

        if lang == "python":
            result = run_python_code(code)
        elif lang == "cpp":
            result = run_cpp_code(code)
        else:
            result = {
                "success": False,
                "output": "",
                "error": f"Unsupported language: {lang}"
            }

        print(result['output'])
        if result['error']:
            print("⚠️ Error:", result['error'])

        log_lines.append(result['output'] + (f"\\n⚠️ Error: {result['error']}" if result['error'] else ""))

    # Save to log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"output/run_{timestamp}.log", "w") as log_file:
        log_file.write("\\n".join(log_lines))

if __name__ == "__main__":
    main()

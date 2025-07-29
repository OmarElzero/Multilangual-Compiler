def validate_mix_file(blocks):
    errors = []
    for i, block in enumerate(blocks):
        if not block["language"]:
            errors.append(f"Block {i+1}: Missing language specification")
        if not block["code"].strip():
            errors.append(f"Block {i+1}: Empty code block")
    return errors


def parse_mix_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    blocks = []
    current_block = {"language": None, "code": [], "start_line": None}
    recording = False
    
    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        if line_stripped.startswith("#lang:"):
            # If we were recording a previous block, save it first
            if recording and current_block["language"]:
                blocks.append({
                    "language": current_block["language"],
                    "code": "".join(current_block["code"]).strip()
                })
            
            # Start new block
            current_block = {
                "language": line_stripped.split(":")[1].strip(),
                "code": [],
                "start_line": line_num
            }
            recording = True
            
        elif recording:
            current_block["code"].append(line)
    
    # Handle the last block at end of file
    if recording and current_block["language"] and current_block["code"]:
        blocks.append({
            "language": current_block["language"],
            "code": "".join(current_block["code"]).strip()
        })

    return blocks

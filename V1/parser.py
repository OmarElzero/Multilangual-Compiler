def parse_mix_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    blocks = []
    current_block = {"language": None, "code": []}
    recording = False
    
    for line in lines:
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
                "code": []
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

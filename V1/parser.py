def parse_mix_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    blocks = []
    current_block = {"language": None, "code": []}
    recording = False

    for line in lines:
        if line.startswith("#lang:"):
            current_block["language"] = line.strip().split(":")[1]
            recording = True
        elif line.strip() == "#end":
            blocks.append({
                "language": current_block["language"],
                "code": "".join(current_block["code"])
            })
            current_block = {"language": None, "code": []}
            recording = False
        elif recording:
            current_block["code"].append(line)

    return blocks
def validate_mix_file(blocks):
    errors = []
    for i, block in enumerate(blocks):
        if not block["language"]:
            errors.append(f"Block {i+1}: Missing language specification")
        if not block["code"].strip():
            errors.append(f"Block {i+1}: Empty code block")
    return errors

def parse_cpp_code(code):
    """
    Parse C++ code to separate headers, main function, and fragments
    Returns: (headers, main_code, fragments, has_main)
    """
    lines = code.split('\n')
    headers = []
    main_code = []
    fragments = []
    has_main = False
    
    in_main = False
    brace_count = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Check for headers (includes, using statements, etc.)
        if (stripped.startswith('#include') or 
            stripped.startswith('using namespace') or
            stripped.startswith('using std::') or
            stripped.startswith('#define') or
            stripped.startswith('#pragma')):
            if line not in headers:
                headers.append(line)
        
        # Check for main function start
        elif 'int main(' in line or 'int main (' in line:
            has_main = True
            in_main = True
            main_code.append(line)
            if '{' in line:
                brace_count += line.count('{') - line.count('}')
        
        # Handle main function content
        elif in_main:
            main_code.append(line)
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0:
                in_main = False
        
        # Everything else is a fragment
        elif stripped and not stripped.startswith('//'):
            fragments.append(line)
    
    return headers, main_code, fragments, has_main

def consolidate_language_blocks(blocks):
    """
    Consolidate multiple blocks of the same language.
    For compiled languages (C++, C), extract headers and merge code fragments.
    """
    consolidated = {}
    
    for block in blocks:
        lang = block["language"]
        code = block["code"]
        imports = block.get("imports", [])
        exports = block.get("exports", [])
        
        if lang not in consolidated:
            consolidated[lang] = {
                "language": lang,
                "headers": set(),  # Use set to avoid duplicates
                "main_bodies": [],  # Store main function bodies
                "has_main": False,
                "start_line": block.get("start_line", 1),
                "imports": set(),  # Collect all imports
                "exports": set(),  # Collect all exports
                "code": []
            }
        
        # Add imports and exports
        consolidated[lang]["imports"].update(imports)
        consolidated[lang]["exports"].update(exports)
        
        if lang.lower() in ['cpp', 'c', 'c++']:
            # Extract headers and main function body
            lines = code.split('\n')
            main_body = []
            in_main = False
            brace_count = 0
            
            for line in lines:
                stripped = line.strip()
                
                # Check for headers
                if (stripped.startswith('#include') or 
                    stripped.startswith('using namespace') or
                    stripped.startswith('using std::') or
                    stripped.startswith('#define') or
                    stripped.startswith('#pragma')):
                    consolidated[lang]["headers"].add(line.strip())
                
                # Check for main function start
                elif 'int main(' in line:
                    in_main = True
                    consolidated[lang]["has_main"] = True
                    if '{' in line:
                        brace_count += line.count('{') - line.count('}')
                    continue  # Skip the main function declaration line
                
                # Handle main function content
                elif in_main:
                    brace_count += line.count('{') - line.count('}')
                    if brace_count <= 0 and line.strip() == '}':
                        in_main = False
                        break  # End of main function
                    elif line.strip() != 'return 0;':  # Skip return statement
                        main_body.append(line)
            
            # Add this main body to the list
            if main_body:
                # Add a comment separator if this isn't the first block
                if consolidated[lang]["main_bodies"]:
                    consolidated[lang]["main_bodies"].append('')
                    consolidated[lang]["main_bodies"].append('    // --- Block {} ---'.format(len(consolidated[lang]["main_bodies"]) + 1))
                consolidated[lang]["main_bodies"].extend(main_body)
        else:
            # For interpreted languages, just concatenate
            if "code" not in consolidated[lang]:
                consolidated[lang]["code"] = []
            consolidated[lang]["code"].append(code)
    
    # Build final consolidated blocks
    result = []
    for lang, data in consolidated.items():
        if lang.lower() in ['cpp', 'c', 'c++']:
            final_code = build_cpp_code_simple(data)
        else:
            final_code = "\n\n".join(data["code"])
        
        result.append({
            "language": lang,
            "code": final_code,
            "start_line": data["start_line"],
            "consolidated": True,
            "imports": list(data.get("imports", [])),
            "exports": list(data.get("exports", []))
        })
    
    return result

def build_cpp_code_simple(data):
    """Build final C++ code from consolidated components"""
    final_code = []
    
    # Add headers
    if data["headers"]:
        for header in sorted(data["headers"]):  # Sort headers for consistency
            final_code.append(header)
        final_code.append("")  # Empty line after headers
    
    # Add main function with all bodies
    if data["has_main"] and data["main_bodies"]:
        final_code.append("int main() {")
        final_code.extend(data["main_bodies"])
        final_code.append("    return 0;")
        final_code.append("}")
    
    return '\n'.join(final_code)


def build_cpp_code(data):
    """Build final C++ code from parsed components"""
    final_code = []
    
    # Add headers
    if data["headers"]:
        final_code.extend(data["headers"])
        final_code.append("")  # Empty line after headers
    
    # Add main function with integrated fragments
    if data["has_main"]:
        main_lines = data["main_code"]
        
        # Find where to insert fragments (before the final return statement)
        for i, line in enumerate(main_lines):
            # Check if this is the final return statement
            if line.strip() in ['return 0;'] and i == len(main_lines) - 2:  # -2 because last line is closing brace
                # Insert fragments before return
                if data["fragments"]:
                    final_code.extend(data["fragments"])
                    final_code.append("")  # Empty line before return
            final_code.append(line)
    else:
        # No main function, just add fragments
        if data["fragments"]:
            final_code.extend(data["fragments"])
    
    return '\n'.join(final_code)



def parse_mix_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    blocks = []
    current_block = {"language": None, "code": [], "start_line": None, "imports": [], "exports": []}
    recording = False
    
    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        if line_stripped.startswith("#lang:"):
            # If we were recording a previous block, save it first
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
            
        # Check for import directives
        elif line_stripped.startswith("#import:") and recording:
            import_vars = line_stripped.replace("#import:", "").strip()
            current_block["imports"].extend([var.strip() for var in import_vars.split(",") if var.strip()])
            
        # Check for export directives  
        elif line_stripped.startswith("#export:") and recording:
            export_vars = line_stripped.replace("#export:", "").strip()
            current_block["exports"].extend([var.strip() for var in export_vars.split(",") if var.strip()])
            
        elif recording:
            current_block["code"].append(line)
    
    # Handle the last block at end of file
    if recording and current_block["language"] and current_block["code"]:
        blocks.append({
            "language": current_block["language"],
            "code": "".join(current_block["code"]).strip(),
            "start_line": current_block["start_line"],
            "imports": current_block["imports"],
            "exports": current_block["exports"]
        })

    return blocks

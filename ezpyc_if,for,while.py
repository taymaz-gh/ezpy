# ezpyc.py
# Unified parser for if/elif/else/endif, for/next, while/loop blocks

import sys
from pathlib import Path

def convert_ezpy_to_python(input_path, output_path):
    output_lines = []             # Final list of Python lines
    block_stack = []              # Track opened blocks (e.g., 'if', 'for', 'while')
    INDENT = "    "               # Standard 4-space indentation

    with open(input_path, "r") as infile:
        for line in infile:
            raw = line.rstrip("\n")
            stripped = raw.strip()

            if not stripped:
                output_lines.append("")
                continue

            # --- End of blocks ---
            if stripped.lower() in ["endif", "next", "loop"]:
                if block_stack:
                    block_stack.pop()
                continue

            indent = len(block_stack)

            # --- ELSE ---
            if stripped.lower().startswith("else"):
                if block_stack and block_stack[-1] == "if":
                    block_stack.pop()
                    indent -= 1
                output_lines.append(INDENT * indent + "else:")
                block_stack.append("if")
                continue

            # --- ELIF ---
            if stripped.lower().startswith("elif "):
                if block_stack and block_stack[-1] == "if":
                    block_stack.pop()
                    indent -= 1
                colon_index = stripped.find(":")
                head = stripped[:colon_index].strip() if colon_index != -1 else stripped
                body = stripped[colon_index + 1:].strip() if colon_index != -1 else ""
                output_lines.append(INDENT * indent + head + ":")
                block_stack.append("if")
                if body:
                    output_lines.append(INDENT * (indent + 1) + body)
                continue

            # --- IF ---
            if stripped.lower().startswith("if "):
                colon_index = stripped.find(":")
                head = stripped[:colon_index].strip() if colon_index != -1 else stripped
                body = stripped[colon_index + 1:].strip() if colon_index != -1 else ""
                output_lines.append(INDENT * indent + head + ":")
                block_stack.append("if")
                if body:
                    output_lines.append(INDENT * (indent + 1) + body)
                continue

            # --- FOR ---
            if stripped.lower().startswith("for "):
                colon_index = stripped.find(":")
                head = stripped[:colon_index].strip() if colon_index != -1 else stripped
                body = stripped[colon_index + 1:].strip() if colon_index != -1 else ""
                output_lines.append(INDENT * indent + head + ":")
                block_stack.append("for")
                if body:
                    output_lines.append(INDENT * (indent + 1) + body)
                continue

            # --- WHILE ---
            if stripped.lower().startswith("while "):
                colon_index = stripped.find(":")
                head = stripped[:colon_index].strip() if colon_index != -1 else stripped
                body = stripped[colon_index + 1:].strip() if colon_index != -1 else ""
                output_lines.append(INDENT * indent + head + ":")
                block_stack.append("while")
                if body:
                    output_lines.append(INDENT * (indent + 1) + body)
                continue

            # --- Regular line ---
            output_lines.append(INDENT * indent + stripped)

    # --- Write output Python file ---
    with open(output_path, "w") as outfile:
        outfile.write("\n".join(output_lines))

# --- CLI entry point ---
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ezpyc.py input.ezpy output.py")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Input file {input_file} not found.")
        sys.exit(1)

    convert_ezpy_to_python(input_file, output_file)
    print(f"Converted {input_file} -> {output_file}")

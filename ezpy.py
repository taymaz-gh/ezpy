# ezpyc.py
# Extended parser with block validation and syntax error reporting

import sys
from pathlib import Path

def error(line_num, message):
    print(f"[Syntax Error] Line {line_num}: {message}")
    sys.exit(1)

def convert_ezpy_to_python(input_path, output_path):
    output_lines = []
    block_stack = []  # Stack of tuples: (block_type, line_num)
    INDENT = "   "

    with open(input_path, "r") as infile:
        for line_num, line in enumerate(infile, start=1):
            raw = line.rstrip("\n")
            stripped = raw.strip()

            if not stripped:
                output_lines.append("")
                continue

            # --- End of blocks ---
            if stripped.lower() == "endif":
                if not block_stack or block_stack[-1][0] != "if":
                    error(line_num, "'endif' without matching 'if'")
                block_stack.pop()
                continue

            if stripped.lower() == "next":
                if not block_stack or block_stack[-1][0] != "for":
                    error(line_num, "'next' without matching 'for'")
                block_stack.pop()
                continue

            if stripped.lower() == "loop":
                if not block_stack or block_stack[-1][0] != "while":
                    error(line_num, "'loop' without matching 'while'")
                block_stack.pop()
                continue

            indent = len(block_stack)

            # --- ELSE ---
            if stripped.lower().startswith("else"):
                if not block_stack or block_stack[-1][0] != "if":
                    error(line_num, "'else' without matching 'if'")
                block_stack.pop()
                indent -= 1
                output_lines.append(INDENT * indent + "else:")
                block_stack.append(("if", line_num))
                continue

            # --- ELIF ---
            if stripped.lower().startswith("elif "):
                if not block_stack or block_stack[-1][0] != "if":
                    error(line_num, "'elif' without matching 'if'")
                block_stack.pop()
                indent -= 1
                colon_index = stripped.find(":")
                if colon_index == -1:
                    error(line_num, "Missing ':' in 'elif' statement")
                head = stripped[:colon_index].strip()
                body = stripped[colon_index + 1:].strip()
                output_lines.append(INDENT * indent + head + ":")
                block_stack.append(("if", line_num))
                if body:
                    output_lines.append(INDENT * (indent + 1) + body)
                continue

            # --- IF ---
            if stripped.lower().startswith("if "):
                colon_index = stripped.find(":")
                if colon_index == -1:
                    error(line_num, "Missing ':' in 'if' statement")
                head = stripped[:colon_index].strip()
                body = stripped[colon_index + 1:].strip()
                output_lines.append(INDENT * indent + head + ":")
                block_stack.append(("if", line_num))
                if body:
                    output_lines.append(INDENT * (indent + 1) + body)
                continue

            # --- FOR ---
            if stripped.lower().startswith("for "):
                colon_index = stripped.find(":")
                if colon_index == -1:
                    error(line_num, "Missing ':' in 'for' statement")
                head = stripped[:colon_index].strip()
                body = stripped[colon_index + 1:].strip()
                output_lines.append(INDENT * indent + head + ":")
                block_stack.append(("for", line_num))
                if body:
                    output_lines.append(INDENT * (indent + 1) + body)
                continue

            # --- WHILE ---
            if stripped.lower().startswith("while "):
                colon_index = stripped.find(":")
                if colon_index == -1:
                    error(line_num, "Missing ':' in 'while' statement")
                head = stripped[:colon_index].strip()
                body = stripped[colon_index + 1:].strip()
                output_lines.append(INDENT * indent + head + ":")
                block_stack.append(("while", line_num))
                if body:
                    output_lines.append(INDENT * (indent + 1) + body)
                continue

            # --- Regular line ---
            output_lines.append(INDENT * indent + stripped)

    # Final check: All blocks must be closed
    if block_stack:
        remaining = "\n".join([f"{b[0]} (opened on line {b[1]})" for b in block_stack])
        error("EOF", f"Unclosed blocks:\n{remaining}")

    # Write output Python file
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

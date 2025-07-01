# ezpyc.py
# Fixed parser to support if-elif-else with 'endif' and normalize indentation

import sys
from pathlib import Path

def convert_ezpy_to_python(input_path, output_path):
    output_lines = []                   # List to store output lines
    block_stack = []                    # Stack to track nested block types (e.g., "if", "while", etc.)
    INDENT_UNIT = "    "                # 4-space indent

    with open(input_path, "r") as infile:
        for line in infile:
            raw = line.rstrip("\n")             # Keep original spacing for inline parsing
            stripped = raw.strip()

            if not stripped:
                output_lines.append("")
                continue

            # End of block
            if stripped.lower() == "endif":
                if block_stack and block_stack[-1] == "if":
                    block_stack.pop()
                continue  # Don't write 'endif' to output

            # Determine current indent level
            indent = len(block_stack)

            # Handle 'else'
            if stripped.lower().startswith("else"):
                if block_stack and block_stack[-1] == "if":
                    block_stack.pop()              # Pop the 'if' before writing 'else'
                output_lines.append(INDENT_UNIT * (len(block_stack)) + "else:")
                block_stack.append("if")           # Push again to maintain block for inner lines
                continue

            # Handle 'elif'
            if stripped.lower().startswith("elif "):
                if block_stack and block_stack[-1] == "if":
                    block_stack.pop()              # Pop the 'if' before writing 'elif'
                colon_index = stripped.find(":")
                condition = stripped[:colon_index].strip() if colon_index != -1 else stripped
                after_colon = stripped[colon_index + 1:].strip() if colon_index != -1 else ""
                output_lines.append(INDENT_UNIT * len(block_stack) + condition + ":")
                block_stack.append("if")
                if after_colon:
                    output_lines.append(INDENT_UNIT * (len(block_stack)) + after_colon)
                continue

            # Handle 'if'
            if stripped.lower().startswith("if "):
                colon_index = stripped.find(":")
                condition = stripped[:colon_index].strip() if colon_index != -1 else stripped
                after_colon = stripped[colon_index + 1:].strip() if colon_index != -1 else ""
                output_lines.append(INDENT_UNIT * len(block_stack) + condition + ":")
                block_stack.append("if")
                if after_colon:
                    output_lines.append(INDENT_UNIT * (len(block_stack)) + after_colon)
                continue

            # Regular line inside block
            output_lines.append(INDENT_UNIT * len(block_stack) + stripped)

    # Write the result to output
    with open(output_path, "w") as outfile:
        outfile.write("\n".join(output_lines))

# CLI usage
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

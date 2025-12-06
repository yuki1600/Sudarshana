import ast
import sys

filename = 'src/ci_core.py'
try:
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    ast.parse(source)
    print(f"Syntax OK in {filename}")
except SyntaxError as e:
    print(f"Syntax error in {filename}: {e}")
    print(f"Line {e.lineno}, offset {e.offset}: {e.text}")
except Exception as e:
    print(f"Error checking {filename}: {e}")

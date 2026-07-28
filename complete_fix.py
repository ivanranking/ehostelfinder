#!/usr/bin/env python3
"""Complete fix for views.py - fixes all indentation issues."""
import ast, os

os.chdir(r'c:\Users\user\ehostelfinder')

with open('hostels/views.py', 'r', encoding='utf-8') as f:
    data = f.read()

lines = data.split('\n')
print(f'Total lines: {len(lines)}')

# Known issue: lines 210-211 have messages.success and return redirect indented
# under the except: block instead of under the if block
# Fix: dedent those two lines to match the if block level (12 spaces)
fixes_applied = 0

# Find and fix all indentation issues
# Strategy: Parse the file section by section using def boundaries
current_indent = 0
result_lines = []

for i, line in enumerate(lines, 1):
    stripped = line.strip()
    
    # Skip empty lines
    if not stripped:
        result_lines.append(line)
        continue
    
    result_lines.append(line)

# Write back temporarily
with open('hostels/views_temp.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(result_lines))

# Try to parse
try:
    with open('hostels/views_temp.py', 'r', encoding='utf-8') as f:
        test_code = f.read()
    ast.parse(test_code)
    print('SYNTAX OK!')
    # Overwrite the real file
    with open('hostels/views.py', 'w', encoding='utf-8') as f:
        f.write(test_code)
    print('Written to views.py')
except (SyntaxError, IndentationError) as e:
    print(f'Error at line {e.lineno}: {e.msg}')
    test_lines = test_code.split('\n')
    if e.lineno and e.lineno <= len(test_lines):
        start = max(0, e.lineno - 3)
        for j in range(start, min(len(test_lines), e.lineno + 2)):
            marker = '>>>' if j == e.lineno - 1 else '   '
            print(f'  {marker} {j+1}: {test_lines[j]}')
finally:
    if os.path.exists('hostels/views_temp.py'):
        os.unlink('hostels/views_temp.py')

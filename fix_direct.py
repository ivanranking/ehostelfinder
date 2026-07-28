#!/usr/bin/env python3
"""Direct fix of views.py signup function indentation."""
import ast

with open('hostels/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Show the context around lines 210-220
print("Current lines 210-220:")
for i in range(209, 221):
    if i < len(lines):
        print(f'  {i+1}: {lines[i].rstrip()}')

# The issue: line 214 = '    else:', line 215 = '    return render(...)'
# Need to add '        form = UserRegistrationForm()' between them
# The else needs a body before the return

# Find '    else:' and insert a body before the return
for i in range(len(lines)):
    if lines[i].rstrip() == '    else:' and i+1 < len(lines) and 'return render' in lines[i+1]:
        # Insert form = UserRegistrationForm() after else:
        lines.insert(i+1, '        form = UserRegistrationForm()\n')
        print(f"Inserted 'form = UserRegistrationForm()' after line {i+1}")
        break

# Also ensure the return render stays at function level (4 spaces)
for i in range(len(lines)):
    line = lines[i].rstrip()
    if line == '    else:' and i+2 < len(lines):
        pass  # Already handled

with open('hostels/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
t = open('hostels/views.py').read()
try:
    tree = ast.parse(t)
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    print(f'SYNTAX OK! Total functions: {len(funcs)}')
    for fn in sorted(funcs):
        print(f'  - {fn}')
except (SyntaxError, IndentationError) as e:
    print(f'Error at line {e.lineno}: {e.msg}')
    lines_t = t.split('\n')
    if e.lineno and e.lineno <= len(lines_t):
        start = max(0, e.lineno - 3)
        for j in range(start, min(len(lines_t), e.lineno + 2)):
            marker = '>>>' if j == e.lineno - 1 else '   '
            print(f'  {marker} {j+1}: {lines_t[j]}')

#!/usr/bin/env python3
"""Build complete views.py from gen_views.py + gen_views_p2.py + gen_views_p3_fixed.py rebuild section"""
import os, ast, re

os.chdir(r'c:\Users\user\ehostelfinder')

def load_and_run(path, label):
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    try:
        ast.parse(code)
        exec(compile(code, path, 'exec'))
        print(f'{label}: OK')
        return True
    except SyntaxError as e:
        print(f'{label}: SyntaxError at line {e.lineno}')
        return False

# Step 1: gen_views.py writes the base (85 lines, syntax OK)
if not load_and_run('gen_views.py', 'gen_views'):
    raise SystemExit(1)

# Step 2: gen_views_p2.py adds hostel_detail etc (148 lines)
if not load_and_run('gen_views_p2.py', 'gen_views_p2'):
    raise SystemExit(1)

# Now we have ~19 functions. Read gen_views_p3_fixed.py's rebuild section
with open('gen_views_p3_fixed.py', 'r', encoding='utf-8') as f:
    p3_code = f.read()

# Find the second docstring
idx = p3_code.find('"""Generate the complete views.py')
if idx < 0:
    print('ERROR: Could not find rebuild section in gen_views_p3_fixed.py')
    raise SystemExit(1)

# Extract from there to end
rebuild_section = p3_code[idx:]

# Now read current views.py
with open('hostels/views.py', 'r') as f:
    existing = f.read()

lines = existing.rstrip().split('\n')
while lines and lines[-1] == '':
    lines.pop()

indent = 0
def w(s):
    global indent
    if indent:
        lines.append('    ' * indent + s)
    else:
        lines.append(s)
def i():
    global indent; indent += 1
def d():
    global indent; indent -= 1

# Execute the rebuild section to append new functions
exec(compile(rebuild_section, 'rebuild_section', 'exec'))

# Now write back
with open('hostels/views.py', 'w') as f:
    f.write('\n'.join(lines))
    f.write('\n')

# Verify
with open('hostels/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

try:
    tree = ast.parse(content)
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    print(f'\nSUCCESS: {len(funcs)} functions in views.py')

    with open('hostels/urls.py', 'r', encoding='utf-8') as f:
        urls_content = f.read()
    needed = set()
    for m in re.finditer(r'views\.(\w+)', urls_content):
        needed.add(m.group(1))

    missing = sorted(needed - funcs)
    if missing:
        print(f'MISSING ({len(missing)}): {missing}')
    else:
        print('ALL FUNCTIONS MATCH URLS!')
except SyntaxError as e:
    print(f'SYNTAX ERROR at line {e.lineno}: {e.msg}')
DSMLparameter>
DSMLinvoke>
DSMLtool_calls>

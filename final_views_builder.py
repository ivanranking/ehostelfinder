#!/usr/bin/env python3
"""Build all remaining view functions for hostels/views.py.
Reads current views.py, then appends all missing views by writing raw Python code."""
import os, ast, re, json

os.chdir(r'c:\Users\user\ehostelfinder')

# 1. Read existing views
with open('hostels/views.py', 'r', encoding='utf-8') as f:
    existing = f.read()

lines = existing.rstrip().split('\n')
# Remove trailing blank lines
while lines and lines[-1].strip() == '':
    lines.pop()

# 2. Read urls.py to know what functions are needed
with open('hostels/urls.py', 'r', encoding='utf-8') as f:
    urls_content = f.read()

needed = set()
for m in re.finditer(r'views\.(\w+)', urls_content):
    needed.add(m.group(1))

# 3. Parse existing functions
try:
    tree = ast.parse('\n'.join(lines))
    existing_funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
except:
    existing_funcs = set()
    for m in re.finditer(r'def (\w+)\s*\(', '\n'.join(lines)):
        existing_funcs.add(m.group(1))

to_add = needed - existing_funcs
print(f"Existing: {len(existing_funcs)}, Needed: {len(needed)}, To Add: {len(to_add)}")
if not to_add:
    print("ALL FUNCTIONS PRESENT!")
    # Write back
    with open('hostels/views.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    exit(0)

print(f"Adding: {sorted(to_add)}")

# 4. Define all missing functions as raw strings
# Each function is a tuple of (function_name, source_code_string)
# Using triple-quoted strings to avoid escaping issues

missing_funcs_source = []
</｜｜DSML｜｜parameter>

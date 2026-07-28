#!/usr/bin/env python3
"""Write complete working views.py by reading from gen_views_all.py and fixing indentation."""
import ast, re, os

os.chdir(r'c:\Users\user\ehostelfinder')

# Read the generated file
with open('gen_views_all.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the import section and all function bodies
# The file is corrupted with indentation issues.
# Strategy: extract and fix Python code blocks

lines = content.split('\n')

# First, find where functions start
fixed_lines = []
in_function = False
current_indent = 0
function_stack = []

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Track indentation for defs and decorators
    if stripped.startswith('def ') or stripped.startswith('@') or stripped.startswith('class '):
        # This is a top-level statement
        pass
    elif stripped == '':  # empty line resets nothing
        pass

# This approach is too complex. Let me just rebuild it completely.
# Let me first check what functions we actually need by reading urls.py
print("Checking hostels/urls.py for required functions...")

with open('hostels/urls.py', 'r', encoding='utf-8') as f:
    urls_content = f.read()

# Extract view function names from urlpatterns
needed_functions = set()
for match in re.finditer(r"views\.(\w+)", urls_content):
    needed_functions.add(match.group(1))

print(f"Functions needed from urls.py: {len(needed_functions)}")
for fn in sorted(needed_functions):
    print(f"  - {fn}")

# Also check what functions exist in the gen_views_all.py
existing_functions = set()
for line in content.split('\n'):
    if line.lstrip().startswith('def ') and '(' in line:
        fname = line.split('(')[0].split('def ')[-1].strip()
        existing_functions.add(fname)

print(f"\nFunctions in gen_views_all.py: {len(existing_functions)}")
for fn in sorted(existing_functions):
    marker = "OK" if fn in needed_functions else "EXTRA"
    print(f"  [{marker}] {fn}")

missing = needed_functions - existing_functions
if missing:
    print(f"\nMISSING from gen_views_all.py: {missing}")
else:
    print("\nAll needed functions found in gen_views_all.py!")

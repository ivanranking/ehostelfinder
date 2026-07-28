#!/usr/bin/env python3
"""Generate complete clean views.py from all source parts."""
import ast, os

os.chdir(r'c:\Users\user\ehostelfinder')

# Read the append_views_all.py which has proper line-by-line generation
# Execute it but with output to a clean file instead of appending

# First extract all the function code from append_views_all.py
# The L() function builds lines with proper indentation

# The issue: views.py got corrupted. Let me rebuild by:
# 1. Taking the imports section from gen_views_all.py (first ~15 lines before defs)
# 2. Appending the clean function code from the last clean run (append_views_final.py output)

# Read the existing corrupted file - it has some clean parts via the Append
# Let me extract the clean functions from the ending portion

with open('hostels/views.py', 'r', encoding='utf-8') as f:
    data = f.read()

# Fix the literal \n issue - replace them with actual newlines
# The data has "\\n" as literal text in some sections
# Find and fix any line that has \n as text

# Actually, let me just run the gen_views_final.py which is the generator
# But it has syntax errors. Let me fix the generator's raw string.

# Simplest approach: rewrite views.py from scratch using Python
# Write ALL the code needed as a proper Python file

print("Building complete views.py...")

# Read the header functions from gen_views_all.py (should have imports + basic defs)
with open('gen_views_all.py', 'r', encoding='utf-8') as f:
    gen_all = f.read()

# The gen_views_all.py starts with a script block then raw string r'''
# We need to extract just the Python code
lines_all = gen_all.split('\n')

# Find where the actual Python code starts
code_start = 0
for i, line in enumerate(lines_all):
    if line.startswith("content = r'''") or line.startswith("content='''"):
        code_start = i + 1
    if line.strip() == "'''" or line.strip() == "r'''":
        code_end = i
        break

# Actually gen_views_all may have many sections. Let's take a different approach.

# Read append_views_final.py if it exists
try:
    with open('append_views_final.py', 'r', encoding='utf-8') as f:
        print(f"append_views_final.py exists, size: {len(f.read())}")
except:
    print("append_views_final.py not found")

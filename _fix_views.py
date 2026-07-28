#!/usr/bin/env python3
"""Fix views.py - generate the complete working version."""
import ast, os

os.chdir('c:/Users/user/ehostelfinder')

# Read gen_views_all.py
with open('gen_views_all.py', 'r', encoding='utf-8') as f:
    script = f.read()

# Find all the lines that are actual Python code (after the content = r''' block)
# The problem is gen_views_all.py has indentation logic issues.
# Instead, let's write the complete views.py directly.

# But first, let's see what gen_views_p3.py contains
with open('gen_views_p3.py', 'r', encoding='utf-8') as f:
    p3 = f.read()

# Check if there's a content block
idx = p3.find("content = r'''")
if idx >= 0:
    start = idx + 14
    end = p3.find("'''", start)
    if end >= 0:
        block = p3[start:end]
        # Check for syntax errors
        try:
            ast.parse(block)
            print("gen_views_p3.py content block is syntactically valid!")
            print(f"Content size: {len(block)} bytes, {block.count('def ')} functions")
        except SyntaxError as e:
            print(f"gen_views_p3.py has syntax error: {e}")
            # Find the error line
            lines = block.split('\n')
            if e.lineno and e.lineno <= len(lines):
                start_line = max(0, e.lineno - 5)
                end_line = min(len(lines), e.lineno + 2)
                print("Context around error:")
                for i in range(start_line, end_line):
                    marker = ">>>" if i == e.lineno - 1 else "   "
                    print(f"  {marker} {i+1}: {lines[i]}")
    else:
        print("No closing ''' found in gen_views_p3.py")
        # Find where it breaks
        idx2 = p3.find("'''", start + 1000)
        if idx2 >= 0:
            print(f"Found second ''' at {idx2}")
else:
    print("No content block in gen_views_p3.py")
    
# Also check write_views.py
with open('write_views.py', 'r', encoding='utf-8') as f:
    wv = f.read()
idx = wv.find("content = r'''")
if idx >= 0:
    start = idx + 14
    end = wv.find("'''", start)
    if end >= 0:
        block = wv[start:end]
        try:
            ast.parse(block)
            print("\nwrite_views.py content block is syntactically valid!")
            print(f"Content size: {len(block)} bytes, {block.count('def ')} functions")
        except SyntaxError as e:
            print(f"\nwrite_views.py has syntax error: {e}")
    else:
        print("\nNo closing ''' in write_views.py")

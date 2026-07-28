#!/usr/bin/env python3
"""Fix indentation errors in views.py - handle the except: pass issue."""
import ast

with open('hostels/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the signup function and fix the except: pass issue
# Line 210: "            except: pass" 
# Lines 211-212: "                messages.success..." and "                return redirect("login")"
# These should be "                messages.success..." and "                return redirect("login")" 
# But the problem is except: pass is a compound statement on one line, 
# so the next indented lines become part of the except block (which Python doesn't allow)

# Fix: split except: pass into two lines
for i, line in enumerate(lines):
    ls = line.lstrip()
    if ls == 'except: pass':
        # Replace with multi-line version
        indent = line[:len(line) - len(ls)]
        lines[i] = f'{indent}except Exception:\n'
        lines.insert(i+1, f'{indent}    pass\n')
        print(f"Fixed except: pass at line {i+1}")
        break

with open('hostels/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
t = open('hostels/views.py').read()
try:
    tree = ast.parse(t)
    print("SYNTAX OK!")
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    print(f"Total functions: {len(funcs)}")
    for fn in sorted(funcs):
        print(f"  - {fn}")
except SyntaxError as e:
    print(f"\nSyntaxError at line {e.lineno}: {e.msg}")
    lines_t = t.split('\n')
    if e.lineno and e.lineno <= len(lines_t):
        start = max(0, e.lineno - 3)
        for j in range(start, min(len(lines_t), e.lineno + 2)):
            marker = ">>>" if j == e.lineno - 1 else "   "
            print(f"  {marker} {j+1}: {lines_t[j]}")
except IndentationError as e:
    print(f"\nIndentationError at line {e.lineno}: {e.msg}")
    lines_t = t.split('\n')
    if e.lineno and e.lineno <= len(lines_t):
        start = max(0, e.lineno - 3)
        for j in range(start, min(len(lines_t), e.lineno + 2)):
            marker = ">>>" if j == e.lineno - 1 else "   "
            print(f"  {marker} {j+1}: {lines_t[j]}")

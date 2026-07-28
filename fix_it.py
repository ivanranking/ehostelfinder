#!/usr/bin/env python3
"""Fix indentation errors in views.py and append missing functions."""
import ast

with open('hostels/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the signup function (lines ~203-214)
# Current issue: after 'except: pass', the messages.success and return 
# have too much indentation (should be inside the if form.is_valid() block)
# The else/return after should also be properly indented

# Find the signup function
fixes = {}
for i, line in enumerate(lines):
    ls = line.lstrip()
    if 'except: pass' in ls and i >= 200:
        # Extra indentation was added to the following lines
        # Fix the next 4 lines
        if i + 1 < len(lines) and 'messages.success' in lines[i + 1]:
            fixes[i + 1] = '                messages.success(request, "Account created! Please check your email to confirm.")\n'
        if i + 2 < len(lines) and 'return redirect' in lines[i + 2]:
            fixes[i + 2] = '                return redirect("login")\n'
        # Fix the else line
        if i + 3 < len(lines) and 'else:' in lines[i + 3]:
            fixes[i + 3] = '    else:\n'
        # Fix the form line
        if i + 4 < len(lines) and 'form = UserRegistrationForm()' in lines[i + 4].lstrip():
            fixes[i + 4] = '        form = UserRegistrationForm()\n'
        # Fix the return render line
        if i + 5 < len(lines) and 'return render' in lines[i + 5].lstrip():
            fixes[i + 5] = '    return render(request, "signup.html", {"form": form})\n'

if fixes:
    for idx, content in fixes.items():
        print(f"Fixing line {idx+1}: {repr(content.rstrip())}")
        lines[idx] = content

with open('hostels/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify syntax
t = open('hostels/views.py').read()
try:
    ast.parse(t)
    print("\nSYNTAX OK!")
except SyntaxError as e:
    print(f"\nStill has error at line {e.lineno}: {e.msg}")
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

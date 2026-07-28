#!/usr/bin/env python3
"""Fix the else block in signup function of views.py."""
import ast

with open('hostels/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Current state after previous fixes:
# Line 213: '                return redirect("login")'
# Line 214: '    else:'
# Line 215: '    return render(request, "signup.html", {"form": form})'
# Line 216: '' (empty)

# Fix: after else:, need 'form = UserRegistrationForm()' indented
# Then the return render at function level
for i, line in enumerate(lines):
    ls = line.lstrip()
    # Find the buggy else: return pattern
    if ls.startswith('else:') and 'return render' in ls:
        old_line = lines[i]
        indent = old_line[:len(old_line) - len(ls)]
        lines[i] = f'{indent}else:\n'
        lines.insert(i+1, f'{indent}    form = UserRegistrationForm()\n')
    # Find standalone '    else:' followed by '    return render'
    if ls == 'else:' and i+1 < len(lines):
        next_ls = lines[i+1].lstrip()
        if next_ls.startswith('return render(request, "signup.html"'):
            indent = line[:len(line) - len(ls)]
            # Insert the form assignment after else:
            lines.insert(i+1, f'{indent}    form = UserRegistrationForm()\n')
            break

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

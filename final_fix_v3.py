#!/usr/bin/env python3
"""Fix views.py - fix syntax errors and append missing functions."""
import ast, os

os.chdir(r'c:\Users\user\ehostelfinder')
lines = open('hostels/views.py', 'r', encoding='utf-8').readlines()

# Show context around signup function
print("BEFORE - lines 208-218:")
for i in range(207, 219):
    if i < len(lines):
        print(f"{i+1}: {lines[i].rstrip()}")

# === FIX 1: Fix except: pass to multi-line ===
for i, line in enumerate(lines):
    ls = line.lstrip()
    if ls.startswith('except') and ':pass' in ls.replace(' ', ''):
        indent = line[:len(line) - len(ls)]
        lines[i] = indent + 'except Exception:\n'
        lines.insert(i+1, indent + '    pass\n')
        print(f"Fixed except:pass at line {i+1}")
        break

# === FIX 2: Fix else: without body ===
for i in range(len(lines)-1):
    if lines[i].rstrip() == '    else:' and i+1 < len(lines):
        next_ls = lines[i+1].lstrip()
        if next_ls.startswith('return render'):
            indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
            lines.insert(i+1, indent + '    form = UserRegistrationForm()\n')
            print(f"Fixed else at line {i+1}")
            break

# === FIX 3: Fix logout_view body indentation ===
for i in range(len(lines)-1):
    if lines[i].strip().startswith('def logout_view(request):'):
        if i+1 < len(lines) and lines[i+1].strip() and not lines[i+1].startswith(' '):
            lines[i+1] = '    ' + lines[i+1].lstrip()
            print(f"Fixed logout_view body at line {i+1}")
        break

with open('hostels/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify syntax
t = open('hostels/views.py').read()
try:
    tree = ast.parse(t)
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    print(f'\nSYNTAX OK! Total: {len(funcs)}')
    for fn in sorted(funcs):
        print(f'  - {fn}')
    
    # Check missing
    needed = ['cancel_booking', 'custom_404', 'custom_500', 'api_notifications',
              'mark_notification_read', 'mark_all_notifications_read',
              'view_notifications', 'my_favorites', 'toggle_favorite', 'process_payment']
    missing = [f for f in needed if f not in funcs]
    if missing:
        print(f'\nMissing: {missing}')
    else:
        print('\nAll functions present!')
        print(f'  Total size: {len(t)} bytes')
except Exception as e:
    print(f'\nError: {e}')
    lines_t = t.split('\n')
    if hasattr(e, 'lineno') and e.lineno:
        start = max(0, e.lineno-3)
        for j in range(start, min(len(lines_t), e.lineno+2)):
            marker = '>>>' if j == e.lineno-1 else '   '
            print(f'{marker} {j+1}: {lines_t[j]}')

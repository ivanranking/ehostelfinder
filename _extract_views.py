#!/usr/bin/env python3
"""Extract views code from gen_views_final.py and write to views.py"""
with open('gen_views_final.py', 'r', encoding='utf-8') as f:
    data = f.read()

idx = data.find("content = r'''")
if idx < 0:
    print("ERROR: content block not found")
    exit(1)

start = idx + 14
end = data.find("'''", start)
if end < 0:
    print("ERROR: closing ''' not found")
    exit(1)

block = data[start:end]

# Find the broken comment and truncate there if present
broken = block.find("The indentation tracking is broken")
if broken > 0:
    block = block[:broken].rstrip()

# Also check for any remaining commands/scripts at the end
extra = block.find("add(0,")
if extra > 0:
    # There's extra code appended - find the last function and cut
    pass  # already handled by broken check

with open('hostels/views.py', 'w', encoding='utf-8') as f:
    f.write(block + '\n')

# Verify
import ast
with open('hostels/views.py', 'r') as f:
    verify = f.read()

tree = ast.parse(verify)
funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
print(f"Written: {len(verify)} bytes, {len(funcs)} functions")
for fn in funcs:
    print(f"  - {fn}")

# Check for missing required functions
required = ['cancel_booking', 'custom_404', 'custom_500', 'api_notifications', 
            'mark_notification_read', 'mark_all_notifications_read', 
            'view_notifications', 'my_favorites', 'toggle_favorite', 'process_payment']
missing = [fn for fn in required if fn not in funcs]
if missing:
    print(f"\nMISSING: {missing}")
else:
    print("\nAll required functions present!")


    lines = f.readlines()

# Fix lines around signup function (line 211-213 in 0-indexed = 210-212)
# The indentation for the else/return after signup's if form.is_valid() was wrong
lines[210] = '                messages.success(request, "Account created! Please check your email to confirm.")\n'
lines[211] = '                return redirect("login")\n'
lines[212] = '    else: form = UserRegistrationForm()\n'
lines[213] = '    return render(request, "signup.html", {"form": form})\n'

with open('hostels/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
import ast
t = open('hostels/views.py').read()
try:
    ast.parse(t)
    print("Syntax OK!")
except SyntaxError as e:
    print(f"Still has error: {e}")
    lines_before = t.split('\n')
    if e.lineno:
        ctx_start = max(0, e.lineno - 3)
        ctx_end = min(len(lines_before), e.lineno + 2)
        for i in range(ctx_start, ctx_end):
            marker = ">>>" if i == e.lineno - 1 else "   "
            print(f"  {marker} {i+1}: {lines_before[i]}")

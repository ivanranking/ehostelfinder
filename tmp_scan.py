from pathlib import Path
p = Path('templates/base.html')
data = p.read_bytes()
print(data[:200])
controls = [(i, b) for i, b in enumerate(data) if b < 32 and b not in (9, 10, 13)]
print('controls', controls[:20])

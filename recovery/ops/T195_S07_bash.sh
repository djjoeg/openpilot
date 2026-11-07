python3 - <<'EOF'
p = 'slotplate.py'
s = open(p).read()
s = s.replace('''def text(s: str, x: float, y: float, z0: float, rot: float = 0.0) -> Manifold:
  """Raised text, lower-left corner at (x, y) on a face at z0, reading in +X; rot 90 turns it to read in +Y."""
  cells = []
  for i, ch in enumerate(s):
    for r, row in enumerate(FONT[ch]):
      for c, bit in enumerate(row):
        if bit == "1":
          cx, cy = (i * 4 + c) * PIX, (4 - r) * PIX
          cells.append(box(cx, cx + PIX, cy, cy + PIX, z0, z0 + LABEL_H))
  return union(cells).rotate((0.0, 0.0, rot)).translate((x, y, 0.0))


def text_width(s: str) -> float:
  return (len(s) * 4 - 1) * PIX''',
'''def text(s: str, x: float, y: float, z0: float, rot: float = 0.0, pix: float = PIX) -> Manifold:
  """Raised text, lower-left corner at (x, y) on a face at z0, reading in +X; rot 90 turns it to read in +Y."""
  cells = []
  for i, ch in enumerate(s):
    for r, row in enumerate(FONT[ch]):
      for c, bit in enumerate(row):
        if bit == "1":
          cx, cy = (i * 4 + c) * pix, (4 - r) * pix
          cells.append(box(cx, cx + pix, cy, cy + pix, z0, z0 + LABEL_H))
  return union(cells).rotate((0.0, 0.0, rot)).translate((x, y, 0.0))


def text_width(s: str, pix: float = PIX) -> float:
  return (len(s) * 4 - 1) * pix''')
s = s.replace('''  for k, xc in enumerate(cols, start=1):
    s = str(k)
    labels.append(text(s, xc - text_width(s) / 2, Y - END_RAIL + 2.0, T))''',
'''  for k, xc in enumerate(cols, start=1):
    s = str(k)
    labels.append(text(s, xc - text_width(s, 0.9) / 2, Y - END_RAIL + 2.5, T, pix=0.9))''')
open(p, 'w').write(s)
EOF
/home/claude/bin/ruff check --output-format concise --line-length 140 slotplate.py && PYTHONPATH=/home/claude/pylib timeout 900 python3 slotplate.py 2>&1 | tail -2
python3 - <<'EOF'
p = 'measureplate.py'
s = open(p).read()

old_ticks_x = s[s.index("def ticks_along_x"):s.index("def ticks_along_y")]
old_ticks_y = s[s.index("def ticks_along_y"):s.index("def rim_ticks")]
new_ticks = '''def ticks_along_x(x0: float, x1: float, y: float, z0: float, up: bool, skip=()) -> list:
  """Scale ticks at every 5 mm of X from x0 to x1 (a long one every 10), standing on a face at z0, pointing +Y if up;
  none over the X ranges in skip (a window's)."""
  w, ln, h = TICK
  parts = []
  x = x0
  while x <= x1 + 1e-6:
    if not any(a <= x <= b for a, b in skip):
      L = ln * 2 if abs(x % 10) < 1e-6 or abs(x % 10 - 10) < 1e-6 else ln
      y0, y1 = (y, y + L) if up else (y - L, y)
      parts.append(box(x - w / 2, x + w / 2, y0, y1, z0, z0 + h))
    x += 5.0
  return parts


def ticks_along_y(y0: float, y1: float, x: float, z0: float, right: bool, skip=()) -> list:
  w, ln, h = TICK
  parts = []
  y = y0
  while y <= y1 + 1e-6:
    if not any(a <= y <= b for a, b in skip):
      L = ln * 2 if abs(y % 10) < 1e-6 or abs(y % 10 - 10) < 1e-6 else ln
      x0, x1 = (x, x + L) if right else (x - L, x)
      parts.append(box(x0, x1, y - w / 2, y + w / 2, z0, z0 + h))
    y += 5.0
  return parts


'''
s = s.replace(old_ticks_x + old_ticks_y, new_ticks)

# labels: numbers placed by hand so none floats over a window; all of them keep holes away
s = s.replace('''WORDS = (("WHEEL ^", (20.0, 110.0)), ("KEY >", (72.0, 110.0)))   # raised words: lower-left corners''',
'''# raised words and numbers (text, lower-left corner): the plate's X values along the dash-end edge and its Y values
# along the right edge, except where a window is; those values sit beside the window instead
LABELS = (("WHEEL ^", (20.0, 110.0)), ("KEY >", (72.0, 110.0)),
          ("40", (36.4, 10.0)), ("60", (56.4, 10.0)), ("80", (76.4, 10.0)), ("20", (16.4, 49.0)),
          ("20", (83.0, 17.0)), ("40", (83.0, 37.0)), ("60", (40.8, 57.0)), ("80", (40.8, 77.0)), ("100", (37.2, 97.0)))''')

s = s.replace('''  for word, (wx, wy) in WORDS:
    if wx - r < cx < wx + text_width(word) + r and wy - r < cy < wy + 5 * PIX + r:
      return False
  return True''',
'''  for word, (wx, wy) in LABELS:
    if wx - r < cx < wx + text_width(word) + r and wy - r < cy < wy + 5 * PIX + r:
      return False
  return True''')

s = s.replace('''  # the plate's own scales, on the plate's face just inside the rim: X along the dash-end edge (numbers above the
  # ticks), Y along the right edge (numbers to the left of the ticks)
  labels += ticks_along_x(5.0, X1 - 10.0, Y0 + RIM_W, T, up=True, numbers=True)
  labels += ticks_along_y(10.0, Y1 - 10.0, X1 - RIM_W, T, right=False, numbers=True)
  # words: which way is the wheel, which side the key is on
  for word, (wx, wy) in WORDS:
    labels.append(text(word, wx, wy, T))
  return body + union(labels)''',
'''  # the plate's own scales, on the plate's face just inside the rim: X along the dash-end edge, Y along the right
  # edge, neither where a window's rim is (the window's own ticks carry on the count there)
  skip_x = [(x0 - RIM_W, x1 + RIM_W) for (x0, x1, y0, y1) in WINDOWS.values() if y0 < Y0 + 12]
  skip_y = [(y0 - RIM_W, y1 + RIM_W) for (x0, x1, y0, y1) in WINDOWS.values() if x1 > X1 - 12]
  labels += ticks_along_x(5.0, X1 - 10.0, Y0 + RIM_W, T, up=True, skip=skip_x)
  labels += ticks_along_y(10.0, Y1 - 10.0, X1 - RIM_W, T, right=False, skip=skip_y)
  for word, (wx, wy) in LABELS:
    labels.append(text(word, wx, wy, T))
  return body + union(labels)''')
open(p, 'w').write(s)
print('ok')
EOF
PYTHONPATH=/home/claude/pylib timeout 600 python3 measureplate.py 2>&1 | tail -3 && PYTHONPATH=/home/claude/pylib timeout 600 python3 - <<'EOF'
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import measureplate as M, render as R
p = M.plate(); b = M.bar()
img = R.render([(p, (0.6, 0.72, 0.9)), (b.translate((50, -14, 0)), (0.95, 0.72, 0.45))], R.view_matrix(-90, 89), size=(1400, 1500), margin=0.03)
plt.imsave('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/mplate_top.png', np.clip(img, 0, 1))
print("ok")
EOF
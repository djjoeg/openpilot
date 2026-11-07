python3 - <<'EOF'
p = 'measureplate.py'
s = open(p).read()

# ticks: only on the rims (no numbers), 0.4 high; plate scales keep their numbers
s = s.replace('''TICK = (0.8, 3.0, 0.5)       # scale ticks: width, length, height; a long tick (x2) every 10 mm''',
'''TICK = (0.8, 3.0, 0.5)       # the plate's scale ticks: width, length, height; a long tick (x2) every 10 mm
RIM_TICK = (0.8, 1.4, 2.4, 0.4)   # ticks on a window's rim: width, short length, long length (every 10 mm), height
GRID_X, GRID_Y = (20.0, 70.0), (20.0, 100.0)   # the hole grid: X 20 to 70, Y 20 to 100, every PITCH
WORDS = (("WHEEL ^", (20.0, 110.0)), ("KEY >", (72.0, 110.0)))   # raised words: lower-left corners''')

s = s.replace('''def hole_ok(cx: float, cy: float) -> bool:
  r = HOLE_D / 2 + HOLE_KEEP
  X0, X1, Y0, Y1 = PLATE
  if cx - r < X0 + RIM_W or cx + r > X1 - RIM_W or cy - r < Y0 + RIM_W or cy + r > Y1 - RIM_W:
    return False
  for (x0, x1, y0, y1) in [NOTCH] + list(WINDOWS.values()):
    if x0 - r < cx < x1 + r and y0 - r < cy < y1 + r:
      return False
  return True''',
'''def rim_ticks(x0: float, x1: float, y0: float, y1: float) -> list:
  """Ticks every 5 mm on a window's rim, standing on the rim's top, pointing out from the window's edge."""
  w, short, long, h = RIM_TICK
  z0 = T + RIM_H
  parts = []
  def L(v):
    return long if abs(v % 10) < 1e-6 or abs(v % 10 - 10) < 1e-6 else short
  v = 5.0 * round(x0 / 5.0 + 0.4999)
  while v <= x1 + 1e-6:
    parts.append(box(v - w / 2, v + w / 2, y1 + 0.3, y1 + 0.3 + L(v), z0, z0 + h))
    parts.append(box(v - w / 2, v + w / 2, y0 - 0.3 - L(v), y0 - 0.3, z0, z0 + h))
    v += 5.0
  v = 5.0 * round(y0 / 5.0 + 0.4999)
  while v <= y1 + 1e-6:
    parts.append(box(x1 + 0.3, x1 + 0.3 + L(v), v - w / 2, v + w / 2, z0, z0 + h))
    parts.append(box(x0 - 0.3 - L(v), x0 - 0.3, v - w / 2, v + w / 2, z0, z0 + h))
    v += 5.0
  return parts


def hole_ok(cx: float, cy: float) -> bool:
  r = HOLE_D / 2 + HOLE_KEEP
  X0, X1, Y0, Y1 = PLATE
  if cx - r < X0 + RIM_W or cx + r > X1 - RIM_W or cy - r < Y0 + RIM_W or cy + r > Y1 - RIM_W:
    return False
  for (x0, x1, y0, y1) in [NOTCH] + list(WINDOWS.values()):
    if x0 - r < cx < x1 + r and y0 - r < cy < y1 + r:
      return False
  for word, (wx, wy) in WORDS:
    if wx - r < cx < wx + text_width(word) + r and wy - r < cy < wy + 5 * PIX + r:
      return False
  return True''')

s = s.replace('''    # ticks on the rim's top: along the window's wheel-end edge (X values) and its right edge (Y values)
    labels += ticks_along_x(x0, x1, y1 + RIM_W, T + RIM_H, up=True, numbers=True)
    labels += ticks_along_y(y0, y1, x1 + RIM_W, T + RIM_H, right=True, numbers=(x1 + RIM_W + 14 < X1))
  # the grid of holes
  x = PITCH
  while x < X1:
    y = PITCH
    while y < Y1:
      if hole_ok(x, y):
        body = body - cyl(HOLE_D / 2, -1.0, T + RIM_H + 1, x=x, y=y, segments=32)
      y += PITCH
    x += PITCH
  # the plate's own scales: X along the dash-end edge, Y along the right edge, on the rim's top
  labels += ticks_along_x(10.0, X1 - 10.0, Y0 + RIM_W, T + RIM_H, up=True, numbers=True)
  labels += ticks_along_y(10.0, Y1 - 10.0, X1 - RIM_W, T + RIM_H, right=False, numbers=True)
  # words: which way is the wheel, which side the key is on
  labels.append(text("WHEEL ^", 40.0, Y1 - RIM_W - 8.0, T))
  labels.append(text("KEY SIDE >", X1 - RIM_W - text_width("KEY SIDE >") - 1.0, Y1 - RIM_W - 16.0, T))
  labels.append(text("X", X1 - 22.0, Y0 + RIM_W + 8.0, T))
  labels.append(text("Y", X1 - RIM_W - 12.0, 52.0, T))
  return body + union(labels)''',
'''    # ticks every 5 mm on the rim, all four sides: they line up with the plate's scales (long ones at every 10)
    labels += rim_ticks(x0, x1, y0, y1)
  # the grid of holes
  x = GRID_X[0]
  while x <= GRID_X[1] + 1e-6:
    y = GRID_Y[0]
    while y <= GRID_Y[1] + 1e-6:
      if hole_ok(x, y):
        body = body - cyl(HOLE_D / 2, -1.0, T + RIM_H + 1, x=x, y=y, segments=32)
      y += PITCH
    x += PITCH
  # the plate's own scales, on the plate's face just inside the rim: X along the dash-end edge (numbers above the
  # ticks), Y along the right edge (numbers to the left of the ticks)
  labels += ticks_along_x(5.0, X1 - 10.0, Y0 + RIM_W, T, up=True, numbers=True)
  labels += ticks_along_y(10.0, Y1 - 10.0, X1 - RIM_W, T, right=False, numbers=True)
  # words: which way is the wheel, which side the key is on
  for word, (wx, wy) in WORDS:
    labels.append(text(word, wx, wy, T))
  return body + union(labels)''')
open(p, 'w').write(s)
print('ok')
EOF
PYTHONPATH=/home/claude/pylib timeout 600 python3 measureplate.py 2>&1 | tail -3
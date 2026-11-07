python3 - << 'EOF'
p = "accord_lka_parts.py"
s = open(p).read()
a = """    # turn it about the vertical to fit the bed if it needs to
    best = None
    for zr in range(0, 91, 5):
      p2 = on_bed(placed, (0, 0, zr))
      x0, y0, z0, x1, y1, z1 = p2.bounding_box()
      sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
      fit = sx <= bed[0] and sy <= bed[1] and sz <= bed[2]
      if best is None or (fit and not best[0]) or (fit == best[0] and max(sx / bed[0], sy / bed[1]) < best[2]):
        best = (fit, p2, max(sx / bed[0], sy / bed[1]), (sx, sy, sz), zr)
    fits, p2, _, size, zr = best"""
b = """    # turn it about the vertical only if it needs that to fit the bed
    best = None
    for zr in range(0, 91, 5):
      p2 = on_bed(placed, (0, 0, zr))
      x0, y0, z0, x1, y1, z1 = p2.bounding_box()
      sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
      fit = sx <= bed[0] and sy <= bed[1] and sz <= bed[2]
      if best is None or (fit and not best[0]) or (not fit and not best[0] and max(sx / bed[0], sy / bed[1]) < best[2]):
        best = (fit, p2, max(sx / bed[0], sy / bed[1]), (sx, sy, sz), zr)
      if fit:
        break
    fits, p2, _, size, zr = best"""
assert a in s; s = s.replace(a, b); open(p, "w").write(s)
EOF
echo ok
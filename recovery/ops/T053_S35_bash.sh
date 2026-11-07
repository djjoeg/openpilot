python3 - <<'EOF'
p = "mountparts.py"
s = open(p).read()
old = '''def switch_screws(length: float = 16.0) -> Manifold:
  """The switch's two M2 screws: heads on the front wall's face, tips out past the rear wall (carrier frame)."""
  parts = []
  for sx in (-1, 1):
    x = SW_X + sx * SW_PITCH / 2
    parts.append(cyl(1.0, CAGE_FRONT[1] - length, CAGE_FRONT[1], x, SW_HOLES, 24) +
                 cyl(1.9, CAGE_FRONT[1], CAGE_FRONT[1] + 2.0, x, SW_HOLES, 24))
  return union(parts)'''
new = '''def switch_screws(length: float = 16.0, dy: float = 0.0) -> Manifold:
  """The switch's two M2 screws: heads on the front wall's face, tips out past the rear wall (carrier frame). dy: where
  they sit in their slots (the switch slides +-SW_SLOT to set where it clicks)."""
  parts = []
  for sx in (-1, 1):
    x = SW_X + sx * SW_PITCH / 2
    parts.append(cyl(1.0, CAGE_FRONT[1] - length, CAGE_FRONT[1], x, SW_HOLES + dy, 24) +
                 cyl(1.9, CAGE_FRONT[1], CAGE_FRONT[1] + 2.0, x, SW_HOLES + dy, 24))
  return union(parts)'''
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w").write(s)
EOF
echo ok
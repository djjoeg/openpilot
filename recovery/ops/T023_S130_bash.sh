export PYTHONPATH=/home/claude/pylib && python3 -c "
import manifold3d as m
print([x for x in dir(m.Manifold) if 'trans' in x or 'mirror' in x])
help(m.Manifold.transform)
" 2>&1 | head -20 && python3 - <<'EOF'
p = "/home/claude/deliver/hardware/cad/cadlib.py"
s = open(p).read()
start = s.index("def side_profile_x(")
end = s.index("def union(parts)")
new = '''def prism_x(points_yz, x0, x1) -> Manifold:
  """Extrudes a (y, z) outline along X from x0 to x1 (either winding)."""
  cs = CrossSection([list(points_yz)])
  if cs.area() < 1e-9:
    cs = CrossSection([list(points_yz)[::-1]])
  # extruded points are (u=y, v=z, w); map (u, v, w) -> (w + x0, u, v), a proper rotation
  return cs.extrude(x1 - x0).transform([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]])


'''
s = s[:start] + new + s[end:]
open(p, "w").write(s)
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib:. python3 -c "
from cadlib import *
m = prism_x([(0,0),(10,0),(10,5),(0,5)], -2, 3)
print(m.volume(), m.bounding_box(), m.status())
m2 = prism_x([(0,0),(0,5),(10,5),(10,0)], -2, 3)
print(m2.volume(), m2.bounding_box())
"
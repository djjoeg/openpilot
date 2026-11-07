cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/overhang.py << 'EOF'
import sys, math, itertools
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import wheelparts as WP, mountparts as MP
from cadlib import on_bed

def support_area(m, rot):
  p = on_bed(m, rot)
  mesh = p.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3]
  t = np.asarray(mesh.tri_verts)
  a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
  n = np.cross(b - a, c - a)
  area = np.linalg.norm(n, axis=1) / 2
  nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
  zmin = np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2])
  steep = (nz < -math.cos(math.radians(45))) & (zmin > 0.3)
  bed = (nz < -0.999) & (zmin <= 0.3)
  x0, y0, z0, x1, y1, z1 = p.bounding_box()
  return float(area[steep].sum()), float(area[bed].sum()), (x1 - x0, y1 - y0, z1 - z0)

t = WP.Teeth()
parts = {"carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(), "arm150": MP.arm(150),
         "clamp": MP.dash_clamp(), "gauge": MP.setup_gauge(), "pad": MP.clamp_pad(), "gear": WP.motor_gear()}
cands = [(0, 0, 0), (180, 0, 0), (90, 0, 0), (-90, 0, 0), (0, 90, 0), (0, -90, 0)]
for name, m in parts.items():
  rows = []
  for r in cands:
    s, b, size = support_area(m, r)
    rows.append((s, r, b, size))
  rows.sort()
  print(name, " ".join("%s:%.0f(bed %.0f)" % (r, s, b) for s, r, b, size in rows))
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/overhang.py
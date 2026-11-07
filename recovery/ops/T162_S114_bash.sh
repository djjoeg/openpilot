cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/orient.py <<'EOF'
import sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import sideparts as S
from cadlib import on_bed

def support_area(m, max_angle=45.0):
  mesh = m.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3]
  tri = np.asarray(mesh.tri_verts)
  a, b, c = v[tri[:, 0]], v[tri[:, 1]], v[tri[:, 2]]
  n = np.cross(b - a, c - a)
  area = np.linalg.norm(n, axis=1) / 2
  nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
  zmin = np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2]) - v[:, 2].min()
  steep = (nz < -math.cos(math.radians(max_angle)) - 0.01) & (zmin > 0.3)
  on_bed_faces = (nz < -0.999) & (zmin <= 0.3)
  return float(area[steep].sum()), float(area[on_bed_faces].sum())

for name, m in (("bracket", S.side_bracket()), ("plate", S.side_plate()), ("gear", S.side_gear()), ("spool", S.side_spool()), ("cap", S.side_board_cap())):
  rows = []
  for rot in ((0, 0, 0), (180, 0, 0), (90, 0, 0), (-90, 0, 0), (0, 90, 0), (0, -90, 0)):
    p = on_bed(m, rot)
    sa, bed = support_area(p)
    rows.append((round(sa), round(bed), rot))
  rows.sort()
  print(name, rows[:6])
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && PYTHONPATH=/home/claude/pylib timeout 600 python3 orient.py
cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/overhangs.py <<'EOF'
import sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import sideparts as S
from cadlib import on_bed

def faces(m, rot):
  # keep the part frame: rotate only (on_bed also translates; undo by using the same rotation on the original)
  r = m.rotate(rot)
  mesh = r.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3]
  tri = np.asarray(mesh.tri_verts)
  a, b, c = v[tri[:, 0]], v[tri[:, 1]], v[tri[:, 2]]
  n = np.cross(b - a, c - a)
  area = np.linalg.norm(n, axis=1) / 2
  nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
  zmin = np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2]) - v[:, 2].min()
  steep = (nz < -math.cos(math.radians(45)) - 0.01) & (zmin > 0.3)
  cen = (a + b + c) / 3
  # back to the part frame: inverse rotation
  inv = m.rotate(rot)
  return cen[steep], area[steep]

for name, m, rot in (("bracket", S.side_bracket(), (90, 0, 0)), ("plate", S.side_plate(), (0, -90, 0))):
  cen, ar = faces(m, rot)
  # group by rounded centroid (5 mm cells) in the rotated frame
  cells = {}
  for c, a in zip(cen, ar):
    key = tuple((np.round(c / 6.0) * 6).astype(int))
    cells[key] = cells.get(key, 0) + a
  print(name, round(ar.sum()), sorted(cells.items(), key=lambda kv: -kv[1])[:12])
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && PYTHONPATH=/home/claude/pylib python3 overhangs.py
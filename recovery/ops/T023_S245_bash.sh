cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/overhang_where.py << 'EOF'
import sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import mountparts as MP
from cadlib import on_bed

def where(m, rot, cell=8.0):
  # report overhang triangles grouped by location in the part's own frame
  mesh = m.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3]
  t = np.asarray(mesh.tri_verts)
  R = np.eye(3)
  for ang, ax in zip(rot, range(3)):
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    if ax == 0: Ri = np.array([[1,0,0],[0,c,-s],[0,s,c]])
    elif ax == 1: Ri = np.array([[c,0,s],[0,1,0],[-s,0,c]])
    else: Ri = np.array([[c,-s,0],[s,c,0],[0,0,1]])
    R = Ri @ R
  vp = v @ R.T
  zmin_all = vp[:, 2].min()
  a, b, c = vp[t[:, 0]], vp[t[:, 1]], vp[t[:, 2]]
  n = np.cross(b - a, c - a)
  area = np.linalg.norm(n, axis=1) / 2
  nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
  zmin = np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2]) - zmin_all
  steep = (nz < -math.cos(math.radians(45))) & (zmin > 0.3)
  cent = (v[t[:, 0]] + v[t[:, 1]] + v[t[:, 2]]) / 3   # original frame
  groups = {}
  for i in np.where(steep)[0]:
    key = tuple((cent[i] // cell).astype(int))
    groups[key] = groups.get(key, 0.0) + area[i]
  items = sorted(groups.items(), key=lambda kv: -kv[1])
  tot = sum(groups.values())
  print("total %.0f mm2" % tot)
  for k, ar in items[:25]:
    print("  around x %5.0f y %5.0f z %5.0f : %6.1f mm2" % ((k[0] + .5) * cell, (k[1] + .5) * cell, (k[2] + .5) * cell, ar))

print("hinge block, front face down")
where(MP.hinge_block(), (180, 0, 0))
print("carrier, finger guard down")
where(MP.motor_carrier(), (180, 0, 0), cell=12.0)
print("clamp on its side")
where(MP.dash_clamp(), (0, 90, 0), cell=12.0)
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/overhang_where.py
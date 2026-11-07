cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face/diag2.py <<'EOF'
import sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import faceparts as FP
t = FP.FaceTeeth()
whole = FP.face_solid(t)
for phi in (50.0, 53.0, 55.0, 56.0, 58.0):
  m = whole.rotate((0, 0, -phi))
  # slice by the plane y = 0: map (x, y, z) -> (x, z, y) and slice at height 0
  cs = m.transform([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]]).slice(0.0)
  polys = cs.to_polygons()
  # for r in 170..178 find the lowest z (most negative) of material
  out = []
  for r in (170.0, 172.0, 173.6, 174.0, 174.5, 174.9, 175.2, 176.0, 176.9, 178.0):
    zs = []
    for poly in polys:
      p = np.asarray(poly)
      n = len(p)
      for i in range(n):
        (x0, z0), (x1, z1) = p[i], p[(i + 1) % n]
        if (x0 - r) * (x1 - r) < 0:
          zs.append(z0 + (r - x0) * (z1 - z0) / (x1 - x0))
    out.append((r, round(min(zs), 2) if zs else None))
  print(phi, out)
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && PYTHONPATH=/home/claude/pylib timeout 600 python3 diag2.py
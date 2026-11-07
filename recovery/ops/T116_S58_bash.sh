cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > facecheck2.py <<'EOF'
import sys, math, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
sys.path.insert(0, ".")
import numpy as np
from facegen_test import *

sp = tooth_space()
print("space verts", sp.num_vert(), "tris", sp.num_tri())
s2 = sp.simplify(0.005)
print("simplified verts", s2.num_vert())
fb = face_block(5)
# slice at x = r: rotate so +x -> +z, then slice at z = r
for r in (160.6, 163.0, 166.0, 169.0, 171.4):
  m = fb.rotate((0, -90, 0))      # x -> z? check bbox
  cs = fb.transform([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]).slice(r)   # (y, z, x): slice at x = r
  polys = cs.to_polygons()
  # tooth thickness at the pitch plane z = Z_P and at the tip z = Z_TIP + 0.2: find intervals in y of material
  def widths(zq):
    xs = []
    for poly in polys:
      p = np.asarray(poly)
      n = len(p)
      for i in range(n):
        (y0, z0), (y1, z1) = p[i], p[(i + 1) % n]
        if (z0 - zq) * (z1 - zq) < 0:
          xs.append(y0 + (zq - z0) * (y1 - y0) / (z1 - z0))
    xs.sort()
    return [round(xs[i + 1] - xs[i], 3) for i in range(0, len(xs) - 1, 2)]
  print(f"r={r}: tooth widths at pitch plane {widths(Z_P)}; at 0.2 above tips {widths(Z_TIP + 0.2)}; near root {widths(Z_ROOT - 0.3)}")
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 facecheck2.py 2>&1 | tail -8
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > overhang.py <<'EOF'
import sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
from closeups import load  # noqa
EOF
cat > overhang2.py <<'EOF'
import sys, math, struct
import numpy as np
from manifold3d import Manifold, Mesh
def load(p):
  d = open(p, "rb").read()
  n = struct.unpack("<I", d[80:84])[0]
  a = np.frombuffer(d[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
  return a["v"].astype(np.float64)
for name in ["back-teeth-upper", "fit-test-back-teeth", "fit-test-back-teeth-spoke"]:
  t = load(f"/home/claude/deliver/hardware/stl/back-teeth-mount/{name}.stl")
  a, b, c = t[:, 0], t[:, 1], t[:, 2]
  n = np.cross(b - a, c - a)
  area = np.linalg.norm(n, axis=1) / 2
  nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
  z0 = t[:, :, 2].min()
  zmin = t[:, :, 2].min(axis=1) - z0
  steep = (nz < -math.cos(math.radians(45)) - 0.01) & (zmin > 0.3)
  print(name, "total", round(area[steep].sum()), "height of part", round(t[:, :, 2].max() - z0, 1))
  # group by height
  hz = np.round(zmin[steep] / 1.0) * 1.0
  for h in sorted(set(hz)):
    s = area[steep][hz == h].sum()
    if s > 20:
      flat = (nz[steep][hz == h] < -0.99)
      print(f"   z {h:5.1f}: {s:7.0f} mm2, flat-down share {area[steep][hz == h][flat].sum() / s:.2f}")
EOF
python3 overhang2.py
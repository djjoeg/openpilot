cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > islands.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
from closeups import load
S = "/home/claude/deliver/hardware/stl/back-teeth-mount/"
for name in sys.argv[1:]:
  m = load(S + name + ".stl")
  x0, y0, z0, x1, y1, z1 = m.bounding_box()
  tiny = []
  for z in np.arange(0.1, z1, 0.2):
    cs = m.slice(float(z))
    for piece in cs.decompose():
      a = piece.area()
      if a < 2.0:
        b = piece.bounds()
        tiny.append((round(float(z), 1), round(a, 3), [round(v, 1) for v in b]))
  print(name, "tiny islands (<2 mm2):", len(tiny))
  zs = sorted(set(t[0] for t in tiny))
  if tiny:
    print("  z from", zs[0], "to", zs[-1])
    for t in tiny[:12]:
      print("  ", t)
EOF
PYTHONPATH=/home/claude/pylib python3 islands.py back-teeth-upper back-teeth-lower fit-test-back-teeth fit-test-back-teeth-spoke 2>&1 | tail -60
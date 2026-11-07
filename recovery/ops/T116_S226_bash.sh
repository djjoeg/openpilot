cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > slivercheck.py <<'EOF'
"""Slices each STL along x, y and z every 0.25 mm and counts islands under 0.05 mm2 (films and needles a slicer drops)."""
import sys, os, glob
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
from closeups import load
root = sys.argv[1]
skip = sys.argv[2:] if len(sys.argv) > 2 else []
tot = 0
for path in sorted(glob.glob(os.path.join(root, "**", "*.stl"), recursive=True)):
  rel = os.path.relpath(path, root)
  if any(s in rel for s in skip):
    continue
  m0 = load(path)
  n = 0
  where = []
  for rot in ((0, 0, 0), (90, 0, 0), (0, 90, 0)):
    m = m0.rotate(rot)
    z0, z1 = m.bounding_box()[2], m.bounding_box()[5]
    for z in np.arange(z0 + 0.13, z1, 0.25):
      for piece in m.slice(float(z)).decompose():
        if piece.area() < 0.05:
          n += 1
          if len(where) < 3:
            where.append((rot, round(float(z), 2), [round(v, 1) for v in piece.bounds()]))
  tot += n
  print(f"{rel:55s} {n:5d}", where if n else "")
print("total", tot)
EOF
PYTHONPATH=/home/claude/pylib python3 slivercheck.py /home/claude/deliver/hardware/stl back-teeth-mount 2>&1 | tail -45
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > hbzoom.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import render as R
from cadlib import box
from closeups import load
m = load("../facebuild2/stl/back-teeth-mount/back-hinge-block.stl")
print([round(v, 1) for v in m.bounding_box()])
c = (.6, .72, .9)
z = m ^ box(-40, -12, -2, 25, 38, 60)
for piece in z.decompose():
  print("piece vol", round(piece.volume(), 3), [round(v, 1) for v in piece.bounding_box()])
R.save("hb-zoom.png", [([(z, c)], R.look((0.3, 1, 0.5), (0, 0, 1))), ([(z, c)], R.look((-1, 0.3, 0.6), (0, 0, 1))),
                       ([(m, c)], R.look((0.3, 1, 0.5), (0, 0, 1)))], ["zoom", "zoom other side", "whole"], size=(700, 600))
# thin slices near the spot
for zz in (24.1, 25.0, 26.0):
  pass
mr = m.rotate((0, 90, 0))
for zz in np.arange(23.5, 27.6, 0.25):
  for p in mr.slice(float(zz)).decompose():
    if p.area() < 0.5:
      print(round(float(zz), 2), round(p.area(), 4), [round(v, 2) for v in p.bounds()])
EOF
PYTHONPATH=/home/claude/pylib python3 hbzoom.py
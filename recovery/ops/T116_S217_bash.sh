cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > zoomend.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import render as R
from cadlib import box
from closeups import load
S = "/home/claude/deliver/hardware/stl/back-teeth-mount/"
up = load(S + "back-teeth-upper.stl")
x0, y0, z0, x1, y1, z1 = up.bounding_box()
print("bbox", [round(v, 1) for v in up.bounding_box()])
# the left end in the parts view: lowest x
c = (.6, .72, .9)
end = up ^ box(x0 - 1, x0 + 40, y0 - 1, y1 + 1, z0 - 1, z1 + 1)
end2 = up ^ box(x1 - 40, x1 + 1, y0 - 1, y1 + 1, z0 - 1, z1 + 1)
v1 = R.look((0.8, -1.0, 0.7), (0, 0, 1))
v2 = R.look((0.0, -0.3, 1.0), (0, 1, 0))
v3 = R.look((-1.0, -0.5, 0.6), (0, 0, 1))
R.save("zoom-upper-ends.png", [([(end, c)], v1), ([(end, c)], v2), ([(end2, c)], v1), ([(end2, c)], v3)],
       ["left end", "left end from above", "right end", "right end, other side"], size=(700, 600))
lo = load(S + "back-teeth-lower.stl")
x0, y0, z0, x1, y1, z1 = lo.bounding_box()
print("bbox lower", [round(v, 1) for v in lo.bounding_box()])
e1 = lo ^ box(x0 - 1, x1 + 1, y1 - 45, y1 + 1, z0 - 1, z1 + 1)
e2 = lo ^ box(x0 - 1, x1 + 1, y0 - 1, y0 + 45, z0 - 1, z1 + 1)
R.save("zoom-lower-ends.png", [([(e1, c)], v1), ([(e1, c)], v2), ([(e2, c)], v1), ([(e2, c)], v2)],
       ["top end", "top end from above", "bottom end", "bottom end from above"], size=(700, 600))
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 zoomend.py
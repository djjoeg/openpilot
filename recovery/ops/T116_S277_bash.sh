cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > short_test.py <<'EOF'
import sys, time, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import params as P
import faceparts as FP
from cadlib import on_bed, size_of, write_stl
import render as R
T0 = time.time()
t = FP.FaceTeeth(P.WHEEL_OD, P.GRIP, P.RIGHT_SPOKE_DEG, n_teeth=FP.N_TEETH_SHORT)
print("teeth_half", round(t.teeth_half, 2), "roll_half", round(t.roll_half, 2), "lead_end", round(t.lead_end, 2), "half", round(t.half, 2),
      "tracked", round(t.tracked_arc_deg, 2), "joint", t.joint_deg, "spoke", t.spoke)
print("ties", [round(a, 2) for a in FP.tie_angles(t)])
whole = FP.face_solid(t)
pcs = FP.face_pieces(t, whole)
m = pcs["one-piece"]
b = on_bed(m, (180, 0, 0))
best = None
for zr in range(0, 91, 5):
  p2 = on_bed(b, (0, 0, zr))
  sx, sy, sz = size_of(p2)
  if sx <= 220 and sy <= 220:
    best = (zr, (round(sx, 1), round(sy, 1), round(sz, 1)))
    break
print("one piece vol", round(m.volume()), "pieces", len(m.decompose()), "fits", best, round(time.time() - T0), "s")
write_stl(on_bed(b, (0, 0, best[0])), "short.stl")
c = (.6, .72, .9)
R.save("short.png", [([(b, c)], R.look((0.8, -1.0, 0.7), (0, 0, 1))), ([(m, c)], R.look((0, 0, 1), (0, 1, 0))),
                     ([(m, c)], R.look((0, 0, -1), (0, 1, 0)))], ["on the bed", "from the driver (front face)", "from behind (teeth)"],
       size=(700, 600))
EOF
PYTHONPATH=/home/claude/pylib python3 short_test.py && PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
" && mkdir -p shortstl && mv short.stl shortstl/ && PYTHONPATH=/home/claude/pylib python3 slivercheck.py shortstl
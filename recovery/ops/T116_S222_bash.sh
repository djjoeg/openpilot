cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > slivers.py <<'EOF'
import sys, math, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import params as P
import faceparts as FP
t = FP.FaceTeeth(P.WHEEL_OD, P.GRIP, P.RIGHT_SPOKE_DEG)
T0 = time.time()
m = FP.face_solid(t)
print("solid", round(time.time() - T0), "s; z_root", t.z_root, "z_band", round(t.z_band, 2), "z_tip", t.z_tip, "roll_half", round(t.roll_half, 2),
      "lead_end", round(t.lead_end, 2), "half", round(t.half, 2))
found = []
for z in np.arange(-28.0, -19.0, 0.1):
  cs = m.slice(float(z))
  for piece in cs.decompose():
    if piece.area() < 0.05:
      b = piece.bounds()
      cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
      found.append((round(float(z), 2), round(math.hypot(cx, cy), 2), round(math.degrees(math.atan2(cy, cx)), 2), round(piece.area(), 4)))
print(len(found))
import collections
byang = collections.Counter(round(f[2]) for f in found)
byr = collections.Counter(round(f[1]) for f in found)
byz = collections.Counter(round(f[0]) for f in found)
print("angles", sorted(byang.items()))
print("radii", sorted(byr.items()))
print("z", sorted(byz.items()))
for f in found[:20]:
  print(f)
EOF
PYTHONPATH=/home/claude/pylib python3 slivers.py
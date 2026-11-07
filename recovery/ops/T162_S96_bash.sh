cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()
old = '''  return [((-16.0, 12.0), (BUMPER_Z[0], -16.0)), ((-13.0, 12.0), (-16.0, Z_RAIL[1])),'''
new = '''  return [((-16.0, 12.0), (BUMPER_Z[0], -26.0)), ((-13.0, 12.0), (-26.0, Z_RAIL[1])),'''
assert old in s
s = s.replace(old, new)
old = '''  # the plate's edge towards the driver cut back 45 degrees, as before
  a, y0 = FP.PLATE_CHAMFER, MP.PLATE_BOTTOM
  part = part - prism_x([(y0 - 1.0, MOTOR_PLATE_T - a - 1.0), (y0 + a + 1.0, MOTOR_PLATE_T + 1.0), (y0 - 1.0, MOTOR_PLATE_T + 1.0)],
                        -60.0, 60.0)'''
new = '''  # the plate's edge towards the driver cut back 45 degrees, as before; beyond the motor's side the flange's end is
  # trimmed too, so it stays inside the teeth's inner edge (radius 160) where it passes under them
  a, y0 = FP.PLATE_CHAMFER, MP.PLATE_BOTTOM
  part = part - prism_x([(y0 - 1.0, MOTOR_PLATE_T - a - 1.0), (y0 + a + 1.0, MOTOR_PLATE_T + 1.0), (y0 - 1.0, MOTOR_PLATE_T + 1.0)],
                        -60.0, 60.0)
  part = part - box(X_FL[0] - 1.0, -MP.PLATE_HALF, y0 - 2.0, -13.0, FLANGE_TRIM_Z, MOTOR_PLATE_T + 1.0)'''
assert old in s
s = s.replace(old, new)
old = '''FL_Z = (BLOCK_Z[0] - 0.5, MOTOR_PLATE_T)         # ... and along: from just past the block to the bracket's face'''
new = '''FL_Z = (BLOCK_Z[0] - 0.5, MOTOR_PLATE_T)         # ... and along: from just past the block to the bracket's face
FLANGE_TRIM_Z = math.sqrt(160.0 ** 2 - (H + FLANGE_GAP + FLANGE_T) ** 2) - PP.R_FACE_P - 0.3   # see side_bracket'''
assert old in s
s = s.replace(old, new)
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import sideparts as S
print('trim z', S.FLANGE_TRIM_Z)
b = S.side_bracket(); print(b.volume(), b.genus())
"
cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/run_wheel2.py <<'EOF'
import time, sys, json
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import sideparts as S
import sideassembly as SA
t0 = time.time()
parts = SA.build_parts()
A = SA.SideAssembly(parts)
r = SA.wheel_turned(A, step=0.5)
print("wheel turned (0.5 deg steps):", {k: v for k, v in r.items() if v[0] > 1e-3}, flush=True)
r = SA.slid_in(A)
print("slid in over 0.001:", {k: round(v, 3) for k, v in r.items() if v > 1e-3}, flush=True)
ring = A.teeth_ring(); fingers = A.fingers()
for s in (0.0, S.STROKE):
    b = A.W(A.movers(s)["motor bracket"])
    print("bracket", s, "to ring", SA.gap(b, ring), "fingers", SA.gap(b, fingers))
pl = A.W(parts["plate"])
print("plate to ring", SA.gap(pl, ring), "to fingers", SA.gap(pl, fingers), "to grip", SA.gap(pl, A.grip()))
res = SA.internal(A)
print("internal:", [(k, v) for k, v in res.items() if v[0] > 1e-3 and "touching" not in k])
print("time", round(time.time() - t0))
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 3000 python3 run_wheel2.py 2>&1 | tail -20
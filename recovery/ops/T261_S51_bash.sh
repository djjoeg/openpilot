python3 - <<'EOF'
p = "rightcheck.py"
s = open(p).read()
a = '''  out["stop nut"] = place_z(nut(), sx, sy, RA.CAP_Z[1] - 2.2)
  out["stop jam nut"] = place_z(nut(), sx, sy, RA.CAP_Z[1] + 2.05)'''
b = '''  turned = (hex_prism_z(7.95, -2.0, 2.0, rot=30.0 + RA.THETA) - cyl(2.5, -3.0, 3.0, segments=24))   # as its pocket
  out["stop nut"] = place_z(turned, sx, sy, RA.CAP_Z[1] - 2.2)
  out["stop jam nut"] = place_z(turned, sx, sy, RA.CAP_Z[1] + 2.05)'''
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 rightcheck.py 2>&1 | tail -5
PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
import math
import rightarm as RA, rightcheck as RC
def gap(a, b, d, step=0.25, limit=40):
  """how far b can move along d before it touches a"""
  t = 0.0
  while t < limit:
    if (a ^ b.translate((d[0]*t, d[1]*t, d[2]*t))).volume() > RC.TOL:
      return t - step
    t += step
  return None
teeth = RC.teeth_piece().rotate((0,0,RA.THETA)); grip = RC.grip()
hw = RC.hardware(0.0, RA.STOP_P, swept=True)
print("stop wings to the teeth piece (moving the teeth piece down the column):", gap(hw["stop bolt"], teeth, (0,0,-1)))
mg = RA.motor_and_gear(0.0)
print("carrier plate to the teeth piece (down the column):", gap(RA.carrier(0.0), teeth, (0,0,-1)))
print("motor to the teeth piece (down the column):", gap(mg["motor"], teeth, (0,0,-1)))
print("pinch wings to the motor (along +v):", gap(mg["motor"], hw["pinch bolt"], (RA.V[0], RA.V[1], 0)))
lo = RA.motor_and_gear(RA.DZ_OUT)
print("slid out: board to the tab (down):", gap(RA.bracket(), lo["board"], (0,0,-1)))
print("slid out: carrier to the tab (down):", gap(RA.bracket(), RA.carrier(RA.DZ_OUT), (0,0,-1)))
print("gear slid out 6 mm to the teeth (up):", gap(RA.motor_and_gear(-6.0)["gear"], teeth, (0,0,-1)))
print("bar to the column cover (towards -x):")
import carscene as CS
cover = CS.CarScene(D=125.0).column_cover(back=130.0)
print("  flag/tab to the cover:", gap(cover, RA.bar() + RA.bracket(), (-1,0,0), step=1.0, limit=60))
EOF
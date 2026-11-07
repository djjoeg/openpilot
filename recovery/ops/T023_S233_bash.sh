cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/margin.py << 'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import wheelparts as WP, mountparts as MP, assembly as AS
t = WP.Teeth()
parts = {"teeth": WP.teeth_one_piece(t, WP.teeth_solid(t)), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(), "clamp": MP.dash_clamp()}
fit = AS.solve(t)
A = AS.Assembly(t, fit, parts)
T = A.teeth()
lift = MP.cam_lift(MP.A_OFF)
# how far could the lifted gear move back towards the teeth (straight down, -y) before touching?
G = A.gear(lift)
lo, hi = 0.0, 20.0
for _ in range(30):
  mid = (lo + hi) / 2
  if AS.overlap(G.translate((0, -mid, 0)), T) > 1e-3: hi = mid
  else: lo = mid
print("lever up: lift %.2f deg; the motor gear is %.2f mm clear of the steering wheel teeth (straight down)" % (lift, lo))
# with the wheel turned (teeth anywhere under), and the gear teeth only vs the teeth's tips
for ang in (0, 10, 20, 29):
  Tt = A.teeth(ang)
  lo, hi = 0.0, 20.0
  for _ in range(30):
    mid = (lo + hi) / 2
    if AS.overlap(G.translate((0, -mid, 0)), Tt) > 1e-3: hi = mid
    else: lo = mid
  print("   steering wheel at %2d deg: %.2f mm" % (ang, lo))
# finger guard and carrier clearances to the steering wheel when the carrier is dropped
rest = A.rest_on_grip_lift()
print("wheel turned past the teeth: carrier drops %.2f deg" % -rest)
W = A.wheel_grip()
for name, m in (("carrier", A.carrier(rest)), ("motor gear teeth", AS.turn_about_x(A.p["gear_teeth_only"].translate(tuple(A.b_org)), -rest, A.hinge_w))):
  lo, hi = 0.0, 20.0
  for _ in range(30):
    mid = (lo + hi) / 2
    if AS.overlap(m.translate((0, -mid, 0)), W) > 1e-3: hi = mid
    else: lo = mid
  print("   %s is %.2f mm above the part of the steering wheel you hold" % (name, lo))
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/margin.py
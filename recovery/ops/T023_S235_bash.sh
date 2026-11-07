sed -i '/^STOP_DEG = 11.0/d' mountparts.py && grep -n "STOP_DEG" mountparts.py assembly.py; cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/side.py << 'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import wheelparts as WP, mountparts as MP, assembly as AS, render as R
t = WP.Teeth()
parts = {"teeth": WP.teeth_one_piece(t, WP.teeth_solid(t)), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(), "clamp": MP.dash_clamp()}
up = float(sys.argv[1]) if len(sys.argv) > 1 else 105.0
fwd = float(sys.argv[2]) if len(sys.argv) > 2 else 175.0
fit = AS.solve(t, up, fwd)
A = AS.Assembly(t, fit, parts)
grey, blue, orange, green, red, brown, teal, dark = (.72,.72,.72), (.35,.55,.85), (.95,.6,.25), (.45,.75,.45), (.85,.3,.3), (.6,.5,.4), (.5,.7,.7), (.25,.25,.25)
def scene(lift=0.0, alpha=0.0, wheel=0.0):
  return [(A.teeth(wheel), grey), (A.wheel_grip(), (.3,.3,.3)), (A.gear(lift), orange), (A.carrier(lift), blue), (A.motor(lift), dark),
          (A.hinge_block(), green), (A.lever(alpha), red), (A.switch(), (.9,.85,.2)), (A.arm(), brown), (A.clamp(), teal), (A.hood(), (.85,.85,.75))]
# side view in the car: rotate the view so car-up is up on screen
side = R.look((1, 0, 0), A.up)
lift = MP.cam_lift(MP.A_OFF)
out = "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/side.png"
R.save(out, [(scene(), side), (scene(lift, MP.A_OFF), side), (scene(-MP.DROP_DEG, 0, 70), side)],
       ["lever down: motor gear on the teeth", "lever up: motor gear lifted %.1f deg" % lift, "steering wheel turned 70 deg"], size=(700, 760))
print(fit)
EOF
PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/side.py
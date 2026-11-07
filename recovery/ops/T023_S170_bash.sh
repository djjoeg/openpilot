cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/side.py << 'EOF'
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import wheelparts as WP
import mountparts as MP
import assembly as AS
import render as R

t = WP.Teeth()
whole = WP.teeth_solid(t)
parts = {
  "teeth": WP.teeth_one_piece(t, whole), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
  "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(),
  "slider": MP.arm_slider(), "arm": MP.arm(), "clamp": MP.dash_clamp(),
}
fit = AS.solve(t)
print(fit)
A = AS.Assembly(t, fit, parts)
grey, blue, orange, green, red, purple, brown = (.7,.7,.7), (.35,.55,.85), (.95,.6,.25), (.45,.75,.45), (.85,.3,.3), (.6,.45,.8), (.6,.5,.4)
def scene(lift=0.0, off=False):
  return [(A.teeth(), grey), (A.wheel_grip(), (.3,.3,.3)), (A.gear(lift), orange), (A.carrier(lift), blue), (A.motor(lift), (.25,.25,.25)),
          (A.hinge_block(), green), (A.lever(off), red), (A.slider(), purple), (A.arm(), brown), (A.clamp(), (.5,.7,.7)), (A.hood(), (.85,.85,.75))]
side = R.look((1, 0, 0), (0, 1, 0))   # looking from the driver's right side
out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/side.png"
R.save(out, [(scene(), side), (scene(MP.LIFT_DEG, True), side)], ["motor gear on the teeth", "lifted"], size=(900, 800))
print("saved", out)
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/side.py
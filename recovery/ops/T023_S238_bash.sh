cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/close.py << 'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import wheelparts as WP, mountparts as MP, assembly as AS, render as R
from cadlib import box
t = WP.Teeth()
parts = {"teeth": WP.teeth_one_piece(t, WP.teeth_solid(t)), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(), "clamp": MP.dash_clamp()}
fit = AS.solve(t)
A = AS.Assembly(t, fit, parts)
# crop: only things near the motor
crop = box(-200, 200, A.b_org[1] - 60, A.b_org[1] + 110, A.b_org[2] - 130, A.b_org[2] + 45)
grey, blue, orange, green, red, brown, dark = (.72,.72,.72), (.35,.55,.85), (.95,.6,.25), (.45,.75,.45), (.85,.3,.3), (.6,.5,.4), (.25,.25,.25)
def scene(lift=0.0, alpha=0.0, cut_x=None):
  items = [(A.teeth(), grey), (A.gear(lift), orange), (A.carrier(lift), blue), (A.motor(lift), dark),
           (A.hinge_block(), green), (A.lever(alpha), red), (A.switch(), (.9,.85,.2)), (A.arm(), brown)]
  out = []
  for m, c in items:
    m = m ^ crop
    if cut_x is not None:
      m = m ^ box(-300, cut_x, -1000, 1000, -1000, 1000)
    out.append((m, c))
  return out
side = R.look((1, 0, 0), A.up)
iso = R.look((1.0, 0.8, 0.9), A.up)
lift = MP.cam_lift(MP.A_OFF)
R.save("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/close.png",
       [(scene(cut_x=0.0), side), (scene(lift, MP.A_OFF, cut_x=0.0), side)],
       ["lever down (cut through the middle)", "lever up (cut through the middle)"], size=(900, 760))
R.save("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/iso.png",
       [(scene(), iso), (scene(lift, MP.A_OFF), iso)], ["lever down", "lever up"], size=(900, 760))
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/close.py
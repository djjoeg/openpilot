cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/diag2.py << 'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import wheelparts as WP, mountparts as MP, assembly as AS
t = WP.Teeth()
parts = {"teeth": WP.teeth_one_piece(t, WP.teeth_solid(t)), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(),
         "slider": MP.arm_slider(), "arm": MP.arm(), "clamp": MP.dash_clamp()}
fit = AS.solve(t)
A = AS.Assembly(t, fit, parts)
def bb(m, org):
  x0, y0, z0, x1, y1, z1 = m.bounding_box()
  return "x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f" % (x0 - org[0], x1 - org[0], y0 - org[1], y1 - org[1], z0 - org[2], z1 - org[2])
org = A.b_org
i = A.hinge_block() ^ A.arm()
print("hinge block/arm", i.volume(), bb(i, org))
lift = MP.cam_lift(MP.A_OFF)
i = A.carrier(lift) ^ A.arm()
print("lifted carrier/arm", i.volume(), bb(i, org))
for a in np.arange(80, 105, 1.0):
  v = AS.overlap(A.lever(a), A.hinge_block())
  if v > 1e-3:
    i = A.lever(a) ^ A.hinge_block()
    print("lever at %.0f: %.3f  %s" % (a, v, bb(i, org)))
print("arm end along arm: slider at %.1f..%.1f, arm length %.0f" % (fit.slider_pos, fit.slider_pos + MP.SLIDER_LEN, 190))
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/diag2.py
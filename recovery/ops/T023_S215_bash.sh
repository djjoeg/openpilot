cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/protrude.py << 'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import wheelparts as WP, mountparts as MP, assembly as AS
t = WP.Teeth()
parts = {"teeth": WP.teeth_one_piece(t, WP.teeth_solid(t)), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(),
         "slider": MP.arm_slider(), "arm": MP.arm(), "clamp": MP.dash_clamp()}
for up, fwd in [(105, 175), (60, 175), (150, 175), (105, 120), (105, 250), (60, 120), (150, 250)]:
  fit = AS.solve(t, up, fwd)
  end = fit.slider_pos + MP.SLIDER_LEN
  out = []
  for p in (0, 10, 20, 30, 40):
    L = end + p
    parts["arm"] = MP.arm(L, (55.0, L - 15.0))
    A = AS.Assembly(t, fit, parts)
    lift = MP.cam_lift(MP.A_OFF)
    v1 = AS.overlap(A.carrier(lift), A.arm()) + AS.overlap(A.carrier(MP.STOP_DEG), A.arm())
    v2 = AS.overlap(A.hinge_block(), A.arm())
    v3 = AS.overlap(A.lever(MP.A_OFF), A.arm())
    out.append("%d:%s" % (p, "ok" if max(v1, v2, v3) < 1e-3 else "hit(%.0f/%.1f/%.0f)" % (v1, v2, v3)))
  print("up %3d fwd %3d  arm %.1f deg (to column), %.1f below level, slider %.0f, joint %.0f  %s | %s" %
        (up, fwd, fit.arm_deg, fit.arm_below_level, fit.slider_pos, fit.joint_deg, "ok" if fit.ok else fit.notes, " ".join(out)))
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/protrude.py
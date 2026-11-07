cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2/dbg_arm.py <<'EOF'
import sys, dataclasses, numpy as np
sys.path.insert(0, '/home/claude/deliver/hardware/cad')
import params as P
import assembly as AS, mountparts as MP, wheelparts as WP
t = WP.Teeth()
base = {"teeth": WP.teeth_one_piece(t), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
        "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "bracket": MP.lever_bracket(),
        "lever": MP.lift_lever(), "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "clamp": MP.dash_clamp()}
up, fwd = float(sys.argv[1]), float(sys.argv[2])
for tl in (P.COLUMN_TILT_RANGE[0], P.COLUMN_TILT, P.COLUMN_TILT_RANGE[1]):
  sol = AS.solve(t, up, fwd, tl)
  L = min(P.ARM_LENGTHS, key=lambda L: abs(sol.reach - L))
  g = dataclasses.replace(sol, ok=True, arm_len=float(L), slide=sol.reach - L, notes=[])
  A = AS.Assembly(t, g, dict(base), tl)
  AR = A.arm()
  print(f"tilt {tl}: arm {sol.arm_deg:.1f} deg to column, reach {sol.reach:.1f}, arm {L}")
  for a in list(np.arange(0, MP.A_OFF + 0.1, 4.0)) + [MP.A_OFF]:
    th = max(0.0, MP.cam_lift(a)) + 0.05
    o = A.lever(a, th, part="lever_no_tab") ^ AR
    if o.volume() > 1e-3:
      bb = [round(v, 1) for v in o.bounding_box()]
      print("   alpha", a, "overlap", round(o.volume(), 3), bb)
EOF
PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2/dbg_arm.py 105 175
cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/tiltgrid.py <<'EOF'
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import params as P
import assembly as AS, mountparts as MP, wheelparts as WP
t = WP.Teeth(P.WHEEL_OD, P.GRIP)
whole = WP.teeth_solid(t)
base = {"teeth": WP.teeth_one_piece(t, whole), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
        "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(), "clamp": MP.dash_clamp()}
arms = {L: MP.arm(L) for L in P.ARM_LENGTHS}
tilts = (P.COLUMN_TILT_RANGE[0], P.COLUMN_TILT, P.COLUMN_TILT_RANGE[1])
t0 = time.time()
def ok_with(u, f, tilt, L):
  g = AS.solve(t, u, f, tilt)
  if abs(g.reach - L) > P.ARM_SLIDE - 0.5:
    return None
  angle_notes = [n for n in g.notes if "arms cover" not in n]
  if angle_notes:
    return False
  g.arm_len = float(L); g.slide = g.reach - L; g.ok = True; g.notes = []
  assy = dict(base); assy["arm"] = arms[L]
  res = AS.check_all(AS.Assembly(t, g, assy, tilt), lever_step=8.0)
  bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
  return not bad
for u in [40, 60, 80, 105, 130, 160]:
  row = []
  for f in [80, 110, 140, 175, 210, 250]:
    reaches = [AS.solve(t, u, f, tl).reach for tl in tilts]
    cands = [L for L in P.ARM_LENGTHS if any(abs(r - L) <= P.ARM_SLIDE - 0.5 for r in reaches)]
    per = {L: [ok_with(u, f, tl, L) for tl in tilts] for L in cands}
    allt = [L for L, v in per.items() if all(x is True for x in v)]
    row.append((u, f, [round(r) for r in reaches], allt, {L: v for L, v in per.items()}))
  for cell in row:
    print(cell)
print("seconds", round(time.time() - t0))
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/tiltgrid.py 2>&1 | tail -45
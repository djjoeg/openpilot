cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/grid.py << 'EOF'
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import wheelparts as WP, mountparts as MP, assembly as AS
t = WP.Teeth()
base = {"teeth": WP.teeth_one_piece(t, WP.teeth_solid(t)), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
        "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(), "clamp": MP.dash_clamp()}
arms = {}
ups = [40, 60, 80, 105, 130, 160]
fwds = [80, 110, 140, 175, 210, 250]
print("rows: up (mm above the motor gear's centre); columns: forward (mm ahead of it). cell: arm length or the problem")
print("      " + "".join("%14d" % f for f in fwds))
for u in ups:
  line = "%5d " % u
  for f in fwds:
    fit = AS.solve(t, u, f)
    if not fit.ok:
      msg = fit.notes[0]
      cell = "joint" if "joint" in msg else ("clamp" if "dash clamp covers" in msg else "reach %.0f" % fit.reach)
      line += "%14s" % cell
      continue
    parts = dict(base)
    L = fit.arm_len
    if L not in arms:
      arms[L] = MP.arm(L)
    parts["arm"] = arms[L]
    A = AS.Assembly(t, fit, parts)
    res = AS.check_all(A, lever_step=8.0)
    bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
    if bad:
      cell = "X:" + bad[0].split(": ")[-1][:10]
    else:
      cell = "ok %d (%.0f)" % (L, fit.arm_deg)
    line += "%14s" % cell
  print(line, flush=True)
EOF
cd /home/claude/deliver/hardware/cad && time PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/grid.py
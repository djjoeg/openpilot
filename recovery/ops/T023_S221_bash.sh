cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py << 'EOF'
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import wheelparts as WP
import mountparts as MP
import assembly as AS

t0 = time.time()
t = WP.Teeth()
whole = WP.teeth_solid(t)
parts = {
  "teeth": WP.teeth_one_piece(t, whole), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
  "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(), "clamp": MP.dash_clamp(),
}
up = float(sys.argv[1]) if len(sys.argv) > 1 else 105.0
fwd = float(sys.argv[2]) if len(sys.argv) > 2 else 175.0
fit = AS.solve(t, up, fwd)
print(fit)
A = AS.Assembly(t, fit, parts)
for k, v in parts.items():
  print("%-16s vol %9.0f  pieces %d  genus %d" % (k, v.volume(), len(v.decompose()), v.genus()))
res = AS.check_all(A)
bad = 0
for k, v in res.items():
  flag = ""
  if "should touch" in k:
    flag = "   <-- NOT STOPPING" if v > -1e-3 else ""
  elif v > 1e-3:
    flag = "   <-- TOUCHING"
  if flag: bad += 1
  print("%10.3f  %s%s" % (v, k, flag))
print("problems:", bad, " time %.1f s" % (time.time() - t0))
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py
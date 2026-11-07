sed -i 's/bare steering wheel, or the tail meets the lift lever.s cam first (DROP_DEG), whichever comes first./bare steering wheel, or the fin meets the lift lever'"'"'s cam first (DROP_DEG), whichever comes first./' assembly.py && sed -n 150,175p assembly.py && cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py << 'EOF'
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
  "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(),
  "slider": MP.arm_slider(), "arm": MP.arm(), "clamp": MP.dash_clamp(),
}
for k, v in parts.items():
  print("%-16s vol %9.0f  pieces %d  genus %d" % (k, v.volume(), len(v.decompose()), v.genus()))
fit = AS.solve(t)
print(fit)
A = AS.Assembly(t, fit, parts)
res = AS.check_all(A)
bad = 0
for k, v in res.items():
  flag = "   <-- TOUCHING" if v > 1e-3 else ""
  if v > 1e-3: bad += 1
  print("%10.3f  %s%s" % (v, k, flag))
print("touching:", bad, " time %.1f s" % (time.time() - t0))
EOF
PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py
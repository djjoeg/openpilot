mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork && cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/diag.py << 'EOF'
import sys, time, importlib
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import wheelparts as WP
import mountparts as MP
import assembly as AS

t0 = time.time()
t = WP.Teeth()
whole = WP.teeth_solid(t)
parts = {
  "teeth": WP.teeth_one_piece(t, whole),
  "gear": WP.motor_gear(),
  "gear_teeth_only": WP.motor_gear_teeth_only(),
  "carrier": MP.motor_carrier(),
  "hinge_block": MP.hinge_block(),
  "lever": MP.lift_lever(),
  "slider": MP.arm_slider(),
  "arm": MP.arm(),
  "clamp": MP.dash_clamp(),
}
print("built in %.1f s" % (time.time() - t0))
fit = AS.solve(t)
print(fit)
A = AS.Assembly(t, fit, parts)

def bb(m):
  x0, y0, z0, x1, y1, z1 = m.bounding_box()
  return "x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % (x0, x1, y0, y1, z0, z1)

def show(name, a, b, org=None):
  i = a ^ b
  v = i.volume()
  print(f"{name}: {v:.3f} mm3")
  if v > 1e-3:
    if org is not None:
      i = i.translate(tuple(-np.asarray(org)))
    for c in i.decompose():
      if c.volume() > 1e-3:
        print("   piece %.3f  %s" % (c.volume(), bb(c)))

org = A.b_org
show("carrier/hinge block (carrier frame)", A.carrier(), A.hinge_block(), org)
show("carrier/lever on (carrier frame)", A.carrier(), A.lever(), org)
show("lifted carrier/lever off (carrier frame)", A.carrier(MP.LIFT_DEG), A.lever(off=True), org)
EOF
cd /home/claude/deliver/hardware/cad && time python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/diag.py
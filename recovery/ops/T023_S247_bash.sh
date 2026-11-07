cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/diag4.py << 'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import wheelparts as WP, mountparts as MP, assembly as AS
t = WP.Teeth()
parts = {"teeth": WP.teeth_one_piece(t, WP.teeth_solid(t)), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "lever": MP.lift_lever(), "clamp": MP.dash_clamp()}
fit = AS.solve(t)
A = AS.Assembly(t, fit, parts)
org = A.b_org
def bb(m):
  x0, y0, z0, x1, y1, z1 = m.bounding_box()
  return "x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f" % (x0 - org[0], x1 - org[0], y0 - org[1], y1 - org[1], z0 - org[2], z1 - org[2])
for th in (0, 2, 4, 6, 8, 10, 10.3, -3):
  i = A.carrier(th) ^ A.hinge_block()
  if i.volume() > 1e-3:
    for c in i.decompose():
      if c.volume() > 1e-4: print("lift %.1f: %.3f %s" % (th, c.volume(), bb(c)))
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/diag4.py
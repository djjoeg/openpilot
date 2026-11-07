cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/diag3.py << 'EOF'
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
def show(name, a, b):
  i = a ^ b
  if i.volume() > 1e-3:
    for c in i.decompose():
      if c.volume() > 1e-3:
        print(name, "%.3f" % c.volume(), bb(c))
show("carrier/switch", A.carrier(), A.switch())
show("dropped carrier/switch", A.carrier(-3), A.switch())
lift = MP.cam_lift(MP.A_OFF)
show("lifted carrier/hb", A.carrier(lift), A.hinge_block())
for a in np.arange(4, 60, 4):
  show("lever %d/hb" % a, A.lever(a), A.hinge_block())
  th = max(0, MP.cam_lift(a)) + 0.05
  show("carrier at lever %d (%.2f deg)/hb" % (a, th), A.carrier(th), A.hinge_block())
print("switch box", bb(A.switch()))
print("carrier tail z range", MP.LEVER_PIVOT[1] - MP.FIN_LEN/2 - 2, "fin top", MP.FIN_TOP)
print("stop bar corner", MP.stop_bar_corner())
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/diag3.py
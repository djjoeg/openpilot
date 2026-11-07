python3 - << 'EOF'
p = "accord_lka_parts.py"
s = open(p).read()
a = """def support_area(m, max_angle: float = 46.0):
  \"\"\"Area (mm^2) of downward faces more than max_angle from upright that are not on the bed (faces at exactly 45
  degrees print fine and are not counted), and the bed area.\"\"\""""
b = """def support_area(m, max_angle: float = 45.0):
  \"\"\"Area (mm^2) of downward faces leaning more than max_angle from upright that are not on the bed (faces at
  exactly 45 degrees print fine and are not counted), and the bed area.\"\"\""""
assert a in s; s = s.replace(a, b)
a = """  steep = (nz < -math.cos(math.radians(max_angle))) & (zmin > 0.3)"""
b = """  steep = (nz < -math.cos(math.radians(max_angle)) - 0.01) & (zmin > 0.3)"""
assert a in s; s = s.replace(a, b)
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sys, math, numpy as np
import accord_lka_parts as B
import wheelparts as WP, mountparts as MP
from cadlib import on_bed
t = WP.Teeth()
for name, m, r in [('grip test', WP.grip_fit_test(t), (180,0,0)), ('one piece', WP.teeth_one_piece(t), (180,0,0)), ('left', WP.teeth_half(t,'left'), (180,0,0)), ('gear', WP.motor_gear(), (180,0,0)), ('carrier', MP.motor_carrier(), (180,0,0)), ('hinge', MP.hinge_block(), (180,0,0)), ('clamp', MP.dash_clamp(), (0,90,0))]:
  print(name, round(B.support_area(on_bed(m, r))[0]))
"
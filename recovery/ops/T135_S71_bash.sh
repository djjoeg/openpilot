python3 - <<'EOF'
s = open('popparts.py').read()
old = """  post = box(POST_X[0], POST_X[1], y0 - FP.PL_RIB_H, PLATE_FLANGE_XY[2][1] - dy, fz0, fz1 + 6.0)
  gusset = prism_x([(y0, fz1 + 6.0), (y0, fz1 + 26.0), (y0 + 20.0, fz1 + 6.0)], POST_X[0], POST_X[1])"""
new = """  post = box(POST_X[0], POST_X[1], y0 - FP.PL_RIB_H, PLATE_FLANGE_XY[2][1] - dy, fz0 - 6.0, fz1)
  gusset = prism_x([(y0, fz0 - 6.0), (y0, fz0 - 30.0), (y0 + 24.0, fz0 - 6.0)], POST_X[0], POST_X[1])"""
assert old in s
s = s.replace(old, new)
s = s.replace("""    part = part - Manifold.batch_hull([cyl(M5_CLEAR / 2, fz0 - 1, fz1 + 7, bx, by - dy + s, 32) for s in (-SLOT_Y, SLOT_Y)])""",
"""    part = part - Manifold.batch_hull([cyl(M5_CLEAR / 2, fz0 - 7, fz1 + 1, bx, by - dy + s, 32) for s in (-SLOT_Y, SLOT_Y)])""")
open('popparts.py', 'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import popparts as PP, numpy as np
b = PP.pop_hinge_block(); p = PP.pop_column_plate()
bw = PP.to_wheel(b)
x = bw ^ p
print('block/plate overlap', round(x.volume(),2), [round(v,1) for v in x.bounding_box()] if x.volume() > 0 else '')
"

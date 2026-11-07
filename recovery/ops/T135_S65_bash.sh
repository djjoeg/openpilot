python3 - <<'EOF'
s = open('popparts.py').read()
old = """  for cz_c in (-62.0, -40.0):
    for cx_c in (-CHEEK_X[1], -CHEEK_X[0]):"""
new = """  for cz_c in (-64.0, -53.0):          # kept towards the column of the hinge: the carrier swings over the other side
    for cx_c in (-CHEEK_X[1], -CHEEK_X[0] - 0.6):"""
assert old in s
s = s.replace(old, new)
s = s.replace("""  strip_cs = CrossSection.batch_hull([CrossSection.circle(1.0, 8).translate(p) for p in cheek_strip])""",
"""  strip_cs = CrossSection.batch_hull([CrossSection.square((0.01, 0.01)).translate(p) for p in cheek_strip])""")
open('popparts.py', 'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import popparts as PP, numpy as np
from cadlib import union
b = PP.pop_hinge_block(); c = PP.pop_carrier(); mb = PP.motor_and_board(); m = mb['body'] + mb['board'] + mb['plugs']
g = PP.pop_motor_gear()
print('block vol', round(b.volume()), [round(v,1) for v in b.bounding_box()], 'genus', b.genus(), 'pieces', len(b.decompose()))
worst = {}
for L in [-3.0] + list(np.arange(-2.5, 75.01, 2.5)):
  for name, part in (('carrier', c), ('motor', m), ('gear', g)):
    v = (PP.swung(part, L) ^ b).volume()
    if v > 1e-3: worst.setdefault(name, []).append((round(float(L),1), round(v,2)))
  sp = PP.spring_solid(L)
  for name, part in (('block', b), ('carrier', PP.swung(c, L)), ('motor', PP.swung(m, L))):
    v = (sp ^ part).volume()
    if v > 1e-3: worst.setdefault('springs/'+name, []).append((round(float(L),1), round(v,2)))
print(worst)
"

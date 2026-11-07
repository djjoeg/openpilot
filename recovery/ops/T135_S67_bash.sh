python3 - <<'EOF'
s = open('popparts.py').read()
# pads through the knuckles' length so they are one with them
old = """  for b0, b1 in (PARK_PAD, DROP_PAD):
    pad = _sector_yz(PAD_R[0], PAD_R[1], b0, b1, 0.5)
    for s0, s1 in ((WEB_X[0], BLOCK_KNUCKLE_X[0] + 0.01), (-BLOCK_KNUCKLE_X[0] - 0.01, -WEB_X[0])):
      parts.append(extrude_x(pad, s0, s1))"""
new = """  for b0, b1 in (PARK_PAD, DROP_PAD):
    pad = _sector_yz(BLOCK_KNUCKLE_R - 1.0, PAD_R[1], b0, b1, 0.5)
    for s0, s1 in ((WEB_X[0], BLOCK_KNUCKLE_X[1]), (-BLOCK_KNUCKLE_X[1], -WEB_X[0])):
      parts.append(extrude_x(pad, s0, s1))"""
assert old in s
s = s.replace(old, new)
s = s.replace("""J2_M = (85.0, 45.0, -118.0)   # the arm's joint on the hinge block (mount frame): above the motor's side, behind it""",
"""J2_M = (66.0, -30.0, -125.0)  # the arm's joint on the hinge block (mount frame): below the block, behind the springs
J2_TIE = ((15.4, -86.0), (25.5, -86.0), (15.4, -70.0), (25.5, -70.0))   # carrier (x, z): where its ears join the block""")
old2 = s[s.index("  # the near cheek's outer face in the wheel frame"):s.index("  ears = [FP.ear_plate(j2[:2]")]
new2 = """  # the ears are tied to the block's lower cheek by a post (carrier x, z from J2_TIE, the full height between the ears)
  Rm, _ = mount_to_wheel()
  tie = []
  for cx_c, cz_c in J2_TIE:
    pw = Rm @ carrier_to_mount_pt((cx_c, 0.0, cz_c))
    tie.append((float(pw[0]), float(pw[1])))
  strip_cs = CrossSection([tie[:2] + tie[2:][::-1]])
  strip_cs = strip_cs if strip_cs.area() > 0 else CrossSection([(tie[:2] + tie[2:][::-1])[::-1]])
"""
s = s.replace(old2, new2)
open('popparts.py', 'w').write(s)
EOF
grep -n "web = strip_cs" -B2 -A3 popparts.py; PYTHONPATH=/home/claude/pylib python3 -c "
import popparts as PP, numpy as np
b = PP.pop_hinge_block(); c = PP.pop_carrier(); mb = PP.motor_and_board(); m = mb['body'] + mb['board'] + mb['plugs']
g = PP.pop_motor_gear()
print('j2 wheel', PP.j2_wheel().round(1), 'arm reach to J1', round(float(np.linalg.norm(PP.j2_wheel()[:2] - np.array(PP.FP.J1_W))),1))
print('block vol', round(b.volume()), [round(v,1) for v in b.bounding_box()], 'genus', b.genus(), 'pieces', [round(p.volume()) for p in b.decompose()])
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

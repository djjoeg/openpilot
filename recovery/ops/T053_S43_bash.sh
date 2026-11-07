python3 - <<'EOF'
p = "mountparts.py"
s = open(p).read()
old = '''  ears = [extrude_x(ear_cs, EAR_X[0], EAR_X[1]), extrude_x(ear_cs, -EAR_X[1], -EAR_X[0])]
  part = union([body] + kn + ears)
'''
new = '''  ears = [extrude_x(ear_cs, EAR_X[0], EAR_X[1]), extrude_x(ear_cs, -EAR_X[1], -EAR_X[0])]
  part = union([body] + kn + ears)
  # room in the ears for bolts that go in from the sides: the hinge bolt's head and nut (the ears reach out past the
  # knuckles), and the lift lever's bolt, which goes in through the ears' front corner above the block (cut back at
  # 45 degrees so the ears still print without supports there), with room for a socket on its nut
  for sgn in (-1, 1):
    x0, x1 = (BLOCK_KNUCKLE[1], 60.0) if sgn > 0 else (-60.0, -BLOCK_KNUCKLE[1])
    part = part - cyl_x(EAR_HINGE_ROOM, x0, x1, y=hy, z=hz, segments=48)
    ex0, ex1 = (EAR_X[0] - 0.01, EAR_X[1] + 1.0) if sgn > 0 else (-EAR_X[1] - 1.0, -EAR_X[0] + 0.01)
    y0, y1 = HB_TOP + 0.5, EAR_CUT_TOP
    part = part - prism_x([(y0, HB_FRONT + 1.0), (y0, EAR_CUT_Z), (y1, EAR_CUT_Z - (y1 - y0)), (y1, HB_FRONT + 1.0)], ex0, ex1)
'''
assert s.count(old) == 1
s = s.replace(old, new)
old_c = '''EAR_X = (ARM_W / 2 + GAP, ARM_W / 2 + GAP + 6.0)   # ears either side of the arm's end
'''
new_c = '''EAR_X = (ARM_W / 2 + GAP, ARM_W / 2 + GAP + 6.0)   # ears either side of the arm's end
EAR_HINGE_ROOM = 5.6         # the ears are cut back round the hinge bolt's axis: room for its head, nut or a washer
EAR_CUT_Z, EAR_CUT_TOP = -4.0, 72.0   # the ears' front corner above the block is cut away (45 degrees from here up to
                                      # this height) so the lift lever's bolt goes in from the side
'''
assert s.count(old_c) == 1
s = s.replace(old_c, new_c)
open(p, "w").write(s)
EOF
grep -n "prism_x" mountparts.py | head -3; PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import math, sys
sys.path.insert(0, '.')
import mountparts as MP
from cadlib import cyl_x, union
HB = MP.hinge_block()
print("hinge block volume", round(HB.volume()), "genus", HB.genus())
hy, hz = MP.HINGE
k = MP.BLOCK_KNUCKLE[1]
def ring(y, z, xa, xb, r, seg=32): return cyl_x(r, xa, xb, y=y, z=z, segments=seg)
hw = union([ring(hy, hz, -k - 1.0 - 5.0, -k - 1.0, 4.25), ring(hy, hz, -k - 1.0, -k, 5.0), ring(hy, hz, k, k + 1.0, 5.0),
            ring(hy, hz, k + 1.0, k + 6.2, 8.0 / 2 / math.cos(math.pi / 6), 6)])
print("hinge bolt head, washers, nut vs hinge block:", round((HB ^ hw).volume(), 4))
LB = MP.lever_bolt()
print("lever bolt vs hinge block (lever down):", round((HB ^ LB).volume(), 4))
y, z = MP.LEVER_PIVOT
sock = cyl_x(6.0, MP.BR_LEG_X[1] + MP.M4_WASHER_T, 45.0, y=y, z=z, segments=32)
print("7 mm socket on the lever nut vs hinge block:", round((HB ^ sock).volume(), 4))
key = cyl_x(1.6, -45.0, -MP.BR_LEG_X[1] - MP.M4_WASHER_T - 4.0, y=y, z=z, segments=16)
print("hex key into the lever bolt head vs hinge block:", round((HB ^ key).volume(), 4))
EOF
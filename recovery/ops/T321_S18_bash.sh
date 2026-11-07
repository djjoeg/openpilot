python3 - <<'EOF'
p = 'rightarm.py'
s = open(p, encoding='utf-8').read()
reps = [
("""SLIDE_NUT_U = (213.6, 218.0)     # the nut's slot in the bar: 3 mm of bar outside it, the bolt's end 1 mm past the nut""",
 """SLIDE_NUT_U = (213.6, 218.0)     # the nut's slot in the bar: 3 mm of bar outside it, the bolt's end 1 mm past the nut
SLIDE_NUT_W = M5_NUT_AF + 0.3    # the slot across the nut's flats, 8.3: even the smallest standard nut can't turn in it"""),
("""  tw, tt = NUT_TRAP                                             # 8.4 along the bar (the flats), 4.4 thick
  m = m - uvz(SLIDE_NUT_U[0], SLIDE_NUT_U[1], bv - M5_NUT_AF / 2 / math.cos(math.radians(30)) - 0.25, BAR_V[1] + 1.0,
              SLIDE_Z0 - tw / 2, SLIDE_Z0 + tw / 2)""",
 """  # the nut's slot: dropped in from the motor's side, flats along the bar; its bottom the nut's own shape, a corner
  # down, so the nut sits centred on the bolt's line
  w = SLIDE_NUT_W
  r = w / math.sqrt(3)                                           # the hex pocket's corner radius
  hexp = CrossSection([[(0.0 + r * math.cos(math.radians(90 + 60 * i)), bv + r * math.sin(math.radians(90 + 60 * i)))
                        for i in range(6)]])                    # in (z, v), a corner along -v; then along u
  pocket = hexp.extrude(SLIDE_NUT_U[1] - SLIDE_NUT_U[0]).rotate((0.0, 90.0, 0.0))     # extrusion z -> x (u)
  pocket = pocket.translate((SLIDE_NUT_U[1], 0.0, SLIDE_Z0))
  m = m - (pocket + box(SLIDE_NUT_U[0], SLIDE_NUT_U[1], bv, BAR_V[1] + 1.0, SLIDE_Z0 - w / 2, SLIDE_Z0 + w / 2)).rotate(
    (0.0, 0.0, THETA))"""),
("""from manifold3d import Manifold""", """from manifold3d import CrossSection, Manifold"""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
p = 'rightcheck.py'
s = open(p, encoding='utf-8').read()
a = """  rn = RA.plate_to_wheel(nut_min(30.0).rotate((90.0, 0.0, 0.0)).translate((RA.PINCH_X, yn, pz)))"""
b = """  rn = RA.plate_to_wheel(nut_min(0.0).rotate((90.0, 0.0, 0.0)).translate((RA.PINCH_X, yn, pz)))   # seated it's 30"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
EOF
PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
# where does the pocket sit? the slot's lowest point on the bar's middle line, and the nut's centre for real nut sizes
import math, numpy as np, rightarm as RA, rightcheck as RC
c = RA.carrier(0.0).rotate((0.0, 0.0, -RA.THETA))      # back into the motor frame: u along x, v along y
bu, bv = RA.BAR_UV
sl = c.slice(RA.SLIDE_Z0)                               # the cross-section across the bar at the bolt's height
pts = np.vstack([np.asarray(p) for p in sl.to_polygons()])
print("pocket corner radius", round(RA.SLIDE_NUT_W / math.sqrt(3), 3), "-> a nut of AF 8.0 sits", round(RA.SLIDE_NUT_W / math.sqrt(3) - 8.0 / math.sqrt(3), 3), "mm low; AF 7.78:", round(RA.SLIDE_NUT_W / math.sqrt(3) - 7.78 / math.sqrt(3), 3))
seat = RC.slide_nut(0.0)
print("seated nut / carrier overlap", round((seat ^ RA.carrier(0.0)).volume(), 3), "mm3")
turned = RC.slide_nut(0.0, small_turned=True)
print("smallest nut turned / carrier overlap", round((turned ^ RA.carrier(0.0)).volume(), 3), "mm3")
EOF
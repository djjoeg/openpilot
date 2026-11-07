cat >> columnparts.py <<'EOF'


# ***** side bracket (the right-side mount: tied round the column covers and screwed to the dash) *****
# Bracket frame: origin on the covers' right-hand surface at the column's height, in the middle of the bracket along
# the column; +x the driver's right (away from the column), +y up, +z towards the driver.

SB_PLATE_T = 8.0              # the saddle plate against the covers
SB_PLATE_Y = 25.0             # it spans y +-this ...
SB_PLATE_Z = (-45.0, 25.0)    # ... and this along the column
SB_FACE_R = 45.0              # its inside face is hollowed to this radius (the covers' side, taken as an oval 120 x 95)
SB_TIE_Y = 19.0               # zip tie slots through the plate at y +-this ...
SB_TIE_Z = (-35.0, 15.0)      # ... at these z: two ties round the covers
SB_NECK = 24.0                # the arm's bolt this far out from the plate's outer face (room for the arm's slot end)
SB_PIVOT = (SB_PLATE_T + SB_NECK, 0.0)      # the arm's bolt (x, z); it runs along y
SB_FORK_Y = MP.SIDE_PLATE_X                 # the fork's two plates, y range each side (the arm swings between them)
SB_ARM_ANGLES = (0.0, 60.0)                 # the arm from along the column (towards you) to 60 degrees outwards
SB_BAR_Y = (-30.4, -SB_FORK_Y[0])           # the bar to the screw: below the arm, level with the lower fork plate
SB_BAR_Z = (-25.0, 5.0)
SB_BAR_X1 = 68.0                            # the bar's end
SB_BAR_SLOT = (28.0, 60.0)                  # its slot for the screw tab's two M5 bolts (x range)
TAB_LENGTHS = (100.0, 160.0)                # screw tabs to print: bar length from its own slot start to the end plate
TAB_PLATE = (40.0, 70.0, 6.0)               # the end plate: wide (x), tall (y), thick (z)
TAB_PLATE_Z = (-16.0, -10.0)                # its faces (z): the back face bears on the dash's trim
TAB_SLOT_HALF = 25.0                        # the screw's slot, y +-this
SCREW_CLEAR = 5.5                           # the dash's screw passes through this


def side_bracket() -> Manifold:
  """The saddle plate with its zip tie slots, the arm's fork, and the start of the bar to the screw. Prints on its
  side with the bar down; tree supports under the upper fork plate."""
  y0, y1 = -SB_PLATE_Y, SB_PLATE_Y
  z0, z1 = SB_PLATE_Z
  plate = box(-12.0, SB_PLATE_T, y0, y1, z0, z1) - cyl(SB_FACE_R, z0 - 1, z1 + 1, x=-SB_FACE_R, segments=360)
  for y in (-SB_TIE_Y, SB_TIE_Y):
    for z in SB_TIE_Z:
      plate = plate - box(-20.0, SB_PLATE_T + 1.0, y - 1.2, y + 1.2, z - 2.9, z + 2.9)
  px, pz = SB_PIVOT
  r = MP.ARM_LOCK_R
  a0, a1 = SB_ARM_ANGLES[0] - 15.0, SB_ARM_ANGLES[1] + 15.0
  pts = [(px, pz)]
  for a in np.linspace(a0, a1, 41):
    pts.append((px + (r + 9.0) * math.sin(math.radians(a)), pz + (r + 9.0) * math.cos(math.radians(a))))
  pie = CrossSection([pts])
  if pie.area() < 1e-9:
    pie = CrossSection([pts[::-1]])
  # a fork plate's outline in (x, z); extruded along y with a transform mapping (u=x, v=z, w=y) -> (u, w, v)
  outline = CrossSection.batch_hull([pie, CrossSection.circle(10.0, 64).translate((px, pz)),
                                     CrossSection.square((1.0, z1 - z0)).translate((SB_PLATE_T - 0.01, z0))])

  def plate_y(cs, ya, yb):
    return cs.extrude(yb - ya).transform([[1, 0, 0, 0], [0, 0, 1, ya], [0, 1, 0, 0]])

  forks = [plate_y(outline, SB_FORK_Y[0], SB_FORK_Y[1]), plate_y(outline, -SB_FORK_Y[1], -SB_FORK_Y[0])]
  bar = box(SB_PLATE_T - 0.01, SB_BAR_X1, SB_BAR_Y[0], SB_BAR_Y[1] + 0.01, SB_BAR_Z[0], SB_BAR_Z[1])
  part = union([plate] + forks + [bar])
  part = part - cyl_y(M5_CLEAR / 2, -60, 60, x=px, z=pz, segments=32)        # the arm's bolt
  slot = [cyl_y(M5_CLEAR / 2, -60, 60, x=px + r * math.sin(math.radians(a)), z=pz + r * math.cos(math.radians(a)), segments=20)
          for a in np.linspace(SB_ARM_ANGLES[0], SB_ARM_ANGLES[1], 81)]
  part = part - union(slot)
  # the bar's slot for the tab's bolts
  sx0, sx1 = SB_BAR_SLOT
  zc = (SB_BAR_Z[0] + SB_BAR_Z[1]) / 2
  part = part - Manifold.batch_hull([cyl_y(M5_CLEAR / 2, -60, 60, x=sx0 + M5_CLEAR / 2, z=zc, segments=24),
                                     cyl_y(M5_CLEAR / 2, -60, 60, x=sx1 - M5_CLEAR / 2, z=zc, segments=24)])
  return clean(part)


def screw_tab(length: float) -> Manifold:
  """The bar from the side bracket to the dash's screw: its own slot overlaps the bracket's bar (two M5 bolts, so the
  length adjusts), and an end plate with a vertical slot for the screw, whose back face bears on the dash's trim.
  Bracket frame, the tab's slot start at x = 0; the assembly slides it along the bar. Prints with the bar flat and
  the end plate standing, no supports."""
  w, h, t = TAB_PLATE
  ya, yb = SB_BAR_Y[0] - (SB_BAR_Y[1] - SB_BAR_Y[0]), SB_BAR_Y[0]     # under the bracket's bar
  bar = box(0.0, length, ya, yb, SB_BAR_Z[0], SB_BAR_Z[1])
  zc = (SB_BAR_Z[0] + SB_BAR_Z[1]) / 2
  sx0, sx1 = 0.0, SB_BAR_SLOT[1] - SB_BAR_SLOT[0]
  bar = bar - Manifold.batch_hull([cyl_y(M5_CLEAR / 2, -60, 60, x=sx0 + M5_CLEAR / 2 + 3.0, z=zc, segments=24),
                                   cyl_y(M5_CLEAR / 2, -60, 60, x=sx1 - M5_CLEAR / 2 + 3.0, z=zc, segments=24)])
  plate = box(length - w, length, -h / 2, h / 2, TAB_PLATE_Z[0], TAB_PLATE_Z[1])
  plate = plate - Manifold.batch_hull([cyl(SCREW_CLEAR / 2, TAB_PLATE_Z[0] - 1, TAB_PLATE_Z[1] + 1, length - w / 2, -TAB_SLOT_HALF, 24),
                                       cyl(SCREW_CLEAR / 2, TAB_PLATE_Z[0] - 1, TAB_PLATE_Z[1] + 1, length - w / 2, TAB_SLOT_HALF, 24)])
  # a web from the bar up the plate's back, so the plate doesn't hinge on the bar
  web = box(length - w, length, ya, -h / 2 + 0.01, TAB_PLATE_Z[0], SB_BAR_Z[0] + 0.01)
  return clean(union([bar, plate, web]))


def bracket_fastener_rows() -> list:
  """The side bracket's bolts."""
  rows = []
  stack = 2 * SB_FORK_Y[1]
  spare = 60.0 - stack - 2 * MP.M5_WASHER_T - MP.M5_NYLOC_T
  rows.append({"bolt": "M5 x 60", "use": "arm to side bracket: both fork plates and the arm, a washer each side, lock nut",
               "length": 60.0, "through_mm": round(stack + 2 * MP.M5_WASHER_T, 1), "nut_mm": MP.M5_NYLOC_T,
               "past_the_nut_mm": round(spare, 1), "ok": spare >= 1.5})
  stack = (SB_BAR_Y[1] - SB_BAR_Y[0]) * 2
  spare = 35.0 - stack - 2 * MP.M5_WASHER_T - MP.M5_NYLOC_T
  rows.append({"bolt": "M5 x 35 (2)", "use": "screw tab to the bracket's bar (both slots), a washer each side, lock nut",
               "length": 35.0, "through_mm": round(stack + 2 * MP.M5_WASHER_T, 1), "nut_mm": MP.M5_NYLOC_T,
               "past_the_nut_mm": round(spare, 1), "ok": spare >= 1.5})
  rows.append({"bolt": "the dash's own screw, 6 mm longer", "use": "screw tab to the dash (through the tab's slot and a washer)",
               "length": 0.0, "needs_mm": [round(TAB_PLATE[2] + 1.0, 1), round(TAB_PLATE[2] + 1.0, 1)], "ok": True})
  return rows
EOF
PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import columnparts as CP, render as R
from cadlib import size_of, on_bed
sb = CP.side_bracket(); tab = CP.screw_tab(160.0); tab2 = CP.screw_tab(100.0)
for n, m in (("bracket", sb), ("tab160", tab), ("tab100", tab2)):
  print(n, len(m.decompose()), m.status(), [round(v,1) for v in m.bounding_box()], round(m.volume()/1000,1))
R.save("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/photo/bracket1.png",
       [([(sb,(.55,.7,.9))], R.look((1,0.8,0.9),(0,1,0))), ([(sb,(.55,.7,.9))], R.look((0,1,0),(0,0,1))), ([(tab,(.55,.7,.9))], R.look((1,0.8,0.9),(0,1,0)))],
       ["side bracket", "from above", "screw tab 160"], size=(700,600))
EOF
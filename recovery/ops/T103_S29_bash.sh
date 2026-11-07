python3 - <<'EOF'
import re
src = open('columnparts.py').read()
start = src.index('# ***** side bracket')
new = '''# ***** side bracket and screw tab (the right-side mount: tied to the column covers and screwed to the dash) *****
# Bracket frame: origin on the covers' right-hand surface at the column's height, at the bracket's reference place
# along the column (its back face is 25 mm behind it, level with the screw tab's plate against the dash);
# +x the driver's right (away from the column), +y up, +z towards the driver.

SB_PAD_T = PAD_T                            # two rubber strips between the plate and the covers (the clamp's strips)
SB_PAD_Y, SB_PAD_W = 12.0, 10.0             # the strips at y +-this, this wide, along the column
SB_PLATE_X = (SB_PAD_T, SB_PAD_T + 8.0)     # the plate: flat, 8 thick, outside the strips
SB_PLATE_Y = 35.0                           # it spans y +-this ...
SB_PLATE_Z = (-25.0, 45.0)                  # ... and this along the column: its back face level with the screw tab's plate
SB_TIE_Y = 20.0                             # zip tie slots through the plate at y +-this (a tie goes round the covers
SB_TIE_Z = (-17.0, -7.0, 3.0, 13.0, 23.0, 33.0)   # from an upper slot to the lower one), at every one of these z: use any
SB_NECK = 34.0                              # the arm's bolt this far out from the plate: room for the arm's slot end at
                                            # the biggest angle, slid fully towards the bracket
SB_PIVOT = (SB_PLATE_X[1] + SB_NECK, 0.0)   # the arm's bolt (x, z); it runs along y
SB_FORK_Y = MP.SIDE_PLATE_X                 # the fork's two plates, y range each side (the arm swings between them)
SB_ARM_ANGLES = (-10.0, 25.0)               # the arm from 10 degrees in (towards the column, going towards you) to 25 out
SB_BAR_Y = (-30.4, -SB_FORK_Y[0])           # the bar to the screw tab: under the arm, joined to the lower fork plate
SB_BAR_Z = (-25.0, 5.0)
SB_BAR_X1 = 92.0                            # the bar's end
SB_BAR_HOLES = (60.0, 80.0)                 # the screw tab's two M5 bolts through the bar, along y, at these x
SB_BOLT_Z = -15.0                           # ... and this z (the middle of the tab's bar)
TAB_LENGTHS = (100.0, 140.0, 180.0)         # screw tabs to print: bar length from the tab's start to the end plate
TAB_BAR_Y = (SB_BAR_Y[0] - 30.0, SB_BAR_Y[0])     # the tab's bar, under the bracket's bar: 30 tall ...
TAB_BAR_Z = (SB_BAR_Z[0], SB_BAR_Z[0] + 20.0)     # ... 20 deep, its back face level with the bracket's
TAB_SLOT = (3.0, 68.0)                      # the tab's slot for the bracket's two bolts, x range (tab frame)
TAB_PLATE = (40.0, 70.0, 6.0)               # the end plate: wide (x), tall (y), thick (z); its back face on the dash's trim
TAB_PLATE_Z = (TAB_BAR_Z[0], TAB_BAR_Z[0] + 6.0)
TAB_SLOT_HALF = 25.0                        # the screw's slot, y +-this around the plate's middle
TAB_SCREW_FROM_END = 20.0                   # the screw's slot this far from the tab's end
SCREW_CLEAR = 5.5                           # the dash's screw passes through this
TAB_PLATE_Y = -60.0                         # the end plate's middle below the column's axis, unless the screw is measured


def tab_slide_range() -> tuple[float, float]:
  """Where the tab's start (its x = 0) can sit along the bracket's bar: both of the bar's bolts in the tab's slot."""
  s0, s1 = TAB_SLOT[0] + M5_CLEAR / 2, TAB_SLOT[1] - M5_CLEAR / 2
  return (SB_BAR_HOLES[1] - s1, SB_BAR_HOLES[0] - s0)


def side_bracket() -> Manifold:
  """The flat plate against the covers (on two rubber strips) with zip tie slots all along it, the arm's fork, and the
  bar the screw tab bolts to. Prints standing on the plate's inner face, nothing needs supports."""
  x0, x1 = SB_PLATE_X
  y0, y1 = -SB_PLATE_Y, SB_PLATE_Y
  z0, z1 = SB_PLATE_Z
  plate = box(x0, x1, y0, y1, z0, z1)
  for y in (-SB_TIE_Y, SB_TIE_Y):
    for z in SB_TIE_Z:
      plate = plate - box(x0 - 1.0, x1 + 1.0, y - 1.3, y + 1.3, z - 3.0, z + 3.0)
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
                                     CrossSection.square((1.0, z1 - z0)).translate((x1 - 0.01, z0))])

  def plate_y(cs, ya, yb):
    return cs.extrude(yb - ya).transform([[1, 0, 0, 0], [0, 0, 1, ya], [0, 1, 0, 0]])

  forks = [plate_y(outline, SB_FORK_Y[0], SB_FORK_Y[1]), plate_y(outline, -SB_FORK_Y[1], -SB_FORK_Y[0])]
  bar = box(x1 - 0.01, SB_BAR_X1, SB_BAR_Y[0], SB_BAR_Y[1] + 0.01, SB_BAR_Z[0], SB_BAR_Z[1])
  part = union([plate] + forks + [bar])
  part = part - cyl_y(M5_CLEAR / 2, -60, 60, x=px, z=pz, segments=32)        # the arm's bolt
  slot = [cyl_y(M5_CLEAR / 2, -60, 60, x=px + r * math.sin(math.radians(a)), z=pz + r * math.cos(math.radians(a)), segments=20)
          for a in np.linspace(SB_ARM_ANGLES[0], SB_ARM_ANGLES[1], 81)]
  part = part - union(slot)                                                    # the arm's locking bolt, any angle
  for hx in SB_BAR_HOLES:
    part = part - cyl_y(M5_CLEAR / 2, -60, 60, x=hx, z=SB_BOLT_Z, segments=32)
  return clean(part)


def side_bracket_pads() -> Manifold:
  """Where the two rubber strips sit between the plate and the covers (bracket frame)."""
  z0, z1 = SB_PLATE_Z
  return union([box(0.0, SB_PAD_T, y - SB_PAD_W / 2, y + SB_PAD_W / 2, z0 + 2.0, z1 - 2.0) for y in (-SB_PAD_Y, SB_PAD_Y)])


def screw_tab(length: float, plate_y: float = TAB_PLATE_Y) -> Manifold:
  """The bar from the side bracket to the dash's screw. Its slot takes the bracket's two bolts, so the length adjusts;
  the end plate, with a vertical slot for the screw, bears on the dash's trim with its back face. The plate's middle
  sits plate_y below the column's axis (negative: below) and the plate reaches up or down to the bar whatever that
  is. Tab frame: x = 0 at the tab's start, otherwise the bracket frame; the assembly slides it along the bar.
  Prints lying on its back face, nothing needs supports."""
  w, h, _ = TAB_PLATE
  ya, yb = TAB_BAR_Y
  za, zb = TAB_BAR_Z
  bar = box(0.0, length, ya, yb, za, zb)
  s0, s1 = TAB_SLOT
  bar = bar - Manifold.batch_hull([cyl_y(M5_CLEAR / 2, ya - 1, yb + 1, x=s0 + M5_CLEAR / 2, z=SB_BOLT_Z, segments=24),
                                   cyl_y(M5_CLEAR / 2, ya - 1, yb + 1, x=s1 - M5_CLEAR / 2, z=SB_BOLT_Z, segments=24)])
  pz0, pz1 = TAB_PLATE_Z
  plate = box(length - w, length, min(plate_y - h / 2, ya - 0.01), max(plate_y + h / 2, yb + 0.01), pz0, pz1)
  xs = length - TAB_SCREW_FROM_END
  plate = plate - Manifold.batch_hull([cyl(SCREW_CLEAR / 2, pz0 - 1, pz1 + 1, xs, plate_y - TAB_SLOT_HALF, 24),
                                       cyl(SCREW_CLEAR / 2, pz0 - 1, pz1 + 1, xs, plate_y + TAB_SLOT_HALF, 24)])
  return clean(bar + plate)


def tab_bolts(tab_x0: float) -> Manifold:
  """The two M5 x 55 bolts through the bracket's bar and the tab (heads under the tab, nuts on the bar), and the arm's
  bolt and locking bolt through the fork, as solids for the clearance checks (bracket frame)."""
  out = []
  ya = TAB_BAR_Y[0]
  for hx in SB_BAR_HOLES:
    out.append(cyl_y(2.5, ya - 4.0, SB_BAR_Y[1] + MP.M5_WASHER_T + MP.M5_NYLOC_T + 6.0, x=hx, z=SB_BOLT_Z, segments=16))
    out.append(cyl_y(4.3, ya - 4.0, ya, x=hx, z=SB_BOLT_Z, segments=24))                                        # head
    out.append(cyl_y(4.6, SB_BAR_Y[1], SB_BAR_Y[1] + MP.M5_WASHER_T + MP.M5_NYLOC_T, x=hx, z=SB_BOLT_Z, segments=24))   # nut
  px, pz = SB_PIVOT
  yo = SB_FORK_Y[1]
  for (bx, bz) in ((px, pz), (px + MP.ARM_LOCK_R * math.sin(math.radians(0.0)), pz + MP.ARM_LOCK_R)):
    out.append(cyl_y(2.5, -yo - 8.0, yo + 8.0, x=bx, z=bz, segments=16))
    out.append(cyl_y(4.6, yo, yo + MP.M5_WASHER_T + MP.M5_NYLOC_T, x=bx, z=bz, segments=24))
    out.append(cyl_y(4.3, -yo - MP.M5_WASHER_T - 5.0, -yo, x=bx, z=bz, segments=24))
  return union(out)


def bracket_fastener_rows() -> list:
  """The side bracket's bolts and ties."""
  rows = []
  stack = 2 * (SB_FORK_Y[1] - SB_FORK_Y[0]) + ARM_T + 2 * GAP
  spare = 60.0 - stack - 2 * MP.M5_WASHER_T - MP.M5_NYLOC_T
  rows.append({"bolt": "M5 x 60 (2)", "use": "arm to side bracket: both fork plates and the arm, a washer each side, lock nut "
               "(the arm's bolt and its locking bolt)", "length": 60.0, "through_mm": round(stack + 2 * MP.M5_WASHER_T, 1),
               "nut_mm": MP.M5_NYLOC_T, "past_the_nut_mm": round(spare, 1), "ok": spare >= 1.5})
  stack = (SB_BAR_Y[1] - SB_BAR_Y[0]) + (TAB_BAR_Y[1] - TAB_BAR_Y[0])
  spare = 55.0 - stack - 2 * MP.M5_WASHER_T - MP.M5_NYLOC_T
  rows.append({"bolt": "M5 x 55 (2)", "use": "screw tab to the side bracket's bar, up through both, a washer each side, lock nut",
               "length": 55.0, "through_mm": round(stack + 2 * MP.M5_WASHER_T, 1), "nut_mm": MP.M5_NYLOC_T,
               "past_the_nut_mm": round(spare, 1), "ok": spare >= 1.5})
  rows.append({"bolt": "the dash's own screw, 8 mm longer (same thread)",
               "use": f"screw tab to the dash, through the plate ({TAB_PLATE[2]:.0f} mm) and a washer",
               "length": 0.0, "through_mm": TAB_PLATE[2] + 1.0, "nut_mm": 0.0, "past_the_nut_mm": 0.0, "ok": True})
  rows.append({"bolt": "zip ties, 8 mm wide, 400 mm or longer (3)", "use": "side bracket round the column covers, through the "
               "plate's slots (any that the stalks and the key leave free)", "length": 0.0, "through_mm": 0.0, "nut_mm": 0.0,
               "past_the_nut_mm": 0.0, "ok": True})
  return rows
'''
open('columnparts.py','w').write(src[:start] + new)
print("ok")
EOF
grep -n "^from params import" -A 3 columnparts.py | head; grep -n "ARM_T\b" params.py | head -3
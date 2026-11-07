python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
start = s.index("# ***** the column plate and the arm *****")
new = '''# ***** the column plate and its screw tabs *****
#
# The plate sits under the lower column cover, right of the adjustment tab, and hooks round the tab's dash side as far
# as the tab's steel arm allows (the arm runs from the tab back into the column and swings down when you pull the tab,
# so nothing may cross under it). It hangs from the cover's own three screws (two 4 x 16 self-tapping, one M5 x 12
# with a washer: Honda's parts list and its remote starter instructions give the types and the layout, not distances)
# through three screw tabs. Each tab is screwed to the cover with a longer copy of the screw that came out of that hole,
# turns to reach one of the plate's two long slots, and bolts to it from below into a nut held in the tab. A tab reaches
# 40 mm from its screw and the slots are long, so the plate fits wherever the screws really are (+-25 mm or more).

TAB_T = 8.0                   # a tab's thickness: the plate's top sits this far below the cover's underside
TAB_W = 16.0
TAB_L = 40.0                  # its screw to its bolt
TAB_BOSS = (6.0, 3.0)         # the boss round its screw that sits in the cover's screw cup: radius, height
TAB_HEAD = (6.6, 4.0)         # the screw head's counterbore from below: radius (the M5's washer head), depth
PL_T_U = 8.0                  # the plate's thickness
PL_MAIN_X = (16.0, 66.0)      # the plate's main part across, right of the adjustment tab (and room for your fingers)
PL_MAIN_Z = (-92.0, -215.0)   # ... along the column: from behind the key cylinder's bulge back towards the dash
PL_HOOK_X = (-2.0, 16.0)      # the hook behind the tab, up to its arm's swing
PL_HOOK_Z = (-152.0, -215.0)
PL_SLOTS = ((40.0, -98.0, -209.0), (6.0, -158.0, -209.0))   # the tabs' slots: x, from z, to z
PL_TIE_Z_U = (-120.0, -190.0)  # notches across the underside for zip ties round the cover, if wanted
FLANGE_PAD = 9.0              # plate's flange beyond its slots' ends and the bolts' outermost positions


def plate_top_y_u(cover_bottom: float = None) -> float:
  from params import COVER_BOTTOM
  return (COVER_BOTTOM if cover_bottom is None else cover_bottom) - TAB_T


def plate_flange_z() -> tuple:
  z0 = block_flange_z()[0]
  return (z0 - FLANGE_T, z0)


def plate_flange_outline() -> list:
  """The plate's flange (x, y), steering wheel frame, round both bolts' slots at the nominal mount."""
  b = flange_bolts_wheel()
  xs, ys = [p[0] for p in b], [p[1] for p in b]
  y_lo = min(ys) - SLOT_Y - FLANGE_PAD
  return [(PL_MAIN_X[1] - 8.0, y_lo), (max(xs) + FLANGE_PAD + 2.0, y_lo), (max(xs) + FLANGE_PAD + 2.0, max(ys) + SLOT_Y + FLANGE_PAD),
          (PL_MAIN_X[1] - 8.0, max(ys) + SLOT_Y + FLANGE_PAD)]


def pop_column_plate(cover_bottom: float = None) -> Manifold:
  """Steering wheel frame. The plate (its top TAB_T below the cover's underside), the hook behind the adjustment tab,
  the two slots for the screw tabs' bolts, and at its right edge the upright flange the hinge block bolts to (upright
  slots), held by a wall along the plate's edge, a shelf under it and a gusset behind it."""
  y1 = plate_top_y_u()
  y0 = y1 - PL_T_U
  main = box(PL_MAIN_X[0], PL_MAIN_X[1], y0, y1, PL_MAIN_Z[1], PL_MAIN_Z[0])
  hook = box(PL_HOOK_X[0], PL_HOOK_X[1] + 1.0, y0, y1, PL_HOOK_Z[1], PL_HOOK_Z[0])
  part = main + hook
  # round off the corners you might touch: the hook's front corner and the main part's front-left corner
  for x, z in ((PL_HOOK_X[0], PL_HOOK_Z[0]), (PL_MAIN_X[0], PL_MAIN_Z[0])):
    corner = box(x - 1.0, x + 6.0, y0 - 1.0, y1 + 1.0, z - 6.0, z + 1.0) - cyl_y(6.0, y0 - 2.0, y1 + 2.0, x=x + 6.0, z=z - 6.0, segments=32)
    part = part - corner
  # the flange, its wall along the plate's edge, the shelf under it and the gusset behind
  fz0, fz1 = plate_flange_z()
  fo = plate_flange_outline()
  fx0, fy0, fx1, fy1 = fo[0][0], fo[0][1], fo[2][0], fo[2][1]
  flange = _xy_poly(fo).extrude(fz1 - fz0).translate((0, 0, fz0))
  wall = box(PL_MAIN_X[1] - 8.0, PL_MAIN_X[1], y0, fy1, fz0 - 30.0, fz1)
  shelf = box(PL_MAIN_X[1] - 8.0, fx1, y0, y0 + 6.0, fz0 - 22.0, fz1) if fy0 <= y0 + 6.0 else box(PL_MAIN_X[1] - 8.0, fx1, fy0, fy0 + 6.0, fz0 - 22.0, fz1)
  gusset = prism_x([(fy0 + 3.0, fz0), (fy1 - 2.0, fz0), (fy0 + 3.0, fz0 - 22.0)], fx1 - 6.0, fx1)
  low = min(y0, fy0)
  skirt = box(PL_MAIN_X[1] - 8.0, fx1, low, y0 + 6.0, fz0 - 22.0, fz1)
  part = union([part, flange, wall, shelf, gusset, skirt])
  # the tabs' slots
  for x, za, zb in PL_SLOTS:
    part = part - Manifold.batch_hull([cyl_y(M5_CLEAR / 2, y0 - 1.0, y1 + 1.0, x=x, z=z, segments=32) for z in (za, zb)])
  # zip-tie notches across the underside (the main part only)
  for z in PL_TIE_Z_U:
    part = part - box(PL_MAIN_X[0] - 1.0, PL_MAIN_X[1] - 8.0, y0 - 1.0, y0 + 1.5, z - 4.0, z + 4.0)
  # the flange's slots (upright)
  for bx, by in flange_bolts_wheel():
    part = part - Manifold.batch_hull([cyl(M5_CLEAR / 2, fz0 - 23.0, fz1 + 1.0, bx, by + s, 32) for s in (-SLOT_Y, SLOT_Y)])
  # the shelf and skirt are cut back where the flange's slots run down through them
  return clean(part)


def pop_screw_tab() -> Manifold:
  """Tab frame: its screw at the origin, its bolt at +x TAB_L, +z towards the cover (its top face z = 0)."""
  t = TAB_T
  body = Manifold.batch_hull([cyl(TAB_W / 2, -t, 0.0, 0.0, 0.0, 48), cyl(TAB_W / 2, -t, 0.0, TAB_L, 0.0, 48)])
  boss = cyl(TAB_BOSS[0], 0.0, TAB_BOSS[1], segments=48)
  part = body + boss
  part = part - cyl(M5_CLEAR / 2, -t - 1.0, TAB_BOSS[1] + 1.0, segments=32)
  part = part - cyl(TAB_HEAD[0], -t - 1.0, -t + TAB_HEAD[1], segments=48)
  # the bolt end: through hole and a pocket for an M5 nyloc nut, from the top
  part = part - cyl(M5_CLEAR / 2, -t - 1.0, 1.0, TAB_L, 0.0, 32)
  r = M5_NUT_AF / math.sqrt(3.0)
  hexagon = CrossSection([[(TAB_L + r * math.cos(math.radians(60 * i)), r * math.sin(math.radians(60 * i))) for i in range(6)]])
  part = part - hexagon.extrude(M5_NUT_T + 0.3).translate((0, 0, -M5_NUT_T - 0.3))
  return clean(part)


def place_tab(screw_xz: tuple, toward_xz: tuple, cover_bottom: float = None) -> tuple:
  """Where a tab sits: its screw at screw_xz (on the cover's underside), turned so its bolt lands on the point
  toward_xz's direction. Returns (R, T) tab frame -> steering wheel frame and the bolt's (x, z)."""
  from params import COVER_BOTTOM
  yc = COVER_BOTTOM if cover_bottom is None else cover_bottom
  sx, sz = screw_xz
  d = np.array([toward_xz[0] - sx, toward_xz[1] - sz], dtype=float)
  d /= np.linalg.norm(d)
  # tab x -> (d_x, 0, d_z); tab z -> +y (up, towards the cover); tab y = z x x
  ex = np.array([d[0], 0.0, d[1]])
  ez = np.array([0.0, 1.0, 0.0])
  ey = np.cross(ez, ex)
  R = np.stack([ex, ey, ez], axis=1)
  T = np.array([sx, yc, sz])
  bolt = (sx + TAB_L * d[0], sz + TAB_L * d[1])
  return R, T, bolt


def tab_bolt_on_slot(screw_xz: tuple, slot: tuple) -> tuple | None:
  """The point on a plate slot (x, z_a, z_b) a tab from screw_xz reaches (TAB_L away), nearest the slot's middle."""
  x, za, zb = slot
  sx, sz = screw_xz
  dx = x - sx
  if abs(dx) > TAB_L:
    return None
  h = math.sqrt(TAB_L ** 2 - dx ** 2)
  lo, hi = min(za, zb) + 3.0, max(za, zb) - 3.0
  cands = [z for z in (sz + h, sz - h) if lo <= z <= hi]
  if not cands:
    return None
  mid = (lo + hi) / 2.0
  z = min(cands, key=lambda v: abs(v - mid))
  return (x, z)
'''
s = s[:start] + new
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import popparts as PP
print('z_axis', PP.Z_AXIS_P, 'mount', PP.MOUNT_DEG)
print('block flange z', PP.block_flange_z(), 'plate flange z', PP.plate_flange_z())
print('bolts', [tuple(round(v,1) for v in b) for b in PP.flange_bolts_wheel()])
print('outline', [tuple(round(v,1) for v in p) for p in PP.plate_flange_outline()])
pl = PP.pop_column_plate(); print('plate', round(pl.volume()), [round(v,1) for v in pl.bounding_box()], 'genus', pl.genus(), 'parts', len(pl.decompose()))
tb = PP.pop_screw_tab(); print('tab', round(tb.volume()), [round(v,1) for v in tb.bounding_box()], len(tb.decompose()))
blk = PP.pop_hinge_block(); print('block', round(blk.volume()), len(blk.decompose()))
"
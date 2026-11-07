python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
start = s.index("# ***** the column plate and its screw tabs *****")
new = '''# ***** the column plate and its screw tabs *****
#
# The plate is a U round the adjustment tab (the steering column's tilt and reach lever): a leg each side of the tab's
# paddle, joined behind the tab's pivot where nothing moves when you pull it. The right leg carries the upright flange
# the hinge block bolts to. It hangs from the lower column cover's own screws through swivel tabs.
#
# The cover's three screws (Honda's parts list: two 4 x 16 self-tapping, 90101-S2K-000, and one M5 x 12 screw-washer,
# 93891-05012-08). Honda's remote starter instructions (AII 42271, step 12) draw where they go: the two self-tapping
# screws near the cover's steering wheel end into the column's bracket there, one under the key cylinder (the round cup
# in your photos, right of the paddle) and one in line with the tab's slot (behind the paddle, so it can't be used); the
# M5 beside the tab's slot further back, into the tilt lock's bracket. No source gives distances: their places here are
# read off the drawing and your photos, and each tab reaches anywhere 18 to 40 mm from its screw, turned any way, onto
# one of the plate's long slots, so the plate fits them wherever they really are.

TAB_T = 8.0                   # a tab's thickness: the plate's top sits this far below the cover's underside
TAB_W = 16.0                  # its arm's width
TAB_END_R = 14.0              # the round end round its screw: wider than the cover's screw cup, so it bridges it
TAB_L = 40.0                  # its screw to the far end of its slot
TAB_SLOT = (18.0, 40.0)       # the slot along it for the bolt to the plate, with a channel on top for the nut
TAB_BOSS = (5.5, 3.0)         # a short boss into the cover's screw cup that centres it: radius, height
TAB_HEAD = (6.6, 4.0)         # the screw head's counterbore from below: radius (the M5's washer head), depth
NUT_CHANNEL_T = 5.5           # the nut's channel depth (an M5 nyloc nut, 5.2 mm)
PL_T_U = 8.0                  # the plate's thickness
PL_RIGHT_X = (12.0, 70.0)     # the right leg across (its inner edge 9 mm right of the paddle)
PL_LEFT_X = (-64.0, -50.0)    # the left leg (its inner edge 9 mm left of the paddle)
PL_FRONT_Z = -92.0            # the right leg's front end (behind the key cylinder's bulge)
PL_LEFT_FRONT_Z = -124.0      # the left leg's front end
PL_BRIDGE_Z = (-205.0, -191.0)   # the bridge behind the tab's pivot; the plate's back edge
# the slots the tabs' bolts go through: (x0, z0, x1, z1)
PL_SLOTS = ((52.0, -100.0, 52.0, -186.0), (28.0, -136.0, 28.0, -186.0), (-40.0, -198.0, 4.0, -198.0),
            (-57.0, -132.0, -57.0, -184.0))
PL_TIE_Z_U = (-148.0, -176.0)  # notches across the left leg's underside for a zip tie round the covers, if wanted
PAD_T = 10.0                   # foam strip on the left leg's top (EPDM weatherstrip 10 x 10 mm), squeezed to TAB_T
FLANGE_PAD = 9.0               # the plate's flange beyond its slots' ends
SHELF_X1 = 88.0                # the shelf under the flange, out to here (the springs' front bolt swings past beyond)


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
  x_lo = min(min(xs) - FLANGE_PAD, PL_RIGHT_X[1] - 8.0)
  return [(x_lo, y_lo), (max(xs) + FLANGE_PAD + 2.0, y_lo), (max(xs) + FLANGE_PAD + 2.0, max(ys) + SLOT_Y + FLANGE_PAD),
          (x_lo, max(ys) + SLOT_Y + FLANGE_PAD)]


def _slot_y(x0, z0, x1, z1, y0, y1, r=M5_CLEAR / 2) -> Manifold:
  return Manifold.batch_hull([cyl_y(r, y0, y1, x=x0, z=z0, segments=32), cyl_y(r, y0, y1, x=x1, z=z1, segments=32)])


def _round_corner(part: Manifold, x: float, z: float, sx: int, sz: int, r: float, y0: float, y1: float) -> Manifold:
  """Rounds the plate's corner at (x, z), the plate lying towards +sx in x and +sz in z from it."""
  cut = box(min(x, x + sx * r) - 0.01, max(x, x + sx * r) + 0.01, y0 - 1.0, y1 + 1.0, min(z, z + sz * r) - 0.01, max(z, z + sz * r) + 0.01)
  return part - (cut - cyl_y(r, y0 - 2.0, y1 + 2.0, x=x + sx * r, z=z + sz * r, segments=40))


def pop_column_plate(cover_bottom: float = None) -> Manifold:
  """Steering wheel frame. The U: right leg, bridge, left leg (its top TAB_T below the cover's underside); the tabs'
  slots; at the right leg's outer edge the upright flange the hinge block bolts to (upright slots), held by a wall
  along the leg's edge, a shelf under it and a gusset behind it."""
  y1 = plate_top_y_u()
  y0 = y1 - PL_T_U
  zb0, zb1 = PL_BRIDGE_Z
  right = box(PL_RIGHT_X[0], PL_RIGHT_X[1], y0, y1, zb0, PL_FRONT_Z)
  left = box(PL_LEFT_X[0], PL_LEFT_X[1], y0, y1, zb0, PL_LEFT_FRONT_Z)
  bridge = box(PL_LEFT_X[0], PL_RIGHT_X[0] + 1.0, y0, y1, zb0, zb1)
  part = union([right, left, bridge])
  # round the corners you might touch
  part = _round_corner(part, PL_RIGHT_X[0], PL_FRONT_Z, 1, -1, 8.0, y0, y1)
  part = _round_corner(part, PL_LEFT_X[0], PL_LEFT_FRONT_Z, 1, -1, 7.0, y0, y1)
  part = _round_corner(part, PL_LEFT_X[1], PL_LEFT_FRONT_Z, -1, -1, 7.0, y0, y1)
  part = _round_corner(part, PL_LEFT_X[0], zb0, 1, 1, 8.0, y0, y1)
  # a rib under each leg's edge by the tab, for stiffness
  ribs = [box(PL_RIGHT_X[0], PL_RIGHT_X[0] + 4.0, y0 - 6.0, y0 + 0.01, zb0, PL_FRONT_Z - 8.0),
          box(PL_LEFT_X[1] - 4.0, PL_LEFT_X[1], y0 - 6.0, y0 + 0.01, zb0, PL_LEFT_FRONT_Z - 7.0),
          box(PL_LEFT_X[0] + 8.0, PL_RIGHT_X[0] + 4.0, y0 - 6.0, y0 + 0.01, zb1 - 4.0, zb1)]
  part = union([part] + ribs)
  # the flange, its wall along the leg's edge, the shelf under it and the gusset behind
  fz0, fz1 = plate_flange_z()
  fo = plate_flange_outline()
  fx0, fy0, fx1, fy1 = fo[0][0], fo[0][1], fo[2][0], fo[2][1]
  flange = _xy_poly(fo).extrude(fz1 - fz0).translate((0, 0, fz0))
  wall = box(PL_RIGHT_X[1] - 8.0, PL_RIGHT_X[1], y0, fy1, fz0 - 30.0, fz1)
  low = min(y0, fy0)
  shelf = box(PL_RIGHT_X[1] - 8.0, SHELF_X1, low, y0 + 6.0, fz0 - 16.0, fz1)
  gusset = prism_x([(y0 + 5.0, fz0), (fy1 - 4.0, fz0), (y0 + 5.0, fz0 - 26.0)], PL_RIGHT_X[1] - 8.0, PL_RIGHT_X[1])
  part = union([part, flange, wall, shelf, gusset])
  # the tabs' slots
  for x0, z0, x1, z1 in PL_SLOTS:
    part = part - _slot_y(x0, z0, x1, z1, y0 - 8.0, y1 + 1.0)
  # zip-tie notches across the left leg's underside
  for z in PL_TIE_Z_U:
    part = part - box(PL_LEFT_X[0] - 1.0, PL_LEFT_X[1] + 1.0, y0 - 7.0, y0 + 1.5, z - 4.0, z + 4.0)
  # the flange's slots (upright)
  for bx, by in flange_bolts_wheel():
    part = part - Manifold.batch_hull([cyl(M5_CLEAR / 2, fz0 - 17.0, fz1 + 1.0, bx, by + s, 32) for s in (-SLOT_Y, SLOT_Y)])
  return clean(part)


def plate_pad(cover_bottom: float = None) -> Manifold:
  """The foam strip on the left leg's top, squeezed between it and the cover."""
  y1 = plate_top_y_u(cover_bottom)
  return box(PL_LEFT_X[0] + 1.0, PL_LEFT_X[1] - 1.0, y1, y1 + TAB_T, PL_BRIDGE_Z[0] + 4.0, PL_LEFT_FRONT_Z - 4.0)


def pop_screw_tab() -> Manifold:
  """Tab frame: its screw at the origin, its slot along +x from TAB_SLOT[0] to TAB_SLOT[1], +z towards the cover (its
  top face z = 0). The nut for the plate's bolt sits in a channel along the slot's top and can slide along it."""
  t = TAB_T
  end = cyl(TAB_END_R, -t, 0.0, 0.0, 0.0, 64)
  arm = Manifold.batch_hull([cyl(TAB_W / 2, -t, 0.0, 6.0, 0.0, 48), cyl(TAB_W / 2, -t, 0.0, TAB_L + 3.0, 0.0, 48)])
  boss = cyl(TAB_BOSS[0], 0.0, TAB_BOSS[1], segments=48)
  part = end + arm + boss
  part = part - cyl(M5_CLEAR / 2, -t - 1.0, TAB_BOSS[1] + 1.0, segments=32)
  part = part - cyl(TAB_HEAD[0], -t - 1.0, -t + TAB_HEAD[1], segments=48)
  part = part - Manifold.batch_hull([cyl(M5_CLEAR / 2, -t - 1.0, 1.0, x, 0.0, 32) for x in TAB_SLOT])
  # the nut's channel from the top: its flats against the channel's sides so it can't turn
  ch = box(TAB_SLOT[0] - M5_NUT_AF * 0.6, TAB_SLOT[1] + M5_NUT_AF * 0.6, -(M5_NUT_AF + 0.3) / 2, (M5_NUT_AF + 0.3) / 2,
           -NUT_CHANNEL_T, 0.5)
  part = part - ch
  return clean(part)


def place_tab(screw_xz: tuple, toward_xz: tuple, cover_bottom: float = None) -> tuple:
  """Where a tab sits: its screw at screw_xz (on the cover's underside), turned towards toward_xz. Returns (R, T) tab
  frame -> steering wheel frame and toward_xz."""
  from params import COVER_BOTTOM
  yc = COVER_BOTTOM if cover_bottom is None else cover_bottom
  sx, sz = screw_xz
  d = np.array([toward_xz[0] - sx, toward_xz[1] - sz], dtype=float)
  d /= np.linalg.norm(d)
  ex = np.array([d[0], 0.0, d[1]])
  ez = np.array([0.0, 1.0, 0.0])
  ey = np.cross(ez, ex)
  R = np.stack([ex, ey, ez], axis=1)
  T = np.array([sx, yc, sz])
  return R, T, toward_xz


def tab_bolts_on_slot(screw_xz: tuple, slot: tuple, n: int = 9) -> list:
  """Points on a plate slot (x0, z0, x1, z1) a tab from screw_xz can put its bolt (18 to 40 mm away), sampled."""
  x0, z0, x1, z1 = slot
  out = []
  L = math.hypot(x1 - x0, z1 - z0)
  ux, uz = (x1 - x0) / L, (z1 - z0) / L
  for i in range(int(L) + 1):
    u = min(L, float(i))
    if u < 3.0 or u > L - 3.0:
      continue
    px, pz = x0 + ux * u, z0 + uz * u
    d = math.hypot(px - screw_xz[0], pz - screw_xz[1])
    if TAB_SLOT[0] + 1.0 <= d <= TAB_SLOT[1] - 1.0:
      out.append((px, pz))
  return out
'''
s = s[:start] + new
p.write_text(s)
print("ok")
EOF
python3 - <<'EOF'
import pathlib
p = pathlib.Path("popassembly.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

# ---- the adjustment tab as a lever, the fingers on it, the screws, the knee bolster ----
start = s.index("# the adjustment tab (the steering column's tilt and reach lever), from your photos: its handle hangs under the cover")
end = s.index("FINGERS = (-45.0, 12.0, 8.0)")
new = '''# The adjustment tab (the steering column's tilt and reach lever), from your photos: a flat paddle hanging under the
# lower cover left of its middle, its steel arm running back along the cover's slot to a pivot in the column near the
# cover's dash end. Pulling the paddle down swings both about the pivot. (x0, x1, z0, z1; y0, y1)
TAB_PADDLE = (-41.0, 3.0, -118.0, -62.0)
TAB_PADDLE_Y = (-64.0, -50.0)
TAB_ARM = (-34.0, -6.0, -185.0, -112.0)
TAB_ARM_Y = (-56.0, -50.0)
TAB_PIVOT = (-44.0, -185.0)          # (y, z)
TAB_SWING = 40.0                     # degrees the paddle swings down, pulled all the way (an estimate on the generous side)
TAB_FINGERS = (-46.0, 8.0, -105.0, -50.0, -100.0, -40.0)   # your fingers round the paddle's front edge, pulling it
# The lower cover's three screws (x, z) on its underside, where Honda's drawing and your photos put them, with how far
# off each may be (x, z), and whether a tab can use it: the middle self-tapping screw sits behind the paddle.
COVER_SCREWS = (("4 x 16 self-tapping under the key cylinder", (38.0, -98.0), (12.0, 15.0), True),
                ("M5 x 12 screw-washer beside the tab's slot", (2.0, -178.0), (10.0, 15.0), True),
                ("4 x 16 self-tapping behind the paddle", (-18.0, -125.0), (10.0, 20.0), False))
# the knee bolster (the dash panel under the column): its face, and the opening round the column
BOLSTER_Z = -218.0
BOLSTER_OPENING = (66.0, -78.0)      # half-width round the covers, and the opening's bottom edge (y)
'''
s = s[:start] + new + s[end:]
# ---- lever solids, tab placement over every slot ----
start = s.index("def _tab_clear(screw_xz, bolt_xz) -> bool:")
end = s.index("class PopAssembly:")
new2 = '''def tab_lever(angle: float = 0.0) -> Manifold:
  """The adjustment tab's paddle and arm, pulled down by angle degrees about its pivot."""
  x0, x1, z0, z1 = TAB_PADDLE
  paddle = box(x0, x1, TAB_PADDLE_Y[0], TAB_PADDLE_Y[1], z0, z1)
  a0, a1, c0, c1 = TAB_ARM
  arm = box(a0, a1, TAB_ARM_Y[0], TAB_ARM_Y[1], c0, c1)
  py, pz = TAB_PIVOT
  m = paddle + arm
  return m.translate((0.0, -py, -pz)).rotate((angle, 0.0, 0.0)).translate((0.0, py, pz)) if angle else m


def tab_lever_sweep(step: float = 4.0) -> Manifold:
  """Everywhere the paddle and arm go as you pull the tab, and your fingers on the paddle."""
  parts = [tab_lever(float(a)) for a in np.arange(0.0, TAB_SWING + 1e-9, step)]
  return Manifold.batch_hull([parts[0], parts[-1]]) + union(parts) + box(*TAB_FINGERS)


def _keep_out_xz() -> list:
  """Rectangles (x0, x1, z0, z1) seen from below that a tab must stay out of: the paddle, the arm, your fingers."""
  m = 3.0
  return [(TAB_PADDLE[0] - m, TAB_PADDLE[1] + m, TAB_PADDLE[2] - m, TAB_PADDLE[3] + 25.0),
          (TAB_ARM[0] - m, TAB_ARM[1] + m, TAB_ARM[2] - m, TAB_ARM[3]),
          (TAB_FINGERS[0], TAB_FINGERS[1], TAB_FINGERS[4], TAB_FINGERS[5])]


def _tab_clear(screw_xz, bolt_xz, others=()) -> bool:
  """A tab from its screw to its bolt (its round end and its arm) stays out of the paddle's, the arm's and your fingers'
  room, and clear of the other tabs, seen from below."""
  sx, sz = screw_xz
  bx, bz = bolt_xz
  L = math.hypot(bx - sx, bz - sz)
  d = np.array([bx - sx, bz - sz]) / L
  n = np.array([-d[1], d[0]])
  half = PP.TAB_W / 2
  pts = [np.array([sx, sz]) + d * u + n * v for u in np.linspace(6.0, PP.TAB_L + 3.0 + half, 22)
         for v in np.linspace(-half, half, 5)]
  pts += [np.array([sx, sz]) + PP.TAB_END_R * np.array([math.cos(a), math.sin(a)]) for a in np.linspace(0, 2 * math.pi, 24)]
  for x0, x1, z0, z1 in _keep_out_xz():
    if any(x0 <= q[0] <= x1 and z0 <= q[1] <= z1 for q in pts):
      return False
  for (ox, oz), (obx, obz) in others:
    # keep 4 mm between tabs: sample the other tab's centre line
    oL = math.hypot(obx - ox, obz - oz)
    od = np.array([obx - ox, obz - oz]) / oL
    line = [np.array([ox, oz]) + od * u for u in np.linspace(0.0, PP.TAB_L + 3.0, 12)]
    if any(min(np.linalg.norm(q - c) for c in line) < half + 4.0 + 0.0 for q in pts[::3]):
      return False
  return True


def tab_options(screw_xz, others=()) -> list:
  """Every (slot index, bolt (x, z)) a tab from screw_xz can use."""
  out = []
  for i, slot in enumerate(PP.PL_SLOTS):
    for b in PP.tab_bolts_on_slot(screw_xz, slot):
      if _tab_clear(screw_xz, b, others):
        out.append((i, b))
  return out


def tab_placements(screws=None, plate_dxz=(0.0, 0.0)) -> list:
  """For each usable cover screw: (name, R, T, bolt (x, z), slot index), the plate shifted by plate_dxz. Picks each
  bolt nearest its slot's middle, the screws in order, each tab clear of the ones before."""
  screws = screws if screws is not None else [(n, xz) for n, xz, _, use in COVER_SCREWS if use]
  dx, dz = plate_dxz
  out, placed = [], []
  for name, xz in screws:
    rel = (xz[0] - dx, xz[1] - dz)               # in the plate's own frame
    opts = tab_options(rel, placed)
    if not opts:
      raise ValueError(f"the tab for the {name} can't reach a slot")

    def score(o):
      i, b = o
      x0, z0, x1, z1 = PP.PL_SLOTS[i]
      mid = ((x0 + x1) / 2, (z0 + z1) / 2)
      return math.hypot(b[0] - mid[0], b[1] - mid[1]) + 0.2 * abs(math.hypot(b[0] - rel[0], b[1] - rel[1]) - 29.0)

    i, b = min(opts, key=score)
    placed.append((rel, b))
    R, T, _ = PP.place_tab(xz, (b[0] + dx, b[1] + dz))
    out.append((name, R, T, (b[0] + dx, b[1] + dz), i))
  return out


def tab_fit_study(n: int = 7, shifts=(-10.0, 0.0, 10.0)) -> dict:
  """For the screws anywhere in their boxes (a grid) and the plate slid along the column by each shift: how often the
  tabs can all be placed."""
  total, ok, worst = 0, 0, []
  usable = [(nm, xz, tol) for nm, xz, tol, use in COVER_SCREWS if use]
  grids = [[(xz[0] + fx * tol[0], xz[1] + fz * tol[1]) for fx in np.linspace(-1, 1, n) for fz in np.linspace(-1, 1, n)]
           for _, xz, tol in usable]
  import itertools
  for combo in itertools.product(*grids):
    for dz in shifts:
      total += 1
      try:
        tab_placements([(usable[k][0], combo[k]) for k in range(len(usable))], (0.0, dz))
        ok += 1
      except ValueError:
        worst.append((combo, dz))
  return {"cases": total, "fit": ok, "misses": worst[:6]}


'''
s = s[:start] + new2 + s[end:]
# ---- assembly: tabs and their bolts, the lever, the bolster ----
rep('''  def tabs(self) -> Manifold:
    tab = self.p["tab"]
    return union([PP.place(tab, R, T) for _, R, T, _, _ in tab_placements()]).translate((0, self.cover_bottom - P.COVER_BOTTOM, 0))''',
'''  def tabs(self) -> Manifold:
    tab = self.p["tab"]
    return union([PP.place(tab, R, T) for _, R, T, _, _ in tab_placements()]).translate((0, self.cover_bottom - P.COVER_BOTTOM, 0))

  def pad(self) -> Manifold:
    return PP.plate_pad(self.cover_bottom)''')
rep('''    for _, R, T, (bx, bz), _ in tab_placements():
      parts.append(cyl_y(2.5, y0 - 1.0, y1 + PP.TAB_T, x=bx, z=bz, segments=16) + cyl_y(5.0, y0 - 4.5, y0, x=bx, z=bz, segments=6))
      parts.append(cyl_y(5.5, T[1] - PP.TAB_T + self.cover_bottom - P.COVER_BOTTOM, T[1] - PP.TAB_T + PP.TAB_HEAD[1] - 0.5 + self.cover_bottom - P.COVER_BOTTOM,
                         x=T[0], z=T[2], segments=24))''',
'''    dy = self.cover_bottom - P.COVER_BOTTOM
    for _, R, T, (bx, bz), _ in tab_placements():
      # the plate's bolt: hex head and washer under the plate, up into the nut in the tab's channel
      parts.append(cyl_y(2.5, y0 - 1.0, y1 + PP.TAB_T - 0.5, x=bx, z=bz, segments=16) +
                   cyl_y(4.6, y0 - 4.5, y0 - 1.0, x=bx, z=bz, segments=6) + cyl_y(5.0, y0 - 1.0, y0, x=bx, z=bz, segments=24))
      # the cover screw's head in the tab's counterbore
      parts.append(cyl_y(5.5, T[1] - PP.TAB_T + dy, T[1] - PP.TAB_T + PP.TAB_HEAD[1] - 0.5 + dy, x=T[0], z=T[2], segments=24))''')
rep('''  def tilt_lever(self) -> Manifold:
    return box(*TAB_HANDLE_ZONE) + box(*TAB_ARM_ZONE)''',
'''  def tilt_lever(self) -> Manifold:
    return tab_lever_sweep()

  def bolster(self) -> Manifold:
    """The knee bolster's face below and beside the column, with its opening round the covers."""
    hw, yb = BOLSTER_OPENING
    wall = box(-300.0, 300.0, -400.0, 60.0, BOLSTER_Z - 40.0, BOLSTER_Z)
    opening = box(-hw, hw, yb, 200.0, BOLSTER_Z - 41.0, BOLSTER_Z + 1.0)
    return wall - opening''')
rep('''            ("the key in the ignition", self.key_head()), ("adjustment tab, its arm and their swing", self.tilt_lever()),
            ("dash below the column", self.dash())]''',
'''            ("the key in the ignition", self.key_head()), ("adjustment tab, its arm, their swing and your fingers", self.tilt_lever()),
            ("knee bolster", self.bolster())]''')
# checks: the pad is a fixed part too
rep('''  B, SW, PL, TB = A.block(), A.switch(), A.plate(), A.tabs()''', '''  B, SW, PL, TB = A.block(), A.switch(), A.plate() + A.pad(), A.tabs()''')
p.write_text(s)
print("ok")
EOF
grep -n "TAB_HANDLE_ZONE\|TAB_ARM_ZONE\|TILT_LEVER_ZONE\|tab_bolt_on_slot\|TAB_REACHES" popassembly.py popparts.py
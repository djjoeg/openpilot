"""
The pop-off mount in the car, and the checks that it fits and works: the motor gear meshing the back teeth through
their whole arc with no overlap and some free play; nothing touching with the motor on, while it swings off and back,
and parked off, with the wheel straight, turned through the teeth and past them (the carrier dropping onto its stop);
the springs' pull, the stops, the power switch; and everything clear of the column covers, the hub, the zone the
spokes sweep, the wiper stalk in all its positions, the key and your fingers on it, the tilt lever's swing, and (parked)
your fingers round the grip anywhere.

Frames: see popparts.py.
"""
import math
import os

import numpy as np
from manifold3d import Manifold, Mesh

import columnassembly as CA
import faceparts as FP
import mountparts as MP
import params as P
import popparts as PP
from cadlib import box, cyl, revolve, union

MESH_PHASE = 180.0 / FP.FACE_MOTOR_TEETH
STALK_DOWN_DEG = 36.0      # the wiper stalk pushed all the way down (HI): 3 notches (your count), taken as 12 degrees
                           # each until you measure it
STALK_UP_DEG = 10.0        # ... and lifted for MIST
STALK_LEN = 105.0          # your tape: the stalk sticks out about 105 mm from the cover
KEY_HEAD = (20.0, 45.0)    # the key in the ignition, its head turned to any position: radius and length out from the bezel
KEY_ROOM = (22.0, 60.0)    # your fingers turning the key: radius and length out from the bezel (checked with the motor
                           # popped off; with it on the report gives the room left)
# The adjustment tab (the steering column's tilt and reach lever), from your photos: a flat paddle hanging under the
# lower cover left of its middle, its steel arm running back along the cover's slot to a pivot in the column near the
# cover's dash end. Pulling the paddle down swings both about the pivot. (x0, x1, z0, z1; y0, y1)
TAB_PADDLE = (-41.0, 3.0, -118.0, -62.0)
TAB_PADDLE_Y = (-64.0, -50.0)
TAB_ARM = (-41.0, -11.0, -185.0, -112.0)    # under the paddle's left two thirds, as in your photos
TAB_ARM_Y = (-56.0, -50.0)
TAB_PIVOT = (-44.0, -185.0)          # (y, z)
TAB_SWING = 40.0                     # degrees the paddle swings down, pulled all the way (an estimate on the generous side)
TAB_FINGERS = (-46.0, 8.0, -105.0, -50.0, -100.0, -40.0)   # your fingers round the paddle's front edge, pulling it
# The lower cover's three screws (x, z) on its underside, where Honda's drawing and your photos put them, with how far
# off each may be (x, z), and whether a tab can use it: the middle self-tapping screw sits behind the paddle.
COVER_SCREWS = (("4 x 16 self-tapping under the key cylinder", (38.0, -98.0), (12.0, 15.0), "cup"),
                ("M5 x 12 screw-washer beside the tab's slot", (1.0, -175.0), (4.0, 15.0), "slim"),
                ("4 x 16 self-tapping behind the paddle", (-18.0, -125.0), (10.0, 20.0), None))
# the knee bolster (the dash panel under the column): its face, and the opening round the column
BOLSTER_Z = -218.0
BOLSTER_OPENING = (66.0, -78.0)      # half-width round the covers, and the opening's bottom edge (y)
FINGERS = (-45.0, 12.0, 8.0)   # parked: your fingers round the grip reach this far behind its middle, this far inside it
                               # and this far outside it


def _cache_path(name: str) -> str:
  d = os.environ.get("POP_CACHE", "/tmp/pop_cache")
  os.makedirs(d, exist_ok=True)
  return os.path.join(d, name + ".npz")


def cached(name: str, build):
  """Builds a solid once and keeps it on disk (the back teeth take a while)."""
  p = _cache_path(name)
  if os.path.exists(p):
    z = np.load(p)
    return Manifold(Mesh(vert_properties=z["v"].astype(np.float32), tri_verts=z["t"].astype(np.uint32)))
  m = build()
  mesh = m.to_mesh()
  np.savez(p, v=np.asarray(mesh.vert_properties)[:, :3], t=np.asarray(mesh.tri_verts))
  return m


def overlap(a: Manifold, b: Manifold) -> float:
  return (a ^ b).volume()


def stalk_positions(down: float = STALK_DOWN_DEG, up: float = STALK_UP_DEG, step: float = 2.5) -> Manifold:
  base = np.array(P.STALK_FROM)
  d = np.array(P.STALK_TO) - base
  d /= np.linalg.norm(d)
  tip = base + STALK_LEN * d
  ax = np.cross(d, [0.0, 1.0, 0.0])
  ax /= np.linalg.norm(ax)
  out = []
  for a in np.arange(-up, down + 1e-9, step):
    th = math.radians(-a)
    v = tip - base
    v_rot = v * math.cos(th) + np.cross(ax, v) * math.sin(th) + ax * np.dot(ax, v) * (1 - math.cos(th))
    out.append(CA.rod(base, base + v_rot, P.STALK_R))
  return union(out)


def key_room(size: tuple = KEY_ROOM) -> Manifold:
  kd = np.array(P.KEY_TO) - np.array(P.KEY_FROM)
  kd /= np.linalg.norm(kd)
  r, L = size
  return CA.rod(np.array(P.KEY_TO), np.array(P.KEY_TO) + L * kd, r)


def cover_model(back_z: float = -400.0) -> Manifold:
  """The steering column covers: a rounded box along the column (flat underneath, as in your photos), COVER_FRONT_W
  wide at its front edge widening to COVER_W at COVER_TAPER_Z, from COVER_BOTTOM up to COVER_H above it."""
  from manifold3d import CrossSection

  def section(w, z):
    r = 26.0
    cs = CrossSection.square((w - 2 * r, P.COVER_H - 2 * r), center=True).offset(r, circular_segments=48)
    return cs.translate((0.0, P.COVER_BOTTOM + P.COVER_H / 2)).extrude(0.5).translate((0, 0, z))

  front_w = min(P.COVER_FRONT_W, P.COVER_W)
  taper = Manifold.batch_hull([section(front_w, P.COVER_FRONT_Z - 0.5), section(P.COVER_W, P.COVER_TAPER_Z)])
  back = section(P.COVER_W, 0.0).scale((1.0, 1.0, (P.COVER_TAPER_Z + 0.5 - back_z) / 0.5)).translate((0, 0, back_z))
  return taper + back


def tab_lever(angle: float = 0.0) -> Manifold:
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
  m = 2.0
  return [(TAB_PADDLE[0] - m, TAB_PADDLE[1] + m, TAB_PADDLE[2] - m, TAB_PADDLE[3] + 25.0),
          (TAB_ARM[0] - m, TAB_ARM[1] + 0.5, TAB_ARM[2] - m, TAB_ARM[3]),
          (TAB_FINGERS[0], TAB_FINGERS[1], TAB_FINGERS[4], TAB_FINGERS[5])]


def _tab_clear(screw_xz, bolt_xz, others=(), end_r: float = PP.TAB_END_R) -> bool:
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
  pts += [np.array([sx, sz]) + end_r * np.array([math.cos(a), math.sin(a)]) for a in np.linspace(0, 2 * math.pi, 24)]
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


def tab_options(screw_xz, others=(), kind: str = "cup") -> list:
  """Every (slot index, bolt (x, z)) a tab from screw_xz can use."""
  out = []
  r = PP.TAB_KINDS[kind]["end_r"]
  for i, slot in enumerate(PP.PL_SLOTS):
    for b in PP.tab_bolts_on_slot(screw_xz, slot):
      if _tab_clear(screw_xz, b, others, r):
        out.append((i, b))
  return out


def tab_placements(screws=None, plate_dxz=(0.0, 0.0)) -> list:
  """For each usable cover screw: (name, R, T, bolt (x, z), slot index, kind), the plate shifted by plate_dxz. Each
  tab's bolt goes as near its slot's middle as it can, the tabs kept clear of each other (tries the next best spots
  for the earlier tabs if a later one can't be placed)."""
  screws = screws if screws is not None else [(n, xz, kind) for n, xz, _, kind in COVER_SCREWS if kind]
  dx, dz = plate_dxz
  rels = [(xz[0] - dx, xz[1] - dz) for _, xz, _ in screws]       # in the plate's own frame

  def score(rel, o):
    i, b = o
    x0, z0, x1, z1 = PP.PL_SLOTS[i]
    mid = ((x0 + x1) / 2, (z0 + z1) / 2)
    return math.hypot(b[0] - mid[0], b[1] - mid[1]) + 0.2 * abs(math.hypot(b[0] - rel[0], b[1] - rel[1]) - 29.0)

  alone = [sorted(tab_options(rel, (), kind), key=lambda o, r=rel: score(r, o)) for rel, (_, _, kind) in zip(rels, screws)]

  def place(k, placed):
    if k == len(screws):
      return []
    for i, b in alone[k][::3] + alone[k][1::3] + alone[k][2::3]:
      if placed and not _tab_clear(rels[k], b, placed, PP.TAB_KINDS[screws[k][2]]["end_r"]):
        continue
      rest = place(k + 1, placed + [(rels[k], b)])
      if rest is not None:
        return [(i, b)] + rest
    return None

  chosen = place(0, [])
  if chosen is None:
    bad = next((screws[k][0] for k in range(len(screws)) if not alone[k]), screws[-1][0])
    raise ValueError(f"the tab for the {bad} can't reach a slot")
  out = []
  for (name, xz, kind), (i, b) in zip(screws, chosen):
    R, T, _ = PP.place_tab(xz, (b[0] + dx, b[1] + dz))
    out.append((name, R, T, (b[0] + dx, b[1] + dz), i, kind))
  return out


def tab_fit_study(n: int = 7, shifts=(-10.0, 0.0, 10.0)) -> dict:
  """For the screws anywhere in their boxes (a grid) and the plate slid along the column by each shift: how often the
  tabs can all be placed."""
  total, ok, worst = 0, 0, []
  usable = [(nm, xz, tol, kind) for nm, xz, tol, kind in COVER_SCREWS if kind]
  grids = [[(xz[0] + fx * tol[0], xz[1] + fz * tol[1]) for fx in np.linspace(-1, 1, n) for fz in np.linspace(-1, 1, n)]
           for _, xz, tol, _ in usable]
  import itertools
  for combo in itertools.product(*grids):
    for dz in shifts:
      total += 1
      try:
        tab_placements([(usable[k][0], combo[k], usable[k][3]) for k in range(len(usable))], (0.0, dz))
        ok += 1
      except ValueError:
        worst.append((combo, dz))
  return {"cases": total, "fit": ok, "misses": worst[:6]}


class PopAssembly:
  def __init__(self, t: PP.PopTeeth, parts: dict, cover_bottom: float = P.COVER_BOTTOM):
    self.t, self.p = t, parts
    self.cover_bottom = cover_bottom
    self.side = CA.SideAssembly.__new__(CA.SideAssembly)
    self.side.cover_w, self.side.cover_h, self.side.cover_front_w = P.COVER_W, P.COVER_H, P.COVER_FRONT_W

  # the mount's parts
  def teeth(self, wheel_deg: float = 0.0) -> Manifold:
    return self.p["teeth"].rotate((0, 0, PP.MOUNT_DEG + wheel_deg))

  def gear(self, lift: float = 0.0, wheel_deg: float = 0.0, part: str = "gear") -> Manifold:
    return PP.to_wheel(self.p[part].rotate((0, 0, MESH_PHASE - FP.FACE_RATIO * wheel_deg)), lift)

  def carrier(self, lift: float = 0.0) -> Manifold:
    return PP.to_wheel(self.p["carrier"], lift)

  def motor(self, lift: float = 0.0) -> Manifold:
    return PP.to_wheel(self.p["motor"], lift)

  def springs(self, lift: float = 0.0) -> Manifold:
    return PP.to_wheel(PP.spring_solid(lift), 0.0)

  def bolts(self, lift: float = 0.0) -> Manifold:
    """The springs' two M5 x 90 bolts (shank, head, washers and nuts), the hinge bolt."""
    from cadlib import cyl_x
    cy, cz = PP.C_BOLT                     # built with the motor on, then swung with the carrier
    by, bz = PP.B_BOLT
    hy, hz = PP.HINGE_P
    def through(y, z):
      # M5 x 80: head and washer outside one spring's loop, washer and lock nut outside the other's
      x_out = PP.SPRING_X + PP.SPRING_WIRE_P / 2 + 1.0
      return (cyl_x(2.5, -x_out, x_out + 6.2, y=y, z=z, segments=16) + cyl_x(4.6, -x_out - 3.5, -x_out, y=y, z=z, segments=16) +
              cyl_x(4.6, x_out, x_out + 5.2, y=y, z=z, segments=6))
    c = through(cy, cz)
    b = through(by, bz)
    k = PP.BLOCK_KNUCKLE_X[1]
    h = cyl_x(2.5, -k - 5, k + 6, y=hy, z=hz, segments=16) + cyl_x(4.3, -k - 5, -k, y=hy, z=hz, segments=16) + \
      cyl_x(4.6, k, k + 6, y=hy, z=hz, segments=6)
    return PP.to_wheel(PP.swung(c, lift), 0.0) + PP.to_wheel(b + h, 0.0)

  def block(self) -> Manifold:
    return PP.to_wheel(self.p["block"], 0.0)

  def switch(self) -> Manifold:
    return PP.to_wheel(PP.switch_body_pop(), 0.0)

  def plate(self) -> Manifold:
    return self.p["plate"].translate((0, self.cover_bottom - P.COVER_BOTTOM, 0))

  def tabs(self) -> Manifold:
    return union([PP.place(self.p["tab_" + kind], R, T) for _, R, T, _, _, kind in tab_placements()]).translate(
      (0, self.cover_bottom - P.COVER_BOTTOM, 0))

  def pad(self) -> Manifold:
    return PP.plate_pad(self.cover_bottom)

  def tab_bolts(self) -> Manifold:
    """The tabs' M5 bolts (head and washer under the plate, nyloc nut in the tab) and the cover screws' heads."""
    from cadlib import cyl_y
    y1 = PP.plate_top_y_u() + self.cover_bottom - P.COVER_BOTTOM
    y0 = y1 - PP.PL_T_U
    parts = []
    dy = self.cover_bottom - P.COVER_BOTTOM
    for _, R, T, (bx, bz), _, kind in tab_placements():
      # the plate's bolt: M5 x 20 hex head in the tab's channel, down through the plate, washer and lock nut under it
      top = y1 + PP.TAB_T - PP.NUT_CHANNEL_T
      parts.append(cyl_y(4.6, top, top + 3.5, x=bx, z=bz, segments=6) + cyl_y(2.5, top - 20.0, top, x=bx, z=bz, segments=16) +
                   cyl_y(5.0, y0 - 1.0, y0, x=bx, z=bz, segments=24) + cyl_y(4.6, y0 - 6.2, y0 - 1.0, x=bx, z=bz, segments=6))
      # the cover screw's head in the tab's counterbore
      hr, hd = PP.TAB_KINDS[kind]["head"]
      parts.append(cyl_y(hr - 0.6, T[1] - PP.TAB_T + dy, T[1] - PP.TAB_T + hd - 0.5 + dy, x=T[0], z=T[2], segments=24))
    return union(parts)

  # the car
  def grip(self) -> Manifold:
    t = self.t
    pts = [(t.rr + (PP.GRIP_P / 2) * math.cos(a), (PP.GRIP_P / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    return revolve(pts, 0.0, 360.0, step_deg=1.0)

  def covers(self) -> Manifold:
    return cover_model()

  def hub(self) -> Manifold:
    return cyl(P.HUB_R, P.HUB_BACK_Z, 25.0, segments=96)

  def spoke_zone(self) -> Manifold:
    return cyl(PP.WHEEL_OD_P / 2 - PP.GRIP_P + 1.0, P.SPOKE_BACK_Z, 25.0, segments=180) + self.hub()

  def dash(self) -> Manifold:
    return box(-300, 300, -400, 60, P.DASH_Z - 60.0, P.DASH_Z)

  def stalk(self) -> Manifold:
    return stalk_positions()

  def key(self) -> Manifold:
    return CA.rod(P.KEY_FROM, P.KEY_TO, P.KEY_R)

  def key_room(self) -> Manifold:
    return key_room()

  def key_head(self) -> Manifold:
    return key_room(KEY_HEAD)

  def tilt_lever(self) -> Manifold:
    return tab_lever_sweep()

  def bolster(self) -> Manifold:
    """The knee bolster's face below and beside the column, with its opening round the covers."""
    hw, yb = BOLSTER_OPENING
    wall = box(-300.0, 300.0, -400.0, 60.0, BOLSTER_Z - 40.0, BOLSTER_Z)
    opening = box(-hw, hw, yb, 200.0, BOLSTER_Z - 41.0, BOLSTER_Z + 1.0)
    return wall - opening

  def fingers(self) -> Manifold:
    t = self.t
    behind, inside, outside = FINGERS
    return cyl(PP.WHEEL_OD_P / 2 + outside, behind, 0.0, segments=180) - cyl(t.rr - PP.GRIP_P / 2 - inside, behind - 1, 1, segments=180)

  def teeth_ring(self) -> Manifold:
    """Everywhere the back teeth (and their zip ties' heads) go as the wheel turns: their outline swept all round."""
    t = self.t
    return revolve([(p[0], p[1]) for p in t.profile()], 0.0, 360.0, step_deg=1.0) + \
      (cyl(t.w_out + 6.0, -t.rho - 3.0, 4.0, segments=180) - cyl(t.w_in - 6.0, -t.rho - 4.0, 5.0, segments=180))

  def car_parts(self) -> list:
    return [("column covers", self.covers()), ("hub", self.hub()), ("spoke sweep zone", self.spoke_zone()),
            ("wiper stalk (all positions)", self.stalk()), ("key cylinder", self.key()),
            ("the key in the ignition", self.key_head()), ("adjustment tab, its arm, their swing and your fingers", self.tilt_lever()),
            ("knee bolster", self.bolster())]


def check_all(A: PopAssembly, swing_step: float = 2.5, wheel_step: float = 3.0) -> dict:
  """Overlap volumes (mm^3) between parts that must not touch."""
  res = {}
  T, W = A.teeth(), A.grip()
  G, C, M, S, BO = A.gear(), A.carrier(), A.motor(), A.springs(), A.bolts()
  B, SW, PL, TB = A.block(), A.switch(), A.plate() + A.pad(), A.tabs()
  car = A.car_parts()
  fixed = [("hinge block", B), ("power switch", SW), ("column plate", PL), ("screw tabs", TB + A.tab_bolts())]
  movers = [("motor gear", G), ("carrier", C), ("motor", M), ("springs", S), ("bolts", BO)]
  # on, wheel straight
  pairs = {"teeth/carrier": (T, C), "teeth/motor": (T, M), "teeth/springs": (T, S), "teeth/bolts": (T, BO),
           "grip/carrier": (W, C), "grip/motor": (W, M), "grip/motor gear": (W, G), "grip/springs": (W, S),
           "carrier/motor": (C, M), "springs/carrier": (S, C), "springs/motor": (S, M)}
  for fn, f in fixed:
    for mn, m in movers:
      if fn == "hinge block" and mn == "bolts":
        continue
      pairs[f"{mn}/{fn}"] = (m, f)
    pairs[f"teeth/{fn}"] = (T, f)
    pairs[f"grip/{fn}"] = (W, f)
  pairs["hinge block/column plate"] = (B, PL)
  pairs["power switch/column plate"] = (SW, PL)
  for cn, c in car:
    for mn, m in movers + fixed:
      if mn == "screw tabs" and cn == "column covers":
        continue                          # they're screwed to it, their bosses in its screw cups
      pairs[f"{mn}/{cn}"] = (m, c)
  pairs["hinge block/screw tabs"] = (B, TB)
  for k, (a, b) in pairs.items():
    res["on: " + k] = overlap(a, b)
  # the wheel turned through the teeth and past them (motor on): nothing fixed or carried may meet the teeth piece
  t = A.t
  for w in np.arange(-t.half - 4.0, t.half + 4.0 + 1e-9, wheel_step):
    Tw = A.teeth(float(w))
    for name, part in (("carrier", C), ("motor", M), ("springs", S), ("bolts", BO), ("hinge block", B), ("power switch", SW),
                       ("column plate", PL)):
      key = f"wheel turned, on: teeth/{name} (worst)"
      res[key] = max(res.get(key, 0.0), overlap(Tw, part))
  # past the teeth the carrier drops onto its stop
  d = PP.LIFT_DROP
  Gd, Cd, Md, Sd, BOd = A.gear(d), A.carrier(d), A.motor(d), A.springs(d), A.bolts(d)
  for side, w in (("left", t.half + 3.0), ("right", -t.half - 3.0)):
    Tw = A.teeth(w)
    for name, part in (("gear", Gd), ("carrier", Cd), ("motor", Md), ("springs", Sd)):
      res[f"dropped {abs(d):.0f} deg, wheel turned {side} past the teeth: teeth/{name}"] = overlap(Tw, part)
  for name, part in (("gear", Gd), ("carrier", Cd), ("motor", Md), ("springs", Sd), ("bolts", BOd)):
    res[f"dropped: grip/{name}"] = overlap(W, part)
    for fn, f in fixed:
      if fn == "hinge block" and name == "bolts":
        continue
      res[f"dropped: {name}/{fn}"] = overlap(part, f) if not (fn == "hinge block" and name == "carrier") else 0.0
    for cn, c in car:
      res[f"dropped: {name}/{cn}"] = overlap(part, c)
  # the stops: dropped, the web rests on the block's pad; swung off, likewise (should touch: negative)
  res["drop stop touches at its angle (should touch)"] = -overlap(A.carrier(d - 0.3), B)
  res["off stop touches at its angle (should touch)"] = -overlap(A.carrier(PP.LIFT_OFF + 0.3), B)
  # the lead-in: the roller runs down the band's ends and the carrier follows it to the stop
  worst = 0.0
  for w in np.arange(t.roll_half, t.half + 1.0, 0.5):
    for sign in (1, -1):
      drop = roller_drop(A, sign * float(w))
      for part in (A.gear(-drop, 0.0, "gear_teeth_only"), A.carrier(-drop)):
        worst = max(worst, overlap(A.teeth(sign * float(w)), part))
  res["lead-in, the carrier following the roller down: teeth/gear teeth and teeth/carrier (worst)"] = worst
  # swinging off and back, wheel straight and turned a little either way; and parked, the wheel anywhere
  ring = A.teeth_ring()
  fingers = A.fingers()
  for lift in list(np.arange(PP.LIFT_DROP, PP.LIFT_OFF + 1e-9, swing_step)):
    if abs(lift) < 1e-6:
      continue
    Gl, Cl, Ml, Sl, BOl = A.gear(lift), A.carrier(lift), A.motor(lift), A.springs(lift), A.bolts(lift)
    sw = {"grip/gear": (W, Gl), "grip/carrier": (W, Cl), "grip/motor": (W, Ml), "grip/springs": (W, Sl),
          "springs/carrier": (Sl, Cl), "springs/motor": (Sl, Ml)}
    if lift > 0.5:
      for name, part in (("gear", Gl), ("carrier", Cl), ("motor", Ml), ("springs", Sl), ("bolts", BOl)):
        for w in (0.0, -15.0, 15.0):
          sw[f"teeth at {w:+.0f} deg/{name}"] = (A.teeth(w), part)
    for fn, f in fixed:
      for name, part in (("gear", Gl), ("carrier", Cl), ("motor", Ml), ("springs", Sl), ("bolts", BOl)):
        if fn == "hinge block" and name == "bolts":
          continue
        if fn == "hinge block" and name == "carrier" and lift >= PP.LIFT_OFF - 1e-6:
          continue                        # resting on its stop
        sw[f"{name}/{fn}"] = (part, f)
    for cn, c in car:
      for name, part in (("gear", Gl), ("carrier", Cl), ("motor", Ml), ("springs", Sl), ("bolts", BOl)):
        sw[f"{name}/{cn}"] = (part, c)
    for k, (a, b) in sw.items():
      key = "swinging: " + k + " (worst)"
      res[key] = max(res.get(key, 0.0), overlap(a, b))
  L = PP.LIFT_OFF
  parked = [("gear", A.gear(L)), ("carrier", A.carrier(L)), ("motor", A.motor(L)), ("springs", A.springs(L)), ("bolts", A.bolts(L))]
  room = A.key_room()
  for name, part in parked + [("hinge block", B), ("power switch", SW), ("column plate", PL), ("screw tabs", TB)]:
    res[f"parked: the teeth anywhere round the wheel/{name}"] = overlap(ring, part)
    res[f"parked: your fingers round the grip anywhere/{name}"] = overlap(fingers, part)
    res[f"parked: your fingers turning the key/{name}"] = overlap(room, part)
  for name, part in (("hinge block", B), ("power switch", SW), ("column plate", PL), ("screw tabs", TB)):
    res[f"on: your fingers turning the key/{name}"] = overlap(room, part)
  return res


def flange_fit(mount_deg: float, cover_dy: float = 0.0, plate_dx: float = 0.0) -> dict:
  """With the mount turned to mount_deg, the cover's underside cover_dy higher (+) than the model, and the plate
  dx to the right: where each flange bolt sits along its block slot (+-SLOT_X) and its plate slot (+-SLOT_Y)."""
  block_c = PP.flange_bolts_wheel(mount_deg)          # the bolts' slot middles in the block, now
  plate_c = PP.flange_bolts_wheel()                   # the plate's slot middles (it was made for the nominal mount)
  a = math.radians(mount_deg)
  ux = (math.cos(a), math.sin(a))                     # the block's slots run along its own x
  out = []
  for (bx, by), (px, py) in zip(block_c, plate_c):
    px += plate_dx
    py += cover_dy
    # the bolt is on the plate slot's line x = px, and on the block slot's line through (bx, by) along ux
    s_along = (px - bx) / ux[0]
    y = by + s_along * ux[1]
    out.append({"along_block_slot": round(s_along, 1), "along_plate_slot": round(y - py, 1),
                "fits": abs(s_along) <= PP.SLOT_X and abs(y - py) <= PP.SLOT_Y})
  return {"bolts": out, "fits": all(o["fits"] for o in out)}


def roller_drop(A: PopAssembly, wheel_deg: float) -> float:
  """How far (degrees) the carrier drops with the wheel turned wheel_deg: until the roller rests on the teeth piece's
  lead-in or the carrier reaches its drop stop."""
  roller = PP.pop_roller()
  T = A.teeth(wheel_deg)
  most = -PP.LIFT_DROP
  if overlap(PP.to_wheel(roller, -most), T) <= 1e-3:
    return most
  lo, hi = 0.0, most
  for _ in range(24):
    mid = (lo + hi) / 2
    if overlap(PP.to_wheel(roller, -mid), T) > 1e-3:
      hi = mid
    else:
      lo = mid
  return lo


def mesh_sweep(A: PopAssembly, step: float = 1.0) -> dict:
  worst, at = 0.0, 0.0
  t = A.t
  for w in np.arange(-t.roll_half, t.roll_half + 1e-9, step):
    v = overlap(A.teeth(float(w)), A.gear(0.0, float(w)))
    if v > worst:
      worst, at = v, float(w)
  plays = []
  inner = t.n_teeth // 2 - 3
  for w in (0.0, 0.5 * t.pitch_deg, min(10, inner) * t.pitch_deg, -min(15, inner) * t.pitch_deg):
    T = A.teeth(w)
    res = []
    for sgn in (1, -1):
      a = 0.0
      while a < 10.0:
        g = PP.to_wheel(A.p["gear_teeth_only"].rotate((0, 0, MESH_PHASE - FP.FACE_RATIO * w + sgn * (a + 0.05))), 0.0)
        if overlap(T, g) > 1e-4:
          break
        a += 0.05
      res.append(round(a, 2))
    plays.append(res)
  return {"worst_overlap_mm3": round(worst, 4), "worst_at_deg": round(at, 1), "free_play_motor_gear_deg": plays,
          "free_play_steering_wheel_deg": round(min(min(p) for p in plays) * 2 / FP.FACE_RATIO, 3)}


def gap(moving: Manifold, fx: Manifold, direction, far: float = 30.0) -> float:
  lo, hi = 0.0, far
  d = np.asarray(direction, dtype=float)
  if overlap(moving, fx) > 1e-3:
    return 0.0
  for _ in range(24):
    mid = (lo + hi) / 2
    if overlap(moving.translate(tuple(d * mid)), fx) > 1e-3:
      hi = mid
    else:
      lo = mid
  return round(lo, 2)


def switch_states() -> dict:
  """Where the switch's roller sits (mm from its holes' line) as the carrier swings: pressed while the motor is on."""
  out = {}
  for lift in (PP.LIFT_DROP, 0.0, 1.0, 2.0, 2.5, 3.0, 4.0, 5.0, 10.0):
    b = PP.SW_BETA + lift                  # the carrier's angle facing the roller
    b0, b1 = PP.SW_BETA + PP.LOBE_ON[0], PP.SW_BETA + PP.LOBE_ON[1]
    if b0 <= b <= b1:
      r = PP.LOBE_R
    elif b1 < b < b1 + PP.LOBE_RAMP:
      r = PP.KNUCKLE_R + (PP.LOBE_R - PP.KNUCKLE_R) * ((b1 + PP.LOBE_RAMP) - b) / PP.LOBE_RAMP
    else:
      r = PP.KNUCKLE_R
    pos = PP.SW_HOLES_R - r
    state = "pressed" if pos <= MP.SW_OP - MP.SW_OP_TOL else ("let go" if pos >= MP.SW_OP + MP.SW_OP_TOL + MP.SW_MD else "between")
    out[lift] = (round(pos, 2), state)
  return out


def spring_rows() -> list:
  rows = []
  for lift in (PP.LIFT_DROP, 0.0, 10.0, 25.0, 40.0, PP.DEAD_DEG, 60.0, PP.LIFT_OFF):
    rows.append({"lift": lift, "length_pins": round(PP.spring_length_pins(lift), 2), "pull_N": round(PP.spring_force(lift), 1),
                 "torque_Nm": round(PP.spring_torque(lift) / 1000.0, 3),
                 "pull_N_if_over_loops": round(PP.spring_force(lift, inside_loops=False), 1),
                 "torque_Nm_if_over_loops": round(PP.spring_torque(lift, inside_loops=False) / 1000.0, 3)})
  return rows


def check_adjusted(A: PopAssembly, adj: float, swing_step: float = 5.0) -> dict:
  """The mount turned adj degrees round the column from where it was made for (the plate and its tabs stay put): the
  mount's parts against the plate, the tabs, the covers, the knee bolster and the adjustment tab, on and swinging off.
  (The wiper stalk and the key are what the turning is for, so they're left to you in the car.)"""
  res = {}
  keep = PP.MOUNT_DEG
  try:
    PP.MOUNT_DEG = keep + adj
    B, SW = A.block(), A.switch()
    PL, TB = A.plate() + A.pad(), A.tabs() + A.tab_bolts()
    others = [("column covers", A.covers()), ("knee bolster", A.bolster()), ("adjustment tab, its swing and your fingers", A.tilt_lever()),
              ("column plate", PL), ("screw tabs", TB)]
    res[f"turned {adj:+.0f}: hinge block/column plate"] = overlap(B, PL)
    res[f"turned {adj:+.0f}: hinge block/screw tabs"] = overlap(B, TB)
    res[f"turned {adj:+.0f}: power switch/column plate"] = overlap(SW, PL)
    for lift in list(np.arange(PP.LIFT_DROP, PP.LIFT_OFF + 1e-9, swing_step)) + [PP.LIFT_OFF]:
      movers = [("gear", A.gear(lift)), ("carrier", A.carrier(lift)), ("motor", A.motor(lift)), ("springs", A.springs(lift)),
                ("bolts", A.bolts(lift))]
      for mn, m in movers:
        for on, o in others:
          k = f"turned {adj:+.0f}, swinging: {mn}/{on} (worst)"
          res[k] = max(res.get(k, 0.0), overlap(m, o))
    for on, o in others[:3]:
      res[f"turned {adj:+.0f}: hinge block/{on}"] = overlap(B, o)
    fit = flange_fit(PP.MOUNT_DEG)
    res[f"turned {adj:+.0f}: the flange bolts outside their slots"] = 0.0 if fit["fits"] else 1.0
  finally:
    PP.MOUNT_DEG = keep
  return res

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
STALK_DOWN_DEG = 30.0      # the wiper stalk pushed all the way down (HI): an estimate, not measured
STALK_UP_DEG = 10.0        # ... and lifted for MIST
STALK_LEN = 105.0          # your tape: the stalk sticks out about 105 mm from the cover
KEY_ROOM = (22.0, 60.0)    # the key in its cylinder and your fingers turning it: radius and length out from the bezel
TILT_LEVER_ZONE = (-45.0, 8.0, -130.0, -48.0, -200.0, -45.0)   # the tilt lever, tucked up to hanging down (estimate from
                                                                 # your photos: left of the middle, under the cover)
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


def key_room() -> Manifold:
  kd = np.array(P.KEY_TO) - np.array(P.KEY_FROM)
  kd /= np.linalg.norm(kd)
  r, L = KEY_ROOM
  return CA.rod(np.array(P.KEY_TO), np.array(P.KEY_TO) + L * kd, r)


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
    cy, cz = PP.turn(PP.C_BOLT, lift)
    by, bz = PP.B_BOLT
    hy, hz = PP.HINGE_P
    c = cyl_x(2.5, -44.0, 44.0, y=cy, z=cz, segments=16) + cyl_x(4.6, -48.0, -44.0, y=cy, z=cz, segments=16) + \
      cyl_x(4.6, 39.5, 45.0, y=cy, z=cz, segments=6)
    b = cyl_x(2.5, -44.0, 44.0, y=by, z=bz, segments=16) + cyl_x(4.6, -48.0, -44.0, y=by, z=bz, segments=16) + \
      cyl_x(4.6, 39.5, 45.0, y=by, z=bz, segments=6)
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

  def pads(self) -> Manifold:
    return PP.pop_plate_pads().translate((0, self.cover_bottom - P.COVER_BOTTOM, 0))

  # the car
  def grip(self) -> Manifold:
    t = self.t
    pts = [(t.rr + (PP.GRIP_P / 2) * math.cos(a), (PP.GRIP_P / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    return revolve(pts, 0.0, 360.0, step_deg=1.0)

  def covers(self) -> Manifold:
    return CA.ColumnAssembly.covers(self.side)

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

  def tilt_lever(self) -> Manifold:
    return box(*TILT_LEVER_ZONE)

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
            ("the key and your fingers on it", self.key_room()), ("tilt lever's swing", self.tilt_lever()),
            ("dash below the column", self.dash())]


def check_all(A: PopAssembly, swing_step: float = 2.5, wheel_step: float = 3.0) -> dict:
  """Overlap volumes (mm^3) between parts that must not touch."""
  res = {}
  T, W = A.teeth(), A.grip()
  G, C, M, S, BO = A.gear(), A.carrier(), A.motor(), A.springs(), A.bolts()
  B, SW, PL, PD = A.block(), A.switch(), A.plate(), A.pads()
  car = A.car_parts()
  fixed = [("hinge block", B), ("power switch", SW), ("column plate", PL), ("plate's rubber strips", PD)]
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
      pairs[f"{mn}/{cn}"] = (m, c)
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
  for name, part in parked + [("hinge block", B), ("power switch", SW), ("column plate", PL)]:
    res[f"parked: the teeth anywhere round the wheel/{name}"] = overlap(ring, part)
    res[f"parked: your fingers round the grip anywhere/{name}"] = overlap(fingers, part)
  return res


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

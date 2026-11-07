"""
The back-teeth mount in the car, and the checks that it fits and works: the motor gear meshing the back teeth through
their whole arc with no overlap and some free play; nothing touching with the lift lever down, up and at every angle
between, nor with the steering wheel turned past the teeth (the carrier dropping along the lead-in); the setup gauge
fitting; the arm reaching from the column plate's joint to the hinge block's with both joints within their range; and
everything fixed clear of the column covers, the hub, the zone the spokes sweep, the wiper stalk, the key cylinder
and the dash.

Frames: see faceparts.py. Parts drawn in the carrier frame are lifted about the hinge (as on the other mounts), then
put in the steering wheel frame by faceparts.mount_rot() and the motor's front face at (R_FACE, 0, z_axis).
"""
import math
from dataclasses import dataclass, field

import numpy as np
from manifold3d import Manifold

import assembly as AS
import columnassembly as CA
import faceparts as FP
import mountparts as MP
from cadlib import cyl, revolve, union
from params import COVER_BOTTOM, COVER_FRONT_W, COVER_H, COVER_W, GRIP, PLATE_FRONT_Z

MESH_PHASE = 180.0 / FP.FACE_MOTOR_TEETH     # the motor gear turned this much more puts a tooth (not a gap) at the teeth


@dataclass
class FaceFit:
  ok: bool
  j1: np.ndarray            # the column plate's joint bolt (steering wheel frame)
  j2: np.ndarray            # the hinge block's joint bolt
  reach: float              # bolt to bolt
  arm_len: float            # the arm to print, 0 if none fits
  slide: float
  j1_deg: float             # the arm's direction at each joint, and how far that is from the middle of its slot
  j1_off: float
  j2_off: float
  notes: list = field(default_factory=list)


def solve_face(t: FP.FaceTeeth, cover_bottom: float = COVER_BOTTOM) -> FaceFit:
  """Which arm reaches from the column plate's joint (the plate under a cover whose underside is cover_bottom below
  the column's axis) to the hinge block's, and at what angles. The plate's ears are drawn for COVER_BOTTOM, so the
  joints turn to take up the difference."""
  j2 = FP.j2_wheel(t)
  j1 = np.array([FP.J1_W[0], FP.J1_W[1] + (cover_bottom - COVER_BOTTOM), j2[2]])
  d = j2 - j1
  reach = float(np.linalg.norm(d[:2]))
  a1 = math.degrees(math.atan2(d[1], d[0]))
  u0 = -FP.nominal_arm_dir(t)
  a1_nom = math.degrees(math.atan2(u0[1], u0[0]))
  off = (a1 - a1_nom + 180.0) % 360.0 - 180.0
  notes = []
  fits = [L for L in FP.ARM_LENGTHS_F if abs(reach - L) <= FP.ARM_SLIDE_F - 0.5]
  arm_len = min(fits, key=lambda L: abs(reach - L)) if fits else 0.0
  if not fits:
    notes.append(f"the column plate's joint is {reach:.0f} mm from the hinge block's; the arms cover "
                 f"{FP.ARM_LENGTHS_F[0] - FP.ARM_SLIDE_F:.0f} to {FP.ARM_LENGTHS_F[-1] + FP.ARM_SLIDE_F:.0f}")
  for name in ("column plate's", "hinge block's"):
    if abs(off) > FP.LOCK_RANGE_F - 0.5:
      notes.append(f"the arm is {off:+.1f} degrees from the middle of the {name} joint, which covers +-{FP.LOCK_RANGE_F:.0f}")
  return FaceFit(not notes, j1, j2, reach, float(arm_len), reach - arm_len if arm_len else 0.0, a1, off, off, notes)


class FaceAssembly(AS.Assembly):
  """The back-teeth mount in the steering wheel frame (the motor at 3 o'clock)."""

  def __init__(self, t: FP.FaceTeeth, fit: FaceFit, parts: dict, cover_w: float = COVER_W, cover_h: float = COVER_H,
               cover_front_w: float = COVER_FRONT_W, front_z: float = PLATE_FRONT_Z):
    self.t, self.fit, self.p = t, fit, parts
    self.R = FP.mount_rot()
    self.T = np.array([FP.R_FACE, 0.0, t.z_axis])
    self.hinge_c = np.array([0.0, MP.HINGE[0], MP.HINGE[1]])
    self.cover_w, self.cover_h, self.cover_front_w = cover_w, cover_h, cover_front_w
    self.front_z = front_z
    if fit.arm_len and "arm" not in parts:
      parts["arm"] = FP.face_arm(fit.arm_len)
    # the column covers, hub, spokes' zone, dash, stalk and key: the column mounts' estimates
    self._side = CA.SideAssembly.__new__(CA.SideAssembly)
    self._side.cover_w, self._side.cover_h, self._side.cover_front_w = cover_w, cover_h, cover_front_w

  def _m(self, m: Manifold) -> Manifold:
    """Carrier frame -> steering wheel frame."""
    return AS.place(m, self.R, self.T)

  def _carried(self, m: Manifold, lift: float) -> Manifold:
    if lift:
      m = AS.turn_about_x(m, -lift, self.hinge_c)
    return self._m(m)

  def gear(self, lift=0.0, wheel_deg: float = 0.0, part: str = "gear"):
    """The motor gear, turned with the wheel (FACE_RATIO times as far) and set so a tooth meets the teeth."""
    return self._carried(self.p[part].rotate((0, 0, MESH_PHASE + FP.FACE_RATIO * wheel_deg)), lift)

  def hinge_block(self):
    return self._m(self.p["hinge_block"])

  def arm(self):
    u = self.fit.j2 - self.fit.j1
    u = u / np.linalg.norm(u)
    y = np.array([0.0, 0.0, 1.0])
    x = np.cross(y, u)
    rot = np.stack([x, y, u], axis=1)
    origin = self.fit.j1 + self.fit.slide * u
    return AS.place(self.p["arm"], rot, origin)

  def plate(self):
    return self.p["plate"]

  def plate_pads(self):
    return FP.plate_pads(self.front_z)

  def joint_bolts(self) -> Manifold:
    """The four M5 bolts of the two joints (heads, washers, lock nuts), steering wheel frame."""
    out = []
    zc = self.fit.j1[2]
    half = FP.ARM_T_F / 2 + MP.GAP + FP.J_EAR_T
    u = self.fit.j2 - self.fit.j1
    u = u / np.linalg.norm(u)
    for p in (self.fit.j1, self.fit.j1 + FP.LOCK_R_F * u, self.fit.j2, self.fit.j2 - FP.LOCK_R_F * u):
      out.append(cyl(2.5, zc - half - 6.0, zc + half + 6.0, float(p[0]), float(p[1]), 16))
      out.append(cyl(4.3, zc + half + MP.M5_WASHER_T, zc + half + MP.M5_WASHER_T + 5.0, float(p[0]), float(p[1]), 24))
      out.append(cyl(4.6, zc - half - MP.M5_WASHER_T - MP.M5_NYLOC_T, zc - half, float(p[0]), float(p[1]), 24))
    return union(out)

  def teeth(self, wheel_deg: float = 0.0):
    return self.p["teeth"].rotate((0, 0, wheel_deg))

  def wheel_grip(self):
    t = self.t
    pts = [(t.rr + (GRIP / 2) * math.cos(a), (GRIP / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    return revolve(pts, 0.0, 360.0, step_deg=1.0)

  def covers(self):
    return CA.ColumnAssembly.covers(self._side)

  def hub(self):
    return CA.ColumnAssembly.hub(self._side)

  def spoke_zone(self):
    return CA.ColumnAssembly.spoke_zone(self._side)

  def dash(self):
    return CA.ColumnAssembly.dash(self._side)

  def stalk(self):
    return CA.SideAssembly.stalk(self._side)

  def key(self):
    return CA.SideAssembly.key(self._side)

  def car_parts(self, dash: bool = True) -> list:
    out = [("column covers", self.covers()), ("hub", self.hub()), ("spoke sweep zone", self.spoke_zone()),
           ("wiper stalk", self.stalk()), ("key cylinder", self.key())]
    return out + ([("dash below the column", self.dash())] if dash else [])

  def mount_parts(self) -> list:
    return [("column plate", self.plate()), ("joint bolts", self.joint_bolts())]


def overlap(a: Manifold, b: Manifold) -> float:
  return (a ^ b).volume()


def roller_drop_deg(A: FaceAssembly, wheel_deg: float) -> float:
  """How far (degrees about the hinge) the carrier drops with the wheel turned wheel_deg: until the roller rests on
  the teeth piece (the lead-in) or the lever's rounded end stops it at DROP_DEG."""
  roller = FP.face_roller()
  T = A.teeth(wheel_deg)
  if overlap(A._carried(roller, -MP.DROP_DEG), T) <= 1e-3:
    return MP.DROP_DEG
  lo, hi = 0.0, MP.DROP_DEG
  for _ in range(24):
    mid = (lo + hi) / 2
    if overlap(A._carried(roller, -mid), T) > 1e-3:
      hi = mid
    else:
      lo = mid
  return lo


def mesh_sweep(A: FaceAssembly, step: float = 1.0) -> dict:
  """The motor gear's teeth and roller turned with the wheel over the whole tracked arc: their overlap with the
  teeth piece (should be none), and the free play at a few places (how far the gear turns each way with the wheel
  held, before its teeth touch)."""
  worst, at = 0.0, 0.0
  t = A.t
  for w in np.arange(-t.roll_half, t.roll_half + 1e-9, step):
    v = overlap(A.teeth(float(w)), A.gear(0.0, float(w)))
    if v > worst:
      worst, at = v, float(w)
  plays = []
  for w in (0.0, 0.5 * t.pitch_deg, 10.0 * t.pitch_deg, -15.0 * t.pitch_deg):
    T = A.teeth(w)
    res = []
    for sgn in (1, -1):
      a = 0.0
      while a < 10.0:
        g = A._carried(A.p["gear_teeth_only"].rotate((0, 0, MESH_PHASE + FP.FACE_RATIO * w + sgn * (a + 0.05))), 0.0)
        if overlap(T, g) > 1e-4:
          break
        a += 0.05
      res.append(round(a, 2))
    plays.append(res)
  return {"worst_overlap_mm3": round(worst, 4), "worst_at_deg": round(at, 1),
          "free_play_motor_gear_deg": plays, "free_play_steering_wheel_deg": round(min(min(p) for p in plays) * 2 / FP.FACE_RATIO, 3)}


def check_all(A: FaceAssembly, lever_step: float = 4.0, dash: bool = True) -> dict:
  """Overlap volumes (mm^3) between parts that must not touch, as columnassembly.check_all, for the back-teeth mount."""
  res = {}
  T, W = A.teeth(), A.wheel_grip()
  G, C, M = A.gear(), A.carrier(), A.motor()
  HB, AR, BR, SW = A.hinge_block(), A.arm(), A.bracket(), A.switch()
  LV = A.lever(0.0, 0.0)
  car, mount = A.car_parts(dash), A.mount_parts()
  cp = dict(car)
  pairs = {
    "teeth/gear": (T, G), "teeth/carrier": (T, C), "teeth/motor": (T, M), "grip/carrier": (W, C), "grip/motor": (W, M),
    "grip/gear": (W, G), "carrier/motor": (C, M), "carrier/hinge block": (C, HB), "motor/hinge block": (M, HB),
    "carrier/lever": (C, LV), "lever/hinge block": (LV, HB), "lever/lever bracket": (LV, BR),
    "lever bracket/hinge block": (BR, HB), "lever bracket/carrier": (BR, C), "lever bracket/motor": (BR, M),
    "lever bracket/teeth": (BR, T), "switch/lever": (SW, LV), "switch/hinge block": (SW, HB), "switch/carrier": (SW, C),
    "hinge block/arm": (HB, AR), "arm/carrier": (AR, C), "arm/motor": (AR, M), "arm/teeth": (AR, T),
    "hinge block/teeth": (HB, T), "lever/arm": (LV, AR), "lever bracket/arm": (BR, AR), "switch/arm": (SW, AR),
    "lever/teeth": (LV, T), "lever/grip": (LV, W), "hinge block/grip": (HB, W), "arm/grip": (AR, W),
  }
  for name, part in mount:
    pairs[f"arm/{name}"] = (AR, part) if name != "joint bolts" else (AR, Manifold())
    pairs[f"hinge block/{name}"] = (HB, part) if name != "joint bolts" else (HB, Manifold())
  pairs["column plate/joint bolts"] = (Manifold(), Manifold())
  sws = {dy: A._carried(MP.switch_screws(dy=dy), 0.0) for dy in (-MP.SW_SLOT, 0.0, MP.SW_SLOT)}
  LB = A._carried(MP.lever_bolt(), 0.0)
  for dy, sw in sws.items():
    pairs[f"switch screws ({dy:+.0f} mm in slots)/hinge block"] = (sw, HB)
    pairs[f"switch screws ({dy:+.0f} mm in slots)/arm"] = (sw, AR)
  pairs.update({"lever bolt/hinge block": (LB, HB), "lever bolt/arm": (LB, AR), "lever bolt/teeth": (LB, T),
                "hinge bolt, washers and nut/hinge block": (A._carried(MP.hinge_bolt(), 0.0), HB),
                "room for a hex key and socket on the lever bolt/hinge block": (A._carried(MP.lever_bolt_tools(), 0.0), HB),
                "room for a hex key and socket on the lever bolt/arm": (A._carried(MP.lever_bolt_tools(), 0.0), AR),
                "joint bolts/carrier": (A.joint_bolts(), C), "joint bolts/motor": (A.joint_bolts(), M),
                "joint bolts/lever": (A.joint_bolts(), LV)})
  fixed = tuple(car) + tuple(mount)
  movers = (("motor gear", G), ("carrier", C), ("motor", M), ("hinge block", HB), ("lever bracket", BR), ("switch", SW),
            ("lift lever", LV), ("lever bolt", LB), ("back teeth", T))
  for fixed_name, fx in fixed:
    for mover_name, mover in movers:
      if mover_name == "hinge block" and fixed_name == "joint bolts":
        continue
      pairs[f"{mover_name}/{fixed_name}"] = (mover, fx)
  for name, part in car:
    pairs[f"arm/{name}"] = (AR, part)
  for k, (a, b) in pairs.items():
    if a.is_empty() or b.is_empty():
      continue
    res["down: " + k] = overlap(a, b)
  # the back teeth turned through their arc and past: nothing fixed may touch them anywhere (the teeth piece itself,
  # and its zip ties' heads, which stand up to 6 mm off the walls)
  for w in np.arange(-A.t.half - 2.0, A.t.half + 2.0 + 1e-9, 4.0):
    Tw = A.teeth(float(w))
    for name, part in (("carrier", C), ("motor", M), ("hinge block", HB), ("arm", AR), ("lift lever", LV),
                       ("lever bracket", BR), ("column plate", A.plate())):
      key = f"wheel turned: teeth/{name} (worst)"
      res[key] = max(res.get(key, 0.0), overlap(Tw, part))
  gauge = A._carried(MP.setup_gauge(), 0.0)
  for k, b in {"lever bracket": BR, "spring": A._carried(MP.spring_body(), 0.0), "switch": SW, "carrier": C,
               "hinge block": HB, "arm": AR, "lift lever": LV}.items():
    res[f"setup gauge in: gauge/{k}"] = overlap(gauge, b)
  # lift lever up
  lift = max(0.0, MP.cam_lift(MP.A_OFF))
  hair = lift + 0.05
  Gl, Cl, Ml, BRl, SWl = A.gear(lift), A.carrier(hair), A.motor(hair), A.bracket(hair), A.switch(hair)
  LVo = A.lever(MP.A_OFF, hair)
  tag = f"lever up (lift {lift:.1f} deg): "
  up = {"teeth/gear": (T, Gl), "carrier/hinge block": (Cl, HB), "motor/hinge block": (Ml, HB),
        "carrier/arm": (Cl, AR), "motor/arm": (Ml, AR), "lever bracket/hinge block": (BRl, HB),
        "lever bracket/arm": (BRl, AR), "switch/hinge block": (SWl, HB), "lever/hinge block": (LVo, HB),
        "lever/arm": (LVo, AR), "lever/lever bracket": (LVo, BRl), "lever/carrier": (LVo, Cl), "lever/teeth": (LVo, T),
        "lever/grip": (LVo, W), "carrier/teeth": (Cl, T), "carrier/grip": (Cl, W), "motor/teeth": (Ml, T),
        "lever bolt/hinge block": (A._carried(MP.lever_bolt(), hair), HB),
        "switch screws/hinge block": (A._carried(MP.switch_screws(dy=-MP.SW_SLOT), hair), HB)}
  for name, part in fixed:
    up[f"lever/{name}"] = (LVo, part)
    up[f"carrier/{name}"] = (Cl, part)
    up[f"motor/{name}"] = (Ml, part)
    up[f"lever bracket/{name}"] = (BRl, part)
  for k, (a, b) in up.items():
    res[tag + k] = overlap(a, b)
  for alpha in list(np.arange(lever_step, MP.A_OFF - 0.5, lever_step)) + [MP.A_OFF - 0.5]:
    th = max(0.0, MP.cam_lift(alpha)) + 0.05
    lv = A.lever(alpha, th, part="lever_no_tab")
    br, ca, ge = A.bracket(th), A.carrier(th), A.gear(th)
    swept = {"lever/hinge block": (lv, HB), "lever/arm": (lv, AR), "lever/lever bracket": (lv, br),
             "lever/carrier": (lv, ca), "carrier/hinge block": (ca, HB), "carrier/arm": (ca, AR),
             "lever bracket/hinge block": (br, HB), "lever bracket/arm": (br, AR), "lever/teeth": (lv, T),
             "lever/grip": (lv, W), "carrier/teeth": (ca, T), "carrier/grip": (ca, W), "gear/teeth": (ge, T),
             "lever bolt/hinge block": (A._carried(MP.lever_bolt(), th), HB),
             "switch screws/hinge block": (A._carried(MP.switch_screws(dy=-MP.SW_SLOT), th), HB)}
    for name, part in fixed:
      swept[f"lever/{name}"] = (lv, part)
      swept[f"carrier/{name}"] = (ca, part)
      swept[f"lever bracket/{name}"] = (br, part)
    for k, (a, b) in swept.items():
      key = "lever swept: " + k
      res[key] = max(res.get(key, 0.0), overlap(a, b))
  tab = A.lever(0.0, 0.0, part="tab")
  res["click: tab clear of the bracket, lever down"] = overlap(tab, BR)
  res["click: tab meets its ridge lifting (should touch)"] = -max(overlap(A.lever(a, 0.0, part="tab"), BR) for a in (0.75, 1.25, 1.75))
  res["lever stops past up (should touch)"] = -overlap(A.lever(MP.A_OFF + 4.0, hair), HB)
  # the wheel turned past the teeth: the carrier fully dropped (the lever's rounded end on the hinge block)
  rest = -MP.DROP_DEG
  Gr, Cr, Mr, BRr, SWr = A.gear(rest), A.carrier(rest), A.motor(rest), A.bracket(rest), A.switch(rest)
  LVr, LBr = A.lever(0.0, rest), A._carried(MP.lever_bolt(), rest)
  checks = {"grip/gear": (W, Gr), "grip/carrier": (W, Cr), "grip/motor": (W, Mr), "carrier/hinge block": (Cr, HB),
            "motor/hinge block": (Mr, HB), "lever bracket/hinge block": (BRr, HB), "switch/hinge block": (SWr, HB),
            "carrier/arm": (Cr, AR), "lever bracket/arm": (BRr, AR), "lever/hinge block": (LVr, HB),
            "lever bolt/hinge block": (LBr, HB)}
  for name, part in fixed:
    checks[f"carrier/{name}"] = (Cr, part)
    checks[f"gear/{name}"] = (Gr, part)
    checks[f"lever/{name}"] = (LVr, part)
  for side, w in (("left", A.t.half + 3.0), ("right", -A.t.half - 3.0)):
    TT = A.teeth(w)
    for name, part in (("carrier", Cr), ("gear", Gr), ("lever bracket", BRr), ("motor", Mr), ("switch", SWr),
                       ("lift lever", LVr), ("lever bolt", LBr)):
      checks[f"teeth turned {side}/{name}"] = (TT, part)
  for k, (a, b) in checks.items():
    res[f"wheel turned past the teeth, carrier down {-rest:.1f} deg: " + k] = overlap(a, b)
  # along the lead-in at each end the roller rides down (or up) and the carrier drops with it: the gear's teeth and the
  # carrier must clear the teeth piece all along it
  worst = 0.0
  for w in np.arange(A.t.roll_half, A.t.half + 1.0, 0.5):
    for sign in (1, -1):
      drop = roller_drop_deg(A, sign * float(w))
      for part in (A._carried(A.p["gear_teeth_only"].rotate((0, 0, MESH_PHASE)), -drop), A.carrier(-drop)):
        worst = max(worst, overlap(A.teeth(sign * float(w)), part))
  res["lead-in with the carrier dropping: teeth/gear teeth and teeth/carrier (worst)"] = worst
  return res


def gap(moving: Manifold, fx: Manifold, direction, far: float = 25.0) -> float:
  lo, hi = 0.0, far
  d = np.asarray(direction, dtype=float)
  if overlap(moving, fx) > 1e-3:
    return 0.0
  for _ in range(26):
    mid = (lo + hi) / 2
    if overlap(moving.translate(tuple(d * mid)), fx) > 1e-3:
      hi = mid
    else:
      lo = mid
  return round(lo, 2)


def clearances(A: FaceAssembly) -> dict:
  """How far apart the parts that come closest are (mm)."""
  lift = MP.cam_lift(MP.A_OFF)
  return {"motor_gear_off_the_teeth_with_lever_up": gap(A.gear(lift), A.teeth(), (0.0, 0.0, -1.0)),
          "lift_lever_to_the_spoke_sweep_zone": gap(A.lever(0.0, 0.0), A.spoke_zone(), (0.0, 0.0, 1.0)),
          "carrier_and_motor_to_the_grip": gap(A.carrier() + A.motor(), A.wheel_grip(), (-1.0, 0.0, 0.0)),
          "motor_and_board_to_the_dash": gap(A.motor(), A.dash(), (0.0, 0.0, -1.0), 400.0),
          "arm_to_the_column_covers": gap(A.arm(), A.covers(), (0.0, 1.0, 0.0)),
          "joint_ears_to_the_key_cylinder": gap(A.plate(), A.key(), (0.0, 0.0, 1.0)),
          "lift_lever_to_the_wiper_stalk": gap(A.lever(0.0, 0.0) + A.lever(MP.A_OFF, lift), A.stalk(), (0.0, 1.0, 0.0)),
          "hinge_block_and_motor_to_the_wiper_stalk": gap(A.hinge_block() + A.motor(), A.stalk(), (0.0, 1.0, 0.0))}

"""
The column mount in the car: the motor under the steering wheel, behind it, its gear inside the ring teeth; the
carrier, hinge block, lever bracket, lift lever and spring as on the dash mount; the arm up to the column clamp
round the steering column covers. Checks that nothing touches: the ring teeth, the part of the wheel you hold, the
hub, the zone the wheel's spokes sweep through when the wheel is turned far, the steering column covers, the dash
panel below the column, and the clamp's own parts, with the lift lever down, up and at every angle between.

Frames: the steering wheel frame (see assembly.py); the carrier frame moved to the motor's front face at
(0, -centre distance, Z_MOTOR_FACE_C), not turned: the hinge is still on the hub's side of the motor and the spring
still presses the motor gear away from the hub, into the ring. The lower saddle's frame has its V's middle at
y = 0, +y up, +z towards the driver; it sits under the covers at (0, saddle_y, CLAMP_Z).
"""
import math
from dataclasses import dataclass, field

import numpy as np
from manifold3d import Manifold

import assembly as AS
import columnparts as CP
import mountparts as MP
import wheelparts as WP
from cadlib import box, cyl, revolve, union
from params import (ARM_LENGTHS, ARM_SLIDE, CLAMP_Z, COVER_FRONT_Z, COVER_H, COVER_W, DASH_Z, GRIP, HUB_BACK_Z, HUB_R,
                    SPOKE_BACK_Z, WHEEL_OD, WINDOW_DEG, Z_MOTOR_FACE_C)


def saddle_y(cover_w: float = COVER_W, cover_h: float = COVER_H) -> float:
  """Where the lower saddle's V middle sits below the column's axis: the covers are taken as an oval cover_w wide and
  cover_h tall, resting on the rubber strips where the oval's slope matches the V's."""
  a, b = cover_w / 2.0, cover_h / 2.0
  tv = math.tan(math.radians(CP.V_DEG))
  # slope of the oval's lower side equals tv at x_c: (b / a^2) x / sqrt(1 - (x / a)^2) = tv
  k = b / a ** 2
  x_c = math.sqrt(tv ** 2 / (k ** 2 + tv ** 2 / a ** 2))
  y_c = -b * math.sqrt(max(0.0, 1.0 - (x_c / a) ** 2))
  y_pad = -x_c * tv + CP.PAD_T / math.cos(math.radians(CP.V_DEG))
  return y_c - y_pad


@dataclass
class ColumnFit:
  ok: bool
  arm_deg: float           # arm's angle to the steering column (0 = along it, towards the dashboard)
  reach: float             # clamp bolt to hinge block bolt, mm
  arm_len: float           # the arm to print, 0 if none fits
  slide: float
  pivot_w: np.ndarray      # the clamp's arm bolt, steering wheel frame
  notes: list = field(default_factory=list)


def joint_w() -> np.ndarray:
  """The hinge block's arm bolt, steering wheel frame."""
  return np.array([0.0, -CP.centre_distance() + MP.PIVOT[0], Z_MOTOR_FACE_C + MP.PIVOT[1]])


def pivot_w(cover_w: float = COVER_W, cover_h: float = COVER_H, clamp_z: float = CLAMP_Z) -> np.ndarray:
  return np.array([0.0, saddle_y(cover_w, cover_h) + CP.PIVOT_C[0], clamp_z + CP.PIVOT_C[1]])


def solve(cover_w: float = COVER_W, cover_h: float = COVER_H, clamp_z: float = CLAMP_Z) -> ColumnFit:
  """Which arm reaches from the clamp's bolt to the hinge block's bolt, and at what angle."""
  pv = pivot_w(cover_w, cover_h, clamp_z)
  d = joint_w() - pv
  reach = float(math.hypot(d[1], d[2]))
  arm = math.degrees(math.atan2(-d[1], d[2]))
  notes = []
  fits = [L for L in ARM_LENGTHS if abs(reach - L) <= ARM_SLIDE - 0.5]
  arm_len = min(fits, key=lambda L: abs(reach - L)) if fits else 0.0
  if not fits:
    notes.append(f"the clamp's bolt is {reach:.0f} mm from the hinge block's; the arms cover "
                 f"{ARM_LENGTHS[0] - ARM_SLIDE:.0f} to {ARM_LENGTHS[-1] + ARM_SLIDE:.0f}")
  if abs(arm - MP.ARM_NOMINAL) > MP.LOCK_RANGE - 0.5:
    notes.append(f"arm at {arm:.1f} degrees to the steering column; the hinge block's joint covers "
                 f"{MP.ARM_NOMINAL - MP.LOCK_RANGE:.0f} to {MP.ARM_NOMINAL + MP.LOCK_RANGE:.0f}")
  if not (CP.ARM_ANGLES[0] + 0.5 <= arm <= CP.ARM_ANGLES[1] - 0.5):
    notes.append(f"arm {arm:.1f} degrees below the column; the clamp's joint covers {CP.ARM_ANGLES[0]:.0f} to {CP.ARM_ANGLES[1]:.0f}")
  return ColumnFit(not notes, arm, reach, float(arm_len), reach - arm_len if arm_len else 0.0, pv, notes)


class ColumnAssembly(AS.Assembly):
  def __init__(self, t: CP.RingTeeth, fit: ColumnFit, parts: dict, cover_w: float = COVER_W, cover_h: float = COVER_H,
               clamp_z: float = CLAMP_Z):
    self.t, self.fit, self.p = t, fit, parts
    self.cd = CP.centre_distance()
    self.b_org = np.array([0.0, -self.cd, Z_MOTOR_FACE_C])
    self.hinge_w = self.b_org + np.array([0.0, MP.HINGE[0], MP.HINGE[1]])
    self.a_rot = AS.rot_x(fit.arm_deg)
    self.cover_w, self.cover_h, self.clamp_z = cover_w, cover_h, clamp_z
    self.saddle_org = np.array([0.0, saddle_y(cover_w, cover_h), clamp_z])
    self.up, self.rear = np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0])   # column frame: up is 12 o'clock
    if fit.arm_len and "arm" not in parts:
      parts["arm"] = MP.arm(fit.arm_len)

  def clamp(self):
    """The lower saddle with the arm joint."""
    return self.p["clamp_lower"].translate(tuple(self.saddle_org))

  def clamp_upper(self):
    m = self.p["clamp_upper"].rotate((0, 0, 180)).rotate((180, 0, 0))     # V opening down, +z kept towards the driver
    return m.translate((0.0, -self.saddle_org[1], self.clamp_z))

  def rods(self):
    return CP.rods_and_nuts(self.cover_h + 2 * (-self.saddle_org[1] - self.cover_h / 2 - CP.PAD_T)).translate(tuple(self.saddle_org))

  def pads(self):
    return CP.pads().translate(tuple(self.saddle_org))

  def covers(self, back_z: float = -400.0):
    """The steering column covers: an oval cover_w wide and cover_h tall along the column, from their front edge back."""
    a, b = self.cover_w / 2.0, self.cover_h / 2.0
    pts = [(a * math.cos(u), b * math.sin(u)) for u in np.linspace(0, 2 * math.pi, 96, endpoint=False)]
    from manifold3d import CrossSection
    return CrossSection([pts]).extrude(COVER_FRONT_Z - back_z).translate((0, 0, back_z))

  def hub(self):
    """The steering wheel's hub (the airbag cover and the spokes' roots) as a drum."""
    return cyl(HUB_R, HUB_BACK_Z, 25.0, segments=96)

  def spoke_zone(self):
    """Where the wheel's spokes sweep when it is turned far: inside the part you hold, from the spokes' back face
    forward. Nothing fixed to the car may be in it."""
    return cyl(WHEEL_OD / 2 - GRIP + 1.0, SPOKE_BACK_Z, 25.0, segments=180) + self.hub()

  def dash(self):
    """The dash panel below the column, behind DASH_Z (a wall)."""
    return box(-300, 300, -400, 60, DASH_Z - 60.0, DASH_Z)

  def hood(self, thickness: float = 12.0):
    return self.covers()

  def wheel_grip(self):
    t = self.t.base
    pts = [(t.rr + (GRIP / 2) * math.cos(a), (GRIP / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    return revolve(pts, 180.0, 360.0, step_deg=1.0)


def overlap(a: Manifold, b: Manifold) -> float:
  return (a ^ b).volume()


def check_all(A: ColumnAssembly, wheel_turn: float = 40.0, lever_step: float = 4.0) -> dict:
  """Overlap volumes (mm^3) between parts that must not touch, as assembly.check_all, for the column mount: the ring
  teeth in place of the steering wheel teeth, the covers, hub, spoke zone, dash and the clamp's own parts in place
  of the dash cover and dash clamp."""
  res = {}
  T, W = A.teeth(), A.wheel_grip()
  G, C, M = A.gear(), A.carrier(), A.motor()
  HB, AR, CL, CU, RD, BR, SW = A.hinge_block(), A.arm(), A.clamp(), A.clamp_upper(), A.rods(), A.bracket(), A.switch()
  LV = A.lever(0.0, 0.0)
  COV, HUB, ZONE, DASH = A.covers(), A.hub(), A.spoke_zone(), A.dash()
  pairs = {
    "teeth/gear": (T, G), "teeth/carrier": (T, C), "teeth/motor": (T, M), "grip/carrier": (W, C), "grip/motor": (W, M),
    "grip/gear": (W, G), "carrier/motor": (C, M), "carrier/hinge block": (C, HB), "motor/hinge block": (M, HB),
    "carrier/lever": (C, LV), "lever/hinge block": (LV, HB), "lever/lever bracket": (LV, BR),
    "lever bracket/hinge block": (BR, HB), "lever bracket/carrier": (BR, C), "lever bracket/motor": (BR, M),
    "lever bracket/teeth": (BR, T), "switch/lever": (SW, LV), "switch/hinge block": (SW, HB), "switch/carrier": (SW, C),
    "hinge block/arm": (HB, AR), "arm/carrier": (AR, C), "arm/motor": (AR, M), "arm/clamp": (AR, CL),
    "arm/upper saddle": (AR, CU), "arm/rods": (AR, RD), "arm/teeth": (AR, T), "hinge block/teeth": (HB, T),
    "lever/arm": (LV, AR), "lever bracket/arm": (BR, AR), "switch/arm": (SW, AR), "clamp/upper saddle": (CL, CU),
    "clamp/rods": (CL, RD), "upper saddle/rods": (CU, RD),
  }
  sws = {dy: A._carried(MP.switch_screws(dy=dy), 0.0) for dy in (-MP.SW_SLOT, 0.0, MP.SW_SLOT)}
  LB = A._carried(MP.lever_bolt(), 0.0)
  for dy, sw in sws.items():
    pairs[f"switch screws ({dy:+.0f} mm in slots)/hinge block"] = (sw, HB)
    pairs[f"switch screws ({dy:+.0f} mm in slots)/arm"] = (sw, AR)
  pairs.update({"lever bolt/hinge block": (LB, HB), "lever bolt/arm": (LB, AR), "lever bolt/teeth": (LB, T),
                "hinge bolt, washers and nut/hinge block": (A._carried(MP.hinge_bolt(), 0.0), HB),
                "room for a hex key and socket on the lever bolt/hinge block": (A._carried(MP.lever_bolt_tools(), 0.0), HB),
                "room for a hex key and socket on the lever bolt/arm": (A._carried(MP.lever_bolt_tools(), 0.0), AR)})
  fixed = (("column covers", COV), ("hub", HUB), ("spoke sweep zone", ZONE), ("dash below the column", DASH),
           ("lower saddle", CL), ("upper saddle", CU), ("rods and nuts", RD))
  movers = (("motor gear", G), ("carrier", C), ("motor", M), ("hinge block", HB), ("lever bracket", BR), ("switch", SW),
            ("lift lever", LV), ("lever bolt", LB), ("ring teeth", T), ("arm", AR))
  for fixed_name, fx in fixed:
    for mover_name, mover in movers:
      if fixed_name in ("lower saddle", "upper saddle", "rods and nuts") and mover_name in ("arm",):
        continue
      pairs[f"{mover_name}/{fixed_name}"] = (mover, fx)
  for k, (a, b) in pairs.items():
    res["down: " + k] = overlap(a, b)
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
  for k, (a, b) in {"teeth/gear": (T, Gl), "carrier/hinge block": (Cl, HB), "motor/hinge block": (Ml, HB),
                    "carrier/arm": (Cl, AR), "motor/arm": (Ml, AR), "lever bracket/hinge block": (BRl, HB),
                    "lever bracket/arm": (BRl, AR), "switch/hinge block": (SWl, HB), "lever/hinge block": (LVo, HB),
                    "lever/arm": (LVo, AR), "lever/clamp": (LVo, CL), "lever/lever bracket": (LVo, BRl),
                    "lever/carrier": (LVo, Cl), "lever/hub": (LVo, HUB), "lever/spoke sweep zone": (LVo, ZONE),
                    "lever/column covers": (LVo, COV), "lever/teeth": (LVo, T), "lever/grip": (LVo, W),
                    "carrier/column covers": (Cl, COV), "motor/column covers": (Ml, COV), "motor/dash": (Ml, DASH),
                    "lever bracket/column covers": (BRl, COV), "lever bracket/hub": (BRl, HUB), "carrier/hub": (Cl, HUB),
                    "carrier/grip": (Cl, W), "carrier/teeth": (Cl, T), "lever bracket/spoke sweep zone": (BRl, ZONE),
                    "lever bolt/hinge block": (A._carried(MP.lever_bolt(), hair), HB),
                    "switch screws/hinge block": (A._carried(MP.switch_screws(dy=-MP.SW_SLOT), hair), HB)}.items():
    res[tag + k] = overlap(a, b)
  for alpha in list(np.arange(lever_step, MP.A_OFF - 0.5, lever_step)) + [MP.A_OFF - 0.5]:
    th = max(0.0, MP.cam_lift(alpha)) + 0.05
    lv = A.lever(alpha, th, part="lever_no_tab")
    br, ca = A.bracket(th), A.carrier(th)
    for k, (a, b) in {"lever/hinge block": (lv, HB), "lever/arm": (lv, AR), "lever/lever bracket": (lv, br),
                      "lever/carrier": (lv, ca), "carrier/hinge block": (ca, HB), "carrier/arm": (ca, AR),
                      "lever bracket/hinge block": (br, HB), "lever bracket/arm": (br, AR), "lever/hub": (lv, HUB),
                      "lever/spoke sweep zone": (lv, ZONE), "lever/column covers": (lv, COV), "lever/teeth": (lv, T),
                      "lever/grip": (lv, W), "lever/clamp": (lv, CL), "carrier/column covers": (ca, COV),
                      "carrier/teeth": (ca, T), "carrier/grip": (ca, W), "lever bracket/column covers": (br, COV),
                      "lever bolt/hinge block": (A._carried(MP.lever_bolt(), th), HB),
                      "switch screws/hinge block": (A._carried(MP.switch_screws(dy=-MP.SW_SLOT), th), HB)}.items():
      key = "lever swept: " + k
      res[key] = max(res.get(key, 0.0), overlap(a, b))
  tab = A.lever(0.0, 0.0, part="tab")
  res["click: tab clear of the bracket, lever down"] = overlap(tab, BR)
  res["click: tab meets its ridge lifting (should touch)"] = -max(overlap(A.lever(a, 0.0, part="tab"), BR) for a in (0.75, 1.25, 1.75))
  res["lever stops past up (should touch)"] = -overlap(A.lever(MP.A_OFF + 4.0, hair), HB)
  # the wheel turned past the ring: the carrier drops to DROP_DEG (the roller finds nothing to rest on)
  rest = -MP.DROP_DEG
  Gr, Cr, Mr, BRr, SWr = A.gear(rest), A.carrier(rest), A.motor(rest), A.bracket(rest), A.switch(rest)
  LVr, LBr = A.lever(0.0, rest), A._carried(MP.lever_bolt(), rest)
  SWSr = A._carried(MP.switch_screws(dy=-MP.SW_SLOT), rest)
  checks = {"grip/gear": (W, Gr), "grip/carrier": (W, Cr), "grip/motor": (W, Mr), "carrier/hinge block": (Cr, HB),
            "motor/hinge block": (Mr, HB), "lever bracket/hinge block": (BRr, HB), "switch/hinge block": (SWr, HB),
            "carrier/arm": (Cr, AR), "lever bracket/arm": (BRr, AR), "lever/hinge block": (LVr, HB),
            "lever bolt/hinge block": (LBr, HB), "switch screws/hinge block": (SWSr, HB), "gear/column covers": (Gr, COV),
            "carrier/column covers": (Cr, COV), "motor/dash": (Mr, DASH), "gear/spoke sweep zone": (Gr, ZONE)}
  for side, TT in (("left", A.teeth(wheel_turn)), ("right", A.teeth(-wheel_turn))):
    for name, part in (("carrier", Cr), ("gear", Gr), ("lever bracket", BRr), ("motor", Mr), ("switch", SWr),
                       ("lift lever", LVr), ("lever bolt", LBr), ("switch screws", SWSr), ("hinge block", HB), ("arm", AR)):
      checks[f"teeth turned {side}/{name}"] = (TT, part)
  for k, (a, b) in checks.items():
    res[f"wheel turned {wheel_turn:.0f}, carrier down {-rest:.1f} deg: " + k] = overlap(a, b)
  # the ring sweeping past the motor gear everywhere the gear is on it: every 2 degrees over the tracked arc
  worst = 0.0
  for w in np.arange(-A.t.roll_half, A.t.roll_half + 1e-9, 2.0):
    worst = max(worst, overlap(A.teeth(float(w)), G), overlap(A.teeth(float(w)), C))
  res["ring turned through its arc: teeth/gear and teeth/carrier (worst)"] = worst
  return res


def window_check(t: CP.RingTeeth) -> dict:
  """The ring teeth must fit between the steering wheel's two lower spokes, zip ties included."""
  margin = WINDOW_DEG / 2 - t.half
  return {"ring_spans_deg": round(t.span_deg, 1), "window_between_spokes_deg": WINDOW_DEG,
          "room_each_side_deg": round(margin, 1), "room_each_side_mm_along_the_grip": round(math.radians(margin) * WHEEL_OD / 2, 0),
          "ok": margin >= 2.0}


def margins(A: ColumnAssembly) -> dict:
  """How far apart the parts that come closest are (mm)."""
  def gap(moving, fx, direction):
    lo, hi = 0.0, 25.0
    d = np.asarray(direction, dtype=float)
    for _ in range(26):
      mid = (lo + hi) / 2
      if overlap(moving.translate(tuple(d * mid)), fx) > 1e-3:
        hi = mid
      else:
        lo = mid
    return round(lo, 2)
  lift = MP.cam_lift(MP.A_OFF)
  out_dir = (0.0, -1.0, 0.0)     # away from the hub, into the ring
  fwd = (0.0, 0.0, 1.0)          # towards the driver
  return {"motor_gear_to_ring_teeth_with_lever_up": min(gap(A.gear(lift), A.teeth(w), out_dir) for w in (0, 7, 14)),
          "lift_lever_handle_to_the_spoke_sweep_zone": gap(A.lever(0.0, 0.0), A.spoke_zone(), fwd),
          "lift_lever_up_to_the_hub": gap(A.lever(MP.A_OFF, lift), A.hub(), (0.0, 1.0, 0.0)),
          "motor_and_board_to_the_dash": gap(A.motor(), A.dash(), (0.0, 0.0, -1.0)),
          "arm_to_the_column_covers": gap(A.arm(), A.covers(), (0.0, 1.0, 0.0))}


def parts_scene(A: ColumnAssembly, lift_deg=0.0, alpha=0.0, wheel=0.0):
  """(manifold, colour) pairs for the pictures."""
  col = {"teeth": (.72, .72, .72), "grip": (.3, .3, .3), "gear": (.95, .6, .25), "carrier": (.35, .55, .85), "motor": (.25, .25, .25),
         "hinge": (.45, .75, .45), "bracket": (.6, .45, .8), "lever": (.85, .3, .3), "switch": (.9, .85, .2),
         "arm": (.6, .5, .4), "clamp": (.5, .7, .7), "covers": (.85, .85, .75), "hub": (.4, .4, .4), "rods": (.6, .6, .6)}
  items = [(A.teeth(wheel), col["teeth"]), (A.wheel_grip(), col["grip"]), (A.gear(lift_deg), col["gear"]),
           (A.carrier(lift_deg), col["carrier"]), (A.motor(lift_deg), col["motor"]), (A.hinge_block(), col["hinge"]),
           (A.bracket(lift_deg), col["bracket"]), (A.lever(alpha, lift_deg), col["lever"]), (A.switch(lift_deg), col["switch"]),
           (A.arm(), col["arm"]), (A.clamp(), col["clamp"]), (A.clamp_upper(), col["clamp"]), (A.rods(), col["rods"]),
           (A.covers(-260.0), col["covers"]), (A.hub(), col["hub"])]
  return [(m, c) for m, c in items if not m.is_empty()]

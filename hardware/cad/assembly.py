"""
Puts the parts where they sit in the car and checks they fit: the motor gear on the steering wheel teeth, the motor
carrier and finger guard clear of the steering wheel, the hinge block over the carrier with the lever bracket's legs
through it, the arm reaching from the dash clamp to the hinge block with both angle joints within their range, the
lift lever turning freely, its click working, and the motor gear lifted clear of the teeth when the lift lever is up.
With the steering wheel turned past the teeth, the carrier drops until the roller rests on the steering wheel or the
lift lever's rounded end meets the hinge block, and nothing else touches.

Frames: see mountparts.py. The steering wheel frame: the steering column is the z axis (towards the driver), +y is
12 o'clock, +x the driver's right. The carrier frame is the steering wheel frame moved to the motor's front face.
"""
import math
from dataclasses import dataclass, field

import numpy as np
from manifold3d import Manifold

import mountparts as MP
import wheelparts as WP
from cadlib import box, cyl, revolve
from params import (ARM_LENGTHS, ARM_PIVOT_FORWARD, ARM_PIVOT_UP, ARM_SLIDE, COLUMN_TILT, GRIP, NEMA, NEMA_LEN,
                    ROLLER_R, Z_GEAR_ROLLER, Z_MOTOR_FACE)


def car_axes(tilt_deg: float = COLUMN_TILT):
  """Car up and car rearward (towards the driver) as steering wheel frame vectors. The steering column rises towards
  the driver, so its axis (+z) points rearward and up by the tilt, and 12 o'clock (+y) leans forward by the same."""
  c, s = math.cos(math.radians(tilt_deg)), math.sin(math.radians(tilt_deg))
  return np.array([0.0, c, s]), np.array([0.0, -s, c])


def rot_x(deg: float) -> np.ndarray:
  a = math.radians(deg)
  return np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])


def place(m: Manifold, rot: np.ndarray, origin) -> Manifold:
  return m.transform([[float(rot[i, 0]), float(rot[i, 1]), float(rot[i, 2]), float(origin[i])] for i in range(3)])


def turn_about_x(m: Manifold, deg: float, centre) -> Manifold:
  c = np.asarray(centre, dtype=float)
  return place(m.translate((-c[0], -c[1], -c[2])), rot_x(deg), c)


def angle_in_car(direction_w, tilt_deg: float = COLUMN_TILT) -> float:
  """Degrees below level of a steering-wheel-frame direction (y, z components used), pointing towards the driver."""
  up, rear = car_axes(tilt_deg)
  return -math.degrees(math.atan2(float(direction_w @ up), float(direction_w @ rear)))


@dataclass
class Fit:
  ok: bool
  arm_deg: float           # arm's angle to the steering column (0 = along it, towards the dashboard)
  arm_below_level: float   # the arm in the car: degrees below level, going towards the driver
  reach: float             # dash clamp bolt to hinge block bolt, mm
  arm_len: float           # the arm to print (from ARM_LENGTHS), 0 if none fits
  slide: float             # how far the arm sits from the middle of its slide at the dash clamp
  pivot_w: np.ndarray      # dash clamp's bolt, steering wheel frame
  notes: list = field(default_factory=list)


def joint_w() -> np.ndarray:
  cd = WP.centre_distance()
  return np.array([0.0, cd + MP.PIVOT[0], Z_MOTOR_FACE + MP.PIVOT[1]])


def clamp_pivot_w(up_mm: float, forward_mm: float, tilt: float = COLUMN_TILT) -> np.ndarray:
  """The dash clamp's bolt for a clamp bolt up_mm above and forward_mm ahead of the motor gear's centre (in the car)."""
  up, rear = car_axes(tilt)
  return np.array([0.0, WP.centre_distance(), 0.0]) + up_mm * up - forward_mm * rear


def solve(t: WP.Teeth, up_mm: float = ARM_PIVOT_UP, forward_mm: float = ARM_PIVOT_FORWARD, tilt: float = COLUMN_TILT) -> Fit:
  """Which arm reaches from a dash clamp bolt at the given place to the hinge block's bolt, and at what angles."""
  pivot_w = clamp_pivot_w(up_mm, forward_mm, tilt)
  d = joint_w() - pivot_w
  reach = float(math.hypot(d[1], d[2]))
  arm = math.degrees(math.atan2(-d[1], d[2]))      # arm direction (dash clamp to hinge block) = (0, -sin a, cos a)
  arm_dir = np.array([0.0, -math.sin(math.radians(arm)), math.cos(math.radians(arm))])
  below = angle_in_car(arm_dir, tilt)
  notes = []
  fits = [L for L in ARM_LENGTHS if abs(reach - L) <= ARM_SLIDE - 0.5]
  arm_len = min(fits, key=lambda L: abs(reach - L)) if fits else 0.0
  if not fits:
    notes.append(f"the dash clamp's bolt is {reach:.0f} mm from the hinge block's; the arms cover "
                 f"{ARM_LENGTHS[0] - ARM_SLIDE:.0f} to {ARM_LENGTHS[-1] + ARM_SLIDE:.0f}")
  if abs(arm - MP.ARM_NOMINAL) > MP.LOCK_RANGE - 0.5:
    notes.append(f"arm at {arm:.1f} degrees to the steering column; the hinge block's joint covers "
                 f"{MP.ARM_NOMINAL - MP.LOCK_RANGE:.0f} to {MP.ARM_NOMINAL + MP.LOCK_RANGE:.0f}")
  if not (MP.ARM_ANGLES[0] + 0.5 <= below <= MP.ARM_ANGLES[1] - 0.5):
    notes.append(f"arm {below:.1f} degrees below level; the dash clamp covers {MP.ARM_ANGLES[0]:.0f} to {MP.ARM_ANGLES[1]:.0f}")
  return Fit(not notes, arm, below, reach, float(arm_len), reach - arm_len if arm_len else 0.0, pivot_w, notes)


class Assembly:
  def __init__(self, t: WP.Teeth, fit: Fit, parts: dict, tilt: float = COLUMN_TILT):
    self.t, self.fit, self.p = t, fit, parts
    self.cd = WP.centre_distance()
    self.b_org = np.array([0.0, self.cd, Z_MOTOR_FACE])
    self.hinge_w = self.b_org + np.array([0.0, MP.HINGE[0], MP.HINGE[1]])
    self.a_rot = rot_x(fit.arm_deg)
    up, rear = car_axes(tilt)
    self.up, self.rear = up, rear
    self.c_rot = np.stack([np.array([1.0, 0, 0]), up, rear], axis=1)
    py, pz = MP.ARM_PIVOT
    self.c_org = fit.pivot_w - py * up - pz * rear
    if fit.arm_len and "arm" not in parts:
      parts["arm"] = MP.arm(fit.arm_len)

  # parts that move with the carrier: lift > 0 turns the motor gear away from the steering wheel
  def _carried(self, m: Manifold, lift: float) -> Manifold:
    m = m.translate(tuple(self.b_org))
    return turn_about_x(m, -lift, self.hinge_w) if lift else m

  def carrier(self, lift=0.0):
    return self._carried(self.p["carrier"], lift)

  def gear(self, lift=0.0):
    return self._carried(self.p["gear"], lift)

  def motor(self, lift=0.0):
    """The motor, the StepperServoCAN board on its back (side wings broken off: 42 mm square, parts up to 12 mm tall
    on its back), the board's plugs (car plug below, motor and debug plugs at the sides: the board's edge without a
    plug faces up), and the motor's own cable plug facing down."""
    h = NEMA / 2
    body = box(-h, h, -h, h, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
    board = box(-h, h, -h, h, -NEMA_LEN - 14.0, -NEMA_LEN)
    plugs = box(-6, 6, -h - 14, -h, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0) + \
      box(h, h + 14, -6, 6, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0) + box(-h - 14, -h, -6, 6, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0)
    motor_plug = box(-8, 8, -h - 12, -h, -NEMA_LEN + 2.0, -NEMA_LEN + 18.0)
    return self._carried(body + board + plugs + motor_plug, lift)

  def hinge_block(self):
    return self.p["hinge_block"].translate(tuple(self.b_org))

  def bracket(self, lift=0.0):
    return self._carried(self.p["bracket"], lift)

  def lever(self, alpha: float = 0.0, lift: float | None = None, part: str = "lever"):
    """Lift lever lifted alpha degrees from down (MP.A_OFF is 'up'), on the lever bracket, with the carrier at lift
    (by default the lift its rounded end holds, and never below the motor gear on the teeth)."""
    if lift is None:
      lift = max(0.0, MP.cam_lift(alpha))
    return self._carried(MP.lever_in_carrier(self.p[part], alpha), lift)

  def switch(self, lift=0.0):
    return self._carried(MP.switch_body(), lift)

  def arm(self):
    """The arm, its lower bolt on the hinge block's bolt; its slot slid fit.slide from the middle at the dash clamp."""
    d = np.array([0.0, -math.sin(math.radians(self.fit.arm_deg)), math.cos(math.radians(self.fit.arm_deg))])
    return place(self.p["arm"], self.a_rot, self.fit.pivot_w + self.fit.slide * d)

  def clamp(self):
    return place(self.p["clamp"], self.c_rot, self.c_org)

  def hood(self, thickness: float = 12.0):
    return place(box(-80, 80, -thickness, 0.0, -150, 0.0), self.c_rot, self.c_org)

  def teeth(self, wheel_deg: float = 0.0):
    return self.p["teeth"].rotate((0, 0, wheel_deg))

  def wheel_grip(self):
    t = self.t
    pts = [(t.rr + (GRIP / 2) * math.cos(a), (GRIP / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    return revolve(pts, 0.0, 180.0, step_deg=1.0)

  def rest_on_grip_lift(self) -> float:
    """Carrier angle (negative = gear lowered) with the steering wheel turned past the teeth: the roller rests on the
    bare steering wheel, or the fin meets the lift lever's cam first (DROP_DEG), whichever comes first."""
    lo, hi = -MP.DROP_DEG, 0.0
    if overlap(self.gear(lo), self.wheel_grip()) <= 1e-3:
      return lo
    grip = self.wheel_grip()
    for _ in range(30):
      mid = (lo + hi) / 2
      if overlap(self.gear(mid), grip) > 1e-3:
        lo = mid
      else:
        hi = mid
    return hi


def overlap(a: Manifold, b: Manifold) -> float:
  return (a ^ b).volume()


def check_all(A: "Assembly", wheel_turn: float = 70.0, lever_step: float = 4.0) -> dict:
  """Overlap volumes (mm^3) between parts that must not touch, in these states: lift lever down with the motor gear on
  the teeth; lift lever up (carrier at the lift its rounded end gives); the lever at every angle from down to up;
  steering wheel turned wheel_turn degrees either way with the carrier dropped as far as it goes; the setup gauge in place.
  Every moving part is also checked against the dash cover and the dash clamp, and the bought screws and bolts (motor
  screws, the switch's screws anywhere in their slots, the lift lever's bolt and nut) against what is near them. Keys
  ending "(should touch)" hold minus the overlap, so they must be negative: the click's tab must meet its ridge, the
  lever's heel must stop it."""
  res = {}
  T, W = A.teeth(), A.wheel_grip()
  G, C, M = A.gear(), A.carrier(), A.motor()
  HB, AR, CL, BR, SW = A.hinge_block(), A.arm(), A.clamp(), A.bracket(), A.switch()
  LV = A.lever(0.0, 0.0)
  hood = A.hood()
  pairs = {
    "teeth/gear": (T, G), "teeth/carrier": (T, C), "teeth/motor": (T, M), "grip/carrier": (W, C), "grip/motor": (W, M),
    "carrier/motor": (C, M), "carrier/hinge block": (C, HB), "motor/hinge block": (M, HB), "carrier/lever": (C, LV),
    "lever/hinge block": (LV, HB), "lever/lever bracket": (LV, BR), "lever bracket/hinge block": (BR, HB),
    "lever bracket/carrier": (BR, C), "lever bracket/motor": (BR, M), "lever bracket/teeth": (BR, T),
    "switch/lever": (SW, LV), "switch/hinge block": (SW, HB), "switch/carrier": (SW, C), "hinge block/arm": (HB, AR),
    "arm/carrier": (AR, C), "arm/motor": (AR, M), "arm/clamp": (AR, CL), "clamp/hood": (CL, hood), "arm/hood": (AR, hood),
    "arm/teeth": (AR, T), "hinge block/teeth": (HB, T), "lever/arm": (LV, AR), "lever bracket/arm": (BR, AR),
    "switch/arm": (SW, AR),
  }
  # the bought hardware, and everything against the dash cover and the dash clamp
  sws = {dy: A._carried(MP.switch_screws(dy=dy), 0.0) for dy in (-MP.SW_SLOT, 0.0, MP.SW_SLOT)}
  LB = A._carried(MP.lever_bolt(), 0.0)
  for dy, sw in sws.items():
    pairs[f"switch screws ({dy:+.0f} mm in slots)/hinge block"] = (sw, HB)
    pairs[f"switch screws ({dy:+.0f} mm in slots)/arm"] = (sw, AR)
  pairs.update({"lever bolt/hinge block": (LB, HB), "lever bolt/arm": (LB, AR), "lever bolt/teeth": (LB, T),
                "hinge bolt, washers and nut/hinge block": (A._carried(MP.hinge_bolt(), 0.0), HB),
                "room for a hex key and socket on the lever bolt/hinge block": (A._carried(MP.lever_bolt_tools(), 0.0), HB),
                "room for a hex key and socket on the lever bolt/arm": (A._carried(MP.lever_bolt_tools(), 0.0), AR)})
  for fixed_name, fixed in (("dash cover", hood), ("dash clamp", CL)):
    for mover_name, mover in (("motor gear", G), ("carrier", C), ("motor", M), ("hinge block", HB), ("lever bracket", BR),
                              ("switch", SW), ("lift lever", LV), ("lever bolt", LB), ("teeth", T)):
      pairs[f"{mover_name}/{fixed_name}"] = (mover, fixed)
  pairs["lever bolt/clamp"] = (LB, CL)
  for k, (a, b) in pairs.items():
    res["down: " + k] = overlap(a, b)
  # the motor's screw heads (button heads in their counterbores) clear the motor gear even pushed right against the
  # plate with its roller 0.15 mm oversize
  zr0, zr1 = (z - Z_MOTOR_FACE for z in Z_GEAR_ROLLER)
  worst_gear = (A.p["gear"] + cyl(ROLLER_R + 0.15, zr0, zr1, segments=360)).translate((0, 0, -0.5))
  res["motor screw heads/motor gear (gear against the plate, roller 0.15 mm oversize)"] = overlap(MP.motor_screw_heads(), worst_gear)
  # the setup gauge in place, motor gear on the teeth
  gauge = A._carried(MP.setup_gauge(), 0.0)
  for k, b in {"lever bracket": BR, "spring": A._carried(MP.spring_body(), 0.0), "switch": SW, "carrier": C,
               "hinge block": HB, "arm": AR, "lift lever": LV}.items():
    res[f"setup gauge in: gauge/{k}"] = overlap(gauge, b)
  # lift lever up: the rounded end rests on the hinge block's top (checked a hair higher, leaving room for the contact)
  lift = max(0.0, MP.cam_lift(MP.A_OFF))
  hair = lift + 0.05
  Gl, Cl, Ml, BRl, SWl = A.gear(lift), A.carrier(hair), A.motor(hair), A.bracket(hair), A.switch(hair)
  LVo = A.lever(MP.A_OFF, hair)
  tag = f"lever up (lift {lift:.1f} deg): "
  for k, (a, b) in {"teeth/gear": (T, Gl), "carrier/hinge block": (Cl, HB), "motor/hinge block": (Ml, HB),
                    "carrier/arm": (Cl, AR), "motor/arm": (Ml, AR), "lever bracket/hinge block": (BRl, HB),
                    "lever bracket/arm": (BRl, AR), "switch/hinge block": (SWl, HB), "lever/hinge block": (LVo, HB),
                    "lever/arm": (LVo, AR), "lever/clamp": (LVo, CL), "lever/lever bracket": (LVo, BRl),
                    "lever/carrier": (LVo, Cl), "lever/dash cover": (LVo, hood), "carrier/dash cover": (Cl, hood),
                    "motor/dash cover": (Ml, hood), "lever bracket/dash cover": (BRl, hood), "switch/dash cover": (SWl, hood),
                    "carrier/clamp": (Cl, CL), "motor/clamp": (Ml, CL), "lever bracket/clamp": (BRl, CL),
                    "lever bolt/hinge block": (A._carried(MP.lever_bolt(), hair), HB),
                    "lever bolt/dash cover": (A._carried(MP.lever_bolt(), hair), hood),
                    "switch screws/hinge block": (A._carried(MP.switch_screws(dy=-MP.SW_SLOT), hair), HB)}.items():
    res[tag + k] = overlap(a, b)
  # every lever angle up to up: the lever (without the click's tab, which bends past its ridge) clears the bracket,
  # the hinge block and the arm; the carrier and bracket, at the lift the rounded end gives (a hair higher), clear
  # everything fixed
  for alpha in list(np.arange(lever_step, MP.A_OFF - 0.5, lever_step)) + [MP.A_OFF - 0.5]:
    th = max(0.0, MP.cam_lift(alpha)) + 0.05
    lv = A.lever(alpha, th, part="lever_no_tab")
    br, ca = A.bracket(th), A.carrier(th)
    for k, (a, b) in {"lever/hinge block": (lv, HB), "lever/arm": (lv, AR), "lever/lever bracket": (lv, br),
                      "lever/carrier": (lv, ca), "carrier/hinge block": (ca, HB), "carrier/arm": (ca, AR),
                      "lever bracket/hinge block": (br, HB), "lever bracket/arm": (br, AR),
                      "lever/dash cover": (lv, hood), "lever/clamp": (lv, CL), "carrier/dash cover": (ca, hood),
                      "lever bracket/dash cover": (br, hood),
                      "lever bolt/hinge block": (A._carried(MP.lever_bolt(), th), HB),
                      "switch screws/hinge block": (A._carried(MP.switch_screws(dy=-MP.SW_SLOT), th), HB)}.items():
      key = "lever swept: " + k
      res[key] = max(res.get(key, 0.0), overlap(a, b))
  # the click: lever down, the tab's hook sits just under its ridge; a degree or two up, it must meet it
  tab = A.lever(0.0, 0.0, part="tab")
  res["click: tab clear of the bracket, lever down"] = overlap(tab, BR)
  res["click: tab meets its ridge lifting (should touch)"] = -max(overlap(A.lever(a, 0.0, part="tab"), BR) for a in (0.75, 1.25, 1.75))
  # the heel stops the lever: a few degrees past up, the rounded end would be pushed into the hinge block's top
  res["lever stops past up (should touch)"] = -overlap(A.lever(MP.A_OFF + 4.0, hair), HB)
  # steering wheel turned past the teeth: roller rests on the steering wheel, or the rounded end meets the hinge block
  Tt = A.teeth(wheel_turn)
  rest = A.rest_on_grip_lift()
  Gr, Cr, Mr, BRr, SWr = A.gear(rest), A.carrier(rest), A.motor(rest), A.bracket(rest), A.switch(rest)
  teeth_only = turn_about_x(A.p["gear_teeth_only"].translate(tuple(A.b_org)), -rest, A.hinge_w)
  Ld = A.lever(0.0, -MP.DROP_DEG + 0.1)
  Tt2 = A.teeth(-wheel_turn)
  LVr, LBr = A.lever(0.0, rest), A._carried(MP.lever_bolt(), rest)
  SWSr = A._carried(MP.switch_screws(dy=-MP.SW_SLOT), rest)
  checks = {"grip/gear teeth": (W, teeth_only), "grip/carrier": (W, Cr), "grip/motor": (W, Mr),
            "carrier/hinge block": (Cr, HB), "motor/hinge block": (Mr, HB), "lever bracket/hinge block": (BRr, HB),
            "switch/hinge block": (SWr, HB), "carrier/arm": (Cr, AR), "lever bracket/arm": (BRr, AR),
            "carrier fully dropped, lever/hinge block": (Ld, HB), "lever bolt/hinge block": (LBr, HB),
            "switch screws/hinge block": (SWSr, HB)}
  for side, TT in (("left", Tt), ("right", Tt2)):
    for name, part in (("carrier", Cr), ("gear", Gr), ("lever bracket", BRr), ("motor", Mr), ("switch", SWr),
                       ("lift lever", LVr), ("lever bolt", LBr), ("switch screws", SWSr)):
      checks[f"teeth turned {side}/{name}"] = (TT, part)
  for k, (a, b) in checks.items():
    res[f"wheel turned {wheel_turn:.0f}, carrier down {-rest:.1f} deg: " + k] = overlap(a, b)
  return res

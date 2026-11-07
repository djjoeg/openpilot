"""
Puts the parts where they sit in the car and checks they fit: the motor gear on the steering wheel teeth, the motor
carrier and finger guard clear of the steering wheel, the hinge block over the carrier, the arm reaching from the dash
clamp to the hinge block with both angle joints within their range, the lift lever turning freely, and the motor gear
lifted clear of the teeth when the lift lever is up. With the steering wheel turned past the teeth, the carrier drops
until the roller rests on the steering wheel or the fin meets the cam, and nothing else touches.

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
from params import ARM_LENGTHS, ARM_PIVOT_FORWARD, ARM_PIVOT_UP, ARM_SLIDE, COLUMN_TILT, GRIP, NEMA, NEMA_LEN, Z_MOTOR_FACE


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
    body = box(-NEMA / 2, NEMA / 2, -NEMA / 2, NEMA / 2, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
    board = box(-NEMA / 2, NEMA / 2, -NEMA / 2, NEMA / 2, -NEMA_LEN - 10.0, -NEMA_LEN)   # StepperServoCAN board + cover
    return self._carried(body + board, lift)

  def hinge_block(self):
    return self.p["hinge_block"].translate(tuple(self.b_org))

  def lever(self, alpha: float = 0.0):
    """Lift lever lifted alpha degrees from down (MP.A_OFF is 'up')."""
    return MP.lever_in_block(self.p["lever"], alpha).translate(tuple(self.b_org))

  def switch(self):
    return MP.place_yz(MP.switch_body(), MP.LEVER_ON, *MP.LEVER_PIVOT).translate(tuple(self.b_org))

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
  the teeth; lift lever up (carrier at the lift the cam gives); the lever at every angle from down to its stop;
  steering wheel turned wheel_turn degrees with the carrier dropped as far as it goes."""
  res = {}
  T, W = A.teeth(), A.wheel_grip()
  G, C, M = A.gear(), A.carrier(), A.motor()
  HB, AR, CL, LV, SW = A.hinge_block(), A.arm(), A.clamp(), A.lever(), A.switch()
  hood = A.hood()
  pairs = {
    "teeth/gear": (T, G), "teeth/carrier": (T, C), "teeth/motor": (T, M), "grip/carrier": (W, C), "grip/motor": (W, M),
    "carrier/motor": (C, M), "carrier/hinge block": (C, HB), "motor/hinge block": (M, HB), "carrier/lever": (C, LV),
    "lever/hinge block": (LV, HB), "carrier/switch": (C, SW), "motor/switch": (M, SW), "hinge block/arm": (HB, AR),
    "arm/carrier": (AR, C), "arm/motor": (AR, M), "arm/clamp": (AR, CL), "clamp/hood": (CL, hood), "arm/hood": (AR, hood),
    "arm/teeth": (AR, T), "hinge block/teeth": (HB, T), "lever/arm": (LV, AR), "switch/arm": (SW, AR),
  }
  for k, (a, b) in pairs.items():
    res["down: " + k] = overlap(a, b)
  # lift lever up
  lift = max(0.0, MP.cam_lift(MP.A_OFF))
  Gl, Cl, Ml, LVo = A.gear(lift), A.carrier(lift), A.motor(lift), A.lever(MP.A_OFF)
  tag = f"lever up (lift {lift:.1f} deg): "
  for k, (a, b) in {"teeth/gear": (T, Gl), "carrier/hinge block": (Cl, HB), "motor/hinge block": (Ml, HB),
                    "carrier/arm": (Cl, AR), "motor/arm": (Ml, AR), "carrier/switch": (Cl, SW),
                    "lever/hinge block": (LVo, HB), "lever/arm": (LVo, AR), "lever/clamp": (LVo, CL)}.items():
    res[tag + k] = overlap(a, b)
  # every lever angle up to the stop: the lever clears the hinge block and the arm; the carrier, at the cam's lift
  # (a hair higher, leaving room for the contact), clears the lever and everything fixed
  for alpha in list(np.arange(lever_step, MP.A_HARD_STOP - 0.5, lever_step)) + [MP.A_HARD_STOP - 0.5]:
    lv = A.lever(alpha)
    th = max(0.0, MP.cam_lift(alpha)) + 0.05
    ca = A.carrier(th)
    for k, (a, b) in {"lever/hinge block": (lv, HB), "lever/arm": (lv, AR), "carrier/lever": (ca, lv),
                      "carrier/hinge block": (ca, HB), "carrier/arm": (ca, AR)}.items():
      key = "lever swept: " + k
      res[key] = max(res.get(key, 0.0), overlap(a, b))
  # the stop bar stops the lever
  res["lever stops at the bar (should touch)"] = -overlap(A.lever(MP.A_HARD_STOP + 1.5), HB)
  # steering wheel turned past the teeth: roller rests on the steering wheel, or the fin meets the cam
  Tt = A.teeth(wheel_turn)
  rest = A.rest_on_grip_lift()
  Gr, Cr, Mr = A.gear(rest), A.carrier(rest), A.motor(rest)
  teeth_only = turn_about_x(A.p["gear_teeth_only"].translate(tuple(A.b_org)), -rest, A.hinge_w)
  Cd = A.carrier(-MP.DROP_DEG + 0.1)
  for k, (a, b) in {"grip/gear teeth": (W, teeth_only), "grip/carrier": (W, Cr), "grip/motor": (W, Mr),
                    "turned teeth/carrier": (Tt, Cr), "turned teeth/gear": (Tt, Gr), "carrier/hinge block": (Cr, HB),
                    "motor/hinge block": (Mr, HB), "carrier/switch": (Cr, SW), "carrier/arm": (Cr, AR),
                    "carrier fully dropped/lever": (Cd, LV), "carrier fully dropped/hinge block": (Cd, HB)}.items():
    res[f"wheel turned {wheel_turn:.0f}, carrier down {-rest:.1f} deg: " + k] = overlap(a, b)
  return res

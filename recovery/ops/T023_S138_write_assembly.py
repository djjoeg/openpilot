"""
Puts the parts where they sit in the car and checks they fit: the motor gear on the steering wheel teeth, the
motor bracket and finger guard clear of the steering wheel, the arm between the bracket's ears and over the motor,
the arm slider within the arm's slot and the angle joint within its range, the arm clear of the dash clamp, and
the motor gear lifted clear of the teeth when the lift lever is flipped.

Frames: see mountparts.py. The car frame here: Y up, Z towards the driver (level), X to the driver's right.
"""
import math
from dataclasses import dataclass

import numpy as np
from manifold3d import Manifold

import mountparts as MP
import wheelparts as WP
from cadlib import box, cyl, revolve
from gears import pitch_radius
from params import (ARM_SLOT, COLUMN_TILT, GRIP, HINGE_FORWARD, HINGE_UP, MOTOR_TEETH, NEMA, NEMA_LEN, ROLL_GROW,
                    Z_GEAR_TEETH, Z_MOTOR_FACE)


def centre_distance(t: WP.Teeth) -> float:
  return t.r_roll + pitch_radius(MOTOR_TEETH) + ROLL_GROW


def car_axes(tilt_deg: float = COLUMN_TILT):
  """Car up (Y_K) and car rearward (Z_K) in steering wheel coordinates (y, z)."""
  c, s = math.cos(math.radians(tilt_deg)), math.sin(math.radians(tilt_deg))
  up = np.array([0.0, c, -s])
  rear = np.array([0.0, s, c])
  return up, rear


def rot_x_matrix(deg: float) -> np.ndarray:
  a = math.radians(deg)
  return np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])


def place(m: Manifold, rot: np.ndarray, origin) -> Manifold:
  mat = [[float(rot[i, 0]), float(rot[i, 1]), float(rot[i, 2]), float(origin[i])] for i in range(3)]
  return m.transform(mat)


@dataclass
class Fit:
  ok: bool
  arm_deg: float          # arm direction, from the steering column axis, positive turns +z towards +y
  slider_pos: float       # slider's back end along the arm from the hinge
  joint_deg: float        # angle joint setting (bracket relative to the arm)
  hinge_w: np.ndarray     # hinge axis centre, steering wheel frame
  notes: list


def solve(t: WP.Teeth, hinge_up: float = HINGE_UP, hinge_forward: float = HINGE_FORWARD, tilt: float = COLUMN_TILT) -> Fit:
  """Arm angle and slider position that put the motor gear on the teeth, for a hinge at the given place."""
  cd = centre_distance(t)
  gear_w = np.array([0.0, cd, 0.0])
  up, rear = car_axes(tilt)
  hinge_w = gear_w + hinge_up * up - hinge_forward * rear
  pivot_w = np.array([0.0, cd, Z_MOTOR_FACE]) + np.array([0.0, MP.PIVOT[0], MP.PIVOT[1]])
  d = pivot_w - hinge_w
  jy, jz = MP.slider_joint()
  dist2 = d[1] ** 2 + d[2] ** 2
  notes = []
  if dist2 <= jy ** 2:
    return Fit(False, 0, 0, 0, hinge_w, ["hinge too close to the motor"])
  along = math.sqrt(dist2 - jy ** 2)        # pivot's distance along the arm from the hinge
  s = along - jz
  arm = math.degrees(math.atan2(d[2], d[1]) - math.atan2(along, jy))
  arm = (arm + 180.0) % 360.0 - 180.0
  joint = -arm
  ok = True
  bolts = (s + 10.0, s + MP.SLIDER_LEN - 10.0)
  if bolts[0] < ARM_SLOT[0] + 2.75 or bolts[1] > ARM_SLOT[1] - 2.75:
    ok = False
    notes.append(f"slider bolts at {bolts[0]:.0f}-{bolts[1]:.0f} mm, outside the slot {ARM_SLOT[0]:.0f}-{ARM_SLOT[1]:.0f}")
  if abs(joint) > MP.LOCK_RANGE:
    ok = False
    notes.append(f"angle joint {joint:.1f} degrees, beyond +-{MP.LOCK_RANGE:.0f}")
  return Fit(ok, arm, s, joint, hinge_w, notes)


class Assembly:
  def __init__(self, t: WP.Teeth, fit: Fit, parts: dict):
    self.t, self.fit, self.p = t, fit, parts
    cd = centre_distance(t)
    self.cd = cd
    eye = np.eye(3)
    self.b_rot, self.b_org = eye, np.array([0.0, cd, Z_MOTOR_FACE])
    self.a_rot = rot_x_matrix(fit.arm_deg)
    self.a_org = fit.hinge_w
    up, rear = car_axes()
    self.c_rot = np.stack([np.array([1.0, 0, 0]), up, rear], axis=1)    # columns: clamp x, y, z in wheel frame
    hy, hz = MP.HINGE_AXIS
    self.c_org = fit.hinge_w - hy * up - hz * rear

  def motor_body(self) -> Manifold:
    body = box(-NEMA / 2, NEMA / 2, -NEMA / 2, NEMA / 2, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
    return place(body, self.b_rot, self.b_org)

  def bracket(self, lift_deg: float = 0.0) -> Manifold:
    return self._lifted(place(self.p["bracket"], self.b_rot, self.b_org), lift_deg)

  def motor(self, lift_deg: float = 0.0) -> Manifold:
    return self._lifted(self.motor_body(), lift_deg)

  def gear(self, lift_deg: float = 0.0, wheel_deg: float = 0.0) -> Manifold:
    g = place(self.p["gear"], self.b_rot, self.b_org)
    return self._lifted(g, lift_deg)

  def arm(self, lift_deg: float = 0.0) -> Manifold:
    return self._lifted(place(self.p["arm"], self.a_rot, self.a_org), lift_deg)

  def slider(self, lift_deg: float = 0.0) -> Manifold:
    org = self.a_org + self.a_rot @ np.array([0.0, 0.0, self.fit.slider_pos])
    return self._lifted(place(self.p["slider"], self.a_rot, org), lift_deg)

  def clamp(self) -> Manifold:
    return place(self.p["clamp"], self.c_rot, self.c_org)

  def hood(self, thickness: float = 12.0) -> Manifold:
    """The edge of the cover over the gauges, as a slab (clamp frame), for checking the clamp's fit."""
    slab = box(-80, 80, -thickness, 0.0, -150, 0.0)
    return place(slab, self.c_rot, self.c_org)

  def teeth(self, wheel_deg: float = 0.0) -> Manifold:
    return self.p["teeth"].rotate((0, 0, wheel_deg))

  def wheel_grip(self) -> Manifold:
    """The part of the steering wheel you hold, as a torus around its top half (for clearance checks)."""
    t = self.t
    pts = [(t.rr + (GRIP / 2) * math.cos(a), (GRIP / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    return revolve(pts, 0.0, 180.0, step_deg=1.0)

  def _lifted(self, m: Manifold, lift_deg: float) -> Manifold:
    """Turns a part that moves with the arm about the hinge axis (positive lifts the motor gear)."""
    if lift_deg == 0.0:
      return m
    h = self.fit.hinge_w
    # lifting turns the arm towards +y (away from the steering wheel): rotate about x through the hinge
    sign = 1.0 if self._lift_sign() > 0 else -1.0
    return place(m.translate((-h[0], -h[1], -h[2])), rot_x_matrix(sign * lift_deg), h)

  def _lift_sign(self) -> float:
    """+1 if a positive rotation about x moves the motor gear away from the steering wheel's centre (up in y)."""
    g = np.array([0.0, self.cd, 0.0]) - self.fit.hinge_w
    moved = rot_x_matrix(1.0) @ g
    return 1.0 if moved[1] > g[1] else -1.0


def overlap(a: Manifold, b: Manifold) -> float:
  return (a ^ b).volume()

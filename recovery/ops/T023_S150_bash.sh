python3 - <<'EOF'
p = "params.py"
s = open(p).read()
old = '''# Where the dash clamp's hinge ends up relative to the motor gear's centre, in the car (not the steering wheel frame):
# up (towards the roof) and forward (towards the windshield). Only used to check the parts reach; the arm slider and
# the angle joint adjust over a wide range.
HINGE_UP = 105.0
HINGE_FORWARD = 175.0'''
new = '''# Where the arm's pivot bolt on the dash clamp ends up relative to the motor gear's centre, in the car (not the
# steering wheel frame): up (towards the roof) and forward (towards the windshield). Only used to check that the parts
# reach; the dash clamp's angle, the arm slider and the hinge block's angle adjust over a wide range.
ARM_PIVOT_UP = 105.0
ARM_PIVOT_FORWARD = 175.0'''
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
EOF
cat > assembly.py <<'EOF'
"""
Puts the parts where they sit in the car and checks they fit: the motor gear on the steering wheel teeth, the motor
carrier and finger guard clear of the steering wheel, the hinge block over the carrier, the arm slider within the
arm's slot and both angle joints within their range, and the motor gear lifted clear of the teeth when the lift lever
is flipped. With the steering wheel turned past the teeth, the roller rests on the steering wheel and nothing else
touches it.

Frames: see mountparts.py. The car frame here: Y up, Z towards the driver (level), X to the driver's right.
"""
import math
from dataclasses import dataclass, field

import numpy as np
from manifold3d import Manifold

import mountparts as MP
import wheelparts as WP
from cadlib import box, cyl, revolve
from params import ARM_PIVOT_FORWARD, ARM_PIVOT_UP, ARM_SLOT, COLUMN_TILT, GRIP, NEMA, NEMA_LEN, Z_MOTOR_FACE


def car_axes(tilt_deg: float = COLUMN_TILT):
  """Car up and car rearward (towards the driver) as steering wheel frame vectors."""
  c, s = math.cos(math.radians(tilt_deg)), math.sin(math.radians(tilt_deg))
  return np.array([0.0, c, -s]), np.array([0.0, s, c])


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
  arm_deg: float           # arm direction in the steering wheel frame (rotation about x from +z)
  arm_below_level: float   # arm direction in the car: degrees below level towards the driver
  slider_pos: float        # slider's back end, measured along the arm from the dash clamp's pivot
  joint_deg: float         # hinge block angle joint setting
  pivot_w: np.ndarray      # dash clamp pivot, steering wheel frame
  notes: list = field(default_factory=list)


def solve(t: WP.Teeth, up_mm: float = ARM_PIVOT_UP, forward_mm: float = ARM_PIVOT_FORWARD, tilt: float = COLUMN_TILT) -> Fit:
  """Arm angle and slider position that put the hinge block (and the carrier with the motor gear on the teeth) in place,
  for a dash clamp pivot at the given place relative to the motor gear's centre."""
  cd = WP.centre_distance()
  gear_w = np.array([0.0, cd, 0.0])
  up, rear = car_axes(tilt)
  pivot_w = gear_w + up_mm * up - forward_mm * rear
  joint_w = np.array([0.0, cd + MP.PIVOT[0], Z_MOTOR_FACE + MP.PIVOT[1]])
  d = joint_w - pivot_w
  jy, jz = MP.slider_joint()
  dist2 = d[1] ** 2 + d[2] ** 2
  if dist2 <= jy ** 2:
    return Fit(False, 0, 0, 0, 0, pivot_w, ["dash clamp too close to the motor"])
  along = math.sqrt(dist2 - jy ** 2)
  s = along - jz
  arm = math.degrees(math.atan2(d[2], d[1]) - math.atan2(along, jy))
  arm = (arm + 180.0) % 360.0 - 180.0
  joint = -arm
  arm_dir = rot_x(arm) @ np.array([0.0, 0.0, 1.0])
  below = angle_in_car(arm_dir, tilt)
  notes = []
  bolts = (s + 10.0, s + MP.SLIDER_LEN - 10.0)
  if bolts[0] < ARM_SLOT[0] + 2.75 or bolts[1] > ARM_SLOT[1] - 2.75:
    notes.append(f"slider bolts at {bolts[0]:.0f}-{bolts[1]:.0f} mm, outside the slot {ARM_SLOT[0]:.0f}-{ARM_SLOT[1]:.0f}")
  if abs(joint) > MP.LOCK_RANGE - 1.0:
    notes.append(f"hinge block angle {joint:.1f} degrees, beyond +-{MP.LOCK_RANGE - 1:.0f}")
  if not (MP.ARM_ANGLES[0] + 1.0 <= below <= MP.ARM_ANGLES[1] - 1.0):
    notes.append(f"arm {below:.1f} degrees below level, outside the dash clamp's {MP.ARM_ANGLES[0]:.0f} to {MP.ARM_ANGLES[1]:.0f}")
  return Fit(not notes, arm, below, s, joint, pivot_w, notes)


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

  def lever(self, off: bool = False):
    lv = self.p["lever"]
    if off:
      lv = lv.rotate((200.0, 0, 0))
    ly, lz = MP.LEVER_PIVOT
    return lv.translate((0.0, self.b_org[1] + ly, self.b_org[2] + lz))

  def slider(self):
    jy, jz = MP.slider_joint()
    joint_w = self.b_org + np.array([0.0, MP.PIVOT[0], MP.PIVOT[1]])
    org = joint_w - self.a_rot @ np.array([0.0, jy, jz])
    return place(self.p["slider"], self.a_rot, org)

  def arm(self):
    return place(self.p["arm"], self.a_rot, self.fit.pivot_w)

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
    """Carrier angle (negative = gear lowered) at which the roller rests on the bare steering wheel."""
    lo, hi = -15.0, 0.0
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
EOF
export PYTHONPATH=/home/claude/pylib:. && timeout 900 python3 -c "
import time
import wheelparts as WP, mountparts as MP, assembly as AS
t0 = time.time()
t = WP.Teeth()
parts = dict(teeth=WP.teeth_one_piece(t), gear=WP.motor_gear(), carrier=MP.motor_carrier(), hinge_block=MP.hinge_block(), lever=MP.lift_lever(), slider=MP.arm_slider(), arm=MP.arm(), clamp=MP.dash_clamp(), pad=MP.clamp_pad(), gauge=MP.setup_gauge())
for k, m in parts.items(): print(f'{k:12s}', str(m.status()).split('.')[-1], round(m.volume()/1000,2), 'genus', m.genus(), 'parts', len(m.decompose()))
print('build', round(time.time()-t0,2))
f = AS.solve(t)
print('fit', f.ok, 'arm', round(f.arm_deg,1), 'below level', round(f.arm_below_level,1), 'slider', round(f.slider_pos,1), 'joint', round(f.joint_deg,1), f.notes)
"

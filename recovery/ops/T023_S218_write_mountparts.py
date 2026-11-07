"""
The parts that hold the motor over the steering wheel:

  motor carrier  - the motor bolts to its plate; the finger guard wraps the motor gear; it turns on the hinge block's
                   hinge, so the motor gear can be lifted off the steering wheel teeth. The fin on its back end is what
                   the lift lever's cam pushes on.
  hinge block    - holds the carrier's hinge, the spring that presses the motor gear onto the teeth, the lift lever and
                   the power switch; the arm bolts to its ears at an adjustable angle
  lift lever     - down (on): it hangs back towards the dashboard, the motor gear sits on the teeth and the handle
                   holds the power switch pressed. Up (off): its cam lifts the motor gear off the teeth and the switch
                   cuts the motor's power. It clicks into the up position and stays there until pushed back down.
  arm            - from the dash clamp to the hinge block; printed in several lengths, each slides +-10 mm
  dash clamp     - grips the edge of the cover over the gauges; holds the arm at an adjustable angle
  clamp pad      - swivel pad on the end of the dash clamp's screw
  setup gauge    - spacer used once while adjusting: sets the gap between the carrier and the hinge block

Frames (millimetres):
  carrier: origin at the centre of the motor's front face, +z along the shaft (towards the driver), +y away from the
           steering wheel's centre (the steering wheel's 12 o'clock direction), x across. The hinge block is drawn in
           the same frame, as it sits with the motor gear on the teeth.
  lever:   origin on the lever's pivot bolt (the x axis), handle along -z, top face +y. In the hinge block it is
           turned by LEVER_ON (down) plus how far it has been lifted.
  arm:     z along the arm from the dash clamp's bolt (middle of its slide) to the hinge block's bolt at z = length.
  clamp:   origin at the top front corner of the cover's edge; +y up from the cover's top face, +z towards the driver.

Angles in (y, z) planes are measured from +z towards +y. Turning a part by +a about x moves +y towards +z, the same
as Manifold.rotate((a, 0, 0)).
"""
import math

import numpy as np
from manifold3d import CrossSection, Manifold

from cadlib import (box, circle_yz, clean, cyl, cyl_x, cyl_y, extrude_x, hex_prism_y, prism_x, rect_yz, sector,
                    union)
from params import (ARM_LENGTHS, ARM_SLIDE, ARM_T, ARM_W, CLAMP_DEPTH, HOOD_EDGE_MAX, M3_CLEAR, M4_CLEAR, M5_CLEAR,
                    M6_CLEAR, M6_NUT_AF, M6_NUT_T, MOTOR_PLATE_T, NEMA, NEMA_BOSS, NEMA_HOLES, NEMA_LEN, Z_GEAR_TEETH,
                    Z_MOTOR_FACE)

GAP = 0.4                     # running clearance between parts that turn against each other


def rot2(deg: float) -> np.ndarray:
  """Turns (y, z) vectors by deg about x (+y towards +z)."""
  a = math.radians(deg)
  return np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])


def place_yz(m: Manifold, deg: float, y: float, z: float) -> Manifold:
  """Turns a part by deg about x, then moves its origin to (y, z)."""
  return m.rotate((deg, 0, 0)).translate((0.0, y, z))


# ***** motor carrier *****

PLATE_HALF = NEMA / 2 + 2.5           # square plate half width
PLATE_BOTTOM = -20.0                  # plate's lower edge below the motor's axis
GUARD_IN = 26.5                       # finger guard inner radius: clears the motor screws' heads
GUARD_OUT = 28.5
GUARD_LIP_IN = 25.5                   # guard's front lip: fingers can't get past it to the teeth
GUARD_WINDOW = 60.0                   # guard open +- this many degrees around straight down (where the gears meet)
GUARD_FRONT = (Z_GEAR_TEETH[1] - Z_MOTOR_FACE) + 2.0
TOP_Y = (NEMA / 2 + 0.5, NEMA / 2 + 8.5)      # block over the motor (y range): its top face is TOP_Y[1]
SIDE_X = (NEMA / 2 + 0.5, NEMA / 2 + 3.4)     # walls beside the motor's upper half (x range each side)
BLOCK_BACK = -46.0                    # the block and walls reach back over the motor body this far (motor is 48 long)
HINGE_R = 7.5
HINGE = (TOP_Y[1] + HINGE_R + 0.5, -40.0)     # carrier hinge axis (y, z); the hinge block's knuckles clear the
                                              # carrier's top by 0.5 mm at any angle
CARRIER_KNUCKLE = 15.0                # carrier's knuckle spans x +-this
BLOCK_KNUCKLE = (CARRIER_KNUCKLE + GAP, CARRIER_KNUCKLE + GAP + 7.0)   # hinge block's knuckles, x range each side
TAIL_X = 18.0                         # the carrier's tail (behind the hinge) spans x +-this

# Spring that presses the motor gear onto the steering wheel teeth: Lee Spring LCM100E03S (stainless steel, 9 mm
# outside, 7 mm inside, 1 mm wire, 28.5 mm long, 1.98 N/mm, 10.5 mm fully squashed, 35.2 N most load). Any spring of
# those sizes and about 2 N/mm does the same job.
SPRING_OD, SPRING_ID, SPRING_FREE, SPRING_RATE, SPRING_SOLID, SPRING_MAX_N = 9.0, 7.0, 28.5, 1.98, 10.5, 35.18
SPRING_Z = -4.0                       # spring's axis, in front of the hinge
SPRING_ARM = SPRING_Z - HINGE[1]      # its distance from the hinge axis
SPRING_POST_R = 3.1                   # post on the carrier's top, inside the spring
SPRING_POST_H = 7.0
SPRING_POCKET_R = 5.5                 # pocket in the hinge block's underside
SPRING_POCKET_D = 6.5
SETUP_GAP = 12.0                      # carrier top to hinge block underside with the motor gear on the teeth
SPRING_LEN = SETUP_GAP + SPRING_POCKET_D   # spring's length with the motor gear on the teeth

# How far the carrier turns (degrees; positive lifts the motor gear)
LIFT_DEG = 7.5          # lift lever up: motor gear about 7 mm off the teeth
HUMP_DEG = 1.2          # the lever goes over this much more lift either side of 'up', so it clicks in and stays
STOP_DEG = 11.0         # most the lever ever lifts it (the spring is still 1 mm from fully squashed)
DROP_DEG = 3.0          # with the steering wheel turned past the teeth, the carrier drops this much, until the fin
                        # meets the lever's cam (the motor gear's roller stays above the ends of the teeth's rolling band)


def spring_force(theta_deg: float) -> float:
  """Spring force (N) with the carrier turned up by theta."""
  return SPRING_RATE * (SPRING_FREE - SPRING_LEN + SPRING_ARM * math.sin(math.radians(theta_deg)))


def spring_torque(theta_deg: float) -> float:
  """Spring's turning force (N mm) on the carrier about the hinge."""
  return spring_force(theta_deg) * SPRING_ARM * math.cos(math.radians(theta_deg))


# ***** hinge block, lift lever and power switch *****

HB_BOTTOM = TOP_Y[1] + SETUP_GAP      # hinge block underside
HB_T = 9.0
HB_TOP = HB_BOTTOM + HB_T
HB_FRONT = 4.0
HB_HALF = BLOCK_KNUCKLE[1]
HB_BODY_BACK = HINGE[1] - HINGE_R - 3.0          # back end of the main body (just behind the hinge)

TAIL_ARM = 18.0                       # fin's distance behind the hinge axis
HANDLE_T = 8.0                        # lift lever's handle thickness
HANDLE_LEN = 40.0                     # pivot to the end of the handle
LEVER_X = 6.0                         # lever spans x +-this
LEVER_HUB_R = 7.0
LEVER_ON = -20.0                      # the handle hangs this far below the carrier's top plane when down
LEVER_PIVOT = (HB_TOP + 1.0, HINGE[1] - TAIL_ARM)    # (y, z)
CAM_LOW = 9.0                         # cam radius over the fin with the lever down
CAM_GAP = TAIL_ARM * math.sin(math.radians(DROP_DEG))         # cam to fin with the motor gear on the teeth
CAM_R_MAX = 16.0
FIN_HALF = 5.0
FIN_LEN = 14.0
FIN_TOP = LEVER_PIVOT[0] - CAM_LOW - CAM_GAP
LEVER_WALL_X = (LEVER_X + GAP, LEVER_X + GAP + 5.0)           # walls either side of the lever, x range each side
CAM_SLOT = 14.5                       # the cam turns in a slot through the hinge block, +- this along z

# Lever angles (degrees up from down) for the lift the cam is shaped to give
A_START, A_PEAK, A_OFF, A_HUMP2, A_STOP, A_END = 3.0, 40.0, 48.0, 56.0, 63.0, 70.0
A_HARD_STOP = 60.0                    # the handle meets the stop bar here
REST_D = (14.0, HANDLE_LEN + 1.0)     # the rest under the handle, from/to this far from the pivot
REST_T = 7.0

# Power switch: subminiature roller-lever microswitch, 19.8 x 6.4 x 10.2 mm with two holes 9.5 mm apart, such as the
# Omron SS-5GL2 (roller works at 14.5 +-0.8 mm from the holes' line, free at up to 19.3 mm) or a KW11-3Z roller lever.
# It sits in a cage under the rest, its roller up through the rest; the handle presses it when the lever is down.
SW_LEN, SW_THICK, SW_H = 19.8, 6.4, 10.2
SW_PITCH = 9.5
SW_OP, SW_OP_TOL, SW_FP = 14.5, 0.8, 19.3
SW_PRESS = 0.6                        # the handle presses the roller this far past where it clicks
SW_D = 28.0                           # switch's middle, this far from the pivot along the handle
SW_HOLES = -HANDLE_T / 2 - (SW_OP - SW_PRESS)   # holes' line, lever frame (y)
SW_SLOT = 2.0                         # the switch's screws slide +- this to set where it clicks

# Angle joint between the hinge block and the arm
EAR_X = (ARM_W / 2 + GAP, ARM_W / 2 + GAP + 6.0)   # ears either side of the arm's end
PIVOT = (HB_TOP + ARM_T / 2 + 1.5, -24.0)        # the arm's bolt (y, z)
LOCK_R = 22.0                                    # the arm's locking bolt, this far along the arm from its bolt
LOCK_RANGE = 35.0                                # the joint adjusts +- this many degrees ...
ARM_NOMINAL = 60.0                               # ... around the arm at this angle to the steering column


def arm_direction(a_deg: float) -> np.ndarray:
  """Unit (y, z) vector from the hinge block's arm bolt along the arm towards the dash clamp, for the arm at a_deg
  to the steering column."""
  return np.array([math.sin(math.radians(a_deg)), -math.cos(math.radians(a_deg))])


# ----- lift lever's cam -----

def _trapezoid(f: float, b: float = 0.15) -> float:
  """0 to 1 with constant speed in the middle and gentle starts and stops (b of the way at each end)."""
  f = min(1.0, max(0.0, f))
  if f < b:
    return f * f / (2 * b * (1 - b))
  if f > 1 - b:
    return 1 - (1 - f) ** 2 / (2 * b * (1 - b))
  return (f - b / 2) / (1 - b)


def _blend(f: float) -> float:
  f = min(1.0, max(0.0, f))
  return (1 - math.cos(math.pi * f)) / 2


def lift_schedule(alpha: float) -> float:
  """Carrier lift (degrees) the cam is shaped for, at lever angle alpha (degrees up from down). The rise takes an
  even effort on the handle (the spring's stored energy grows evenly with the lever's angle), then 'up' sits in a dip
  between two humps, then a steep rise to STOP_DEG."""
  t0 = spring_torque(0.0)
  c = SPRING_RATE * SPRING_ARM ** 2

  def energy(th):            # N mm, th in degrees
    r = math.radians(th)
    return t0 * r + c * r * r / 2

  def from_energy(e):
    return math.degrees((-t0 + math.sqrt(t0 * t0 + 2 * c * e)) / c)

  top = LIFT_DEG + HUMP_DEG
  if alpha <= A_START:
    return -DROP_DEG
  if alpha <= A_PEAK:
    e0, e1 = energy(-DROP_DEG), energy(top)
    return from_energy(e0 + (e1 - e0) * _trapezoid((alpha - A_START) / (A_PEAK - A_START)))
  if alpha <= A_OFF:
    return top - HUMP_DEG * _blend((alpha - A_PEAK) / (A_OFF - A_PEAK))
  if alpha <= A_HUMP2:
    return LIFT_DEG + HUMP_DEG * _blend((alpha - A_OFF) / (A_HUMP2 - A_OFF))
  if alpha <= A_STOP:
    return top + (STOP_DEG - top) * _blend((alpha - A_HUMP2) / (A_STOP - A_HUMP2))
  return STOP_DEG


def fin_plane(theta_deg: float):
  """The fin's top face with the carrier turned up by theta: a point on it and its upward normal, (y, z), in the
  hinge block's frame."""
  hy, hz = HINGE
  r = rot2(-theta_deg)
  c = r @ np.array([FIN_TOP - hy, LEVER_PIVOT[1] - hz]) + np.array([hy, hz])
  return c, r @ np.array([1.0, 0.0])


def cam_psi_range():
  """Lever-frame directions the fin can touch, with margin."""
  return (-90.0 - LEVER_ON - 12.0, -90.0 - LEVER_ON + A_END + 12.0)


def cam_points(step_deg: float = 0.5):
  """The cam's working face in the lever frame, (y, z) points, from the pivot. It is the boundary of everything that
  stays on the far side of the fin's top face at every lever angle, with the carrier at lift_schedule(angle): so the
  cam pushes the fin to that lift."""
  p = np.array(LEVER_PIVOT)
  ms, ks = [], []
  for a in np.arange(0.0, A_END + 1e-9, 0.25):
    c, n = fin_plane(lift_schedule(a))
    ms.append(rot2(-(LEVER_ON + a)) @ n)
    ks.append(float((c - p) @ n))
  m, k = np.array(ms), np.array(ks)
  pts = []
  lo, hi = cam_psi_range()
  for psi in np.arange(lo, hi + 1e-9, step_deg):
    u = np.array([math.sin(math.radians(psi)), math.cos(math.radians(psi))])
    mu = m @ u
    lim = np.where(mu < -1e-9, k / np.where(mu < -1e-9, mu, -1.0), np.inf)
    r = min(CAM_R_MAX, float(lim.min()))
    pts.append((r * float(u[0]), r * float(u[1])))
  return pts


def lever_outline() -> CrossSection:
  cam = CrossSection([[(0.0, 0.0)] + cam_points()])
  hub = circle_yz(LEVER_HUB_R, segments=96)
  ht = HANDLE_T / 2
  handle = rect_yz(-ht, ht, -HANDLE_LEN + ht, 0.0) + circle_yz(ht, 0.0, -HANDLE_LEN + ht, 48)
  knob = circle_yz(5.0, 2.0, -HANDLE_LEN + 6.0, 48) ^ rect_yz(-ht, 20.0, -HANDLE_LEN - 5, 0.0)   # finger grip
  return (cam + hub + handle + knob) - circle_yz(M4_CLEAR / 2, segments=48)


def lift_lever() -> Manifold:
  """Lever frame: pivot on the x axis, handle along -z."""
  return clean(extrude_x(lever_outline(), -LEVER_X, LEVER_X))


def lever_in_block(lever: Manifold, alpha: float = 0.0) -> Manifold:
  """The lever where it sits in the hinge block's frame, lifted alpha degrees from down."""
  return place_yz(lever, LEVER_ON + alpha, *LEVER_PIVOT)


def cam_lift(alpha: float, cam_pts=None) -> float:
  """The carrier lift (degrees) the cam actually holds at lever angle alpha (the fin's top face taken as a flat face),
  -DROP_DEG or more."""
  pts = np.array(cam_pts if cam_pts is not None else cam_points(0.25))
  pb = pts @ rot2(LEVER_ON + alpha).T + np.array(LEVER_PIVOT)

  def clear(th):
    c, n = fin_plane(th)
    return float(((pb - c) @ n).min())

  lo, hi = -DROP_DEG - 2.0, STOP_DEG + 3.0
  if clear(lo) >= 0:
    return lo
  for _ in range(50):
    mid = (lo + hi) / 2
    if clear(mid) >= 0:
      hi = mid
    else:
      lo = mid
  return hi


def lever_lift_table(step: float = 1.0, end: float = A_HARD_STOP):
  """(lever angle, carrier lift, force in N at the end of the handle to turn the lever) from down to the stop. The
  carrier never sits lower than the motor gear on the teeth (lift 0)."""
  pts = cam_points(0.25)
  rows = []
  prev = None
  for a in np.arange(0.0, end + 1e-9, step):
    th = max(0.0, cam_lift(a, pts))
    force = 0.0
    if prev is not None:
      dth = math.radians(th - prev[1])
      dal = math.radians(a - prev[0])
      force = spring_torque((th + prev[1]) / 2) * dth / dal / HANDLE_LEN
    rows.append((float(a), th, force))
    prev = (a, th)
  return rows


# ----- hinge block -----

def _lever_frame_point(y: float, z: float, alpha: float = 0.0) -> np.ndarray:
  return rot2(LEVER_ON + alpha) @ np.array([y, z]) + np.array(LEVER_PIVOT)


def stop_bar_corner() -> np.ndarray:
  """Where the handle's top face, 11 mm from the pivot, is when the lever reaches A_HARD_STOP."""
  return _lever_frame_point(HANDLE_T / 2 + 0.2, -11.0, A_HARD_STOP)


def rest_and_cage() -> Manifold:
  """The rest under the handle and the power switch's cage, drawn in the lever frame (handle along -z, its underside
  at y = -HANDLE_T/2): the handle lies on the rest when the lever is down."""
  ht = HANDLE_T / 2
  lx1 = LEVER_WALL_X[1]
  rest = box(-lx1, lx1, -ht - REST_T, -ht, -REST_D[1], -REST_D[0])
  cx0 = SW_THICK / 2 + 0.3
  cy0 = SW_HOLES - 8.5
  cage = box(cx0, cx0 + 2.5, cy0, -ht - REST_T + 0.5, -SW_D - 12.0, -SW_D + 12.0) + \
    box(-cx0 - 2.5, -cx0, cy0, -ht - REST_T + 0.5, -SW_D - 12.0, -SW_D + 12.0)
  part = rest + cage
  # the switch's roller comes up through the rest
  part = part - box(-cx0, cx0, -ht - REST_T - 1.0, -ht + 1.0, -SW_D - SW_LEN / 2 - 0.5, -SW_D + SW_LEN / 2 + 0.5)
  # switch screw slots (M2) through the cage walls, along the switch's working direction
  for dz in (-SW_PITCH / 2, SW_PITCH / 2):
    for dy in np.linspace(-SW_SLOT, SW_SLOT, 9):
      part = part - cyl_x(1.2, -cx0 - 4, cx0 + 4, y=SW_HOLES + dy, z=-SW_D + dz, segments=16)
  return part


def switch_body() -> Manifold:
  """Room the power switch takes in its cage (body, and its lever pressed by the handle), lever frame."""
  return box(-SW_THICK / 2, SW_THICK / 2, SW_HOLES - 6.0, -HANDLE_T / 2 - 0.05, -SW_D - SW_LEN / 2, -SW_D + SW_LEN / 2)


def hinge_block() -> Manifold:
  hy, hz = HINGE
  py, pz = PIVOT
  vy, vz = LEVER_PIVOT
  body = box(-HB_HALF, HB_HALF, HB_BOTTOM, HB_TOP, HB_BODY_BACK, HB_FRONT)
  kn = []
  for sgn in (-1, 1):
    x0, x1 = (BLOCK_KNUCKLE[0], BLOCK_KNUCKLE[1]) if sgn > 0 else (-BLOCK_KNUCKLE[1], -BLOCK_KNUCKLE[0])
    kn.append(cyl_x(HINGE_R, x0, x1, y=hy, z=hz) + box(x0, x1, hy, HB_BOTTOM + 0.5, hz - HINGE_R, hz + HINGE_R))

  # ears either side of the arm's end: the arm's bolt, and a curved slot for its locking bolt
  slot_pts = [np.array([py, pz]) + LOCK_R * arm_direction(a)
              for a in np.linspace(ARM_NOMINAL - LOCK_RANGE, ARM_NOMINAL + LOCK_RANGE, 15)]
  ear_cs = CrossSection.batch_hull([circle_yz(10.0, py, pz), rect_yz(HB_BOTTOM, HB_TOP, pz - 14.0, pz + 12.0)] +
                                   [circle_yz(7.0, float(q[0]), float(q[1])) for q in slot_pts])
  ears = [extrude_x(ear_cs, EAR_X[0], EAR_X[1]), extrude_x(ear_cs, -EAR_X[1], -EAR_X[0])]

  # walls either side of the lever around its pivot, with the stop bar over the lever; the rest and switch cage
  c = stop_bar_corner()
  bar = rect_yz(float(c[0]), float(c[0]) + 4.0, float(c[1]) - 5.0, float(c[1]))
  rest_root = _lever_frame_point(-HANDLE_T / 2 - REST_T, -REST_D[0] - 3.0)
  wall_cs = CrossSection.batch_hull([circle_yz(8.0, vy, vz), rect_yz(HB_BOTTOM, HB_TOP, vz - 4.0, HB_BODY_BACK + 2.0),
                                     bar, circle_yz(2.0, float(rest_root[0]), float(rest_root[1]))])
  lx0, lx1 = LEVER_WALL_X
  walls = [extrude_x(wall_cs, lx0, lx1), extrude_x(wall_cs, -lx1, -lx0)]
  stop_bar = extrude_x(bar, -lx1, lx1)
  rest = place_yz(rest_and_cage(), LEVER_ON, vy, vz)
  part = union([body] + kn + ears + walls + [rest])

  # the carrier's knuckle turns in a channel in the underside
  part = part - (cyl_x(HINGE_R + GAP, -CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, y=hy, z=hz, segments=96) +
                 box(-CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, hy - 20.0, hy, hz - HINGE_R - GAP, hz + HINGE_R + GAP))
  part = part - cyl_x(2.75, -60, 60, y=hy, z=hz, segments=32)                    # M5 hinge bolt
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=py, z=pz, segments=32)            # the arm's bolt
  part = part - union([cyl_x(M5_CLEAR / 2, -60, 60, y=float(q[0]), z=float(q[1]), segments=20)
                       for q in [np.array([py, pz]) + LOCK_R * arm_direction(a)
                                 for a in np.linspace(ARM_NOMINAL - LOCK_RANGE, ARM_NOMINAL + LOCK_RANGE, 71)]])
  part = part - cyl_x(M4_CLEAR / 2, -60, 60, y=vy, z=vz, segments=32)            # lift lever's bolt
  # the cam turns in a slot through the block; the fin comes up into it from below
  part = part - box(-lx0, lx0, HB_BOTTOM - 20.0, vy + 20.0, vz - CAM_SLOT, vz + CAM_SLOT)
  # the handle swings up between the walls
  part = part - (place_yz(box(-lx0, lx0, -HANDLE_T / 2 - 0.3, 60.0, -HANDLE_LEN - 10.0, 0.0), LEVER_ON, vy, vz) -
                 place_yz(rest_and_cage(), LEVER_ON, vy, vz))
  part = part + stop_bar
  part = part - cyl_y(SPRING_POCKET_R, HB_BOTTOM - 1.0, HB_BOTTOM + SPRING_POCKET_D, z=SPRING_Z, segments=64)
  return clean(part)


# ***** arm *****

ARM_LOCK_R = 24.0          # the dash clamp's locking bolt, this far along the arm from the clamp's pivot bolt


def arm(length: float) -> Manifold:
  """Arm frame: z along the arm from the dash clamp's pivot bolt (middle of the slide) to the hinge block's bolt at
  z = length. The bolts run across the arm (along x). One slot at the dash clamp end takes both of the clamp's bolts,
  so the arm slides +-ARM_SLIDE before they are tightened."""
  ht, w = ARM_T / 2, ARM_W / 2
  z_top = -ARM_SLIDE - 12.0
  bar = box(-w, w, -ht, ht, z_top, length) + cyl_x(ht, -w, w, z=length, segments=64) + cyl_x(ht, -w, w, z=z_top, segments=64)
  slot = Manifold.batch_hull([cyl_x(M5_CLEAR / 2, -w - 1, w + 1, z=-ARM_SLIDE, segments=32),
                              cyl_x(M5_CLEAR / 2, -w - 1, w + 1, z=ARM_LOCK_R + ARM_SLIDE, segments=32)])
  holes = cyl_x(M5_CLEAR / 2, -w - 1, w + 1, z=length, segments=32) + \
    cyl_x(M5_CLEAR / 2, -w - 1, w + 1, z=length - LOCK_R, segments=32)
  if length - LOCK_R - M5_CLEAR / 2 < ARM_LOCK_R + ARM_SLIDE + M5_CLEAR / 2 + 3.0:
    raise ValueError(f"arm {length} mm is too short")
  return clean(bar - slot - holes)


# ***** dash clamp *****

PLATE_T = 6.0
LIP_T = 8.0
LIP_GAP = 0.5
JAW_T = 9.0
JAW_DEPTH = 24.0
SCREW_Z = -12.0
JAW_Y0 = -(HOOD_EDGE_MAX + 5.0 + JAW_T)
SIDE_PLATE_X = (ARM_W / 2 + GAP, ARM_W / 2 + GAP + 7.0)
CLAMP_HALF_W = SIDE_PLATE_X[1]
ARM_PIVOT = (PLATE_T + ARM_T / 2 + 3.0, LIP_GAP + LIP_T + 12.0)   # (y, z) clamp frame
ARM_ANGLES = (0.0, 75.0)       # the arm can point from level to 75 degrees below level


def dash_clamp() -> Manifold:
  w = CLAMP_HALF_W
  zf = LIP_GAP + LIP_T
  plate = box(-w, w, 0.0, PLATE_T, -CLAMP_DEPTH, zf)
  lip = box(-w, w, JAW_Y0, PLATE_T, LIP_GAP, zf)
  jaw = box(-w, w, JAW_Y0, JAW_Y0 + JAW_T, -JAW_DEPTH, zf)
  part = plate + lip + jaw
  part = part - cyl_y(M6_CLEAR / 2, JAW_Y0 - 1, JAW_Y0 + JAW_T + 1, z=SCREW_Z, segments=32)
  part = part - hex_prism_y(M6_NUT_AF, JAW_Y0 - 0.01, JAW_Y0 + M6_NUT_T + 0.3, z=SCREW_Z)
  py, pz = ARM_PIVOT
  r = ARM_LOCK_R
  plates = []
  for sgn in (-1, 1):
    x0, x1 = (SIDE_PLATE_X[0], SIDE_PLATE_X[1]) if sgn > 0 else (-SIDE_PLATE_X[1], -SIDE_PLATE_X[0])
    a0, a1 = ARM_ANGLES[0] - 15.0, ARM_ANGLES[1] + 15.0    # past the slot's ends so the plate stays in one piece
    pts = [(py, pz)]
    for a in np.linspace(-a1, -a0, 41):        # angle above level; z points towards the driver
      pts.append((py + (r + 9.0) * math.sin(math.radians(a)), pz + (r + 9.0) * math.cos(math.radians(a))))
    pie = prism_x(pts, x0, x1)
    web = box(x0, x1, min(p[0] for p in pts), PLATE_T, LIP_GAP, pz + 1.0)
    plates.append(pie + web + cyl_x(10.0, x0, x1, y=py, z=pz))
  part = part + union(plates)
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=py, z=pz, segments=32)
  slot = []
  for a in np.linspace(-ARM_ANGLES[1], -ARM_ANGLES[0], 81):
    slot.append(cyl_x(M5_CLEAR / 2, -60, 60, y=py + r * math.sin(math.radians(a)), z=pz + r * math.cos(math.radians(a)), segments=20))
  part = part - union(slot)
  # the arm turns between the side plates
  part = part - (cyl_x(ARM_T / 2 + 1.0, -SIDE_PLATE_X[0], SIDE_PLATE_X[0], y=py, z=pz) +
                 box(-SIDE_PLATE_X[0], SIDE_PLATE_X[0], JAW_Y0 + JAW_T + 0.5, py + 40, zf + 0.01, pz + 60))
  return clean(part)


# ***** small parts *****

def clamp_pad() -> Manifold:
  """Swivel pad for the end of the M6 clamp screw. Stick rubber on top."""
  return cyl(11.0, 0, 5.0, segments=96) - cyl(3.4, -1, 3.0, segments=32)


def setup_gauge() -> Manifold:
  """Spacer SETUP_GAP thick that slides between the carrier's top and the hinge block, either side of the spring."""
  g = box(-14.0, 14.0, 0.0, SETUP_GAP - 0.2, 0.0, 40.0) + box(-14.0, 14.0, 0.0, 16.0, 34.0, 40.0)
  return g - box(-SPRING_OD / 2 - 0.6, SPRING_OD / 2 + 0.6, -1, SETUP_GAP + 1, -1, 22.0)


# ***** motor carrier *****

def motor_carrier() -> Manifold:
  t = MOTOR_PLATE_T
  outline = CrossSection.square((2 * PLATE_HALF, 2 * PLATE_HALF), center=True) + CrossSection.circle(GUARD_OUT, 180)
  # nothing below PLATE_BOTTOM: stays clear of the steering wheel when the carrier drops (wheel turned far)
  outline = outline ^ CrossSection.square((200, 200)).translate((-100, PLATE_BOTTOM))
  plate = outline.extrude(t)

  # finger guard: a shell around the motor gear, open below where it meets the steering wheel teeth
  shell = cyl(GUARD_OUT, t, GUARD_FRONT, segments=180) - cyl(GUARD_IN, t - 1, GUARD_FRONT + 1, segments=180)
  lip = cyl(GUARD_OUT, GUARD_FRONT - 1.6, GUARD_FRONT, segments=180) - cyl(GUARD_LIP_IN, GUARD_FRONT - 3, GUARD_FRONT + 1, segments=180)
  window = sector(GUARD_OUT + 6, 270.0 - GUARD_WINDOW, 270.0 + GUARD_WINDOW).extrude(GUARD_FRONT + 4).translate((0, 0, t - 2))
  guard = (shell + lip) - window
  for sgn in (-1, 1):   # rounded lower ends: a hand that meets the guard pushes it up instead of catching an edge
    a = math.radians(270.0 + sgn * GUARD_WINDOW)
    rm = (GUARD_IN + GUARD_OUT) / 2
    guard = guard + cyl((GUARD_OUT - GUARD_IN) / 2 + 0.6, t, GUARD_FRONT, rm * math.cos(a), rm * math.sin(a), 24)

  # block over the motor, walls beside its upper half, the hinge knuckle, the tail with the fin, and the spring post
  block = box(-SIDE_X[1], SIDE_X[1], TOP_Y[0], TOP_Y[1], BLOCK_BACK, t)
  walls = union([box(SIDE_X[0], SIDE_X[1], 0.0, TOP_Y[1], BLOCK_BACK, t), box(-SIDE_X[1], -SIDE_X[0], 0.0, TOP_Y[1], BLOCK_BACK, t)])
  hy, hz = HINGE
  knuckle = cyl_x(HINGE_R, -CARRIER_KNUCKLE, CARRIER_KNUCKLE, y=hy, z=hz) + \
    box(-CARRIER_KNUCKLE, CARRIER_KNUCKLE, TOP_Y[1] - 1.0, hy, hz - HINGE_R, hz + HINGE_R)
  vz = LEVER_PIVOT[1]
  tail = box(-TAIL_X, TAIL_X, TOP_Y[0], TOP_Y[1], vz - FIN_LEN / 2 - 2.0, BLOCK_BACK + 0.01)
  fin = box(-FIN_HALF, FIN_HALF, TOP_Y[0], FIN_TOP, vz - FIN_LEN / 2, vz + FIN_LEN / 2)
  post = cyl_y(SPRING_POST_R, TOP_Y[1] - 0.5, TOP_Y[1] + SPRING_POST_H, z=SPRING_Z, segments=40)
  part = plate + guard + block + walls + knuckle + tail + fin + post
  part = part - cyl_x(2.75, -40, 40, y=hy, z=hz, segments=32)        # M5 hinge bolt
  # motor screws (heads recessed on the gear side) and the motor's boss
  part = part - cyl(NEMA_BOSS / 2 + 0.4, -3, t + 1, segments=128)
  for sx in (-1, 1):
    for sy in (-1, 1):
      x, y = sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2
      part = part - cyl(M3_CLEAR / 2, -1, t + 1, x, y, 32) - cyl(3.4, t - 2.6, t + 1, x, y, 32)
  # the motor body stays clear
  part = part - box(-NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA_LEN - 20, 0.0)
  return clean(part)

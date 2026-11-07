"""
The parts that hold the motor over the steering wheel:

  motor carrier  - the motor bolts to its plate; the finger guard wraps the motor gear; it turns on the hinge block's
                   hinge, so the motor gear can be lifted off the steering wheel teeth. The fin on its back end is what
                   the lift lever's cam pushes on.
  hinge block    - holds the carrier's hinge, the spring that presses the motor gear onto the teeth, the lift lever and
                   the power switch; bolts to the arm slider at an adjustable angle
  lift lever     - lying flat (on): the motor gear sits on the teeth and the lever holds the power switch pressed.
                   Flipped up (off): its cam lifts the motor gear off the teeth and the switch cuts the motor's power.
                   It clicks into the up position and stays there until pushed back down.
  arm slider     - clamps anywhere along the arm's slot; its cheeks hold the hinge block's ears
  arm            - from the dash clamp to the arm slider; fixed once adjusted
  dash clamp     - grips the edge of the cover over the gauges; holds the arm at an adjustable angle
  clamp pad      - swivel pad on the end of the dash clamp's screw
  setup gauge    - spacer used once while adjusting: sets the gap between the carrier and the hinge block

Frames (millimetres):
  carrier: origin at the centre of the motor's front face, +z along the shaft (towards the driver), +y away from the
           steering wheel's centre (the steering wheel's 12 o'clock direction), x across. The hinge block is drawn in
           the same frame, as it sits with the motor gear on the teeth.
  lever:   origin on the lever's pivot bolt (the x axis), drawn 'on': handle along -z, lying on the hinge block.
  slider:  the arm's centre line is the z axis; the slider starts at z = 0.
  arm:     origin on the dash clamp's pivot axis (x); the arm runs along +z.
  clamp:   origin at the top front corner of the cover's edge; +y up from the cover's top face, +z towards the driver.

Angles in (y, z) planes are measured from +z towards +y. Turning a part by +a about x moves +y towards +z, the same
as Manifold.rotate((a, 0, 0)).
"""
import math

import numpy as np
from manifold3d import CrossSection, Manifold

from cadlib import box, circle_yz, clean, cyl, cyl_x, cyl_y, extrude_x, hex_prism_y, prism_x, rect_yz, sector, union
from params import (ARM_LEN, ARM_SLOT, ARM_T, ARM_W, CLAMP_DEPTH, HOOD_EDGE_MAX, M3_CLEAR, M4_CLEAR, M5_CLEAR, M6_CLEAR,
                    M6_NUT_AF, M6_NUT_T, MOTOR_PLATE_T, NEMA, NEMA_BOSS, NEMA_HOLES, NEMA_LEN, Z_GEAR_TEETH, Z_MOTOR_FACE)

GAP = 0.4                     # running clearance between parts that turn against each other


def rot2(deg: float) -> np.ndarray:
  """Turns (y, z) vectors by deg about x (+y towards +z)."""
  a = math.radians(deg)
  return np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])


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
LIFT_DEG = 8.0          # lift lever up: motor gear about 8.5 mm off the teeth
HUMP_DEG = 1.5          # the lever goes over this much more lift either side of 'up', so it clicks in and stays
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
HANDLE_LEN = 35.0                     # pivot to the end of the handle
LEVER_X = 6.0                         # lever spans x +-this
LEVER_HUB_R = 7.0
LEVER_PIVOT = (HB_TOP + HANDLE_T / 2, HINGE[1] - TAIL_ARM)    # (y, z): the handle lies on the hinge block's top
CAM_LOW = 9.0                         # cam radius over the fin with the lever down
CAM_GAP = TAIL_ARM * math.sin(math.radians(DROP_DEG))         # cam to fin with the motor gear on the teeth
CAM_R_MAX = 16.0
CAM_PSI = (-100.0, 35.0)              # the cam's working face spans these lever angles (0 = handle's opposite)
FIN_HALF = 5.0
FIN_LEN = 14.0
FIN_TOP = LEVER_PIVOT[0] - CAM_LOW - CAM_GAP
LEVER_EAR_X = (LEVER_X + GAP, LEVER_X + GAP + 5.0)            # lever's bearing walls, x range each side
CAM_SLOT = 15.5                       # the cam turns in a slot through the hinge block, +- this along z
TRAY_BACK = LEVER_PIVOT[1] - HANDLE_LEN - 3.0                 # the handle lies on the tray behind the pivot
TRAY_T = 5.0
STOP_BAR = (9.0, 15.0, 5.7, 10.0)     # bar over the lever (y0, y1, z0, z1 from the pivot): the handle stops on it

# Lever angles (degrees up from lying flat) for the lift the cam is shaped to give
A_START, A_PEAK, A_OFF, A_HUMP2, A_STOP, A_END = 6.0, 70.0, 82.0, 94.0, 104.0, 115.0

# Power switch: subminiature roller-lever microswitch, 19.8 x 6.4 x 10.2 mm with two holes 9.5 mm apart, such as the
# Omron SS-5GL2 (roller works at 14.5 +-0.8 mm from the holes' line, free at up to 19.3 mm) or a KW11-3Z roller lever.
SW_LEN, SW_THICK, SW_H = 19.8, 6.4, 10.2
SW_PITCH = 9.5
SW_OP, SW_OP_TOL, SW_FP = 14.5, 0.8, 19.3
SW_PRESS = 0.6                        # the handle presses the roller this far past where it clicks
SW_Z = LEVER_PIVOT[1] - 22.0          # switch's middle, under the handle
SW_HOLES_Y = HB_TOP - (SW_OP - SW_PRESS)
SW_SLOT = 2.0                         # the switch's screws slide +- this up and down to set where it clicks
SW_CAGE_Y0 = SW_HOLES_Y - 8.5

# Angle joint between the hinge block and the arm slider
EAR_X = (HB_HALF + GAP, HB_HALF + GAP + 6.0)    # ears for the angle joint, outside the block
PIVOT = (HB_TOP + 9.0, -24.0)                   # angle joint pivot (y, z)
LOCK_R = 22.0                                   # locking bolt's distance from the pivot
LOCK_RANGE = 40.0                               # the angle joint adjusts +- this many degrees ...
ARM_NOMINAL = 40.0                              # ... around the arm at this angle to the steering column


def lock_point(pivot=PIVOT):
  """The hinge block's locking bolt hole: where the slider's curved slot is centred when the arm is at ARM_NOMINAL."""
  d = rot2(ARM_NOMINAL) @ np.array([0.0, -LOCK_R])
  return (pivot[0] + float(d[0]), pivot[1] + float(d[1]))


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
  """Carrier lift (degrees) the cam is shaped for, at lever angle alpha (degrees up from lying flat). The rise has an
  even turning effort on the lever (the spring's stored energy grows evenly), then 'up' sits in a dip between two
  humps, then a steep rise to STOP_DEG."""
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


def cam_points(step_deg: float = 0.5):
  """The cam's working face in the lever frame, (y, z) points, from the pivot. It is the boundary of everything that
  stays on the far side of the fin's top face at every lever angle, with the carrier at lift_schedule(angle): so the
  cam pushes the fin to exactly that lift."""
  p = np.array(LEVER_PIVOT)
  ms, ks = [], []
  for a in np.arange(0.0, A_END + 1e-9, 0.25):
    c, n = fin_plane(lift_schedule(a))
    ms.append(rot2(-a) @ n)
    ks.append(float((c - p) @ n))
  m, k = np.array(ms), np.array(ks)
  pts = []
  for psi in np.arange(CAM_PSI[0], CAM_PSI[1] + 1e-9, step_deg):
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
  """Lever frame: pivot on the x axis, drawn lying flat ('on') with the handle along -z."""
  return clean(extrude_x(lever_outline(), -LEVER_X, LEVER_X))


def cam_lift(alpha: float, cam_pts=None) -> float:
  """The carrier lift (degrees) the cam actually holds at lever angle alpha (the fin's top face taken as a flat face):
  -DROP_DEG or more. Used to check the cam against lift_schedule."""
  pts = np.array(cam_pts if cam_pts is not None else cam_points(0.25))
  pb = pts @ rot2(alpha).T + np.array(LEVER_PIVOT)

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


def lever_lift_table(step: float = 1.0):
  """(lever angle, carrier lift, handle-end force in N to turn the lever) from flat to past 'up'. The carrier never
  sits lower than the motor gear on the teeth (lift 0)."""
  pts = cam_points(0.25)
  rows = []
  prev = None
  for a in np.arange(0.0, A_STOP + 1e-9, step):
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

def hinge_block() -> Manifold:
  hy, hz = HINGE
  py, pz = PIVOT
  ly, lz = lock_point()
  vy, vz = LEVER_PIVOT
  body = box(-HB_HALF, HB_HALF, HB_BOTTOM, HB_TOP, HB_BODY_BACK, HB_FRONT)
  kn = []
  for sgn in (-1, 1):
    x0, x1 = (BLOCK_KNUCKLE[0], BLOCK_KNUCKLE[1]) if sgn > 0 else (-BLOCK_KNUCKLE[1], -BLOCK_KNUCKLE[0])
    kn.append(cyl_x(HINGE_R, x0, x1, y=hy, z=hz) + box(x0, x1, hy, HB_BOTTOM + 0.5, hz - HINGE_R, hz + HINGE_R))
  # ears for the angle joint, outside the block
  ear_cs = CrossSection.batch_hull([circle_yz(9.0, py, pz), circle_yz(7.0, ly, lz),
                                    rect_yz(HB_BOTTOM, HB_TOP, min(pz, lz) - 7.0, pz + 12.0)])
  ears, bridges = [], []
  for sgn in (-1, 1):
    x0, x1 = (EAR_X[0], EAR_X[1]) if sgn > 0 else (-EAR_X[1], -EAR_X[0])
    ears.append(extrude_x(ear_cs, x0, x1))
    b0, b1 = (HB_HALF - 0.1, EAR_X[0] + 0.1) if sgn > 0 else (-EAR_X[0] - 0.1, -HB_HALF + 0.1)
    bridges.append(box(b0, b1, HB_BOTTOM, HB_TOP, min(pz, lz) - 7.0, pz + 12.0))
  # lever section behind the body: side walls, the tray the handle lies on, the lever's bearing walls rising around
  # the pivot, and the switch's cage under the tray
  lx1 = LEVER_EAR_X[1]
  walls = [box(LEVER_EAR_X[0], lx1, HB_BOTTOM, HB_TOP, TRAY_BACK, HB_BODY_BACK + 2.0),
           box(-lx1, -LEVER_EAR_X[0], HB_BOTTOM, HB_TOP, TRAY_BACK, HB_BODY_BACK + 2.0)]
  tray = box(-lx1, lx1, HB_TOP - TRAY_T, HB_TOP, TRAY_BACK, vz - CAM_SLOT + 0.5)
  bear_cs = CrossSection.batch_hull([circle_yz(8.0, vy, vz), rect_yz(HB_TOP - 1.0, HB_TOP, vz - 10.0, vz + 10.0),
                                     rect_yz(vy + STOP_BAR[0], vy + STOP_BAR[1], vz + STOP_BAR[2], vz + STOP_BAR[3])])
  bearing = [extrude_x(bear_cs, LEVER_EAR_X[0], lx1), extrude_x(bear_cs, -lx1, -LEVER_EAR_X[0])]
  cx0 = SW_THICK / 2 + 0.3
  cage = [box(cx0, cx0 + 2.8, SW_CAGE_Y0, HB_TOP - TRAY_T + 0.5, SW_Z - 12.0, SW_Z + 12.0),
          box(-cx0 - 2.8, -cx0, SW_CAGE_Y0, HB_TOP - TRAY_T + 0.5, SW_Z - 12.0, SW_Z + 12.0)]
  part = union([body] + kn + ears + bridges + walls + [tray] + bearing + cage)

  # the carrier's knuckle turns in a channel in the underside
  part = part - (cyl_x(HINGE_R + GAP, -CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, y=hy, z=hz, segments=96) +
                 box(-CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, hy - 20.0, hy, hz - HINGE_R - GAP, hz + HINGE_R + GAP))
  part = part - cyl_x(2.75, -60, 60, y=hy, z=hz, segments=32)                    # M5 hinge bolt
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=py, z=pz, segments=32)            # angle joint pivot
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=ly, z=lz, segments=32)            # angle joint locking bolt
  part = part - cyl_x(M4_CLEAR / 2, -60, 60, y=vy, z=vz, segments=32)            # lift lever pivot
  # the cam turns in a slot through the block; the fin comes up into it from below
  part = part - box(-LEVER_EAR_X[0], LEVER_EAR_X[0], HB_BOTTOM - 20.0, vy + STOP_BAR[0], vz - CAM_SLOT, vz + CAM_SLOT)
  # the switch's roller comes up through the tray under the handle
  part = part - box(-cx0, cx0, HB_TOP - TRAY_T - 1.0, HB_TOP + 1.0, SW_Z - SW_LEN / 2 - 0.5, SW_Z + SW_LEN / 2 + 0.5)
  # switch screw slots (M2) through the cage walls
  for dz in (-SW_PITCH / 2, SW_PITCH / 2):
    for dy in np.linspace(-SW_SLOT, SW_SLOT, 9):
      part = part - cyl_x(1.2, -cx0 - 4, cx0 + 4, y=SW_HOLES_Y + dy, z=SW_Z + dz, segments=16)
  part = part - cyl_y(SPRING_POCKET_R, HB_BOTTOM - 1.0, HB_BOTTOM + SPRING_POCKET_D, z=SPRING_Z, segments=64)
  return clean(part)


def switch_body() -> Manifold:
  """Room the power switch takes in its cage (body, and its lever pressed by the handle), for clearance checks."""
  return box(-SW_THICK / 2, SW_THICK / 2, SW_HOLES_Y - 6.0, HB_TOP - 0.05, SW_Z - SW_LEN / 2, SW_Z + SW_LEN / 2)


# ***** arm slider *****

SLIDER_LEN = 50.0
SLIDER_BASE = 7.0
CHEEK_X = (EAR_X[1] + GAP, EAR_X[1] + GAP + 6.0)     # cheeks just outside the hinge block's ears
JOINT_DROP = 17.0                                    # pivot below the arm's centre line
JOINT_Z = SLIDER_LEN - 10.0                          # pivot along the slider


def slider_joint():
  return (-JOINT_DROP, JOINT_Z)


def arm_slider() -> Manifold:
  """Two M5 bolts through the base and the arm's slot clamp it (nyloc nuts under the arm). The cheeks hang down
  outside the hinge block's ears and carry the pivot hole and the curved slot for the locking bolt."""
  top = ARM_T / 2
  w = ARM_W / 2
  base = box(-CHEEK_X[1], CHEEK_X[1], top, top + SLIDER_BASE, 0.0, SLIDER_LEN)
  guides = box(-w - 2.5, -w - 0.3, -top + 2.0, top + SLIDER_BASE, 0.0, SLIDER_LEN) + \
           box(w + 0.3, w + 2.5, -top + 2.0, top + SLIDER_BASE, 0.0, SLIDER_LEN)
  part = base + guides
  for z in (10.0, SLIDER_LEN - 10.0):
    part = part - cyl_y(M5_CLEAR / 2, -20, 40, z=z, segments=32)
  jy, jz = slider_joint()
  ly, lz = jy, jz - LOCK_R
  cheeks = []
  for sgn in (-1, 1):
    x0, x1 = (CHEEK_X[0], CHEEK_X[1]) if sgn > 0 else (-CHEEK_X[1], -CHEEK_X[0])
    outline = [(top + SLIDER_BASE, 0.0), (top + SLIDER_BASE, SLIDER_LEN), (jy + 4.0, jz + 11.0), (jy - 11.0, jz + 2.0),
               (ly - LOCK_R * math.sin(math.radians(LOCK_RANGE)) - 8.0, lz + 6.0), (ly - 10.0, lz - 8.0), (top, lz - 10.0)]
    cheeks.append(prism_x(outline, x0, x1) + cyl_x(10.0, x0, x1, y=jy, z=jz))
  part = part + union(cheeks)
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=jy, z=jz, segments=32)
  slot = []
  for a in np.linspace(-LOCK_RANGE, LOCK_RANGE, 65):
    ang = math.radians(180.0 + a)
    slot.append(cyl_x(M5_CLEAR / 2, -60, 60, y=jy + LOCK_R * math.sin(ang), z=jz + LOCK_R * math.cos(ang), segments=20))
  part = part - union(slot)
  return clean(part)


# ***** arm *****

ARM_LOCK_R = 24.0          # locking bolt's distance from the dash clamp pivot, along the arm


def arm(length: float = ARM_LEN, slot=ARM_SLOT) -> Manifold:
  """Arm frame: the dash clamp's pivot bolt is the x axis; the bar runs along +z. A boss at the pivot and one at the
  locking bolt take the two bolts across the arm's width."""
  ht, w = ARM_T / 2, ARM_W / 2
  bar = box(-w, w, -ht, ht, 0.0, length)
  bosses = cyl_x(9.0, -w, w) + cyl_x(7.5, -w, w, z=ARM_LOCK_R)
  rib = box(-3.0, 3.0, ht, ht + 5.0, 12.0, slot[0] - 6.0)
  part = bar + bosses + rib
  part = part - box(-M5_CLEAR / 2, M5_CLEAR / 2, -ARM_T, ARM_T, slot[0], slot[1])
  part = part - cyl_x(M5_CLEAR / 2, -40, 40, segments=32) - cyl_x(M5_CLEAR / 2, -40, 40, z=ARM_LOCK_R, segments=32)
  end = cyl_y(w, -ht - 10, ht + 10, z=length - w, segments=96) + box(-w, w, -ht - 10, ht + 10, -20, length - w)
  return clean(part ^ end)


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
ARM_PIVOT = (PLATE_T + 8.0, LIP_GAP + LIP_T + 12.0)   # (y, z) clamp frame
ARM_ANGLES = (-15.0, 65.0)     # the arm can point from 15 degrees above level to 65 degrees below


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
  # the arm's end turns between the side plates
  part = part - (cyl_x(9.0 + 1.0, -SIDE_PLATE_X[0], SIDE_PLATE_X[0], y=py, z=pz) +
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

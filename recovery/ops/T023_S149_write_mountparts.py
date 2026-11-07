"""
The parts that hold the motor over the steering wheel:

  motor carrier  - the motor bolts to its plate; the finger guard wraps the motor gear; it hangs on the hinge block's
                   hinge and flips up to lift the motor gear off the steering wheel teeth
  hinge block    - holds the carrier's hinge, the spring that presses the motor gear onto the teeth, the lift lever and
                   the switch that cuts the motor's power when the carrier is lifted; bolts to the arm slider at an
                   adjustable angle
  arm slider     - clamps anywhere along the arm's slot; its cheeks hold the hinge block's ears
  arm            - from the dash clamp to the arm slider; fixed once adjusted
  dash clamp     - grips the edge of the cover over the gauges; holds the arm at an adjustable angle
  lift lever     - flip it over to lift the carrier (motor gear off the teeth, power off); it stays until flipped back
  clamp pad      - swivel pad on the end of the dash clamp's screw
  setup gauge    - spacer used once while adjusting: sets the gap between the carrier and the hinge block

Frames (millimetres):
  carrier: origin at the centre of the motor's front face, +z along the shaft (towards the driver), +y away from the
           steering wheel's centre (the steering wheel's 12 o'clock direction), x across. The hinge block is drawn in
           the same frame, as it sits with the motor gear on the teeth.
  slider:  the arm's centre line is the z axis; the slider starts at z = 0.
  arm:     origin on the dash clamp's pivot axis (x); the arm runs along +z.
  clamp:   origin at the top front corner of the cover's edge; +y up from the cover's top face, +z towards the driver.
"""
import math

import numpy as np
from manifold3d import CrossSection, Manifold

from cadlib import box, clean, cyl, cyl_x, cyl_y, hex_prism_y, prism_x, sector, union
from params import (ARM_LEN, ARM_SLOT, ARM_T, ARM_W, CLAMP_DEPTH, HOOD_EDGE_MAX, M3_CLEAR, M4_CLEAR, M5_CLEAR, M6_CLEAR,
                    M6_NUT_AF, M6_NUT_T, MOTOR_PLATE_T, NEMA, NEMA_BOSS, NEMA_HOLES, NEMA_LEN, Z_GEAR_TEETH, Z_MOTOR_FACE)

GAP = 0.4                     # running clearance between parts that turn against each other

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
HINGE = (TOP_Y[1] + 7.0, -40.0)       # carrier hinge axis (y, z)
HINGE_R = 7.5
CARRIER_KNUCKLE = 15.0                # carrier's knuckle spans x +-this
BLOCK_KNUCKLE = (CARRIER_KNUCKLE + GAP, CARRIER_KNUCKLE + GAP + 7.0)   # hinge block's knuckles, x range each side
TAIL_Z = (-56.0, -47.0)               # tail behind the hinge: the lift lever's cam presses down on its top
SPRING_Z = -6.0                       # spring post on the carrier's top, in front of the hinge
SPRING_POST_R = 2.3                   # for a compression spring 5 mm or more inside diameter
SETUP_GAP = 8.0                       # carrier top to hinge block underside with the motor gear on the teeth


def motor_carrier() -> Manifold:
  t = MOTOR_PLATE_T
  outline = CrossSection.square((2 * PLATE_HALF, 2 * PLATE_HALF), center=True) + CrossSection.circle(GUARD_OUT, 180)
  # nothing below PLATE_BOTTOM: stays clear of the steering wheel when the roller rests on it (wheel turned far)
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

  # block over the motor, walls beside its upper half, and the hinge knuckle on top
  block = box(-SIDE_X[1], SIDE_X[1], TOP_Y[0], TOP_Y[1], BLOCK_BACK, t)
  walls = union([box(SIDE_X[0], SIDE_X[1], 0.0, TOP_Y[1], BLOCK_BACK, t), box(-SIDE_X[1], -SIDE_X[0], 0.0, TOP_Y[1], BLOCK_BACK, t)])
  hy, hz = HINGE
  knuckle = cyl_x(HINGE_R, -CARRIER_KNUCKLE, CARRIER_KNUCKLE, y=hy, z=hz) + \
    box(-CARRIER_KNUCKLE, CARRIER_KNUCKLE, TOP_Y[1] - 1.0, hy, hz - HINGE_R, hz + HINGE_R)
  tail = box(-CARRIER_KNUCKLE, CARRIER_KNUCKLE, TOP_Y[0], TOP_Y[1], TAIL_Z[0], BLOCK_BACK + 0.01)
  post = cyl_y(SPRING_POST_R, TOP_Y[1] - 0.5, TOP_Y[1] + 9.0, z=SPRING_Z, segments=32)
  part = plate + guard + block + walls + knuckle + tail + post
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


# ***** hinge block *****

HB_BOTTOM = TOP_Y[1] + SETUP_GAP      # hinge block underside
HB_T = 9.0
HB_Z = (-66.0, 4.0)
HB_HALF = BLOCK_KNUCKLE[1]
EAR_X = (HB_HALF + GAP, HB_HALF + GAP + 6.0)    # ears for the angle joint, outside the block
PIVOT = (HB_BOTTOM + HB_T + 9.0, -24.0)         # angle joint pivot (y, z)
LOCK_R = 22.0                                   # locking bolt's distance from the pivot (straight back)
LOCK_RANGE = 40.0                               # the angle joint adjusts +- this many degrees
SPRING_POCKET = (5.0, 4.6)                      # pocket radius and depth in the underside, for an 8 mm spring
LEVER_PIVOT = (TOP_Y[1] + 1.5 + 9.0, -60.0)     # lift lever pivot (y, z): cam's low point 1.5 above the tail
LEVER_X = 9.0                                   # lever spans x +-this
SWITCH_Z = -24.0                                # microswitch position along the block
SWITCH_X = (-HB_HALF + 1.0, -HB_HALF + 1.0 + 6.4)   # microswitch body, x range (left of the spring)


def lock_point(pivot=PIVOT):
  return (pivot[0], pivot[1] - LOCK_R)


def hinge_block() -> Manifold:
  hy, hz = HINGE
  z0, z1 = HB_Z
  body = box(-HB_HALF, HB_HALF, HB_BOTTOM, HB_BOTTOM + HB_T, z0, z1)
  kn = []
  for sgn in (-1, 1):
    x0, x1 = (BLOCK_KNUCKLE[0], BLOCK_KNUCKLE[1]) if sgn > 0 else (-BLOCK_KNUCKLE[1], -BLOCK_KNUCKLE[0])
    kn.append(cyl_x(HINGE_R, x0, x1, y=hy, z=hz) + box(x0, x1, hy, HB_BOTTOM + 0.5, hz - HINGE_R, hz + HINGE_R))
  py, pz = PIVOT
  ly, lz = lock_point()
  ears = []
  for sgn in (-1, 1):
    x0, x1 = (EAR_X[0], EAR_X[1]) if sgn > 0 else (-EAR_X[1], -EAR_X[0])
    outline = [(HB_BOTTOM, pz + 12.0), (py, pz + 12.0), (py + 7.0, pz + 2.0), (ly + 7.0, lz), (ly, lz - 7.0), (HB_BOTTOM, lz - 7.0)]
    ear = prism_x(outline, x0, x1) + cyl_x(9.0, x0, x1, y=py, z=pz) + cyl_x(7.0, x0, x1, y=ly, z=lz)
    ears.append(ear)
  bridge = [box(HB_HALF - 0.1, EAR_X[0] + 0.1, HB_BOTTOM, HB_BOTTOM + HB_T, lz - 7.0, pz + 12.0),
            box(-EAR_X[0] - 0.1, -HB_HALF + 0.1, HB_BOTTOM, HB_BOTTOM + HB_T, lz - 7.0, pz + 12.0)]
  ly2, lz2 = LEVER_PIVOT
  lugs = []
  for sgn in (-1, 1):
    x0, x1 = (LEVER_X + GAP, LEVER_X + GAP + 6.0) if sgn > 0 else (-LEVER_X - GAP - 6.0, -LEVER_X - GAP)
    lugs.append(cyl_x(6.5, x0, x1, y=ly2, z=lz2) + box(x0, x1, ly2, HB_BOTTOM + 0.5, lz2 - 6.5, lz2 + 6.5))
  # microswitch seat: a plate hanging below the block; the switch's lever reaches down onto the carrier's top
  seat = box(SWITCH_X[0] - 3.0, SWITCH_X[0], HB_BOTTOM - 10.0, HB_BOTTOM + 0.5, SWITCH_Z - 9.0, SWITCH_Z + 9.0)
  part = body + union(kn) + union(ears) + union(bridge) + union(lugs) + seat
  part = part - cyl_x(2.75, -60, 60, y=hy, z=hz, segments=32)
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=py, z=pz, segments=32)
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=ly, z=lz, segments=32)
  part = part - cyl_x(M4_CLEAR / 2, -60, 60, y=ly2, z=lz2, segments=32)
  # the lever turns between the lugs, through the block
  part = part - box(-LEVER_X - GAP, LEVER_X + GAP, HB_BOTTOM - 1.0, HB_BOTTOM + HB_T + 1.0, lz2 - 15.0, lz2 + 15.0)
  part = part - cyl_y(SPRING_POCKET[0], HB_BOTTOM - 1.0, HB_BOTTOM + SPRING_POCKET[1], z=SPRING_Z, segments=48)
  # switch screw slots (M2, holes 9.5 mm apart): +-2 mm up and down to set where it clicks
  for dz in (-4.75, 4.75):
    for dy in np.linspace(-2.0, 2.0, 9):
      part = part - cyl_x(1.15, SWITCH_X[0] - 4.0, SWITCH_X[0] + 1.0, y=HB_BOTTOM - 5.0 + dy, z=SWITCH_Z + dz, segments=16)
  return clean(part)


# ***** lift lever *****

CAM_LOW = 9.0          # cam radius that faces the tail when the carrier is down ("on")
CAM_THROW = 6.5        # how much further the cam reaches when flipped ("off")
LEVER_HANDLE = 45.0


def lift_lever() -> Manifold:
  """Lever frame: pivot axis along x through the origin, drawn 'on' (handle pointing back, -z). The cam is an
  eccentric disc whose low point faces straight down (onto the carrier's tail) when 'on'. Flipping the handle over
  the top turns the high point down, just past the middle, so the carrier's push holds it there."""
  e = CAM_THROW / 2.0
  r = CAM_LOW + e
  cam = cyl_x(r, -LEVER_X, LEVER_X, y=e, z=0.0, segments=96)
  handle = prism_x([(-4.0, 0.0), (4.0, 0.0), (5.0, -LEVER_HANDLE), (-3.0, -LEVER_HANDLE)], -LEVER_X, LEVER_X)
  grip = cyl_x(5.0, -LEVER_X, LEVER_X, y=1.0, z=-LEVER_HANDLE, segments=48)
  part = cam + handle + grip
  part = part - cyl_x(M4_CLEAR / 2, -LEVER_X - 1, LEVER_X + 1, segments=32)
  return clean(part)


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


def arm() -> Manifold:
  """Arm frame: the dash clamp's pivot bolt is the x axis; the bar runs along +z. A boss at the pivot and one at the
  locking bolt take the two bolts across the arm's width."""
  ht, w = ARM_T / 2, ARM_W / 2
  bar = box(-w, w, -ht, ht, 0.0, ARM_LEN)
  bosses = cyl_x(9.0, -w, w) + cyl_x(7.5, -w, w, z=ARM_LOCK_R)
  rib = box(-3.0, 3.0, ht, ht + 5.0, 12.0, ARM_SLOT[0] - 6.0)
  part = bar + bosses + rib
  part = part - box(-M5_CLEAR / 2, M5_CLEAR / 2, -ARM_T, ARM_T, ARM_SLOT[0], ARM_SLOT[1])
  part = part - cyl_x(M5_CLEAR / 2, -40, 40, segments=32) - cyl_x(M5_CLEAR / 2, -40, 40, z=ARM_LOCK_R, segments=32)
  end = cyl_y(w, -ht - 10, ht + 10, z=ARM_LEN - w, segments=96) + box(-w, w, -ht - 10, ht + 10, -20, ARM_LEN - w)
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
    a0, a1 = ARM_ANGLES
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
  """Spacer SETUP_GAP thick that slides between the carrier's top and the hinge block while adjusting."""
  g = box(-12.0, 12.0, 0.0, SETUP_GAP - 0.2, 0.0, 40.0) + box(-12.0, 12.0, 0.0, 14.0, 34.0, 40.0)
  return g - box(-3.5, 3.5, -1, SETUP_GAP + 1, -1, 12.0)

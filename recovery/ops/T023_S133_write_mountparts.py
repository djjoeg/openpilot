"""
The parts that hold the motor over the steering wheel:

  motor bracket  - the motor bolts to its plate; the finger guard wraps the motor gear; two ears carry the angle joint
  arm slider     - clamps anywhere along the arm's slot; its cheeks hold the bracket's ears at an adjustable angle
  arm            - hangs from the dash clamp's hinge; the spring pulls it down so the motor gear rests on the teeth
  dash clamp     - grips the edge of the cover over the gauges; carries the hinge, the spring post, the lift lever
                   and the switch that cuts the motor's power
  lift lever     - flip it to lift the arm (motor gear off the teeth, motor power off) and it stays there; flip it
                   back to lower the arm. Its screw is also the stop that keeps the motor gear from dropping onto the
                   steering wheel when the wheel is turned past the teeth.
  clamp pad      - swivel pad on the end of the dash clamp's screw

Frames (all millimetres):
  bracket: origin at the centre of the motor's front face, +z along the shaft (towards the driver), +y away from
           the steering wheel's centre (the steering wheel's 12 o'clock direction), x across.
  arm:     origin on the hinge axis (x), arm along +z, +y on the arm's top face side.
  slider:  the arm frame shifted along the arm to the slider's back end.
  clamp:   origin at the top front corner of the cover's edge; +y up from the cover's top face, +z towards the driver
           out of the edge's face, x along the edge.
"""
import math

import numpy as np
from manifold3d import CrossSection, Manifold

from cadlib import box, clean, cone, cyl, cyl_x, cyl_y, hex_prism_x, hex_prism_y, hex_prism_z, prism_x, sector, union
from gears import MODULE, pitch_radius
from params import (ARM_LEN, ARM_SLOT, ARM_T, ARM_W, CLAMP_DEPTH, CLAMP_KNUCKLE, HINGE_HALF_SPAN, HINGE_R,
                    HOOD_EDGE_MAX, KNUCKLE_GAP, M3_CLEAR, M4_CLEAR, M4_PILOT, M5_CLEAR, M5_NUT_AF, M5_NUT_T, M6_CLEAR,
                    M6_NUT_AF, M6_NUT_T, MOTOR_PLATE_T, MOTOR_TEETH, NEMA, NEMA_BOSS, NEMA_HOLES, NEMA_LEN, TAIL,
                    Z_GEAR_TEETH, Z_MOTOR_FACE)

# ***** motor bracket *****

PLATE_HALF = NEMA / 2 + 2.5           # square plate half width
GUARD_IN = 26.5                       # finger guard inner radius: clears the motor screws' heads
GUARD_OUT = 28.5
GUARD_LIP_IN = 25.5                   # front lip of the guard: a finger can't get past it to the teeth
GUARD_WINDOW = 55.0                   # guard open +- this many degrees around straight down (where the gears meet)
GUARD_FRONT = (Z_GEAR_TEETH[1] - Z_MOTOR_FACE) + 2.0
TOP_BLOCK = (NEMA / 2 + 0.5, NEMA / 2 + 8.5)   # block over the motor, y range
SIDE_WALL_X = (NEMA / 2 + 0.5, 24.5)           # walls beside the motor's upper half, x range each side
BLOCK_BACK = -30.0                    # how far the block and walls reach back over the motor body
EAR_X = (ARM_W / 2 + 0.5, ARM_W / 2 + 6.5)   # ears (angle joint) each side, x range: just outside the arm
PIVOT = (37.0, -14.0)                 # angle joint pivot (y, z), bracket frame
LOCK_R = 22.0                         # locking bolt distance from the pivot
LOCK_DIR = 180.0                      # direction of the locking bolt from the pivot: 180 = straight back (-z)
LOCK_RANGE = 35.0                     # the angle joint adjusts +- this many degrees


def motor_bracket() -> Manifold:
  t = MOTOR_PLATE_T
  outline = CrossSection.square((2 * PLATE_HALF, 2 * PLATE_HALF), center=True) + CrossSection.circle(GUARD_OUT, 180)
  plate = outline.extrude(t)
  plate = plate - cyl(NEMA_BOSS / 2 + 0.4, -1, t + 1, segments=128)
  for sx in (-1, 1):
    for sy in (-1, 1):
      x, y = sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2
      plate = plate - cyl(M3_CLEAR / 2, -1, t + 1, x, y, 32) - cyl(3.4, t - 2.6, t + 1, x, y, 32)

  # finger guard: a shell around the motor gear, open below where it meets the steering wheel teeth
  shell = cyl(GUARD_OUT, t, GUARD_FRONT, segments=180) - cyl(GUARD_IN, t - 1, GUARD_FRONT + 1, segments=180)
  lip = cyl(GUARD_OUT, GUARD_FRONT - 1.6, GUARD_FRONT, segments=180) - cyl(GUARD_LIP_IN, GUARD_FRONT - 3, GUARD_FRONT + 1, segments=180)
  guard = shell + lip
  window = sector(GUARD_OUT + 6, 270.0 - GUARD_WINDOW, 270.0 + GUARD_WINDOW).extrude(GUARD_FRONT + 4).translate((0, 0, t - 2))
  guard = guard - window
  # rounded lower ends ("skids"): a hand that meets the guard pushes the arm up instead of catching an edge
  for sgn in (-1, 1):
    a = math.radians(270.0 + sgn * GUARD_WINDOW)
    rm = (GUARD_IN + GUARD_OUT) / 2
    guard = guard + cyl((GUARD_OUT - GUARD_IN) / 2 + 0.6, t, GUARD_FRONT, rm * math.cos(a), rm * math.sin(a), 24)
  plate = plate - window   # the plate below the motor gear stays open too (clears the steering wheel teeth)
  plate = plate + (outline.extrude(t) ^ box(-60, 60, -NEMA / 2 + 0.5, 60, 0, t)) - cyl(NEMA_BOSS / 2 + 0.4, -1, t + 1, segments=128)
  for sx in (-1, 1):
    for sy in (-1, 1):
      x, y = sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2
      plate = plate - cyl(M3_CLEAR / 2, -1, t + 1, x, y, 32) - cyl(3.4, t - 2.6, t + 1, x, y, 32)

  # block over the motor and walls beside its upper half: stiffen the plate and carry the ears
  block = box(-SIDE_WALL_X[1], SIDE_WALL_X[1], TOP_BLOCK[0], TOP_BLOCK[1], BLOCK_BACK, t)
  walls = [box(sgn * SIDE_WALL_X[0] if sgn > 0 else -SIDE_WALL_X[1], SIDE_WALL_X[1] if sgn > 0 else -SIDE_WALL_X[0],
               0.0, TOP_BLOCK[1], BLOCK_BACK, t) for sgn in (-1, 1)]
  # ears: up from the block to the pivot, plus a wing back to the locking bolt
  py, pz = PIVOT
  lock = (py + LOCK_R * math.sin(math.radians(LOCK_DIR)), pz + LOCK_R * math.cos(math.radians(LOCK_DIR)))
  ears = []
  for sgn in (-1, 1):
    x0, x1 = (EAR_X[0], EAR_X[1]) if sgn > 0 else (-EAR_X[1], -EAR_X[0])
    outline_yz = [(TOP_BLOCK[0] + 1, pz + 9), (py, pz + 9), (py + 8.5, pz), (py + 6, lock[1] - 1), (lock[0], lock[1] - 7),
                  (TOP_BLOCK[0] + 1, lock[1] - 7)]
    ear = prism_x(outline_yz, x0, x1) + cyl_x(8.5, x0, x1, y=py, z=pz) + cyl_x(7.0, x0, x1, y=lock[0], z=lock[1])
    ear = ear - cyl_x(M5_CLEAR / 2, x0 - 1, x1 + 1, y=py, z=pz, segments=32)
    ear = ear - cyl_x(M5_CLEAR / 2, x0 - 1, x1 + 1, y=lock[0], z=lock[1], segments=32)
    ears.append(ear)
  part = plate + guard + block + union(walls) + union(ears)
  # the motor body and its boss stay clear
  part = part - box(-NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA_LEN - 5, 0.0)
  part = part - cyl(NEMA_BOSS / 2 + 0.4, -3, t + 1, segments=128)
  return clean(part)


def bracket_lock_point():
  py, pz = PIVOT
  return (py + LOCK_R * math.sin(math.radians(LOCK_DIR)), pz + LOCK_R * math.cos(math.radians(LOCK_DIR)))


# ***** arm slider *****

SLIDER_LEN = 50.0
SLIDER_BASE = 7.0
CHEEK_X = (EAR_X[1] + 0.3, EAR_X[1] + 6.3)    # cheeks just outside the bracket's ears
JOINT_DROP = 17.0                             # pivot below the arm's centre line (slider frame y = -17)
JOINT_Z = SLIDER_LEN - 10.0                    # pivot along the slider


def slider_joint():
  """Pivot position (y, z) in the slider frame."""
  return (-JOINT_DROP, JOINT_Z)


def arm_slider() -> Manifold:
  """Slider frame: the arm's centre line is the z axis (arm x +-ARM_W/2, y +-ARM_T/2), slider starts at z = 0.
  Two M5 bolts through the slider's base and the arm's slot clamp it (nyloc nuts under the arm). The cheeks hang
  down outside the motor bracket's ears and carry the pivot hole and the curved slot for the locking bolt."""
  top = ARM_T / 2
  w = ARM_W / 2
  base = box(-CHEEK_X[1], CHEEK_X[1], top, top + SLIDER_BASE, 0.0, SLIDER_LEN)
  guides = box(-w - 2.5, -w - 0.3, -top + 2.0, top + SLIDER_BASE, 0.0, SLIDER_LEN) + \
           box(w + 0.3, w + 2.5, -top + 2.0, top + SLIDER_BASE, 0.0, SLIDER_LEN)
  part = base + guides
  for z in (10.0, SLIDER_LEN - 10.0):
    part = part - cyl_y(M5_CLEAR / 2, -20, 40, z=z, segments=32)
  jy, jz = slider_joint()
  ly = jy + LOCK_R * math.sin(math.radians(LOCK_DIR))
  lz = jz + LOCK_R * math.cos(math.radians(LOCK_DIR))
  cheeks = []
  for sgn in (-1, 1):
    x0, x1 = (CHEEK_X[0], CHEEK_X[1]) if sgn > 0 else (-CHEEK_X[1], -CHEEK_X[0])
    # plate from the slider base down to the pivot and back past the locking slot
    outline_yz = [(top + SLIDER_BASE, 2.0), (top + SLIDER_BASE, SLIDER_LEN), (jy, jz + 10.0), (jy - 10.0, jz),
                  (ly - 9.0, lz - 2.0), (ly - 4.0, lz - 10.0), (top, lz - 10.0)]
    cheek = prism_x(outline_yz, x0, x1) + cyl_x(10.0, x0, x1, y=jy, z=jz)
    cheeks.append(cheek)
  part = part + union(cheeks)
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=jy, z=jz, segments=32)
  # curved slot for the locking bolt: +- LOCK_RANGE around its middle position
  slot = []
  for a in np.linspace(-LOCK_RANGE, LOCK_RANGE, 57):
    ang = math.radians(LOCK_DIR + a)
    slot.append(cyl_x(M5_CLEAR / 2, -60, 60, y=jy + LOCK_R * math.sin(ang), z=jz + LOCK_R * math.cos(ang), segments=20))
  part = part - union(slot)
  return clean(part)


# ***** arm *****

KNUCKLE_HALF = HINGE_HALF_SPAN - CLAMP_KNUCKLE - KNUCKLE_GAP    # arm's knuckle, each side of the middle
SPRING_TAB_Z = 26.0          # spring hook hole under the arm, distance in front of the hinge
SPRING_TAB_X = 13.0


def arm() -> Manifold:
  """Arm frame: hinge axis along x through the origin; the bar runs along +z with its wide face in the x-z plane."""
  ht = ARM_T / 2
  w = ARM_W / 2
  bar = box(-w, w, -ht, ht, 0.0, ARM_LEN)
  knuckle = cyl_x(HINGE_R, -KNUCKLE_HALF, KNUCKLE_HALF) + box(-KNUCKLE_HALF, KNUCKLE_HALF, -ht, ht, 0.0, HINGE_R + 6.0)
  tail = box(-KNUCKLE_HALF, KNUCKLE_HALF, -ht, ht, -TAIL, 0.0)
  # rib along the top between the hinge and the start of the slot
  rib = box(-3.0, 3.0, ht, ht + 6.0, HINGE_R + 2.0, ARM_SLOT[0] - 8.0)
  # spring tab under the arm
  tab = box(SPRING_TAB_X - 3.0, SPRING_TAB_X + 3.0, -ht - 9.0, -ht + 0.5, SPRING_TAB_Z - 7.0, SPRING_TAB_Z + 7.0)
  tab = tab + cyl_x(5.0, SPRING_TAB_X - 3.0, SPRING_TAB_X + 3.0, y=-ht - 9.0, z=SPRING_TAB_Z)
  part = bar + knuckle + tail + rib + tab
  part = part - box(-M5_CLEAR / 2, M5_CLEAR / 2, -ARM_T, ARM_T, ARM_SLOT[0], ARM_SLOT[1])
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, segments=32)
  part = part - cyl_x(1.7, SPRING_TAB_X - 5.0, SPRING_TAB_X + 5.0, y=-ht - 9.0, z=SPRING_TAB_Z, segments=24)
  # round the far end
  part = part - (box(-w - 1, w + 1, -ht - 1, ht + 1, ARM_LEN - 6, ARM_LEN + 1) - cyl_y(w, -ht - 2, ht + 2, z=ARM_LEN - 6 - 0.0, segments=96).scale((1.0, 1.0, 6.0 / w)).translate((0, 0, (ARM_LEN - 6) * (1 - 6.0 / w))))
  return clean(part)


# ***** dash clamp *****

PLATE_T = 6.0
LIP_T = 8.0
LIP_GAP = 0.5
JAW_T = 9.0
JAW_DEPTH = 24.0               # how far the jaw reaches under the cover's edge
SCREW_Z = -12.0                # clamp screw position under the edge
HINGE_AXIS = (PLATE_T + HINGE_R + 0.5, 6.0)    # (y, z) clamp frame: above the plate, over the lip
JAW_Y0 = -(HOOD_EDGE_MAX + 5.0 + JAW_T)        # bottom of the jaw
CLAMP_HALF_W = HINGE_HALF_SPAN
LEVER_PIVOT = (-8.0, LIP_GAP + LIP_T + 14.0)   # lift lever pivot (y, z), clamp frame
LEVER_X = (-12.0, 2.0)                         # lever width
LEVER_LUG_X = ((-18.0, -12.4), (2.4, 8.0))     # clamp lugs either side of the lever
SPRING_POSTS = ((-31.0, LIP_GAP + LIP_T + 4.0), (-23.0, LIP_GAP + LIP_T + 4.0), (-15.0, LIP_GAP + LIP_T + 4.0))
SWITCH_X = (-27.0, -20.6)                      # microswitch body against the clamp's lug, x range


def dash_clamp() -> Manifold:
  w = CLAMP_HALF_W
  zf = LIP_GAP + LIP_T                           # front face of the lip
  plate = box(-w, w, 0.0, PLATE_T, -CLAMP_DEPTH, zf)
  lip = box(-w, w, JAW_Y0, PLATE_T, LIP_GAP, zf)
  jaw = box(-w, w, JAW_Y0, JAW_Y0 + JAW_T, -JAW_DEPTH, zf)
  part = plate + lip + jaw
  # clamp screw up through the jaw with a nut trapped in the jaw's underside
  part = part - cyl_y(M6_CLEAR / 2, JAW_Y0 - 1, JAW_Y0 + JAW_T + 1, z=SCREW_Z, segments=32)
  part = part - hex_prism_y(M6_NUT_AF, JAW_Y0 - 0.01, JAW_Y0 + M6_NUT_T + 0.3, z=SCREW_Z)
  # hinge knuckles on the plate, over the lip
  hy, hz = HINGE_AXIS
  for sgn in (-1, 1):
    x0, x1 = (w - CLAMP_KNUCKLE, w) if sgn > 0 else (-w, -w + CLAMP_KNUCKLE)
    part = part + cyl_x(HINGE_R, x0, x1, y=hy, z=hz) + box(x0, x1, 0.0, hy, hz - HINGE_R, hz + HINGE_R)
  part = part - cyl_x(M5_CLEAR / 2, -w - 1, w + 1, y=hy, z=hz, segments=32)
  # room for the arm's knuckle and tail to turn
  inner = w - CLAMP_KNUCKLE
  part = part - (cyl_x(HINGE_R + 1.2, -inner, inner, y=hy, z=hz) + box(-inner, inner, PLATE_T + 0.3, hy + 30, -TAIL - 15, hz + 40))
  # spring posts on the lip's front face: holes along x through a tab (pick the one that stretches the spring
  # 8-15 mm with the motor gear on the teeth)
  tab = box(SPRING_POST_X[0], SPRING_POST_X[1], SPRING_POSTS[0][0] - 5.0, SPRING_POSTS[-1][0] + 5.0, zf - 0.5, zf + 8.0)
  part = part + tab
  for y, z in SPRING_POSTS:
    part = part - cyl_x(1.8, SPRING_POST_X[0] - 1, SPRING_POST_X[1] + 1, y=y, z=z, segments=24)
  # lift lever lugs, in front of the lip below the arm
  ly, lz = LEVER_PIVOT
  for x0, x1 in LEVER_LUG_X:
    lug = box(x0, x1, ly - 9.0, ly + 7.0, zf - 0.5, lz + 7.0) + cyl_x(7.0, x0, x1, y=ly, z=lz)
    part = part + lug
  part = part - cyl_x(M4_CLEAR / 2, -40, 40, y=ly, z=lz, segments=32)
  # microswitch seat (KW11-3Z, 20 x 10 x 6.4 mm, M2 holes 9.5 mm apart) on the outside of the left lug
  sw = box(SWITCH_X[0] - 3.0, SWITCH_X[0], ly - 14.0, ly + 6.0, zf - 0.5, lz + 12.0)
  part = part + sw
  for dz in (-4.75, 4.75):
    part = part - cyl_x(1.0, SWITCH_X[0] - 4.0, SWITCH_X[0] + 1.0, y=ly - 4.0, z=lz + 2.0 + dz, segments=16)
  return clean(part)


SPRING_POST_X = (SPRING_TAB_X - 3.0, SPRING_TAB_X + 3.0)


# ***** lift lever *****

LEVER_SCREW_R = 11.0      # stop screw distance from the lever's pivot
LEVER_ON_ANGLE = 32.0     # lever turned this far from straight up when the arm is down ("on")
LEVER_OFF_PAST = 6.0      # and this far past straight up the other way when lifted ("off")


def lift_lever() -> Manifold:
  """Lever frame: pivot axis along x through the origin. Built in the 'off' position's reference: the stop
  screw's axis points straight up (+y) at z = 0 from a platform LEVER_SCREW_R above the pivot. A nut trapped in
  the platform takes the M4 stop screw. The finger tab points forward (+z); a foot presses the power switch when
  the lever is 'on'."""
  x0, x1 = LEVER_X
  body = prism_x([(-7.0, -7.0), (-7.0, 7.0), (LEVER_SCREW_R + 4.0, 7.0), (LEVER_SCREW_R + 4.0, -7.0)], x0, x1)
  body = body + cyl_x(7.0, x0, x1)
  # finger tab: forward and up
  tab = prism_x([(LEVER_SCREW_R - 2.0, 5.0), (LEVER_SCREW_R + 4.0, 5.0), (LEVER_SCREW_R + 14.0, 34.0), (LEVER_SCREW_R + 8.0, 36.0)], x0, x1)
  # switch foot on the -x side (the switch sits beyond the left lug)
  foot = prism_x([(-2.0, -7.0), (4.0, -7.0), (4.0, -14.0), (-2.0, -16.0)], x0, x1)
  part = body + tab + foot
  part = part - cyl_x(M4_CLEAR / 2, x0 - 1, x1 + 1, segments=32)
  # stop screw: M4 up through the platform, nut trapped from below
  xc = (x0 + x1) / 2
  part = part - cyl_y(M4_CLEAR / 2, 0.0, LEVER_SCREW_R + 10, x=xc, z=0.0, segments=32)
  part = part - hex_prism_y(7.2, LEVER_SCREW_R - 4.5, LEVER_SCREW_R - 1.0, x=xc, z=0.0)
  return clean(part)


# ***** clamp pad *****

def clamp_pad() -> Manifold:
  """Swivel pad for the end of the M6 clamp screw: the screw's end sits in the pocket. Stick rubber on top."""
  return cyl(11.0, 0, 5.0, segments=96) - cyl(3.4, -1, 3.0, segments=32)

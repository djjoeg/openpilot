#!/usr/bin/env python3
"""
Printed parts for the Honda Accord (2008-12) lane keeping motor.

  steering wheel teeth (left and right half) - zip-tied around the top of the steering wheel
  motor gear                                  - on the motor shaft, meshes with the steering wheel teeth
  motor bracket                               - holds the motor; has the finger guard around the motor gear
  arm slider                                  - clamps onto the arm, holds the motor bracket at an adjustable angle
  arm                                         - hinges on the dash clamp; flips down to put the motor gear on the teeth
  dash clamp                                  - clamps onto the edge of the cover over the gauges; holds the arm,
                                                the spring, the stop screw and the switch that cuts the motor's power
  clamp pad                                   - swivel pad on the dash clamp's screw
  fit tests                                   - a short piece of the steering wheel teeth to check the fit on the
                                                steering wheel, and a few teeth to check the motor gear meshes

Everything is generated from the measurements below. To change them, edit the numbers or pass options, then run

  python3 accord_lka_parts.py --out ../stl

It writes the STL files, checks that every part is a closed solid that fits the print bed, that the gears mesh
without touching through the whole range of the teeth, that the motor gear and its bracket stay clear of the
steering wheel teeth, and how the arm's spring pulls; then saves pictures of each part and of the assembly.

Steering wheel frame used below: the steering column is the Z axis, pointing at the driver; +Y is 12 o'clock;
+X is the driver's right. Millimetres throughout.
"""
import argparse
import json
import math
import os
import struct
import sys

import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments

from gears import MODULE, free_play, gear_outline, mesh_sweep, pitch_radius, sector

set_circular_segments(64)

# ***** measurements of the car (change these to match yours) *****

# Steering wheel. Published cover sizing lists the 2008-12 Accord at 14 3/8 - 14 1/2 in across (365-368 mm) and
# 4 1/8 in (105 mm) around the part you hold, which is 33 mm thick if it is round. Measure yours.
WHEEL_OD = 367.0      # across the steering wheel, outside edge to outside edge, through the centre
GRIP = 33.0           # thickness of the part you hold at the top (distance around it / 3.14)

# ***** design choices *****

PAD = 1.0             # room for one wrap of rubber tape between the steering wheel teeth and the steering wheel
WALL = 3.5            # plastic around the part you hold

RING_TEETH = 197      # tooth count of the full circle the steering wheel teeth are cut from (pitch radius 197 mm)
MOTOR_TEETH = 19      # motor gear: 38 mm across the teeth's pitch circle
TEETH_ON_WHEEL = 32   # teeth actually printed, centred on 12 o'clock: 58.5 degrees of steering wheel turn
BACKLASH = 0.175      # each gear's teeth are this much thinner than nominal (mm at the pitch circle)
ROLL_GROW = 0.15      # the rolling band and the motor gear's roller are this much bigger than the pitch circles

ROLL_PAST_TEETH = 6.5   # degrees of rolling band past the last tooth, each side (the roller spins up before the teeth meet)
END_LEAD_IN = 2.5       # degrees over which the rolling band slopes down at each end
SPLIT_LAP = 3           # the two halves overlap this many teeth at 12 o'clock (glued)
TIE_ANGLES = (9.5, 20.5, 31.0)   # zip tie positions each side of 12 o'clock, degrees
TIE_W, TIE_T = 5.8, 2.4          # zip tie slot for 4.8 mm wide ties

# Along the steering column (z, + towards the driver), the bands both gears share. The part you hold is centred on z=0.
Z_ROLL = (-7.0, -1.65)      # rolling band on the steering wheel teeth
Z_TEETH = (1.0, 13.0)       # teeth on the steering wheel teeth
Z_MOTOR_FACE = -13.5        # front face of the motor (where the shaft comes out)
MOTOR_PLATE_T = 5.0         # motor bracket plate, between the motor and the motor gear
Z_GEAR_ROLLER = (-8.0, 0.5)   # motor gear: roller
Z_GEAR_TEETH = (1.25, 12.5)   # motor gear: teeth

# NEMA 17 motor (STEPPERONLINE 17HS19-2004S1): 42.3 mm square, 48 mm long, M3 holes 31 mm apart, 22 mm boss,
# 5 mm shaft 24 mm long with a D flat 15 mm long (4.5 mm across the flat)
NEMA = 42.3
NEMA_LEN = 48.0
NEMA_HOLES = 31.0
NEMA_BOSS = 22.0
SHAFT_D = 5.0
SHAFT_ACROSS_FLAT = 4.5
SHAFT_LEN = 24.0
SHAFT_FLAT_LEN = 15.0

# Screws and nuts
M3_CLEAR, M3_PILOT = 3.4, 2.6           # M3 through hole / hole an M3 screw cuts its own thread into
M4_PILOT = 3.4
M5_CLEAR, M5_NUT_AF, M5_NUT_T = 5.5, 8.2, 4.4    # M5 hole / nut across flats / nyloc nut thickness (DIN 985: 5 mm, 4.2 plain)
M6_CLEAR, M6_NUT_AF, M6_NUT_T = 6.5, 10.2, 5.4

# Arm and dash clamp
ARM_LEN = 175.0       # hinge to the end of the arm
ARM_W, ARM_T = 36.0, 10.0
ARM_SLOT = (60.0, 160.0)       # slot for the arm slider's bolts, measured from the hinge
HINGE_R = 9.0                  # radius of the hinge knuckles around the M5 hinge bolt
HINGE_HALF_SPAN = 27.0         # outside of the dash clamp's knuckles from the middle
CLAMP_KNUCKLE = 7.0            # thickness of each dash clamp knuckle
KNUCKLE_GAP = 0.4
TAIL = 34.0                    # arm tail behind the hinge (spring, switch, stop screw)
HOOD_EDGE_MAX = 26.0           # the dash clamp grips a cover edge up to this thick

BED = (220.0, 220.0, 250.0)    # print bed it must fit (most printers are this size or bigger)

# Nominal place of the hinge relative to the motor gear's centre when the arm is down (wheel frame, y up the
# steering wheel's face, z towards the driver). The slider and the angle joint take up the real car's differences.
HINGE_FROM_GEAR = (45.0, -165.0)


# ***** small helpers *****

def box(x0, x1, y0, y1, z0, z1) -> Manifold:
  return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def cyl(r, z0, z1, x=0.0, y=0.0, segments=64) -> Manifold:
  return Manifold.cylinder(z1 - z0, r, r, segments).translate((x, y, z0))


def cyl_x(r, x0, x1, y=0.0, z=0.0, segments=64) -> Manifold:
  """Cylinder along X from x0 to x1, centred at (y, z)."""
  return Manifold.cylinder(x1 - x0, r, r, segments).rotate((0, 90, 0)).translate((x0, y, z))


def cyl_y(r, y0, y1, x=0.0, z=0.0, segments=64) -> Manifold:
  """Cylinder along Y from y0 to y1, centred at (x, z)."""
  return Manifold.cylinder(y1 - y0, r, r, segments).rotate((-90, 0, 0)).translate((x, y0, z))


def hex_prism(af, z0, z1, x=0.0, y=0.0, rot=30.0) -> Manifold:
  r = af / math.sqrt(3)
  pts = [(x + r * math.cos(math.radians(rot + 60 * i)), y + r * math.sin(math.radians(rot + 60 * i))) for i in range(6)]
  return CrossSection([pts]).extrude(z1 - z0).translate((0, 0, z0))


def union(parts) -> Manifold:
  parts = [p for p in parts if p is not None]
  return Manifold.batch_boolean(parts, manifold3d_op("Add")) if len(parts) > 1 else parts[0]


def manifold3d_op(name):
  import manifold3d
  return getattr(manifold3d.OpType, name)


def revolve(points, a0_deg: float, a1_deg: float, step_deg: float = 0.5) -> Manifold:
  """Revolves an (r, z) outline about the Z axis from angle a0 to a1 (counterclockwise seen from +Z)."""
  span = a1_deg - a0_deg
  segs = max(4, int(math.ceil(span / step_deg)))
  full = int(round(segs * 360.0 / span))
  return Manifold.revolve(CrossSection([points]), full, span).rotate((0, 0, a0_deg))


def polar_mask(radius_of, a0_deg, a1_deg, z0, z1, step_deg=0.25) -> Manifold:
  """Plan-view outline r = radius_of(angle) from a0 to a1 (pie shape from the centre), extruded from z0 to z1."""
  n = max(2, int(math.ceil((a1_deg - a0_deg) / step_deg)) + 1)
  pts = [(0.0, 0.0)]
  for a in np.linspace(a0_deg, a1_deg, n):
    r = radius_of(a)
    pts.append((r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
  return CrossSection([pts]).extrude(z1 - z0).translate((0, 0, z0))


# ***** steering wheel teeth *****

class Teeth:
  """Radii and angles of the steering wheel teeth for one steering wheel size."""

  def __init__(self, wheel_od: float = WHEEL_OD, grip: float = GRIP):
    self.wheel_od, self.grip = wheel_od, grip
    self.r_wheel = wheel_od / 2.0
    self.rr = self.r_wheel - grip / 2.0               # centre of the part you hold
    self.rho = grip / 2.0 + PAD                        # channel radius around it
    self.r_in = self.r_wheel + PAD                     # inside of the outer band
    self.wz = self.rho                                 # inside faces of the front and back walls
    self.wz_out = self.wz + WALL
    self.rp = pitch_radius(RING_TEETH)
    self.r_root = self.rp - 1.25 * MODULE
    self.r_tip = self.rp + MODULE
    self.r_roll = self.rp + ROLL_GROW
    self.r_base = self.r_in + WALL                     # outer band where it carries no teeth or rolling band
    self.pitch_deg = 360.0 / RING_TEETH
    self.teeth_half = TEETH_ON_WHEEL / 2 * self.pitch_deg
    self.roll_half = self.teeth_half + ROLL_PAST_TEETH
    self.half = self.roll_half + END_LEAD_IN
    self.lap = SPLIT_LAP * self.pitch_deg
    self.r_split = self.r_in + TIE_T + 0.8             # the halves' overlap: outer part on the left half, inner on the right
    self.front_inner = self.rr + 1.0                   # front wall reaches just short of the middle of the part you hold
    # back wall: 45 degree slope that touches the part you hold, so the piece prints face down without supports
    self.back_line = self.rr + self.rho * math.sqrt(2.0)   # r - z = back_line along the slope
    self.z_slope_top = self.r_in - self.back_line          # where the slope meets the outer band (negative z)
    self.back_inner = self.back_line - self.wz_out
    if self.r_root - self.r_base < 2.0:
      raise ValueError(f"steering wheel {wheel_od} mm across is too big for {RING_TEETH} teeth: no room under the teeth")
    if self.r_split > self.r_base - 0.6:
      raise ValueError("no room for the overlap between the two halves")

  @property
  def tracked_arc_deg(self) -> float:
    """Steering wheel turn over which the motor gear turns with the wheel: teeth plus rolling band, end to end."""
    return 2.0 * self.roll_half

  def profile(self, roll_r: float):
    """(r, z) outline of the piece at one angle, with the rolling band at radius roll_r."""
    zf, zk = self.wz_out, -self.wz_out
    zr0, zr1 = Z_ROLL
    zt0, zt1 = Z_TEETH
    rb = max(roll_r, self.r_base)
    cone_top = min(rb, self.r_tip)
    pts = [
      (self.front_inner, zf),                       # front wall (driver side), inner end, outer face
      (self.front_inner, self.wz),                  # front wall inner face
      (self.r_in, self.wz),                         # channel: the part you hold sits here
      (self.r_in, self.z_slope_top),
      (self.back_inner, zk),                        # back wall: 45 degree slope down to its outer face
      (self.r_base, zk),
      (self.r_base, zr0),                           # up the back of the outer band
      (rb, zr0),                                    # rolling band
      (rb, zr1),
      (min(rb, self.r_root) if rb < self.r_root else self.r_root, zt0),   # 45 degree slope down to the teeth's root
      (self.r_root if rb >= self.r_root else rb, zt1),
      (cone_top if rb >= self.r_root else rb, zt1),  # under the teeth's front end
      (max(self.r_base, (cone_top if rb >= self.r_root else rb) - (zf - zt1)), zf),  # 45 degree slope to the front face
    ]
    # drop repeated points (when the rolling band is low at the ends)
    out = []
    for p in pts:
      if not out or (abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6):
        out.append(p)
    return out

  def roll_radius_at(self, angle_from_top: float) -> float:
    """Rolling band radius at an angle from 12 o'clock: full height, then sloping down over END_LEAD_IN."""
    a = abs(angle_from_top)
    if a <= self.roll_half:
      return self.r_roll
    t = min(1.0, (a - self.roll_half) / END_LEAD_IN)
    return self.r_roll - t * (self.r_roll - self.r_base)


def teeth_outline(t: Teeth) -> CrossSection:
  """2D outline of the printed teeth around 12 o'clock (a tooth gap at 12 o'clock), the two end teeth lowered."""
  gear = gear_outline(RING_TEETH, BACKLASH).rotate(90.0 - t.pitch_deg / 2.0)
  ring = gear ^ sector(t.r_tip + 1.0, 90.0 - t.teeth_half, 90.0 + t.teeth_half, r_in=t.r_root - 0.6)
  for k, tip in ((0, t.r_root + 1.2), (1, t.r_root + 3.0)):
    for sign in (1, -1):
      a_out = 90.0 + sign * (t.teeth_half - k * t.pitch_deg)
      a_in = 90.0 + sign * (t.teeth_half - (k + 1) * t.pitch_deg)
      lo, hi = sorted((a_in, a_out))
      s = sector(t.r_tip + 1.0, lo, hi, r_in=t.r_root - 0.6)
      ring = (ring - s) + (ring ^ s ^ CrossSection.circle(tip, 4096))
  return ring


def teeth_solid(t: Teeth) -> Manifold:
  """The whole steering wheel teeth piece, before splitting into halves."""
  a0, a1 = 90.0 - t.half, 90.0 + t.half
  body = revolve(t.profile(t.r_roll), a0, a1)
  # plan-view mask: the rolling band and its slopes only over the middle, lowered at the ends
  mask = polar_mask(lambda a: t.roll_radius_at(a - 90.0) + 0.01, a0, a1, -t.wz_out - 1, t.wz_out + 1)
  body = body ^ (mask + cyl(t.r_base, -t.wz_out - 1, t.wz_out + 1, segments=720))
  teeth = teeth_outline(t).extrude(Z_TEETH[1] - Z_TEETH[0]).translate((0, 0, Z_TEETH[0]))
  return body + teeth


def tie_slots(t: Teeth, angles) -> Manifold:
  """Zip tie slots: along the inside of the outer band, against the part you hold, and through both walls."""
  slots = []
  for a in angles:
    slot = box(t.r_in - 2.0, t.r_in + TIE_T, -TIE_W / 2, TIE_W / 2, -t.wz_out - 5, t.wz_out + 5)
    slots.append(slot.rotate((0, 0, a)))
  return union(slots)


def teeth_half(t: Teeth, side: str) -> Manifold:
  """side 'right': from 12 o'clock towards 3 o'clock (driver's right). 'left': towards 9 o'clock.
  The left half carries the outer band across 12 o'clock for SPLIT_LAP teeth into the right half's side; the
  right half carries the channel part there. Glue the overlap."""
  whole = teeth_solid(t)
  zlo, zhi = -t.wz_out - 2, t.wz_out + 2
  big = t.r_tip + 5
  if side == "right":
    keep = (sector(big, 90.0 - t.half - 1, 90.0 - t.lap, r_in=0.0)
            + sector(t.r_split, 90.0 - t.lap - 0.5, 90.0 + t.lap, r_in=0.0))
    angles = [90.0 - a for a in TIE_ANGLES]
  else:
    keep = (sector(big, 90.0 + t.lap, 90.0 + t.half + 1, r_in=0.0)
            + (sector(big, 90.0 - t.lap, 90.0 + t.lap + 0.5, r_in=0.0) - sector(t.r_split, 90.0 - t.lap - 1, 90.0 + t.lap + 1)))
    angles = [90.0 + a for a in TIE_ANGLES]
  part = whole ^ keep.extrude(zhi - zlo).translate((0, 0, zlo))
  return part - tie_slots(t, angles)


def grip_fit_test(t: Teeth, span_deg: float = 12.0) -> Manifold:
  """A short piece of the channel (no teeth) with one zip tie slot, to try on the steering wheel first."""
  a0, a1 = 90.0 - span_deg / 2, 90.0 + span_deg / 2
  body = revolve(t.profile(t.r_base), a0, a1)
  return body - tie_slots(t, [90.0])


def tooth_fit_test(t: Teeth, n_teeth: int = 6) -> Manifold:
  """A few teeth with their rolling band on a stub of the outer band, to try against the printed motor gear."""
  half = n_teeth / 2 * t.pitch_deg
  a0, a1 = 90.0 - half - 1.0, 90.0 + half + 1.0
  zlo = Z_ROLL[0] - 2.0
  pts = [p for p in t.profile(t.r_roll) if p[0] >= t.r_base - 6.0]
  body = revolve([(t.r_base - 6.0, Z_TEETH[1] + 2.0)] + [(r, z) for r, z in pts if z <= Z_TEETH[1] + 0.01 and z >= zlo]
                 + [(t.r_base - 6.0, zlo)], a0, a1)
  # simple profile: band from r_base-6 to the rolling band / teeth root
  band = revolve([(t.r_base - 6.0, zlo), (t.r_roll, zlo), (t.r_roll, Z_ROLL[1]), (t.r_root, Z_TEETH[0]),
                  (t.r_root, Z_TEETH[1]), (t.r_base - 6.0, Z_TEETH[1])], a0, a1)
  gear = gear_outline(RING_TEETH, BACKLASH).rotate(90.0 - t.pitch_deg / 2.0)
  teeth = (gear ^ sector(t.r_tip + 1, 90.0 - half, 90.0 + half, r_in=t.r_root - 0.6)).extrude(
    Z_TEETH[1] - Z_TEETH[0]).translate((0, 0, Z_TEETH[0]))
  del body
  return band + teeth


# ***** motor gear *****

def motor_gear() -> Manifold:
  """Motor gear in its own frame: z = 0 at the motor's front face, shaft along +z. Teeth, roller, D bore, and a
  hole through a tooth gap for an M3 set screw onto the shaft's flat."""
  off = -Z_MOTOR_FACE
  zr0, zr1 = (z + off for z in Z_GEAR_ROLLER)
  zt0, zt1 = (z + off for z in Z_GEAR_TEETH)
  rp = pitch_radius(MOTOR_TEETH)
  rf = rp - 1.25 * MODULE
  teeth = gear_outline(MOTOR_TEETH, BACKLASH).extrude(zt1 - zt0).translate((0, 0, zt0))
  roller = cyl(rp + ROLL_GROW, zr0, zr1, segments=360)
  core = cyl(rf, zr1 - 0.01, zt0 + 0.01, segments=180)
  part = teeth + roller + core
  # bore: round where the shaft is round, D where it has its flat (the flat is on +y)
  flat_from = SHAFT_LEN - SHAFT_FLAT_LEN
  r = SHAFT_D / 2 + 0.12
  d_shape = CrossSection.circle(r, 96) - CrossSection.square((2 * r + 1, 2 * r)).translate(
    (-r - 0.5, SHAFT_ACROSS_FLAT - SHAFT_D / 2 + 0.12))
  part = part - cyl(r, zr0 - 1, flat_from + 0.01, segments=96) - d_shape.extrude(zt1 + 1 - flat_from).translate((0, 0, flat_from))
  # set screw: radial along +y (onto the flat), through the middle of a tooth gap; M3 cuts its own thread
  z_set = (zt0 + min(zt1, SHAFT_LEN)) / 2.0
  gap_angle = 90.0 + 180.0 / MOTOR_TEETH      # tooth 0 is on +x; gaps sit half a pitch from each tooth
  hole = cyl_y(M3_PILOT / 2, 0.0, rp + 4, z=z_set, segments=32).rotate((0, 0, gap_angle - 90.0))
  return part - hole


# ***** motor bracket (plate + finger guard + angle joint ears) *****

PLATE_HALF = NEMA / 2 + 2.5
EAR_X = 16.0             # ears for the angle joint, inside faces at +-EAR_X ... outside at +-(EAR_X + EAR_T)
EAR_T = 6.0
PIVOT_UP = PLATE_HALF + 14.0   # angle joint pivot above the motor's axis (in the bracket frame, y)
PIVOT_BACK = -26.0             # and behind the motor's front face (towards the dash), z


def motor_bracket() -> Manifold:
  """Bracket frame: z = 0 at the motor's front face, +z towards the motor gear and the driver, motor axis on z,
  +y up (away from the steering wheel). The plate sits in front of the motor (z 0..MOTOR_PLATE_T); the finger
  guard wraps the top and sides of the motor gear; two ears reach back over the motor for the angle joint."""
  t = MOTOR_PLATE_T
  plate = box(-PLATE_HALF, PLATE_HALF, -PLATE_HALF, PLATE_HALF, 0, t)
  plate = plate - cyl(NEMA_BOSS / 2 + 0.4, -1, t + 1, segments=128)
  for sx in (-1, 1):
    for sy in (-1, 1):
      x, y = sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2
      plate = plate - cyl(M3_CLEAR / 2, -1, t + 1, x, y, 32) - cyl(3.3, t - 2.5, t + 1, x, y, 32)  # head recess

  # finger guard: a shell around the gear, open below (where it meets the teeth on the steering wheel)
  g_in, g_out = pitch_radius(MOTOR_TEETH) + MODULE + 2.0, pitch_radius(MOTOR_TEETH) + MODULE + 4.0
  zg0, zg1 = t, (Z_GEAR_TEETH[1] - Z_MOTOR_FACE) + 2.0
  shell = cyl(g_out, zg0, zg1, segments=180) - cyl(g_in, zg0 - 1, zg1 + 1, segments=180)
  lip = (cyl(g_out, zg1 - 1.6, zg1, segments=180) - Manifold.cylinder(1.6, g_in, g_in - 3.0, 180).translate((0, 0, zg1 - 1.6)))
  guard = shell + lip
  # open window at the bottom: +-55 degrees around straight down
  window = sector(g_out + 5, 270.0 - 55.0, 270.0 + 55.0, r_in=0.0).extrude(zg1 - zg0 + 4).translate((0, 0, zg0 - 2))
  guard = guard - window
  # skids: rounded lower ends of the guard so a hand pushes the arm up instead of catching an edge
  for sgn in (-1, 1):
    a = math.radians(270.0 + sgn * 55.0)
    x, y = (g_in + g_out) / 2 * math.cos(a), (g_in + g_out) / 2 * math.sin(a)
    guard = guard + cyl(1.6, zg0, zg1, x, y, 24)

  # ears for the angle joint: reach up from the plate's top and back over the motor body
  ears = []
  for sgn in (-1, 1):
    x0 = sgn * EAR_X if sgn > 0 else -EAR_X - EAR_T
    x1 = x0 + EAR_T
    web = box(x0, x1, PLATE_HALF - 8.0, PIVOT_UP, PIVOT_BACK, t)
    boss = cyl_x(9.0, x0, x1, y=PIVOT_UP, z=PIVOT_BACK)
    ear = web + boss
    ear = ear - cyl_x(M5_CLEAR / 2, x0 - 1, x1 + 1, y=PIVOT_UP, z=PIVOT_BACK, segments=32)
    ears.append(ear)
  # gusset between the ears across the top of the plate
  bridge = box(-EAR_X - EAR_T, EAR_X + EAR_T, PLATE_HALF - 8.0, PLATE_HALF + 2.0, PIVOT_BACK + 6, t)
  part = plate + guard + union(ears) + bridge
  # keep the motor body and the boss clear (the ears reach back over the motor)
  part = part - box(-NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA_LEN - 5, 0.0)
  return part


# ***** arm slider (rides on the arm; angle joint for the motor bracket) *****

SLIDER_LEN = 46.0


def arm_slider() -> Manifold:
  """Slider frame: the arm runs along +z with its wide face in the x-z plane, slider sitting on top (y > 0) of
  the arm's top face at y = ARM_T/2. Two M5 bolts through the arm's slot clamp it. Cheeks reach down past the
  arm on both sides and carry the angle joint's pivot hole and the curved slot for the locking bolt, so the
  motor bracket's ears sit inside the cheeks."""
  top = ARM_T / 2
  base = box(-ARM_W / 2 - 2.0, ARM_W / 2 + 2.0, top, top + 7.0, 0.0, SLIDER_LEN)
  guides = box(-ARM_W / 2 - 2.0, -ARM_W / 2 - 0.25, -top + 1.5, top + 7.0, 0.0, SLIDER_LEN) + \
           box(ARM_W / 2 + 0.25, ARM_W / 2 + 2.0, -top + 1.5, top + 7.0, 0.0, SLIDER_LEN)
  part = base + guides
  for z in (9.0, SLIDER_LEN - 9.0):
    part = part - cyl_y(M5_CLEAR / 2, -20, 40, z=z, segments=32)
    part = part - cyl_y(5.2, top + 4.0, top + 20, z=z, segments=32)       # bolt head recess
  # cheeks: outside the bracket's ears (ears' outer faces at +-(EAR_X + EAR_T)), joint axis along x
  cx_in = EAR_X + EAR_T + 0.3
  joint_y, joint_z = top + 7.0 + 16.0, SLIDER_LEN + 6.0
  cheeks = []
  for sgn in (-1, 1):
    x0, x1 = (cx_in, cx_in + 6.0) if sgn > 0 else (-cx_in - 6.0, -cx_in)
    plate = box(x0, x1, top, joint_y, 4.0, SLIDER_LEN) + cyl_x(12.0, x0, x1, y=joint_y, z=joint_z)
    plate = plate + box(x0, x1, top, joint_y, SLIDER_LEN - 6, joint_z)
    cheeks.append(plate)
  part = part + union(cheeks)
  # pivot hole and the curved locking slot (+-35 degrees at 16 mm from the pivot)
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=joint_y, z=joint_z, segments=32)
  slot_pts = []
  r_slot = 16.0
  for a in np.linspace(-35, 35, 36):
    slot_pts.append((joint_z + r_slot * math.cos(math.radians(180 + a)), joint_y + r_slot * math.sin(math.radians(180 + a))))
  # the slot as a chain of short cylinders
  for zc, yc in slot_pts:
    part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=yc, z=zc, segments=20)
  return part, (joint_y, joint_z)


# ***** arm *****

def arm() -> Manifold:
  """Arm frame: hinge axis along x through the origin; the bar runs along +z (towards the motor) with its wide
  face in the x-z plane and its top face at y = ARM_T/2. Behind the hinge, the tail (along -z) carries the
  spring holes, the pad that presses the motor power switch, and the pad the stop screw rests on."""
  half_t = ARM_T / 2
  bar = box(-ARM_W / 2, ARM_W / 2, -half_t, half_t, HINGE_R - 2.0, ARM_LEN)
  # rib on top for stiffness, stopping short of the slider's travel
  rib = box(-3.0, 3.0, half_t, half_t + 6.0, HINGE_R + 2.0, ARM_SLOT[0] - SLIDER_LEN / 2)
  slot = box(-M5_CLEAR / 2, M5_CLEAR / 2, -ARM_T, ARM_T, ARM_SLOT[0], ARM_SLOT[1])
  knuckle_w = HINGE_HALF_SPAN - CLAMP_KNUCKLE - KNUCKLE_GAP
  knuckle = cyl_x(HINGE_R, -knuckle_w, knuckle_w)
  tail = box(-knuckle_w, knuckle_w, -half_t, half_t, -TAIL, 0.0)
  part = bar + rib + knuckle + tail - slot
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, segments=32)
  # spring holes in the tail (choose one to set how hard the motor gear presses on the steering wheel teeth)
  for z in (-TAIL + 5.0, -TAIL + 12.0, -TAIL + 19.0):
    part = part - cyl_y(1.7, -20, 20, z=z, segments=24)
  return part


def dash_clamp() -> Manifold:
  """Clamp frame: hinge axis along x through the origin. The cover over the gauges ends in an edge facing the
  driver: its top face is at y = CLAMP_TOP_Y and its front face at z = CLAMP_FRONT_Z (the clamp's lip hangs just in
  front of it). The jaw reaches under the edge; an M6 screw with the clamp pad presses up against its underside.
  The two knuckles hang below the lip, outside the arm's knuckle. Above the arm's tail: the spring post, the
  M4 stop screw and the motor power switch."""
  w = HINGE_HALF_SPAN
  top_y = CLAMP_TOP_Y
  front_z = CLAMP_FRONT_Z
  plate = box(-w, w, top_y, top_y + 6.0, front_z - 55.0, front_z + 8.0)
  lip = box(-w, w, -HINGE_R - 2.0, top_y + 6.0, front_z + 0.5, front_z + 8.5)
  jaw_y0 = top_y - HOOD_EDGE_MAX - 12.0
  jaw = box(-w, w, jaw_y0, jaw_y0 + 9.0, front_z - 28.0, front_z + 8.5)
  # lip continues down to the jaw
  lip2 = box(-w, w, jaw_y0, -HINGE_R - 2.0, front_z + 0.5, front_z + 8.5)
  part = plate + lip + jaw + lip2
  # M6 screw up through the jaw, nut trapped underneath
  zs = front_z - 15.0
  part = part - cyl_y(M6_CLEAR / 2, jaw_y0 - 1, jaw_y0 + 12, z=zs, segments=32)
  part = part - hex_prism(M6_NUT_AF, 0, M6_NUT_T + 0.3).rotate((-90, 0, 0)).translate((0, jaw_y0 - 0.01, zs))
  # knuckles below the lip, in front of it
  for sgn in (-1, 1):
    x0, x1 = (w - CLAMP_KNUCKLE, w) if sgn > 0 else (-w, -w + CLAMP_KNUCKLE)
    k = cyl_x(HINGE_R, x0, x1) + box(x0, x1, 0.0, top_y, -HINGE_R, front_z + 8.5)
    part = part + k
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, segments=32)
  # keep the arm's swing clear between the knuckles
  inner = HINGE_HALF_SPAN - CLAMP_KNUCKLE
  part = part - (cyl_x(HINGE_R + 1.5, -inner, inner) + box(-inner, inner, -HINGE_R - 1.5, HINGE_R + 1.5, 0.0, 60.0))
  return part


CLAMP_TOP_Y = 36.0      # top of the cover's edge above the hinge axis
CLAMP_FRONT_Z = -8.0    # front face of the cover's edge, relative to the hinge axis


def clamp_pad() -> Manifold:
  """Swivel pad for the end of the M6 clamp screw. Stick a piece of rubber on top."""
  return cyl(11.0, 0, 5.0, segments=96) - cyl(3.1, -1, 3.0, segments=32)


# ***** checks *****

def report_solid(name: str, m: Manifold, printable: Manifold) -> dict:
  x0, y0, z0, x1, y1, z1 = printable.bounding_box()
  size = (x1 - x0, y1 - y0, z1 - z0)
  return {"name": name, "volume_cm3": round(m.volume() / 1000.0, 2), "triangles": m.num_tri(), "genus": m.genus(),
          "status": str(m.status()).split(".")[-1], "print_size_mm": [round(s, 1) for s in size],
          "fits_bed": size[0] <= BED[0] and size[1] <= BED[1] and size[2] <= BED[2]}


def write_stl(m: Manifold, path: str):
  mesh = m.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3].astype(np.float64)
  t = np.asarray(mesh.tri_verts)
  p0, p1, p2 = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
  n = np.cross(p1 - p0, p2 - p0)
  n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
  data = np.zeros(len(t), dtype=[("n", "<f4", 3), ("v0", "<f4", 3), ("v1", "<f4", 3), ("v2", "<f4", 3), ("a", "<u2")])
  data["n"], data["v0"], data["v1"], data["v2"] = n, p0, p1, p2
  with open(path, "wb") as f:
    f.write(b"Honda Accord lane keeping motor part".ljust(80, b" "))
    f.write(struct.pack("<I", len(t)))
    f.write(data.tobytes())


def on_bed(m: Manifold, rotate=(0, 0, 0)) -> Manifold:
  m = m.rotate(rotate)
  x0, y0, z0, x1, y1, z1 = m.bounding_box()
  return m.translate((-(x0 + x1) / 2, -(y0 + y1) / 2, -z0))


if __name__ == "__main__":
  sys.exit(0)

"""
Steering wheel teeth (whole, or in two halves for smaller printers), the motor gear, and the two fit tests.
"""
import math

from manifold3d import CrossSection, Manifold

from cadlib import box, clean, cyl, cyl_y, polar_mask, revolve, sector, union
from gears import MODULE, gear_outline, pitch_radius
from params import (BACKLASH, END_LEAD_IN, GRIP, M3_PILOT, MOTOR_TEETH, PAD, RING_TEETH, ROLL_GROW, ROLL_PAST_TEETH,
                    SHAFT_ACROSS_FLAT, SHAFT_D, SHAFT_FLAT_LEN, SHAFT_LEN, SPLIT_LAP, TEETH_ON_WHEEL, TIE_ANGLES, TIE_T,
                    TIE_W, WALL, WHEEL_OD, Z_GEAR_ROLLER, Z_GEAR_TEETH, Z_MOTOR_FACE, Z_ROLL, Z_TEETH)


class Teeth:
  """Radii and angles of the steering wheel teeth for one steering wheel size."""

  def __init__(self, wheel_od: float = WHEEL_OD, grip: float = GRIP):
    self.wheel_od, self.grip = wheel_od, grip
    self.r_wheel = wheel_od / 2.0
    self.rr = self.r_wheel - grip / 2.0               # centre of the part you hold
    self.rho = grip / 2.0 + PAD                        # channel radius around it
    self.r_in = self.r_wheel + PAD                     # inside of the outer band
    self.wz = self.rho                                 # inside face of the front wall
    self.wz_out = self.wz + WALL                       # outside faces of the front and back walls
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
    self.r_split = self.r_in + 2.5                     # the halves' overlap: outer part on the left half
    self.front_inner = self.rr + 1.0                   # front wall reaches to just short of the middle of the grip
    # back wall: a 45 degree slope touching the part you hold, so the piece prints front face down without supports
    self.back_line = self.rr + self.rho * math.sqrt(2.0)   # r - z = back_line along the slope
    self.z_slope_top = self.r_in - self.back_line          # where the slope meets the outer band (negative z)
    self.back_inner = self.back_line - self.wz_out
    if self.r_root - self.r_base < 2.0:
      raise ValueError(f"a steering wheel {wheel_od} mm across leaves no room under {RING_TEETH} teeth")
    if self.r_split + 1.0 > self.r_roll - (self.wz_out - Z_TEETH[1]):
      raise ValueError("no room for the overlap between the two halves")

  @property
  def tracked_arc_deg(self) -> float:
    """Steering wheel turn over which the motor gear turns with it (teeth plus rolling band), end to end."""
    return 2.0 * self.roll_half

  @property
  def teeth_arc_deg(self) -> float:
    return 2.0 * self.teeth_half

  def profile(self, roll_r: float):
    """(r, z) outline of the piece at one angle, with the rolling band at radius roll_r (r_base: no band)."""
    zf, zk = self.wz_out, -self.wz_out
    zr0, zr1 = Z_ROLL
    zt0, zt1 = Z_TEETH
    if roll_r <= self.r_base + 1e-6:
      pts = [(self.front_inner, zf), (self.front_inner, self.wz), (self.r_in, self.wz), (self.r_in, self.z_slope_top),
             (self.back_inner, zk), (self.r_base, zk), (self.r_base, zf)]
      return pts
    rb = roll_r
    root = min(self.r_root, rb)
    front_top = min(rb, self.r_tip)
    pts = [
      (self.front_inner, zf),                       # front wall (driver side): inner end, outer face
      (self.front_inner, self.wz),                  # front wall inner face
      (self.r_in, self.wz),                         # channel: the part you hold sits here
      (self.r_in, self.z_slope_top),
      (self.back_inner, zk),                        # back wall: 45 degree slope down to its outer face
      (self.r_base, zk),
      (self.r_base, zr0),                           # up the back of the outer band
      (rb, zr0),                                    # rolling band
      (rb, zr1),
      (root, zt0),                                  # 45 degree slope down to the teeth's root
      (root, zt1),
      (front_top, zt1),                             # under the teeth's front ends
      (max(self.r_base, front_top - (zf - zt1)), zf),   # 45 degree slope to the front face
    ]
    out = []
    for p in pts:
      if not out or abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6:
        out.append(p)
    return out

  def roll_radius_at(self, angle_from_top: float) -> float:
    """Rolling band radius at an angle from 12 o'clock: full height, then sloping down over END_LEAD_IN."""
    a = abs(angle_from_top)
    if a <= self.roll_half:
      return self.r_roll
    t = min(1.0, (a - self.roll_half) / END_LEAD_IN)
    return self.r_roll - t * (self.r_roll - self.r_base)


def teeth_outline(t: Teeth, n_teeth: int | None = None, lowered_ends: bool = True) -> CrossSection:
  """2D outline of the printed teeth around 12 o'clock, a tooth gap at 12 o'clock; the two end teeth each side
  are lowered so the motor gear's teeth meet them gently."""
  n_teeth = n_teeth or TEETH_ON_WHEEL
  half = n_teeth / 2 * t.pitch_deg
  gear = gear_outline(RING_TEETH, BACKLASH).rotate(90.0 - t.pitch_deg / 2.0)
  ring = gear ^ sector(t.r_tip + 1.0, 90.0 - half, 90.0 + half, r_in=t.r_root - 0.6)
  if lowered_ends:
    for k, tip in ((0, t.r_root + 1.2), (1, t.r_root + 3.0)):
      for sign in (1, -1):
        a_out = 90.0 + sign * (half - k * t.pitch_deg)
        a_in = 90.0 + sign * (half - (k + 1) * t.pitch_deg)
        lo, hi = sorted((a_in, a_out))
        s = sector(t.r_tip + 1.0, lo, hi, r_in=t.r_root - 0.6)
        ring = (ring - s) + (ring ^ s ^ CrossSection.circle(tip, 4096))
  return ring


def teeth_solid(t: Teeth) -> Manifold:
  """The whole steering wheel teeth piece, before splitting or cutting zip tie slots."""
  a0, a1 = 90.0 - t.half, 90.0 + t.half
  body = revolve(t.profile(t.r_roll), a0, a1)
  # plan-view mask: the rolling band and its slopes at full height over the middle, lowered at the ends
  mask = polar_mask(lambda a: t.roll_radius_at(a - 90.0) + 0.01, a0, a1, -t.wz_out - 1, t.wz_out + 1)
  body = body ^ (mask + cyl(t.r_base, -t.wz_out - 1, t.wz_out + 1, segments=1440))
  teeth = teeth_outline(t).extrude(Z_TEETH[1] - Z_TEETH[0]).translate((0, 0, Z_TEETH[0]))
  return body + teeth


def tie_slots(t: Teeth, angles) -> Manifold:
  """Zip tie slots: along the inside of the outer band (against the part you hold) and through both walls."""
  slots = []
  for a in angles:
    slot = box(t.r_in - 2.0, t.r_in + TIE_T, -TIE_W / 2, TIE_W / 2, -t.wz_out - 5, t.wz_out + 5)
    slots.append(slot.rotate((0, 0, a)))
  return union(slots)


def teeth_half(t: Teeth, side: str, whole: Manifold | None = None) -> Manifold:
  """side 'right': from 12 o'clock towards 3 o'clock (the driver's right). 'left': towards 9 o'clock.
  Across 12 o'clock, for SPLIT_LAP teeth each side, the left half carries the outer band with the teeth and the
  rolling band (outside r_split, from just behind the rolling band to the front face) and the right half carries
  the channel part under it. Both print front face down without supports. The overlap is glued."""
  whole = whole if whole is not None else teeth_solid(t)
  zlo, zhi = -t.wz_out - 2, t.wz_out + 2
  big = t.r_tip + 5
  z_block = Z_ROLL[0] - 0.3
  lap_zone = sector(big, 90.0 - t.lap, 90.0 + t.lap).extrude(zhi - zlo).translate((0, 0, zlo))
  outer_block = sector(big, 90.0 - t.lap, 90.0 + t.lap, r_in=t.r_split).extrude(zhi - z_block).translate((0, 0, z_block))
  if side == "right":
    region = sector(big, 90.0 - t.half - 1, 90.0 - t.lap).extrude(zhi - zlo).translate((0, 0, zlo))
    part = (whole ^ region) + (whole ^ (lap_zone - outer_block))
    angles = [90.0 - a for a in TIE_ANGLES]
  else:
    region = sector(big, 90.0 + t.lap, 90.0 + t.half + 1).extrude(zhi - zlo).translate((0, 0, zlo))
    part = (whole ^ region) + (whole ^ lap_zone ^ outer_block)
    angles = [90.0 + a for a in TIE_ANGLES]
  return clean(part - tie_slots(t, angles))


def teeth_one_piece(t: Teeth, whole: Manifold | None = None) -> Manifold:
  """The steering wheel teeth in one piece (for print beds about 250 mm or more across)."""
  whole = whole if whole is not None else teeth_solid(t)
  return clean(whole - tie_slots(t, [90.0 + a for a in TIE_ANGLES] + [90.0 - a for a in TIE_ANGLES]))


def grip_fit_test(t: Teeth, span_deg: float = 14.0) -> Manifold:
  """A short piece of the channel, no teeth, with one zip tie slot: try it on the steering wheel first."""
  a0, a1 = 90.0 - span_deg / 2, 90.0 + span_deg / 2
  body = revolve(t.profile(t.r_base), a0, a1)
  return clean(body - tie_slots(t, [90.0]))


def tooth_fit_test(t: Teeth, n_teeth: int = 8) -> Manifold:
  """A few teeth with their rolling band on a short block, to try against the printed motor gear by hand.
  Prints front face down like the steering wheel teeth."""
  half = n_teeth / 2 * t.pitch_deg
  a0, a1 = 90.0 - half - 1.5, 90.0 + half + 1.5
  r0 = t.r_base - 8.0
  zf = Z_TEETH[1] + 3.0
  zk = Z_ROLL[0] - 3.0
  pts = [(r0, zf), (r0, zk), (t.r_roll, zk), (t.r_roll, Z_ROLL[1]), (t.r_root, Z_TEETH[0]), (t.r_root, Z_TEETH[1]),
         (t.r_roll, Z_TEETH[1]), (t.r_roll - 3.0, zf)]
  body = revolve(pts, a0, a1)
  teeth = teeth_outline(t, n_teeth=n_teeth, lowered_ends=False).extrude(Z_TEETH[1] - Z_TEETH[0]).translate((0, 0, Z_TEETH[0]))
  return clean(body + teeth)


# ***** motor gear *****

def motor_gear() -> Manifold:
  """Motor gear in its own frame: z = 0 at the motor's front face, shaft along +z. Teeth, roller, D bore, and a
  hole through a tooth gap for an M3 set screw onto the shaft's flat (the screw cuts its own thread)."""
  off = -Z_MOTOR_FACE
  zr0, zr1 = (z + off for z in Z_GEAR_ROLLER)
  zt0, zt1 = (z + off for z in Z_GEAR_TEETH)
  rp = pitch_radius(MOTOR_TEETH)
  rf = rp - 1.25 * MODULE
  teeth = gear_outline(MOTOR_TEETH, BACKLASH).extrude(zt1 - zt0).translate((0, 0, zt0))
  roller = cyl(rp + ROLL_GROW, zr0, zr1, segments=360)
  core = cyl(rf, zr1 - 0.01, zt0 + 0.01, segments=180)
  part = teeth + roller + core
  # bore: round where the shaft is round, D shaped where it has its flat (flat facing +y)
  flat_from = SHAFT_LEN - SHAFT_FLAT_LEN
  r = SHAFT_D / 2 + 0.12
  flat_y = SHAFT_ACROSS_FLAT - SHAFT_D / 2 + 0.12
  d_shape = CrossSection.circle(r, 96) - CrossSection.square((2 * r + 2, 2 * r)).translate((-r - 1, flat_y))
  part = part - cyl(r, zr0 - 1, flat_from + 0.01, segments=96)
  part = part - d_shape.extrude(zt1 + 1 - flat_from).translate((0, 0, flat_from))
  # chamfer the bore's entry so the gear starts onto the shaft easily
  part = part - Manifold.cylinder(1.0, r + 0.8, r, 48).translate((0, 0, zr0))
  # set screw: radial along +y onto the flat, through the middle of a tooth gap
  z_set = (zt0 + min(zt1, SHAFT_LEN)) / 2.0
  gap_angle = 180.0 / MOTOR_TEETH          # tooth 0 is on +x; gaps sit half a pitch from each tooth
  hole = cyl_y(M3_PILOT / 2, 0.0, rp + 4, z=z_set, segments=32).rotate((0, 0, -90.0 + 90.0 - 0.0))
  # rotate the gear so a gap faces +y (where the hole and the flat are)
  part = part.rotate((0, 0, 90.0 - gap_angle))
  return clean(part - hole)


MOTOR_GEAR_PHASE = 90.0 - 180.0 / MOTOR_TEETH   # motor_gear() is turned this much from "tooth 0 on +x"

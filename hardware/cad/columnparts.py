"""
The column mount's own parts. The motor sits under the steering wheel, behind it, with its gear inside a ring of
teeth that faces the hub; the ring stands back from the bottom of the steering wheel on a skirt. The arm goes up to
a two-piece clamp round the steering column covers. Everything else (motor gear, motor carrier, lever bracket, lift
lever, hinge block, spring, arm, setup gauge) is the dash mount's part, unchanged.

  ring teeth     - zip-tied round the bottom of the steering wheel (5 to 7 o'clock) like the steering wheel teeth, but
                   with no teeth on the outside: a ring at the front face joins a skirt that stands back behind the
                   wheel, and the skirt's inside carries the rolling band and the teeth, facing the hub. The short
                   set only (16 teeth): the long set doesn't fit between the wheel's two lower spokes.
  column clamp   - two V-shaped saddles, one over the steering column covers and one under them, pulled together by
                   four M6 threaded rods beside the covers. The lower saddle carries the arm's angle joint (the same
                   joint as the dash clamp's). Rubber strips on the V faces grip the covers.
  fit test       - a few ring teeth with their rolling band, to try the printed motor gear in by hand.

Frames: the steering wheel frame (z along the steering column towards the driver, +y 12 o'clock, +x the driver's
right; the part of the wheel you hold is centred on z = 0). The clamp parts are drawn in the clamp frame: origin on
the column's axis at the middle of the clamp, +y up (towards 12 o'clock), +z towards the driver.
"""
import math

import numpy as np
from manifold3d import CrossSection, Manifold

import gears as GR
import mountparts as MP
import wheelparts as WP
from cadlib import box, circle_yz, clean, cyl, cyl_x, cyl_y, extrude_x, polar_mask, rect_yz, revolve, sector, union
from params import (ARM_T, ARM_W, BACKLASH, CD_EXTRA, COVER_H, COVER_H_RANGE, COVER_W_RANGE, END_CHAMFER, END_LEAD_IN, FRONT_RING_T,
                    M5_CLEAR, M6_CLEAR, M6_NUT_AF, MOTOR_TEETH, RING_TEETH, ROLLER_R, SKIRT_T, Z_GEAR_ROLLER, Z_GEAR_TEETH,
                    Z_MOTOR_FACE, Z_MOTOR_FACE_C)

GAP = MP.GAP


def centre_distance() -> float:
  """Steering column to the motor's axis with the motor gear inside the ring teeth."""
  return GR.pitch_radius(RING_TEETH) - GR.pitch_radius(MOTOR_TEETH) - CD_EXTRA


# the motor gear's roller and teeth along the column, in the steering wheel frame, with the motor's face at Z_MOTOR_FACE_C
Z_GEAR_ROLLER_C = tuple(z - Z_MOTOR_FACE + Z_MOTOR_FACE_C for z in Z_GEAR_ROLLER)
Z_GEAR_TEETH_C = tuple(z - Z_MOTOR_FACE + Z_MOTOR_FACE_C for z in Z_GEAR_TEETH)
Z_TEETH_C = (Z_GEAR_TEETH_C[0] + 0.2, Z_GEAR_TEETH_C[1] + 0.5)      # the ring's teeth: clear of the roller, past the gear's tips
RING_BACK_Z = Z_GEAR_ROLLER_C[0] + 3.0     # the skirt's back face: the roller's back 3 mm hang off the rolling band, so
                                           # the carrier's plate (1 mm behind the roller) clears the back face as it lifts
Z_ROLL_C = (RING_BACK_Z, Z_TEETH_C[0])     # the rolling band, behind the teeth
# Dropping (the carrier turned DROP_DEG about its hinge, the roller off the rolling band), the motor gear's teeth also
# move about 3.2 mm back along the column into the rolling band's zone; from here forward the ring's inside follows
# the lead-in at the teeth root's distance, so those teeth clear it
Z_TEETH_SPLIT = Z_GEAR_TEETH_C[0] - 3.4
GUARD_WINDOW_C = 64.0                       # the column mount's carrier: finger guard open this far either side of down


SHALLOW_REACH = 8.0           # a shallow channel's walls reach only this far in from the middle of the grip, so the
                              # piece can sit over a spoke's junction with the grip (the right-side ring)
SLOT_EVERY_DEG = 4.5          # zip tie slots all along the piece, this far apart: tie it where the spokes allow


class RingTeeth:
  """Radii and angles of the ring teeth (the short set) for one steering wheel size. shallow: the channel's walls
  reach only SHALLOW_REACH in from the middle of the grip instead of wrapping it to its middle."""

  def __init__(self, wheel_od: float, grip: float, shallow: bool = False):
    self.base = WP.Teeth(wheel_od, grip, 15)        # the channel round the grip and the zip ties: the short set's
    b = self.base
    self.shallow = shallow
    self.front_inner = b.rr + SHALLOW_REACH if shallow else b.front_inner
    self.back_inner = b.rr + SHALLOW_REACH + 1.0 if shallow else b.back_inner
    self.z_slope_top = b.r_in - (self.back_inner + b.wz_out)   # the 45 degree back slope meets the outer band here
    self.n_teeth = b.n_teeth
    self.tie_angles = b.tie_angles
    self.rp = GR.pitch_radius(RING_TEETH)
    self.r_tip = self.rp - GR.ADDENDUM * GR.MODULE         # the ring's teeth point inwards
    self.r_root = self.rp + GR.DEDENDUM * GR.MODULE
    self.r_roll = centre_distance() + ROLLER_R             # the rolling band's inside, where the motor gear's roller rides
    self.r_skirt_in = self.r_root                          # the skirt's inside face
    self.r_out = self.r_root + SKIRT_T
    self.pitch_deg = b.pitch_deg
    self.teeth_half = b.teeth_half
    self.roll_half = b.roll_half
    self.chamfer_deg = math.degrees(END_CHAMFER / self.r_skirt_in)
    self.teeth_chamfer = self.r_root + 0.6 - self.r_tip      # the teeth's front ends slope back 45 degrees over this
    self.half = self.roll_half + END_LEAD_IN + self.chamfer_deg
    if self.r_skirt_in - b.r_base < 2.0:
      raise ValueError(f"a steering wheel {wheel_od} mm across leaves no room between the band and the ring's skirt")

  @property
  def tracked_arc_deg(self) -> float:
    return 2.0 * self.roll_half

  @property
  def teeth_arc_deg(self) -> float:
    return 2.0 * self.teeth_half

  @property
  def span_deg(self) -> float:
    return 2.0 * self.half

  def profile(self):
    """(r, z) outline of the piece at one angle: the channel round the grip (as the steering wheel teeth), the ring at
    the front face, the skirt behind, and on the skirt's inside the teeth's root and the rolling band."""
    b = self.base
    zf, zk = b.wz_out, -b.wz_out
    zr0, zr1 = Z_ROLL_C
    ring_back = zf - FRONT_RING_T
    return [
      (self.front_inner, zf), (self.front_inner, b.wz), (b.r_in, b.wz), (b.r_in, self.z_slope_top), (self.back_inner, zk),
      (b.r_base, zk), (b.r_base, ring_back), (self.r_skirt_in, ring_back),
      (self.r_skirt_in, zr1),                                   # the skirt's inside down to the rolling band
      (self.r_roll, zr1 - (self.r_skirt_in - self.r_roll)),     # 45 degree slope in to the rolling band
      (self.r_roll, RING_BACK_Z), (self.r_out, RING_BACK_Z), (self.r_out, zf),
    ]

  def inner_radius_at(self, angle_from_bottom: float) -> float:
    """Plan view: the skirt's inside radius. Over the teeth and rolling band the profile stands; then the rolling band
    slopes out to the skirt's inside over END_LEAD_IN degrees, and at the very end the skirt flares out so a dropped
    roller is led back in."""
    a = abs(angle_from_bottom)
    if a <= self.roll_half:
      return self.r_roll - 0.5
    if a <= self.roll_half + END_LEAD_IN:
      f = (a - self.roll_half) / END_LEAD_IN
      return self.r_roll + f * (self.r_skirt_in - self.r_roll)
    f = min(1.0, (a - self.roll_half - END_LEAD_IN) / self.chamfer_deg)
    return self.r_skirt_in + f * (self.r_out - 2.0 - self.r_skirt_in)


def ring_teeth_outline(t: RingTeeth, n_teeth: int | None = None, lowered_ends: bool = True) -> CrossSection:
  """2D outline of the ring's teeth around 6 o'clock: the ring from its tips out to its root, a tooth gap at 6 o'clock;
  the two end teeth each side are shortened so the motor gear's teeth meet them gently."""
  n_teeth = n_teeth or t.n_teeth
  half = n_teeth / 2 * t.pitch_deg
  ring = GR.internal_gear_outline(RING_TEETH, BACKLASH, t.r_root + 0.6).rotate(270.0)
  ring = ring ^ sector(t.r_root + 0.6, 270.0 - half, 270.0 + half, r_in=t.r_tip - 1.0)
  if lowered_ends:
    for k, tip in ((0, t.r_root - 1.2), (1, t.r_root - 3.0)):
      for sign in (1, -1):
        a_out = 270.0 + sign * (half - k * t.pitch_deg)
        a_in = 270.0 + sign * (half - (k + 1) * t.pitch_deg)
        lo, hi = sorted((a_in, a_out))
        s = sector(t.r_root + 0.6, lo, hi, r_in=t.r_tip - 1.0)
        ring = (ring - s) + (ring ^ s - CrossSection.circle(tip, 4096))
  return ring


def ring_teeth_solid(t: RingTeeth) -> Manifold:
  """The whole ring teeth piece, before cutting the zip tie slots."""
  a0, a1 = 270.0 - t.half, 270.0 + t.half
  body = revolve(t.profile(), a0, a1)
  # the rolling band's ends: cut the skirt's inside away out to inner_radius_at(angle) over the rolling band's depth,
  # and in the teeth zone the root follows it, the root's distance outside the band kept, so the motor gear's tips
  # (which stand that far outside its roller) stay clear of the ring as the carrier drops along the lead-in
  zlo, zhi = RING_BACK_Z - 1.0, Z_TEETH_SPLIT + 0.01
  cut = polar_mask(lambda a: t.inner_radius_at(a - 270.0), a0 - 0.5, a1 + 0.5, zlo, zhi)
  cut = cut - cyl(t.r_roll - 0.3, zlo - 1, zhi + 1, segments=1440)
  body = body - cut
  step = t.r_root - t.r_roll

  def teeth_zone_inside(a_deg: float) -> float:
    a = abs(a_deg - 270.0)
    return min(t.inner_radius_at(a) + step, t.r_out - 1.5) if a > t.roll_half else t.r_roll - 0.5

  zlo, zhi = Z_TEETH_SPLIT, -t.base.wz_out + 0.01
  cut = polar_mask(teeth_zone_inside, a0 - 0.5, a1 + 0.5, zlo, zhi)
  cut = cut - cyl(t.r_roll - 0.3, zlo - 1, zhi + 1, segments=1440)
  body = body - cut
  # the teeth; their front ends slope back 45 degrees from the root to the tips, so the piece prints front face down
  teeth = ring_teeth_outline(t).extrude(Z_TEETH_C[1] + t.teeth_chamfer - Z_TEETH_C[0]).translate((0, 0, Z_TEETH_C[0]))
  return clean(body + (teeth ^ teeth_front(t, a0 - 1.0, a1 + 1.0)))


def teeth_front(t: RingTeeth, a0: float, a1: float) -> Manifold:
  """The region the ring's teeth may fill: behind a 45 degree slope from the root at the front to the tips."""
  zt0, zt1 = Z_TEETH_C
  c = t.teeth_chamfer
  return revolve([(t.r_root + 0.6, zt1 + c + 0.01), (t.r_tip - 1.0, zt1 - 1.0), (t.r_tip - 1.0, zt0 - 0.01),
                  (t.r_root + 0.6, zt0 - 0.01)], a0, a1)


def slot_angles(t: RingTeeth) -> list:
  """Zip tie slots every SLOT_EVERY_DEG, from near the middle out to near the ends, each side of the middle."""
  out = []
  a = SLOT_EVERY_DEG / 2
  while a + WP.TIE_W / 2 / t.base.r_in * 57.3 < t.half - 1.0:
    out += [a, -a]
    a += SLOT_EVERY_DEG
  return out


def tie_slots(t: RingTeeth) -> Manifold:
  return WP.tie_slots(t.base, [270.0 + a for a in slot_angles(t)])


def ring_teeth(t: RingTeeth, centre_deg: float = 270.0) -> Manifold:
  """The ring teeth in one piece (it spans about 56 degrees, so it fits a 220 mm bed), centred at centre_deg on the
  steering wheel (270 is 6 o'clock, 0 is 3 o'clock)."""
  return clean((ring_teeth_solid(t) - tie_slots(t)).rotate((0, 0, centre_deg - 270.0)))


def ring_tooth_fit_test(t: RingTeeth, n_teeth: int = 8) -> Manifold:
  """A few ring teeth with their rolling band on a short block, to try the printed motor gear in by hand. Prints
  front face down like the ring teeth."""
  half = n_teeth / 2 * t.pitch_deg
  a0, a1 = 270.0 - half - 1.5, 270.0 + half + 1.5
  zt0, zt1 = Z_TEETH_C
  zr0, zr1 = Z_ROLL_C
  zf = zt1 + t.teeth_chamfer + 2.0
  pts = [(t.r_skirt_in, zf), (t.r_skirt_in, zr1), (t.r_roll, zr1 - (t.r_skirt_in - t.r_roll)), (t.r_roll, zr0 - 2.0),
         (t.r_out + 3.0, zr0 - 2.0), (t.r_out + 3.0, zf)]
  body = revolve(pts, a0, a1)
  teeth = ring_teeth_outline(t, n_teeth=n_teeth, lowered_ends=False).extrude(zt1 + t.teeth_chamfer - zt0).translate((0, 0, zt0))
  return clean(body + (teeth ^ teeth_front(t, a0 - 1.0, a1 + 1.0)))


def internal_free_play(ring: CrossSection, motor: CrossSection, cd: float, motor_phase_deg: float,
                       step_deg: float = 0.02, limit_deg: float = 15.0) -> tuple[float, float]:
  """With the steering wheel held, how far the motor gear (inside the ring at (0, -cd)) turns each way before it
  touches (degrees of the motor gear): (counterclockwise, clockwise)."""
  res = []
  for sign in (1, -1):
    a = 0.0
    while a < limit_deg:
      gear = GR.place(motor, motor_phase_deg + sign * (a + step_deg), 0.0, -cd)
      if (ring ^ gear).area() > 1e-6:
        break
      a += step_deg
    res.append(a)
  return res[0], res[1]


# ***** column clamp *****

SADDLE_HALF_X = 92.0          # the saddles reach this far each side (the rod slots are near the ends)
SADDLE_LEN = 50.0             # along the column
V_DEG = 20.0                  # the V's faces rise this much from flat, away from the middle
V_HALF_X = 35.0               # the V runs this far each side of the middle
SADDLE_T = 6.0                # plastic under the V's middle
EAR_T = 10.0                  # the ears with the rod slots
ROD_SLOT_X = (COVER_W_RANGE[0] / 2 + 10.0 - M6_CLEAR / 2, COVER_W_RANGE[1] / 2 + 10.0 + M6_CLEAR / 2)  # rods 10 mm clear of the covers
ROD_Z = (-18.0, 18.0)
PAD_T = 4.0                   # rubber strip on each V face (self-adhesive, 20 mm wide; squashed a little)
V_DEPTH = V_HALF_X * math.tan(math.radians(V_DEG))      # the V's faces end this far above its middle
SADDLE_BOTTOM = -SADDLE_T                                # the lower saddle's underside (its frame: V middle at y = 0, +y up)
NECK = 22.0                   # the arm's bolt this far below the saddle's underside: room for the arm's end past the
                              # bolt (the slot end) at the steepest the arm gets
PIVOT_C = (SADDLE_BOTTOM - NECK, 0.0)                    # the arm's bolt (y, z) in the lower saddle's frame
SIDE_PLATE_X = MP.SIDE_PLATE_X
ARM_ANGLES = (0.0, 60.0)      # the arm can point from along the column (towards you) to 60 degrees below it
ARM_NOMINAL_C = 20.0          # the column mount's hinge block has its slot centred on the arm at this angle to the column
ROD_LEN = 180.0               # M6 threaded rod, four pieces this long (cut shorter to suit: the report says how much is used)


def saddle_v_cut(length: float, extra: float = 1.0) -> Manifold:
  """The V the covers sit in: a trough along z, its middle on the x axis, faces rising away from it (lower saddle
  frame). Everything above the V is cut away."""
  t = math.tan(math.radians(V_DEG))
  w = V_HALF_X + extra
  pts = [(-w, w * t), (0.0, 0.0), (w, w * t), (w, 80.0), (-w, 80.0)]
  cs = CrossSection([pts])
  if cs.area() < 1e-9:
    cs = CrossSection([pts[::-1]])
  return cs.extrude(length + 2).translate((0, 0, -length / 2 - 1))


def saddle_block() -> Manifold:
  """A saddle without its V or slots (lower saddle frame): a block from SADDLE_BOTTOM up to the V's rim between the
  V's ends, and ears EAR_T thick out to SADDLE_HALF_X."""
  body = box(-V_HALF_X, V_HALF_X, SADDLE_BOTTOM, V_DEPTH, -SADDLE_LEN / 2, SADDLE_LEN / 2)
  ears = box(-SADDLE_HALF_X, SADDLE_HALF_X, SADDLE_BOTTOM, SADDLE_BOTTOM + EAR_T, -SADDLE_LEN / 2, SADDLE_LEN / 2)
  return body + ears


def rod_slots() -> Manifold:
  slots = []
  for sx in (-1, 1):
    for z in ROD_Z:
      x0, x1 = sorted((sx * ROD_SLOT_X[0], sx * ROD_SLOT_X[1]))
      slots.append(Manifold.batch_hull([cyl_y(M6_CLEAR / 2, SADDLE_BOTTOM - 1, V_DEPTH + 1.0, x=x0 + M6_CLEAR / 2, z=z, segments=32),
                                        cyl_y(M6_CLEAR / 2, SADDLE_BOTTOM - 1, V_DEPTH + 1.0, x=x1 - M6_CLEAR / 2, z=z, segments=32)]))
  return union(slots)


def column_clamp_upper() -> Manifold:
  """The saddle over the steering column covers (drawn in the lower saddle's frame, V opening up; the assembly
  turns it over). Prints V up, no supports."""
  return clean(saddle_block() - saddle_v_cut(SADDLE_LEN) - rod_slots())


def column_clamp_lower() -> Manifold:
  """The saddle under the covers, with the arm's angle joint hanging below it: two side plates with the arm's bolt
  and a curved slot for its locking bolt, the arm pointing from level (along the column, towards you) to 80 degrees
  below. Prints on its side like the dash clamp."""
  part = saddle_block() - saddle_v_cut(SADDLE_LEN) - rod_slots()
  py, pz = PIVOT_C
  r = MP.ARM_LOCK_R
  plates = []
  for sgn in (-1, 1):
    x0, x1 = (SIDE_PLATE_X[0], SIDE_PLATE_X[1]) if sgn > 0 else (-SIDE_PLATE_X[1], -SIDE_PLATE_X[0])
    a0, a1 = ARM_ANGLES[0] - 15.0, ARM_ANGLES[1] + 15.0
    pts = [(py, pz)]
    for a in np.linspace(-a1, -a0, 41):
      pts.append((py + (r + 9.0) * math.sin(math.radians(a)), pz + (r + 9.0) * math.cos(math.radians(a))))
    pie = CrossSection([pts])
    if pie.area() < 1e-9:
      pie = CrossSection([pts[::-1]])
    # one plate: the pie round the arm's bolt, hulled with a strip along the saddle's underside
    plate = CrossSection.batch_hull([pie, circle_yz(10.0, py, pz),
                                     rect_yz(SADDLE_BOTTOM - 0.01, SADDLE_BOTTOM + 1.0, -SADDLE_LEN / 2, SADDLE_LEN / 2)])
    plates.append(extrude_x(plate, x0, x1))
  part = part + union(plates)
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=py, z=pz, segments=32)
  slot = []
  for a in np.linspace(-ARM_ANGLES[1], -ARM_ANGLES[0], 81):
    slot.append(cyl_x(M5_CLEAR / 2, -60, 60, y=py + r * math.sin(math.radians(a)), z=pz + r * math.cos(math.radians(a)), segments=20))
  part = part - union(slot)
  # the arm turns between the side plates
  part = part - (cyl_x(ARM_T / 2 + 1.0, -SIDE_PLATE_X[0], SIDE_PLATE_X[0], y=py, z=pz) +
                 box(-SIDE_PLATE_X[0], SIDE_PLATE_X[0], py - 60.0, SADDLE_BOTTOM - 2.0, pz - 60.0, pz + 60.0))
  return clean(part)


def rods_and_nuts(top: float) -> Manifold:
  """The four threaded rods with a nut and washer above the upper saddle and below the lower one (lower saddle
  frame). top: the upper saddle's V middle above the lower one's (twice the saddles' distance from the column)."""
  parts = []
  for sx in (-1, 1):
    x = sx * (ROD_SLOT_X[0] + ROD_SLOT_X[1]) / 2
    for z in ROD_Z:
      y0 = SADDLE_BOTTOM - 1.5 - 5.4 - 2.0
      parts.append(cyl_y(3.0, y0, y0 + ROD_LEN, x=x, z=z, segments=24))
      parts.append(MP.hex_prism_z_at(M6_NUT_AF, 0, 5.4, 0, 0).rotate((-90, 0, 0)).translate((x, SADDLE_BOTTOM - 1.5 - 5.4, z)))
      parts.append(MP.hex_prism_z_at(M6_NUT_AF, 0, 5.4, 0, 0).rotate((-90, 0, 0)).translate((x, top - SADDLE_BOTTOM + 1.5, z)))
  return union(parts)


def pads() -> Manifold:
  """Where the rubber strips sit on the lower saddle's V faces (lower saddle frame)."""
  t = math.tan(math.radians(V_DEG))
  out = []
  for sgn in (-1, 1):
    pts = [(0.0, 0.0), (sgn * V_HALF_X, V_HALF_X * t), (sgn * V_HALF_X, V_HALF_X * t + PAD_T), (0.0, PAD_T)]
    cs = CrossSection([pts])
    if cs.area() < 1e-9:
      cs = CrossSection([pts[::-1]])
    out.append(cs.extrude(SADDLE_LEN - 4.0).translate((0, 0, -SADDLE_LEN / 2 + 2.0)))
  return union(out)


def clamp_fastener_rows(cover_h: float = COVER_H) -> list:
  """The column clamp's threaded rods: how much of each is used for a cover this tall, and the range they cover."""
  stack = lambda h: h + 2 * PAD_T + 2 * (-SADDLE_BOTTOM)   # noqa: E731  from the lower saddle's underside to the upper's top
  # (the saddles' V middles sit about 9 mm outside the covers' top and bottom; close enough for the rods)
  used = stack(cover_h) + 2 * (5.4 + 1.0) + 2 * 1.5       # two nuts and washers, 1.5 mm past each
  rows = [{"bolt": f"M6 threaded rod x {ROD_LEN:.0f} (4)",
           "use": "column clamp: lower saddle, covers, upper saddle, a nut and washer each end",
           "length": ROD_LEN, "needs_mm": [round(stack(COVER_H_RANGE[0]) + 2 * 7.9, 1), round(stack(COVER_H_RANGE[1]) + 2 * 7.9, 1)],
           "ok": stack(COVER_H_RANGE[1]) + 2 * 7.9 <= ROD_LEN, "used_for_your_cover_mm": round(used, 1)}]
  return rows


# ***** side bracket and screw tab (the right-side mount: tied to the column covers and screwed to the dash) *****
# Bracket frame: origin on the covers' right-hand surface at the column's height, at the bracket's reference place
# along the column (its back face is 25 mm behind it, level with the screw tab's plate against the dash);
# +x the driver's right (away from the column), +y up, +z towards the driver.

SB_PAD_T = PAD_T                            # two rubber strips between the plate and the covers (the clamp's strips)
SB_PAD_Y, SB_PAD_W = 12.0, 10.0             # the strips at y +-this, this wide, along the column
SB_PLATE_X = (SB_PAD_T, SB_PAD_T + 8.0)     # the plate: flat, 8 thick, outside the strips
SB_PLATE_Y = 35.0                           # it spans y +-this ...
SB_PLATE_Z = (-25.0, 45.0)                  # ... and this along the column: its back face level with the screw tab's plate
SB_TIE_Y = 20.0                             # zip tie slots through the plate at y +-this (a tie goes round the covers
SB_TIE_Z = (-17.0, -7.0, 3.0, 13.0, 23.0, 33.0)   # from an upper slot to the lower one), at every one of these z: use any
SB_NECK = 34.0                              # the arm's bolt this far out from the plate: room for the arm's slot end at
                                            # the biggest angle, slid fully towards the bracket
SB_PIVOT = (SB_PLATE_X[1] + SB_NECK, 30.0)  # the arm's bolt (x, z); it runs along y. 30 forward of the bracket's middle:
                                            # the arm's slot end reaches 51 back from the bolt, and the dash is 25 back
SB_FORK_Y = MP.SIDE_PLATE_X                 # the fork's two plates, y range each side (the arm swings between them)
SB_ARM_ANGLES = (-10.0, 25.0)               # the arm from 10 degrees in (towards the column, going towards you) to 25 out
SB_BAR_Y = (-30.4, -SB_FORK_Y[0])           # the bar to the screw tab: under the arm, joined to the lower fork plate
SB_BAR_Z = (-25.0, 5.0)
SB_BAR_X1 = 112.0                           # the bar's end
SB_BAR_HOLES = (80.0, 100.0)                # the screw tab's two M5 bolts through the bar, along y, at these x
SB_BOLT_Z = -15.0                           # ... and this z (the middle of the tab's bar)
TAB_LENGTHS = (100.0, 160.0, 220.0)         # screw tabs to print: bar length from the tab's start to the end plate
TAB_BAR_Y = (SB_BAR_Y[0] - 30.0, SB_BAR_Y[0])     # the tab's bar, under the bracket's bar: 30 tall ...
TAB_BAR_Z = (SB_BAR_Z[0], SB_BAR_Z[0] + 20.0)     # ... 20 deep, its back face level with the bracket's
TAB_SLOT = (3.0, 108.0)                     # the tab's slot for the bracket's two bolts, x range (tab frame): slides 60 mm
TAB_PLATE = (40.0, 70.0, 6.0)               # the end plate: wide (x), tall (y), thick (z); its back face on the dash's trim
TAB_PLATE_Z = (TAB_BAR_Z[0], TAB_BAR_Z[0] + 6.0)
TAB_SLOT_HALF = 25.0                        # the screw's slot, y +-this around the plate's middle
TAB_SCREW_FROM_END = 20.0                   # the screw's slot this far from the tab's end
SCREW_CLEAR = 5.5                           # the dash's screw passes through this
TAB_PLATE_Y = -60.0                         # the end plate's middle below the column's axis, unless the screw is measured


def tab_slide_range() -> tuple[float, float]:
  """Where the tab's start (its x = 0) can sit along the bracket's bar: both of the bar's bolts in the tab's slot."""
  s0, s1 = TAB_SLOT[0] + M5_CLEAR / 2, TAB_SLOT[1] - M5_CLEAR / 2
  return (max(SB_BAR_HOLES[1] - s1, SB_PLATE_X[1] + 0.5), SB_BAR_HOLES[0] - s0)   # and clear of the plate


def side_bracket() -> Manifold:
  """The flat plate against the covers (on two rubber strips) with zip tie slots all along it, the arm's fork, and the
  bar the screw tab bolts to. Prints standing on the plate's inner face, nothing needs supports."""
  x0, x1 = SB_PLATE_X
  y0, y1 = -SB_PLATE_Y, SB_PLATE_Y
  z0, z1 = SB_PLATE_Z
  plate = box(x0, x1, y0, y1, z0, z1)
  for y in (-SB_TIE_Y, SB_TIE_Y):
    for z in SB_TIE_Z:
      plate = plate - box(x0 - 1.0, x1 + 1.0, y - 1.3, y + 1.3, z - 3.0, z + 3.0)
  px, pz = SB_PIVOT
  r = MP.ARM_LOCK_R
  a0, a1 = SB_ARM_ANGLES[0] - 15.0, SB_ARM_ANGLES[1] + 15.0
  pts = [(px, pz)]
  for a in np.linspace(a0, a1, 41):
    pts.append((px + (r + 9.0) * math.sin(math.radians(a)), pz + (r + 9.0) * math.cos(math.radians(a))))
  pie = CrossSection([pts])
  if pie.area() < 1e-9:
    pie = CrossSection([pts[::-1]])
  # a fork plate's outline in (x, z); extruded along y with a transform mapping (u=x, v=z, w=y) -> (u, w, v)
  outline = CrossSection.batch_hull([pie, CrossSection.circle(10.0, 64).translate((px, pz)),
                                     CrossSection.square((1.0, z1 - z0)).translate((x1 - 0.01, z0))])

  def plate_y(cs, ya, yb):
    return cs.extrude(yb - ya).transform([[1, 0, 0, 0], [0, 0, 1, ya], [0, 1, 0, 0]])

  forks = [plate_y(outline, SB_FORK_Y[0], SB_FORK_Y[1]), plate_y(outline, -SB_FORK_Y[1], -SB_FORK_Y[0])]
  bar = box(x1 - 0.01, SB_BAR_X1, SB_BAR_Y[0], SB_BAR_Y[1] + 0.01, SB_BAR_Z[0], SB_BAR_Z[1])
  part = union([plate] + forks + [bar])
  part = part - cyl_y(M5_CLEAR / 2, -60, 60, x=px, z=pz, segments=32)        # the arm's bolt
  slot = [cyl_y(M5_CLEAR / 2, -60, 60, x=px + r * math.sin(math.radians(a)), z=pz + r * math.cos(math.radians(a)), segments=20)
          for a in np.linspace(SB_ARM_ANGLES[0], SB_ARM_ANGLES[1], 81)]
  part = part - union(slot)                                                    # the arm's locking bolt, any angle
  for hx in SB_BAR_HOLES:
    part = part - cyl_y(M5_CLEAR / 2, -60, 60, x=hx, z=SB_BOLT_Z, segments=32)
  return clean(part)


def side_bracket_pads() -> Manifold:
  """Where the two rubber strips sit between the plate and the covers (bracket frame)."""
  z0, z1 = SB_PLATE_Z
  return union([box(0.0, SB_PAD_T, y - SB_PAD_W / 2, y + SB_PAD_W / 2, z0 + 2.0, z1 - 2.0) for y in (-SB_PAD_Y, SB_PAD_Y)])


def screw_tab(length: float, plate_y: float = TAB_PLATE_Y) -> Manifold:
  """The bar from the side bracket to the dash's screw. Its slot takes the bracket's two bolts, so the length adjusts;
  the end plate, with a vertical slot for the screw, bears on the dash's trim with its back face. The plate's middle
  sits plate_y below the column's axis (negative: below) and the plate reaches up or down to the bar whatever that
  is. Tab frame: x = 0 at the tab's start, otherwise the bracket frame; the assembly slides it along the bar.
  Prints lying on its back face, nothing needs supports."""
  w, h, _ = TAB_PLATE
  ya, yb = TAB_BAR_Y
  za, zb = TAB_BAR_Z
  bar = box(0.0, length, ya, yb, za, zb)
  s0, s1 = TAB_SLOT
  bar = bar - Manifold.batch_hull([cyl_y(M5_CLEAR / 2, ya - 1, yb + 1, x=s0 + M5_CLEAR / 2, z=SB_BOLT_Z, segments=24),
                                   cyl_y(M5_CLEAR / 2, ya - 1, yb + 1, x=s1 - M5_CLEAR / 2, z=SB_BOLT_Z, segments=24)])
  pz0, pz1 = TAB_PLATE_Z
  top = min(plate_y + h / 2, yb)      # never above the tab's bar: the bracket's bar is right above that
  plate = box(length - w, length, min(plate_y - h / 2, ya - 0.01), top, pz0, pz1)
  xs = length - TAB_SCREW_FROM_END
  slot_top = min(plate_y + TAB_SLOT_HALF, top - 5.0)
  plate = plate - Manifold.batch_hull([cyl(SCREW_CLEAR / 2, pz0 - 1, pz1 + 1, xs, plate_y - TAB_SLOT_HALF, 24),
                                       cyl(SCREW_CLEAR / 2, pz0 - 1, pz1 + 1, xs, slot_top, 24)])
  return clean(bar + plate)


def tab_bolts(tab_x0: float, arm_deg: float = 0.0) -> Manifold:
  """The two M5 x 55 bolts through the bracket's bar and the tab (heads under the tab, nuts on the bar), and the arm's
  bolt and locking bolt through the fork (the arm at arm_deg), as solids for the clearance checks (bracket frame)."""
  out = []
  ya = TAB_BAR_Y[0]
  for hx in SB_BAR_HOLES:
    out.append(cyl_y(2.5, ya - 4.0, SB_BAR_Y[1] + MP.M5_WASHER_T + MP.M5_NYLOC_T + 6.0, x=hx, z=SB_BOLT_Z, segments=16))
    out.append(cyl_y(4.3, ya - 4.0, ya - 0.01, x=hx, z=SB_BOLT_Z, segments=24))                                        # head
    out.append(cyl_y(4.6, SB_BAR_Y[1] + 0.01, SB_BAR_Y[1] + MP.M5_WASHER_T + MP.M5_NYLOC_T, x=hx, z=SB_BOLT_Z, segments=24))   # nut
  px, pz = SB_PIVOT
  yo = SB_FORK_Y[1]
  for (bx, bz) in ((px, pz), (px + MP.ARM_LOCK_R * math.sin(math.radians(arm_deg)), pz + MP.ARM_LOCK_R * math.cos(math.radians(arm_deg)))):
    out.append(cyl_y(2.5, -yo - 8.0, yo + 8.0, x=bx, z=bz, segments=16))
    out.append(cyl_y(4.6, yo + 0.01, yo + MP.M5_WASHER_T + MP.M5_NYLOC_T, x=bx, z=bz, segments=24))
    out.append(cyl_y(4.3, -yo - MP.M5_WASHER_T - 5.0, -yo - 0.01, x=bx, z=bz, segments=24))
  return union(out)


def bracket_fastener_rows() -> list:
  """The side bracket's bolts and ties."""
  rows = []
  stack = 2 * (SB_FORK_Y[1] - SB_FORK_Y[0]) + ARM_W + 2 * GAP     # the bolts run across the arm's width
  spare = 60.0 - stack - 2 * MP.M5_WASHER_T - MP.M5_NYLOC_T
  rows.append({"bolt": "M5 x 60 (2)", "use": "arm to side bracket: both fork plates and the arm, a washer each side, lock nut "
               "(the arm's bolt and its locking bolt)", "length": 60.0, "through_mm": round(stack + 2 * MP.M5_WASHER_T, 1),
               "nut_mm": MP.M5_NYLOC_T, "past_the_nut_mm": round(spare, 1), "ok": spare >= 1.5})
  stack = (SB_BAR_Y[1] - SB_BAR_Y[0]) + (TAB_BAR_Y[1] - TAB_BAR_Y[0])
  spare = 55.0 - stack - 2 * MP.M5_WASHER_T - MP.M5_NYLOC_T
  rows.append({"bolt": "M5 x 55 (2)", "use": "screw tab to the side bracket's bar, up through both, a washer each side, lock nut",
               "length": 55.0, "through_mm": round(stack + 2 * MP.M5_WASHER_T, 1), "nut_mm": MP.M5_NYLOC_T,
               "past_the_nut_mm": round(spare, 1), "ok": spare >= 1.5})
  rows.append({"bolt": "the dash's own screw, 8 mm longer (same thread)",
               "use": f"screw tab to the dash, through the plate ({TAB_PLATE[2]:.0f} mm) and a washer",
               "length": 0.0, "through_mm": TAB_PLATE[2] + 1.0, "nut_mm": 0.0, "past_the_nut_mm": 0.0, "ok": True})
  rows.append({"bolt": "zip ties, 8 mm wide, 400 mm or longer (3)", "use": "side bracket round the column covers, through the "
               "plate's slots (any that the stalks and the key leave free)", "length": 0.0, "through_mm": 0.0, "nut_mm": 0.0,
               "past_the_nut_mm": 0.0, "ok": True})
  return rows

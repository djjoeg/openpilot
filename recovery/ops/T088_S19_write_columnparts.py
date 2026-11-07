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
from cadlib import box, circle_yz, clean, cyl, cyl_x, cyl_y, extrude_x, polar_mask, prism_x, revolve, sector, union
from params import (ARM_T, ARM_W, BACKLASH, CD_EXTRA, COVER_H, COVER_H_RANGE, COVER_W_RANGE, END_CHAMFER, END_LEAD_IN,
                    FRONT_RING_T, M3_PILOT, M6_CLEAR, M6_NUT_AF, MOTOR_TEETH, RING_TEETH, ROLL_PAST_TEETH, ROLLER_R, SKIRT_T,
                    TIE_T, TIE_W, Z_GEAR_ROLLER, Z_GEAR_TEETH, Z_MOTOR_FACE, Z_MOTOR_FACE_C)

GAP = MP.GAP


def centre_distance() -> float:
  """Steering column to the motor's axis with the motor gear inside the ring teeth."""
  return GR.pitch_radius(RING_TEETH) - GR.pitch_radius(MOTOR_TEETH) - CD_EXTRA


# the motor gear's roller and teeth along the column, in the steering wheel frame, with the motor's face at Z_MOTOR_FACE_C
Z_GEAR_ROLLER_C = tuple(z - Z_MOTOR_FACE + Z_MOTOR_FACE_C for z in Z_GEAR_ROLLER)
Z_GEAR_TEETH_C = tuple(z - Z_MOTOR_FACE + Z_MOTOR_FACE_C for z in Z_GEAR_TEETH)
Z_TEETH_C = (Z_GEAR_TEETH_C[0] - 0.5, Z_GEAR_TEETH_C[1] + 0.5)      # the ring's teeth cover the motor gear's teeth
Z_ROLL_C = (Z_GEAR_ROLLER_C[0] - 0.5, Z_TEETH_C[0])                 # the rolling band, behind them
RING_BACK_Z = Z_ROLL_C[0] - 1.0                                     # the skirt's back face
TEETH_CHAMFER = 5.0                                                 # the teeth's front ends slope back 45 degrees over this


class RingTeeth:
  """Radii and angles of the ring teeth (the short set) for one steering wheel size."""

  def __init__(self, wheel_od: float, grip: float):
    self.base = WP.Teeth(wheel_od, grip, 15)        # the channel round the grip and the zip ties: the short set's
    b = self.base
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
    zt0 = Z_TEETH_C[0]
    ring_back = zf - FRONT_RING_T
    return [
      (b.front_inner, zf), (b.front_inner, b.wz), (b.r_in, b.wz), (b.r_in, b.z_slope_top), (b.back_inner, zk),
      (b.r_base, zk), (b.r_base, ring_back), (self.r_skirt_in, ring_back),
      (self.r_skirt_in, zr1),                                   # the skirt's inside down to the rolling band
      (self.r_roll, zr1 - (self.r_skirt_in - self.r_roll)),     # 45 degree slope in to the rolling band
      (self.r_roll, zr0),
      (self.r_roll, RING_BACK_Z), (self.r_out, RING_BACK_Z), (self.r_out, zf),
    ]

  def inner_radius_at(self, angle_from_bottom: float) -> float:
    """Plan view: the skirt's inside radius. Over the teeth and rolling band the profile stands; then the rolling band
    slopes out to the skirt's inside over END_LEAD_IN degrees, and at the very end the skirt flares out so a dropped
    roller is led back in."""
    a = abs(angle_from_bottom)
    if a <= self.roll_half:
      return 0.0
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
  ring = GR.internal_gear_outline(RING_TEETH, BACKLASH, t.r_root + 0.6).rotate(270.0 - t.pitch_deg / 2.0)
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
  # the rolling band's ends: cut away the skirt's inside out to inner_radius_at(angle) over the flange's depth
  zlo, zhi = RING_BACK_Z - 1.0, -t.base.wz_out + 0.01
  cut = polar_mask(lambda a: t.inner_radius_at(a - 270.0), a0 - 0.5, a1 + 0.5, zlo, zhi)
  cut = cut - cyl(t.r_roll - 0.01, zlo - 1, zhi + 1, segments=1440)
  body = body - cut
  # the teeth, their front ends sloping back 45 degrees from the root so the piece prints front face down
  zt0, zt1 = Z_TEETH_C
  teeth = ring_teeth_outline(t).extrude(zt1 + TEETH_CHAMFER - zt0).translate((0, 0, zt0))
  chamfer = revolve([(0.0, zt1 + TEETH_CHAMFER + 0.01), (t.r_root + 0.6, zt1 + TEETH_CHAMFER + 0.01),
                     (t.r_root + 0.6, zt1 + TEETH_CHAMFER - 0.01 - (t.r_root + 0.6 - t.r_tip + 1.0)), (0.0, zt1 - 0.01)],
                    a0 - 1.0, a1 + 1.0)
  # keep only what lies within the teeth zone's 45 degree front: r >= r_root + 0.6 - (zt1 + TEETH_CHAMFER - z)
  keep = revolve([(t.r_root + 0.6, zt1 + TEETH_CHAMFER + 0.01), (t.r_tip - 1.0, zt1 + TEETH_CHAMFER - (t.r_root + 0.6 - t.r_tip + 1.0)),
                  (t.r_tip - 1.0, zt0 - 0.01), (t.r_root + 0.6, zt0 - 0.01)], a0 - 1.0, a1 + 1.0)
  teeth = teeth ^ keep
  return clean(body + teeth)


def tie_slots(t: RingTeeth) -> Manifold:
  angles = [270.0 + a for a in t.tie_angles] + [270.0 - a for a in t.tie_angles]
  return WP.tie_slots(t.base, angles)


def ring_teeth(t: RingTeeth) -> Manifold:
  """The ring teeth in one piece (it spans about 56 degrees, so it fits a 220 mm bed)."""
  return clean(ring_teeth_solid(t) - tie_slots(t))


def ring_tooth_fit_test(t: RingTeeth, n_teeth: int = 8) -> Manifold:
  """A few ring teeth with their rolling band on a short block, to try the printed motor gear in by hand. Prints
  front face down like the ring teeth."""
  half = n_teeth / 2 * t.pitch_deg
  a0, a1 = 270.0 - half - 1.5, 270.0 + half + 1.5
  zt0, zt1 = Z_TEETH_C
  zr0, zr1 = Z_ROLL_C
  zf = zt1 + TEETH_CHAMFER + 2.0
  pts = [(t.r_skirt_in, zf), (t.r_skirt_in, zr1), (t.r_roll, zr1 - (t.r_skirt_in - t.r_roll)), (t.r_roll, zr0 - 2.0),
         (t.r_out + 3.0, zr0 - 2.0), (t.r_out + 3.0, zf)]
  body = revolve(pts, a0, a1)
  teeth = ring_teeth_outline(t, n_teeth=n_teeth, lowered_ends=False).extrude(zt1 + TEETH_CHAMFER - zt0).translate((0, 0, zt0))
  keep = revolve([(t.r_root + 0.6, zt1 + TEETH_CHAMFER + 0.01), (t.r_tip - 1.0, zt1 + TEETH_CHAMFER - (t.r_root + 0.6 - t.r_tip + 1.0)),
                  (t.r_tip - 1.0, zt0 - 0.01), (t.r_root + 0.6, zt0 - 0.01)], a0 - 1.0, a1 + 1.0)
  return clean(body + (teeth ^ keep))


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

SADDLE_HALF_X = 88.0          # the saddles reach this far each side (the rod slots are near the ends)
SADDLE_LEN = 50.0             # along the column
V_DEG = 20.0                  # the V faces lean this much from flat
V_HALF_X = 35.0               # the V runs this far each side of the middle
SADDLE_T = 6.0                # plastic under the V's middle
EAR_T = 10.0                  # the ears with the rod slots
ROD_SLOT_X = (COVER_W_RANGE[0] / 2 + 10.0 - M6_CLEAR / 2, COVER_W_RANGE[1] / 2 + 10.0 + M6_CLEAR / 2)  # rods 10 mm clear of the covers
ROD_Z = (-18.0, 18.0)
PAD_T = 4.0                   # rubber strip on each V face (self-adhesive, 20 mm wide; squashed a little)
V_DEPTH = V_HALF_X * math.tan(math.radians(V_DEG))
SADDLE_BOTTOM = -(SADDLE_T + V_DEPTH)                     # the lower saddle's underside (its frame: V middle at y = 0, +y up)
PIVOT_C = (SADDLE_BOTTOM - ARM_T / 2 - 3.0, 0.0)          # the arm's bolt (y, z) in the lower saddle's frame
SIDE_PLATE_X = MP.SIDE_PLATE_X
ARM_ANGLES = MP.ARM_ANGLES
ROD_LEN = 160.0               # M6 threaded rod, cut to this length (four)


def saddle_v_cut(length: float, extra: float = 1.0) -> Manifold:
  """The V the covers sit in: a prism along z, apex on the x axis, opening towards +y (lower saddle frame)."""
  t = math.tan(math.radians(V_DEG))
  pts = [(-V_HALF_X - extra, -(V_HALF_X + extra) * t), (0.0, 0.0), (V_HALF_X + extra, -(V_HALF_X + extra) * t),
         (V_HALF_X + extra, 60.0), (-V_HALF_X - extra, 60.0)]
  cs = CrossSection([pts])
  if cs.area() < 0:
    cs = CrossSection([pts[::-1]])
  return cs.extrude(length + 2).translate((0, 0, -length / 2 - 1))


def saddle_block() -> Manifold:
  """A saddle without its V or slots (lower saddle frame): a block from SADDLE_BOTTOM up to y = 0 between the V's
  ends, ears EAR_T thick out to SADDLE_HALF_X."""
  body = box(-V_HALF_X, V_HALF_X, SADDLE_BOTTOM, 0.0, -SADDLE_LEN / 2, SADDLE_LEN / 2)
  ears = box(-SADDLE_HALF_X, SADDLE_HALF_X, SADDLE_BOTTOM, SADDLE_BOTTOM + EAR_T, -SADDLE_LEN / 2, SADDLE_LEN / 2)
  # the ears' top corners sloped 45 degrees up to the V's ends, so the upper saddle prints V up without supports
  rise = -V_DEPTH - (SADDLE_BOTTOM + EAR_T)
  for sgn in (-1, 1):
    pts = [(SADDLE_BOTTOM + EAR_T - 0.01, sgn * (V_HALF_X + rise)), (SADDLE_BOTTOM + EAR_T - 0.01, sgn * V_HALF_X),
           (-V_DEPTH, sgn * V_HALF_X)]
    web = CrossSection([[(y, x) for y, x in pts]])
    if web.area() < 0:
      web = CrossSection([[(y, x) for y, x in pts[::-1]]])
    # (y, x) outline extruded along z: map (u=y, v=x, w=z) -> (v, u, w)
    ears = ears + web.extrude(SADDLE_LEN).transform([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, -SADDLE_LEN / 2]])
  return body + ears


def rod_slots() -> Manifold:
  slots = []
  for sx in (-1, 1):
    for z in ROD_Z:
      x0, x1 = sorted((sx * ROD_SLOT_X[0], sx * ROD_SLOT_X[1]))
      slots.append(Manifold.batch_hull([cyl_y(M6_CLEAR / 2, SADDLE_BOTTOM - 1, 1.0, x=x0 + M6_CLEAR / 2, z=z, segments=32),
                                        cyl_y(M6_CLEAR / 2, SADDLE_BOTTOM - 1, 1.0, x=x1 - M6_CLEAR / 2, z=z, segments=32)]))
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
    pie = prism_x(pts, x0, x1)
    web = box(x0, x1, min(p[0] for p in pts), SADDLE_BOTTOM + 0.01, min(p[1] for p in pts), pz + 1.0)
    plates.append(pie + web + cyl_x(10.0, x0, x1, y=py, z=pz))
  part = part + union(plates)
  part = part - cyl_x(MP.M5_CLEAR / 2 if hasattr(MP, "M5_CLEAR") else 2.75, -60, 60, y=py, z=pz, segments=32)
  slot = []
  for a in np.linspace(-ARM_ANGLES[1], -ARM_ANGLES[0], 81):
    slot.append(cyl_x(2.75, -60, 60, y=py + r * math.sin(math.radians(a)), z=pz + r * math.cos(math.radians(a)), segments=20))
  part = part - union(slot)
  # the arm turns between the side plates
  part = part - (cyl_x(ARM_T / 2 + 1.0, -SIDE_PLATE_X[0], SIDE_PLATE_X[0], y=py, z=pz) +
                 box(-SIDE_PLATE_X[0], SIDE_PLATE_X[0], py - 60.0, SADDLE_BOTTOM - 2.0, pz - 60.0, pz + 60.0))
  return clean(part)


def rods_and_nuts(cover_h: float = COVER_H) -> Manifold:
  """The four threaded rods with a nut and washer above the upper saddle and below the lower one, for a cover this
  tall (lower saddle frame: the lower V's middle at y = 0, the upper saddle's V middle at y = cover_h + 2 pads)."""
  parts = []
  top = cover_h + 2 * PAD_T
  for sx in (-1, 1):
    x = sx * (ROD_SLOT_X[0] + ROD_SLOT_X[1]) / 2
    for z in ROD_Z:
      y0 = SADDLE_BOTTOM - 10.0
      parts.append(cyl_y(3.0, y0, y0 + ROD_LEN, x=x, z=z, segments=24))
      parts.append(MP.hex_prism_z_at(M6_NUT_AF, 0, 5.4, 0, 0).rotate((-90, 0, 0)).translate((x, SADDLE_BOTTOM - 1.5 - 5.4, z)))
      parts.append(MP.hex_prism_z_at(M6_NUT_AF, 0, 5.4, 0, 0).rotate((-90, 0, 0)).translate((x, top - SADDLE_BOTTOM + 1.5, z)))
  return union(parts)


def pads() -> Manifold:
  """Where the rubber strips sit on the lower saddle's V faces (lower saddle frame)."""
  t = math.tan(math.radians(V_DEG))
  out = []
  for sgn in (-1, 1):
    pts = [(0.0, 0.0), (sgn * V_HALF_X, -V_HALF_X * t), (sgn * V_HALF_X, -V_HALF_X * t + PAD_T), (0.0, PAD_T)]
    cs = CrossSection([pts])
    if cs.area() < 0:
      cs = CrossSection([pts[::-1]])
    out.append(cs.extrude(SADDLE_LEN - 4.0).translate((0, 0, -SADDLE_LEN / 2 + 2.0)))
  return union(out)


def clamp_fastener_rows(cover_h: float = COVER_H) -> list:
  """The column clamp's threaded rods: how much of each is used for a cover this tall, and the range they cover."""
  stack = lambda h: h + 2 * PAD_T + 2 * (-SADDLE_BOTTOM)   # noqa: E731  from the lower saddle's underside to the upper's top
  used = stack(cover_h) + 2 * (5.4 + 1.0) + 2 * 1.5       # two nuts and washers, 1.5 mm past each
  rows = [{"bolt": f"M6 threaded rod x {ROD_LEN:.0f} (4)", "use": "column clamp: lower saddle, covers, upper saddle, a nut and washer each end",
           "length": ROD_LEN, "needs_mm": [round(stack(COVER_H_RANGE[0]) + 2 * 7.9, 1), round(stack(COVER_H_RANGE[1]) + 2 * 7.9, 1)],
           "ok": stack(COVER_H_RANGE[1]) + 2 * 7.9 <= ROD_LEN, "used_for_your_cover_mm": round(used, 1)}]
  return rows

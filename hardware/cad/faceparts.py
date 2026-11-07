"""
The back-teeth mount's own parts. The teeth sit on the back of a channel that wraps the back half of the grip from 1
to 5 o'clock (open towards you, like a hot dog bun round the grip) and face the dash: a face gear, 166 teeth on a full
circle, its teeth pointing straight back. The motor sits behind the steering wheel at 3 o'clock, just outside the
grip, its shaft pointing at the steering column, and its 16-tooth gear meshes the teeth from behind. 166 / 16 is
10.375, within 0.1% of the other mounts' 197 / 19; the car setup saves the back teeth's own gearing for the long set
(its answer 45) and takes the short set as the other mounts' short teeth (15).

  back teeth        - the channel with the teeth and the rolling band on its back, zip-tied round the grip, in two sets
                      like the other mounts' teeth: the short set (14 teeth, 15 degrees each way, from about 2 to 4
                      o'clock, one piece) for the highway, and the long set (42 teeth, 45 degrees each way, from 1 to 5
                      o'clock, two pieces glued end to end, or one piece for print beds 330 mm across). Over the right
                      spoke's junction with the grip the channel wraps only the grip's back and outside.
  back motor gear   - 16 teeth, its roller beside them on the motor's side
  back carrier      - the motor carrier with its finger guard open wider and its plate's lower edge cut back, so it
                      clears the flat face of the teeth as the lift lever swings it away
  back hinge block  - the hinge block without its ears on top: its arm's joint hangs underneath instead
  back lift lever   - the lift lever with a paddle under its handle's end, so you reach it from inside the rim
  back arm          - three lengths, each slides +-15 mm; wide side in the plane it swings in
  column plate      - under the steering column's lower cover, held by the cover's own screws in two long slots, with
                      the arm's other joint hanging under its front
  fit tests         - a short piece of the back teeth, and one of the part over the right spoke's junction

The motor carrier's other parts (lever bracket, spring, setup gauge) are the dash mount's, unchanged; the spring sits
on an M5 washer from the start on this mount (the teeth's smaller radius pushes them apart harder).

Frames: the steering wheel frame (z along the steering column towards the driver, +y 12 o'clock, +x the driver's
right; the grip centred on z = 0). The mount frame is the carrier frame with the motor's front face at
(R_FACE, 0, z_axis), turned so the carrier's +z (along the shaft) points at the column (-x) and its +y (away from
the teeth) points at the dash (-z); the carrier's +x is then +y (12 o'clock). The whole mount may sit turned
mount_deg about the column (0: the motor at 3 o'clock).
"""
import math

import numpy as np
from manifold3d import CrossSection, Manifold, OpType

import gears as GR
import mountparts as MP
from cadlib import box, clean, cyl, cyl_x, cyl_y, prism_x, revolve, sector, union
from params import (BACKLASH, CD_EXTRA, COVER_BOTTOM, END_CHAMFER, END_LEAD_IN, GRIP, M3_PILOT, M5_CLEAR, PAD,
                    PLATE_FRONT_Z, RIGHT_SPOKE_DEG, ROLL_PAST_TEETH, SHAFT_ACROSS_FLAT, SHAFT_D, SHAFT_FLAT_LEN, SHAFT_LEN,
                    TIE_T, TIE_W, WALL, WHEEL_OD)

FACE_TEETH = 166                  # teeth on a full circle (2 mm module): a 166 mm pitch radius, about the grip's middle
FACE_MOTOR_TEETH = 16
FACE_RATIO = FACE_TEETH / FACE_MOTOR_TEETH          # 10.375
R_F = GR.pitch_radius(FACE_TEETH)
R_P = GR.pitch_radius(FACE_MOTOR_TEETH)
N_TEETH = 42                      # the long back teeth: 21 each side of 3 o'clock, reaching 45.5 degrees each way
N_TEETH_SHORT = 14                # the short back teeth: 7 each side, reaching 15.2 degrees each way (the other mounts' short
                                  # teeth reach 14.6): the set for the highway, in one piece from about 2 to 4 o'clock
BACK_T = 6.0                      # plastic behind the grip, from the channel's inside to the teeth's root
CORNER_T = 4.5                    # the channel's 45 degree corners, thickness
FRONT_Z = 1.0                     # the channel's two walls reach this far forward of the grip's middle
FG_ROLLER = (7.0, 11.0)           # the motor gear along the shaft, from the motor's front face: roller ...
FG_TEETH = (12.0, 24.0)           # ... then teeth (the shaft ends at 23)
R_FACE = R_F + (FG_TEETH[0] + FG_TEETH[1]) / 2.0   # the motor's front face, this far from the column's axis
FACE_BAND = (R_F - 5.5, R_F + 5.5)                 # the teeth's inner and outer ends (the gear's teeth overlap 0.5 mm)
ROLL_BAND = (R_FACE - FG_ROLLER[1] + 0.5, R_FACE - FG_ROLLER[0])   # the rolling band, a ridge beside the teeth
R_ROLL_MID = R_FACE - (FG_ROLLER[0] + FG_ROLLER[1]) / 2.0           # the roller turns at exactly the gears' ratio here
ROLLER_R_F = R_ROLL_MID * FACE_MOTOR_TEETH / FACE_TEETH
CUT_SPAN = (FACE_BAND[0] - 2.0, ROLL_BAND[0] - 0.75)   # the tooth spaces are cut over this span of radius
FLAT_CLEAR = 3.3                  # outside the rolling band the channel's back stands this far clear of the carrier plate's edge
GUARD_WINDOW_F = 72.0             # the carrier's finger guard is open this far either side of the teeth (the face is flat)
PLATE_CHAMFER = 4.0               # the carrier plate's lower edge on the gear side is cut back 45 degrees, this much
TEETH_END_DROP = 3.15             # past the rolling band the teeth's zone falls back this much, so the motor gear's
                                  # teeth clear it as the carrier drops (they move 3.35 mm towards the wheel at most)
BAND_END_DROP = 5.1               # ... and the rolling band falls back this much over the lead-in
JOINT_TEETH = 4                   # the long set's two pieces meet at the tooth space this many teeth above 3 o'clock
DOWEL_D, DOWEL_DEPTH = 1.9, 8.0   # holes for 1.75 mm filament pieces as dowels across the joint
SLOT_EVERY_DEG = 4.5              # zip tie slots this far apart where the spokes leave the grip free
SPOKE_ROOM_DEG = 2.0              # the channel stays this far clear of the right spoke's junction each side
NOTCH_R = 158.0                   # over the junction, nothing of the channel inside this radius


def mount_rot() -> np.ndarray:
  """Carrier-frame directions as steering-wheel-frame vectors (columns: carrier x, y, z)."""
  return np.array([[0.0, 0.0, -1.0], [1.0, 0.0, 0.0], [0.0, -1.0, 0.0]])


class FaceTeeth:
  """Radii, depths and angles of the back teeth for one steering wheel size (the part you hold: its middle at radius rr,
  grip mm thick). Angles are degrees from 3 o'clock, + up."""

  def __init__(self, wheel_od: float = WHEEL_OD, grip: float = GRIP, spoke_deg: tuple = RIGHT_SPOKE_DEG, n_teeth: int = N_TEETH):
    self.wheel_od, self.grip, self.n_teeth = wheel_od, grip, n_teeth
    self.rr = wheel_od / 2.0 - grip / 2.0
    self.rho = grip / 2.0 + PAD                       # the channel's inside, round the grip and its tape
    self.c1 = self.rho * (math.sqrt(2.0) - 1.0)       # the 45 degree corners start this far from the walls and the back
    self.z_bridge = -self.rho                         # the channel's inside behind the grip
    self.z_root = self.z_bridge - BACK_T
    self.z_p = self.z_root - GR.DEDENDUM * GR.MODULE   # the teeth's pitch plane
    self.z_tip = self.z_p - GR.ADDENDUM * GR.MODULE
    self.z_axis = self.z_p - R_P - CD_EXTRA           # the motor's shaft
    self.z_band = self.z_axis + ROLLER_R_F            # the rolling band, where the roller rests
    self.z_flat = self.z_axis - MP.PLATE_BOTTOM + FLAT_CLEAR   # outside the rolling band
    self.w_out = self.rr + self.rho + WALL            # the outer wall's outside face
    self.w_in = self.rr - self.rho - WALL             # the inner wall's outside face
    self.k_o = self.rr + self.c1 + self.rho + CORNER_T * math.sqrt(2.0)   # outer corner's outside: r - z = k_o
    self.k_i = self.rr - self.c1 - self.rho - CORNER_T * math.sqrt(2.0)   # inner corner's outside: r + z = k_i
    self.pitch_deg = 360.0 / FACE_TEETH
    self.teeth_half = n_teeth / 2 * self.pitch_deg
    self.roll_half = self.teeth_half + ROLL_PAST_TEETH
    self.lead_end = self.roll_half + END_LEAD_IN
    self.chamfer_deg = math.degrees(END_CHAMFER / ROLL_BAND[1])
    self.half = self.lead_end + self.chamfer_deg
    # two pieces glued end to end when one would not fit a 220 mm print bed (the long set); the short set is one piece
    self.joint_deg = JOINT_TEETH * self.pitch_deg if self.half > 40.0 else None
    self.spoke = (spoke_deg[0] - SPOKE_ROOM_DEG, spoke_deg[1] + SPOKE_ROOM_DEG)
    # the teeth and the rolling band must sit on the back of the channel, behind the grip
    if not (self.rr - self.c1 - 1.0 <= FACE_BAND[0] - 1.0 and ROLL_BAND[1] <= self.k_o + self.z_flat - 0.5):
      raise ValueError(f"a steering wheel {wheel_od} mm across and {grip} mm thick puts the grip off the back teeth's radius")
    if self.half > 75.0:
      raise ValueError("the back teeth reach past 12 o'clock")

  @property
  def tracked_arc_deg(self) -> float:
    """Steering wheel turn over which the motor gear turns with it (teeth plus rolling band), end to end."""
    return 2.0 * self.roll_half

  @property
  def teeth_arc_deg(self) -> float:
    return 2.0 * self.teeth_half

  @property
  def span_deg(self) -> float:
    return 2.0 * self.half

  def profile(self):
    """(r, z) outline of the piece at one angle: the channel's inside round the grip (walls, 45 degree corners and the
    back), and outside it the walls, the corners, the flat beside the rolling band, the rolling band, the teeth (as
    a solid band: the tooth spaces are cut afterwards) and the root plane either side of them."""
    rr, rho, c1 = self.rr, self.rho, self.c1
    return [
      (rr - rho, FRONT_Z), (rr - rho, -c1), (rr - c1, self.z_bridge), (rr + c1, self.z_bridge), (rr + rho, -c1),
      (rr + rho, FRONT_Z), (self.w_out, FRONT_Z), (self.w_out, self.w_out - self.k_o),
      (self.k_o + self.z_flat, self.z_flat), (ROLL_BAND[1], self.z_flat), (ROLL_BAND[1], self.z_band),
      (ROLL_BAND[0], self.z_band), (ROLL_BAND[0], self.z_root), (FACE_BAND[1], self.z_root), (FACE_BAND[1], self.z_tip),
      (FACE_BAND[0], self.z_tip), (FACE_BAND[0], self.z_root), (self.k_i - self.z_root, self.z_root),
      (self.w_in, self.k_i - self.w_in), (self.w_in, FRONT_Z),
    ]


# ***** the tooth spaces: cut by the motor gear itself, rolled along the teeth *****

_SPACE_CACHE = {}


def to_wheel_axis(m: Manifold, z_axis: float) -> Manifold:
  """A solid drawn round its own axis (local +z, a tooth on local +x) into the steering wheel frame: the axis along x
  through (y = 0, z = z_axis), local +x towards the teeth (+z), local +y to -y."""
  return m.transform([[0, 0, 1, 0], [0, -1, 0, 0], [1, 0, 0, z_axis]])


def tooth_space(t: FaceTeeth, theta_max: float = 5.5, step: float = 0.05) -> Manifold:
  """One tooth space round 3 o'clock (angle 0), as a solid to cut away: the motor gear with its teeth thicker by the
  backlash and reaching a quarter module deeper (the teeth's root clearance), its pitch circle on the teeth's pitch
  plane, rolled along the teeth through theta_max degrees of steering wheel each way and turning FACE_RATIO times as
  fast; what it sweeps through, between the two neighbouring teeth' middles."""
  key = (round(t.z_p, 4), theta_max, step)
  if key in _SPACE_CACHE:
    return _SPACE_CACHE[key]
  cutter = GR.gear_outline(FACE_MOTOR_TEETH, -BACKLASH, addendum=GR.DEDENDUM, dedendum=GR.ADDENDUM)
  near = CrossSection.square((40.0, 40.0)).translate((R_P - 4.0, -20.0))     # only the part near the teeth
  z_cut = t.z_p - R_P
  x0, x1 = CUT_SPAN
  pieces = []
  for th in np.arange(-theta_max, theta_max + 1e-9, step):
    cs = cutter.rotate(-FACE_RATIO * float(th)) ^ near
    m = cs.extrude(x1 - x0).translate((0, 0, x0))
    pieces.append(to_wheel_axis(m, z_cut).rotate((0, 0, -float(th))))
  swept = Manifold.batch_boolean(pieces, OpType.Add)
  half = t.pitch_deg / 2.0
  wedge = CrossSection([[(0.0, 0.0)] + [(400 * math.cos(math.radians(a)), 400 * math.sin(math.radians(a)))
                                        for a in np.linspace(-half, half, 9)]])
  space = swept ^ wedge.extrude(30.0).translate((0, 0, t.z_tip - 5.0))
  _SPACE_CACHE[key] = space
  return space


def tooth_spaces(t: FaceTeeth, j0: int, j1: int) -> Manifold:
  """The tooth spaces at j0 .. j1 tooth pitches from 3 o'clock."""
  sp = tooth_space(t)
  return Manifold.batch_boolean([sp.rotate((0, 0, j * t.pitch_deg)) for j in range(j0, j1 + 1)], OpType.Add)


# ***** helpers in polar coordinates *****

def polar_box(r0: float, r1: float, a0: float, a1: float, z0: float, z1: float, step_deg: float = 0.25) -> Manifold:
  """Everything between radii r0 and r1, angles a0 and a1 (degrees) and heights z0 and z1."""
  return sector(r1, a0, a1, r_in=r0, step_deg=step_deg).extrude(z1 - z0).translate((0, 0, z0))


def polar_ramp_cut(r0: float, r1: float, a0: float, a1: float, z_of_a, z_back: float, step_deg: float = 0.25) -> Manifold:
  """Everything between radii r0 and r1 and angles a0 and a1 (degrees) from z_back up to the surface z_of_a(angle)."""
  n = max(2, int(math.ceil(abs(a1 - a0) / step_deg)) + 1)
  us = np.linspace(a0, a1, n)
  pts = [(float(u), float(z_of_a(u))) for u in us] + [(float(a1), z_back), (float(a0), z_back)]
  cs = CrossSection([pts])
  if cs.area() < 1e-9:
    cs = CrossSection([pts[::-1]])
  # every edge short, so the flat facets the warp leaves follow the curve (the end faces at r0 and r1 included)
  m = cs.extrude(r1 - r0).translate((0, 0, r0)).refine_to_length(0.5)

  def warp(v):
    u, w, r = v[0], v[1], v[2]
    a = math.radians(u)
    return [r * math.cos(a), r * math.sin(a), w]

  return m.warp(warp)


# ***** the back teeth *****

def ramps(t: FaceTeeth) -> Manifold:
  """Past the rolling band at each end, the back falls away towards the wheel: the teeth's zone (where the motor
  gear's teeth go as the carrier drops and moves out) quickly, the rolling band over the lead-in so the roller is set
  down and picked up again gently; over the last END_CHAMFER mm everything slopes back to near the channel's inside."""
  zt_end = t.z_root + TEETH_END_DROP
  zb_end = t.z_band + BAND_END_DROP
  z_last = t.z_bridge - 2.0
  r_split = ROLL_BAND[0] + 2.2      # dropped, the gear's teeth reach out to 175.8 mm; the roller rides outside that
  fast = 0.45 * END_LEAD_IN
  overlap = 0.05                    # the two cuts overlap this much at r_split, so no film of plastic is left between them
  cuts = []
  for sgn in (1, -1):
    def band_z(u, s=sgn):
      a = s * u
      if a <= t.lead_end:
        return t.z_band + (zb_end - t.z_band) * min(1.0, (a - t.roll_half) / END_LEAD_IN)
      return zb_end + (z_last - zb_end) * min(1.0, (a - t.lead_end) / t.chamfer_deg)

    def teeth_z(u, s=sgn):
      a = s * u
      if a <= t.lead_end:
        z = t.z_root + (zt_end - t.z_root) * min(1.0, (a - t.roll_half) / fast)
      else:
        z = zt_end + (z_last - zt_end) * min(1.0, (a - t.lead_end) / t.chamfer_deg)
      return max(z, band_z(u, s))     # the teeth's zone never stands further back than the rolling band beside it

    a0, a1 = t.roll_half, t.half + 0.5
    lo, hi = (a0, a1) if sgn > 0 else (-a1, -a0)
    cuts.append(polar_ramp_cut(CUT_SPAN[0] - 3.0, r_split + overlap, lo, hi, teeth_z, t.z_tip - 3.0))
    cuts.append(polar_ramp_cut(r_split - overlap, ROLL_BAND[1] + 3.5, lo, hi, band_z, t.z_tip - 3.0))
  return union(cuts)


def tip_chamfers(t: FaceTeeth, a0: float, a1: float) -> Manifold:
  """The teeth's tips cut back 45 degrees at their inner and outer ends, 1.5 mm: lifting, the motor gear slides in
  across the teeth as it comes away."""
  c = 1.5
  outer = revolve([(FACE_BAND[1] - c - 0.5, t.z_tip - 0.5), (FACE_BAND[1] + 0.5, t.z_tip - 0.5), (FACE_BAND[1] + 0.5, t.z_tip + c + 0.5)],
                  a0, a1)
  inner = revolve([(FACE_BAND[0] + c + 0.5, t.z_tip - 0.5), (FACE_BAND[0] - 0.5, t.z_tip - 0.5), (FACE_BAND[0] - 0.5, t.z_tip + c + 0.5)],
                  a0, a1)
  return outer + inner


def teeth_trim(t: FaceTeeth) -> Manifold:
  """What comes off the solid band of teeth besides the tooth spaces: everything past the last tooth down to the root
  plane, and the two end teeth each side lowered (the last to 1.2 mm, the next to 3 mm) so the motor gear's teeth
  meet them gently."""
  p = t.pitch_deg
  n = t.n_teeth // 2
  r0, r1 = CUT_SPAN
  out = []
  for sgn in (1, -1):
    def span(a, b, s=sgn):
      return (a, b) if s > 0 else (-b, -a)
    out.append(polar_box(r0, r1, *span(n * p, t.half + 1.0), t.z_tip - 1.0, t.z_root))
    out.append(polar_box(r0, r1, *span((n - 1) * p, n * p), t.z_tip - 1.0, t.z_root - 1.2))
    out.append(polar_box(r0, r1, *span((n - 2) * p, (n - 1) * p), t.z_tip - 1.0, t.z_root - 3.0))
  return union(out)


def tie_angles(t: FaceTeeth) -> list:
  """Where the zip tie slots go: every SLOT_EVERY_DEG from 3 o'clock up to the rolling band's end, and down to the
  right spoke's junction (none over the junction, where a tie can't go round the grip, nor at the joint)."""
  out = []
  a = SLOT_EVERY_DEG / 2.0
  w = math.degrees(TIE_W / 2.0 / t.rr) + 1.0
  while a + w < t.roll_half:
    for s in (a, -a):
      if t.spoke[0] - w < s < t.spoke[1] + w or (t.joint_deg is not None and abs(s - t.joint_deg) < w + 1.0):
        continue
      if s < 0 and s < t.spoke[0]:
        continue
      out.append(s)
    a += SLOT_EVERY_DEG
  return sorted(out)


def tie_path(t: FaceTeeth) -> Manifold:
  """One zip tie slot at 3 o'clock: the tie lies against the grip's back in a groove across the channel's inside,
  and comes out through the two corners to run round the outside of the walls and across the front of the grip."""
  rr, rho = t.rr, t.rho
  ring = []
  for a in np.linspace(-152.0, -28.0, 63):
    ring.append((rr + (rho - 0.5) * math.cos(math.radians(a)), (rho - 0.5) * math.sin(math.radians(a))))
  for a in np.linspace(-28.0, -152.0, 63):
    ring.append((rr + (rho + TIE_T) * math.cos(math.radians(a)), (rho + TIE_T) * math.sin(math.radians(a))))
  cs = CrossSection([ring])
  if cs.area() < 1e-9:
    cs = CrossSection([ring[::-1]])
  for a in (-150.0, -30.0):
    d = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
    nrm = np.array([-d[1], d[0]])
    c0 = np.array([rr, 0.0]) + (rho - 0.5) * d
    c1 = np.array([rr, 0.0]) + (rho + 12.0) * d
    lip = TIE_T / 2.0
    q = [c0 + lip * nrm, c1 + lip * nrm, c1 - lip * nrm, c0 - lip * nrm]
    slot = CrossSection([[(float(p[0]), float(p[1])) for p in q]])
    if slot.area() < 1e-9:
      slot = CrossSection([[(float(p[0]), float(p[1])) for p in q[::-1]]])
    cs = cs + slot
  # (r, z) -> extruded across along y, TIE_W wide
  return cs.extrude(TIE_W).transform([[1, 0, 0, 0], [0, 0, 1, -TIE_W / 2.0], [0, 1, 0, 0]])


def tie_slots(t: FaceTeeth, angles=None) -> Manifold:
  angles = tie_angles(t) if angles is None else angles
  path = tie_path(t)
  return union([path.rotate((0, 0, a)) for a in angles])


def spoke_notch(t: FaceTeeth) -> Manifold:
  """Over the right spoke's junction with the grip the channel keeps only the back and the outside."""
  return polar_box(0.0, NOTCH_R, t.spoke[0], t.spoke[1], -60.0, 20.0)


def centre_mark(t: FaceTeeth) -> Manifold:
  """A small notch on the outer wall's front edge at 3 o'clock: line it up with the motor gear."""
  return box(t.w_out - 1.2, t.w_out + 1.0, -0.6, 0.6, FRONT_Z - 3.0, FRONT_Z + 1.0)


def face_solid(t: FaceTeeth) -> Manifold:
  """The whole back teeth in one piece, before the zip tie slots."""
  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2
  body = body - tooth_spaces(t, -n, n) - teeth_trim(t) - tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - ramps(t) - \
    spoke_notch(t) - centre_mark(t)
  return clean(body)


def dowel_holes(t: FaceTeeth) -> Manifold:
  """Across the joint: holes for 1.75 mm filament pieces, DOWEL_DEPTH each side (glued in with the joint)."""
  k_in = (t.rr - t.c1 - t.rho + t.k_i) / 2.0          # the middle of the inner corner's thickness: r + z = k_in
  k_out = (t.rr + t.c1 + t.rho + t.k_o) / 2.0         # ... and the outer corner's: r - z = k_out
  z_c = -t.c1 - 5.0
  spots = [(k_in - z_c, z_c), (k_out + z_c, z_c),
           (FACE_BAND[0] + 3.0, (t.z_bridge + t.z_root) / 2.0), (FACE_BAND[1], (t.z_bridge + t.z_root) / 2.0)]
  holes = [cyl_y(DOWEL_D / 2.0, -DOWEL_DEPTH, DOWEL_DEPTH, x=r, z=z, segments=24) for r, z in spots]
  return union(holes).rotate((0, 0, t.joint_deg))


def face_pieces(t: FaceTeeth, whole: Manifold | None = None) -> dict:
  """The back teeth: the upper piece (from the joint up), the lower piece (from the joint down) and the one piece; the
  one piece only for a set without a joint."""
  whole = whole if whole is not None else face_solid(t)
  slots = tie_slots(t)
  if t.joint_deg is None:
    return {"one-piece": clean(whole - slots)}
  big = 260.0
  up = polar_box(0.0, big, t.joint_deg, t.half + 2.0, -80.0, 40.0)
  down = polar_box(0.0, big, -t.half - 2.0, t.joint_deg, -80.0, 40.0)
  dw = dowel_holes(t)
  return {"upper": clean((whole ^ up) - slots - dw), "lower": clean((whole ^ down) - slots - dw),
          "one-piece": clean(whole - slots)}


def face_fit_tests(t: FaceTeeth, whole: Manifold | None = None) -> dict:
  """Two short pieces to try first: one with 9 teeth and a zip tie slot (on the grip at 1 to 2 o'clock, and with the
  printed motor gear by hand), and one from over the right spoke's junction."""
  whole = whole if whole is not None else face_solid(t)
  p = t.pitch_deg
  a_mid = 9 * p
  teeth = whole ^ polar_box(0.0, 260.0, a_mid - 4.5 * p, a_mid + 4.5 * p, -80.0, 40.0)
  teeth = teeth - tie_slots(t, [a for a in tie_angles(t) if abs(a - a_mid) < 3.0 * p])
  mid = (t.spoke[0] + t.spoke[1]) / 2.0
  spoke = whole ^ polar_box(0.0, 260.0, mid - 7.0, mid + 7.0, -80.0, 40.0)
  return {"teeth": clean(teeth), "spoke": clean(spoke)}


# ***** the motor gear *****

FG_PHASE = 90.0 - 180.0 / FACE_MOTOR_TEETH    # the gear is turned so a tooth gap faces +y (the set screw)


def face_motor_gear() -> Manifold:
  """In its own frame: z = 0 at the motor's front face, the shaft along +z. Roller (on the motor's side), teeth, a D
  bore on the shaft's flat, and an M3 set screw through a tooth gap onto the flat (it cuts its own thread)."""
  zr0, zr1 = FG_ROLLER
  zt0, zt1 = FG_TEETH
  teeth = GR.gear_outline(FACE_MOTOR_TEETH, BACKLASH).extrude(zt1 - zt0).translate((0, 0, zt0))
  roller = cyl(ROLLER_R_F, zr0, zr1, segments=360)
  hub = cyl(R_P - GR.DEDENDUM * GR.MODULE, zr1 - 0.01, zt0 + 0.01, segments=96)
  part = (teeth + roller + hub).rotate((0, 0, FG_PHASE))
  flat_from = SHAFT_LEN - SHAFT_FLAT_LEN
  r = SHAFT_D / 2 + 0.12
  flat_y = SHAFT_ACROSS_FLAT - SHAFT_D / 2 + 0.12
  d_shape = CrossSection.circle(r, 96) - CrossSection.square((2 * r + 2, 2 * r)).translate((-r - 1, flat_y))
  d_from = max(flat_from, zr0 - 1)
  if d_from > zr0 - 1:
    part = part - cyl(r, zr0 - 1, d_from + 0.01, segments=96)
  part = part - d_shape.extrude(zt1 + 1 - d_from).translate((0, 0, d_from))
  part = part - Manifold.cylinder(1.0, r + 0.8, r, 48).translate((0, 0, zr0))
  z_set = (zt0 + min(zt1, SHAFT_LEN)) / 2.0
  hole = cyl_y(M3_PILOT / 2, 0.0, R_P + 4, z=z_set, segments=32)
  return clean(part - hole)


def face_motor_gear_teeth_only() -> Manifold:
  zt0, zt1 = FG_TEETH
  return GR.gear_outline(FACE_MOTOR_TEETH, BACKLASH).extrude(zt1 - zt0).translate((0, 0, zt0)).rotate((0, 0, FG_PHASE))


def face_roller() -> Manifold:
  return cyl(ROLLER_R_F, FG_ROLLER[0], FG_ROLLER[1], segments=360)


# ***** the motor carrier *****

def face_carrier() -> Manifold:
  """The dash mount's carrier with the finger guard open GUARD_WINDOW_F either side of the teeth and the plate's lower
  edge on the gear side cut back at 45 degrees (lifting, the carrier swings that edge in over the rolling band)."""
  part = MP.motor_carrier(GUARD_WINDOW_F)
  a, t, y0 = PLATE_CHAMFER, MP.MOTOR_PLATE_T, MP.PLATE_BOTTOM
  cut = prism_x([(y0 - 1.0, t - a - 1.0), (y0 + a + 1.0, t + 1.0), (y0 - 1.0, t + 1.0)], -60.0, 60.0)
  return clean(part - cut)


# ***** the hinge block and the arm's joints *****

J2_C = (-52.0, 50.0, -35.0)       # the arm's bolt in the hinge block's joint, carrier frame (under the block, its outer end)
J_EAR_T = 5.0                     # the joints' ears, each side of the arm
ARM_T_F, ARM_W_F = 18.0, 36.0     # the back arm: thickness along its bolts, width in the plane it swings in
SPINE_X = (-30.0, -26.0)          # the plate joining the ears to the hinge block, outside the carrier's swing
LOCK_R_F = 22.0                   # each joint's locking bolt, this far along the arm from its bolt
LOCK_RANGE_F = 25.0               # ... in a curved slot covering +- this many degrees
ARM_SLIDE_F = 15.0
ARM_LENGTHS_F = (135, 165, 195)
J1_W = (60.0, COVER_BOTTOM - 45.0)   # the column plate's joint: its bolt (x, y), steering wheel frame (z: the hinge block's)


def j2_wheel(t: FaceTeeth) -> np.ndarray:
  """The hinge block joint's bolt in the steering wheel frame, the motor at 3 o'clock."""
  return mount_rot() @ np.array(J2_C) + np.array([R_FACE, 0.0, t.z_axis])


def arm_z(t: FaceTeeth) -> float:
  """The plane the back arm swings in (steering wheel z)."""
  return float(j2_wheel(t)[2])


def nominal_arm_dir(t: FaceTeeth) -> np.ndarray:
  """Steering wheel frame (x, y): from the hinge block's joint towards the column plate's, the motor at 3 o'clock."""
  d = np.array(J1_W) - j2_wheel(t)[:2]
  return d / np.linalg.norm(d)


def ear_plate(pivot_xy, lock_dir_deg: float, lock_range: float, extra: list, z0: float, z1: float) -> Manifold:
  """A joint's ear in a plane across the column (x, y), from z0 to z1: round the arm's bolt, the curved slot's room for
  the locking bolt (LOCK_R_F along the arm, +-lock_range degrees round lock_dir_deg), hulled with the extra outlines
  that tie it to its part."""
  px, py = pivot_xy
  pts = [CrossSection.circle(10.0, 64).translate((px, py))]
  for a in np.linspace(lock_dir_deg - lock_range, lock_dir_deg + lock_range, 15):
    pts.append(CrossSection.circle(7.5, 48).translate((px + LOCK_R_F * math.cos(math.radians(a)),
                                                       py + LOCK_R_F * math.sin(math.radians(a)))))
  cs = CrossSection.batch_hull(pts + extra)
  return cs.extrude(z1 - z0).translate((0, 0, z0))


def joint_holes(pivot_xy, lock_dir_deg: float, lock_range: float, z0: float, z1: float) -> Manifold:
  px, py = pivot_xy
  out = [cyl(M5_CLEAR / 2, z0 - 1, z1 + 1, px, py, 32)]
  for a in np.linspace(lock_dir_deg - lock_range, lock_dir_deg + lock_range, 61):
    out.append(cyl(M5_CLEAR / 2, z0 - 1, z1 + 1, px + LOCK_R_F * math.cos(math.radians(a)),
                   py + LOCK_R_F * math.sin(math.radians(a)), 20))
  return union(out)


def face_hinge_block(t: FaceTeeth) -> Manifold:
  """The hinge block without its ears on top, and a joint underneath (towards 6 o'clock) for the back arm: two ears
  across the column, the arm's end between them, its bolt and a curved slot for its locking bolt. Drawn in the
  carrier frame. A spine outside the carrier's swing joins the ears to the block, cut back round the hinge bolt."""
  hb = MP.hinge_block(ears=False)
  R = mount_rot()
  # build the joint in the steering wheel frame round the bolt, then bring it into the carrier frame
  p2 = j2_wheel(t)
  u = nominal_arm_dir(t)
  lock_deg = math.degrees(math.atan2(u[1], u[0]))
  zc = float(p2[2])
  half_gap = ARM_T_F / 2.0 + MP.GAP
  # where the spine and its tie to the block are, in the steering wheel frame (x, y): carrier z -> -x, carrier x -> y
  def c_to_w_xy(xc, zc_):
    return (R_FACE - zc_, xc)
  sx0, sx1 = SPINE_X
  spine_xy = [c_to_w_xy(sx0, -48.0), c_to_w_xy(sx1, -48.0), c_to_w_xy(sx1, -8.0), c_to_w_xy(sx0, -8.0)]
  spine_cs = CrossSection([spine_xy])
  if spine_cs.area() < 1e-9:
    spine_cs = CrossSection([spine_xy[::-1]])
  ears = []
  for z0, z1 in ((zc - half_gap - J_EAR_T, zc - half_gap), (zc + half_gap, zc + half_gap + J_EAR_T)):
    ears.append(ear_plate(p2[:2], lock_deg, LOCK_RANGE_F, [spine_cs], z0, z1))
  # the spine: between the ears, outside the carrier's swing; and its tie to the block's side over the block's height
  z_lo, z_hi = zc - half_gap - J_EAR_T, zc + half_gap + J_EAR_T
  spine = spine_cs.extrude(z_hi - z_lo).translate((0, 0, z_lo))
  hb_top_w, hb_bot_w = t.z_axis - MP.HB_TOP, t.z_axis - MP.HB_BOTTOM
  tie_xy = [c_to_w_xy(sx1 - 0.01, -48.0), c_to_w_xy(-MP.HB_HALF + 0.01, -48.0), c_to_w_xy(-MP.HB_HALF + 0.01, -8.0),
            c_to_w_xy(sx1 - 0.01, -8.0)]
  tie_cs = CrossSection([tie_xy])
  if tie_cs.area() < 1e-9:
    tie_cs = CrossSection([tie_xy[::-1]])
  tie = tie_cs.extrude(hb_bot_w - hb_top_w).translate((0, 0, hb_top_w))
  joint_w = union(ears + [spine, tie]) - joint_holes(p2[:2], lock_deg, LOCK_RANGE_F, z_lo, z_hi)
  # the arm's end turns between the ears
  joint_w = joint_w - (cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap, float(p2[0]), float(p2[1]), 96) +
                       Manifold.batch_hull([cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap,
                                                float(p2[0] + 80 * math.cos(math.radians(a))),
                                                float(p2[1] + 80 * math.sin(math.radians(a))), 48)
                                            for a in (lock_deg - LOCK_RANGE_F - 5, lock_deg + LOCK_RANGE_F + 5)] +
                                           [cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap, float(p2[0]), float(p2[1]), 48)]))
  # into the carrier frame: inverse of x_w = R x_c + (R_FACE, 0, z_axis)
  Rt = R.T
  off = -Rt @ np.array([R_FACE, 0.0, t.z_axis])
  joint_c = joint_w.transform([[float(Rt[i, 0]), float(Rt[i, 1]), float(Rt[i, 2]), float(off[i])] for i in range(3)])
  part = hb + joint_c
  # room round the hinge bolt's head and nut (the spine is outside the knuckles)
  hy, hz = MP.HINGE
  part = part - cyl_x(MP.EAR_HINGE_ROOM, -60.0, -MP.BLOCK_KNUCKLE[1], y=hy, z=hz, segments=48)
  return clean(part)


def face_arm(length: float) -> Manifold:
  """Arm frame: z along the arm from the column plate's bolt (middle of its slide) to the hinge block's bolt at
  z = length; x across in the plane it swings in (ARM_W_F wide); y along the bolts (ARM_T_F thick). The column plate's
  two bolts share one slot, so the arm slides +-ARM_SLIDE_F before they are tightened."""
  w, ht = ARM_W_F / 2, ARM_T_F / 2
  z_end = -ARM_SLIDE_F - 12.0
  bar = box(-w, w, -ht, ht, z_end, length) + cyl_y(w, -ht, ht, z=length, segments=96) + cyl_y(w, -ht, ht, z=z_end, segments=96)
  slot = Manifold.batch_hull([cyl_y(M5_CLEAR / 2, -ht - 1, ht + 1, z=-ARM_SLIDE_F, segments=32),
                              cyl_y(M5_CLEAR / 2, -ht - 1, ht + 1, z=LOCK_R_F + ARM_SLIDE_F, segments=32)])
  holes = cyl_y(M5_CLEAR / 2, -ht - 1, ht + 1, z=length, segments=32) + \
    cyl_y(M5_CLEAR / 2, -ht - 1, ht + 1, z=length - LOCK_R_F, segments=32)
  if length - LOCK_R_F - M5_CLEAR / 2 < LOCK_R_F + ARM_SLIDE_F + M5_CLEAR / 2 + 3.0:
    raise ValueError(f"arm {length} mm is too short")
  return clean(bar - slot - holes)


# ***** the column plate *****

PL_X = (0.0, 56.0)                # the plate's width across the column's underside (x), right of its middle
PL_T = 6.0
PL_PAD_T = 4.0                    # two rubber strips between the plate and the cover (the column clamp's strips)
PL_LEN = 152.0                    # the plate's length along the column, from its front end back
PL_SLOTS_X = (14.0, 40.0)         # two long slots for the cover's screws ...
PL_SLOT_Z = (29.0, 139.0)         # ... this far behind the plate's front end
PL_RIB_X = ((4.0, 8.0), (48.0, 52.0))   # ribs under the plate, along the column
PL_RIB_H = 6.0
PL_TIE_Z = (40.0, 75.0, 110.0, 145.0)   # notches across the underside for zip ties round the cover, if wanted


def plate_top_y() -> float:
  return COVER_BOTTOM - PL_PAD_T


def column_plate(t: FaceTeeth, front_z: float = PLATE_FRONT_Z) -> Manifold:
  """Steering wheel frame, the plate under the cover's underside with its front end at front_z: the plate, two ribs
  along it, two long slots for the cover's own screws (put in longer ones), tie notches, and under its front the
  joint for the back arm: two ears across the column, the arm's bolt and a curved slot for its locking bolt."""
  y1 = plate_top_y()
  y0 = y1 - PL_T
  z0, z1 = front_z - PL_LEN, front_z
  plate = box(PL_X[0], PL_X[1], y0, y1, z0, z1)
  ribs = [box(a, b, y0 - PL_RIB_H, y0 + 0.01, z0, z1) for a, b in PL_RIB_X]
  part = union([plate] + ribs)
  for sx in PL_SLOTS_X:
    part = part - Manifold.batch_hull([cyl_y(M5_CLEAR / 2, y0 - PL_RIB_H - 1, y1 + 1, x=sx, z=front_z - PL_SLOT_Z[0], segments=32),
                                       cyl_y(M5_CLEAR / 2, y0 - PL_RIB_H - 1, y1 + 1, x=sx, z=front_z - PL_SLOT_Z[1], segments=32)])
  for dz in PL_TIE_Z:
    z = front_z - dz
    part = part - box(PL_X[0] - 1, PL_X[1] + 1, y0 - PL_RIB_H - 1, y0 + 1.5, z - 4.0, z + 4.0)
  # the front right top corner cut back, clear of the key cylinder's bezel
  part = part - box(PL_X[1] - 13.0, PL_X[1] + 1.0, y1 - 4.0, y1 + 1.0, front_z - 4.0, front_z + 1.0)
  # the joint: ears across the column at the arm's plane, hanging under the plate's front
  zc = arm_z(t)
  half_gap = ARM_T_F / 2.0 + MP.GAP
  u = -nominal_arm_dir(t)                     # from the plate's joint towards the hinge block
  lock_deg = math.degrees(math.atan2(u[1], u[0]))
  top_strip = CrossSection.square((PL_X[1] - 10.0, 1.0)).translate((10.0, y0 - PL_RIB_H))
  z_lo, z_hi = zc - half_gap - J_EAR_T, zc + half_gap + J_EAR_T
  if z_hi > z1 or z_lo < z0:
    raise ValueError("the column plate's joint is past the plate's front end")
  ears = [ear_plate(J1_W, lock_deg, LOCK_RANGE_F, [top_strip], a, b)
          for a, b in ((z_lo, zc - half_gap), (zc + half_gap, z_hi))]
  web = box(10.0, PL_X[1], y0 - PL_RIB_H, y0 + 0.01, z_lo, z_hi)
  part = part + union(ears + [web])
  part = part - joint_holes(J1_W, lock_deg, LOCK_RANGE_F, z_lo, z_hi)
  # the arm turns between the ears; its slotted end reaches back past the bolt
  px, py = J1_W
  ahead = Manifold.batch_hull([cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap,
                                   px + 90 * math.cos(math.radians(a)), py + 90 * math.sin(math.radians(a)), 48)
                               for a in (lock_deg - LOCK_RANGE_F - 8, lock_deg + LOCK_RANGE_F + 8)] +
                              [cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap, px, py, 48)])
  tail = ARM_SLIDE_F + 12.0
  behind = Manifold.batch_hull([cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap,
                                    px + tail * math.cos(math.radians(a)), py + tail * math.sin(math.radians(a)), 48)
                                for a in (lock_deg + 180 - LOCK_RANGE_F - 3, lock_deg + 180 + LOCK_RANGE_F + 3)] +
                               [cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap, px, py, 48)])
  return clean(part - ahead - behind)


def plate_pads(front_z: float = PLATE_FRONT_Z) -> Manifold:
  y1 = plate_top_y()
  return union([box(a, b, y1, y1 + PL_PAD_T, front_z - PL_LEN + 2.0, front_z - 2.0) for a, b in ((PL_X[0] + 1, PL_X[0] + 11),
                                                                                                  (PL_X[1] - 11, PL_X[1] - 1))])


# ***** the lift lever with a paddle *****

PADDLE_LEN = 44.0                 # the paddle reaches this far below the handle's end (lever frame: towards you, lever down)
PADDLE_Z = (MP.HANDLE_LEN - 8.0, MP.HANDLE_LEN)    # ... from this part of the handle


def back_lift_lever(with_finger: bool = True) -> Manifold:
  """The dash mount's lift lever with a paddle under the end of its handle. On this mount the lever sits behind the
  wheel with its handle pointing at the column; the paddle comes down from the handle's end towards you, so with the
  lever down its tip is about 60 mm behind the middle of the grip, inside the rim at 3 o'clock: push it away from
  you to flip the lever up. Lever frame (see mountparts.py); prints on its side like the lift lever."""
  lever = MP.lift_lever(with_finger)
  z0, z1 = PADDLE_Z
  ht = MP.HANDLE_T / 2
  x0, x1 = MP.HANDLE_X
  bar = box(x0, x1, -ht - PADDLE_LEN + ht, 0.0, z0, z1)
  tip = cyl_x((z1 - z0) / 2, x0, x1, y=-ht - PADDLE_LEN + ht, z=(z0 + z1) / 2, segments=48)
  # the corner where the paddle leaves the handle, filled at 45 degrees
  fillet = prism_x([(-ht + 0.01, z0 - 6.0), (-ht + 0.01, z0 + 0.01), (-ht - 6.0, z0 + 0.01)], x0, x1)
  return clean(lever + bar + tip + fillet)


def back_lever_tab() -> Manifold:
  return MP.lever_tab()

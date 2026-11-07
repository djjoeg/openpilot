"""
The pop-off mount: the back-teeth mount with the motor turned round so it sits inside the steering wheel's circle,
behind the spokes at about 3:15, its shaft pointing out at the grip, and its gear running on the back teeth from the
inside. The motor hangs on an upright hinge just behind its inner end. Two springs hold it either on (the gear in
the teeth) or off (swung 75 degrees back towards the dash, out of the way of your hands): push the motor towards the
dash and it snaps off; pull it back towards you and it snaps on. The springs pass the hinge's line at 50 degrees, so
nothing in between is stable.

  pop teeth      - the back teeth with a thick back: the motor now sits inside the grip's circle, so the spokes pass in
                   front of it when the wheel turns with the motor on, and it has to sit far enough back to clear them.
                   The rolling band stays outside the teeth (the roller is now at the shaft's end).
  pop motor gear - 16 teeth near the motor, the roller at the shaft's end
  pop carrier    - the motor bolts to its plate; finger guard round the gear; the hinge's knuckle over the board,
                   the springs' front bolt above the motor; a lobe on the knuckle that holds the power switch pressed
                   only while the motor is on
  pop hinge block - the hinge's outer knuckles, the springs' back bolt, the two stops (on: the carrier can drop 3
                   degrees past the gear sitting on the band when the wheel is turned past the teeth; off: 75 degrees),
                   the power switch, and the joint for the arm down to the column plate

Frames (millimetres) as faceparts.py: the steering wheel frame has z along the column towards the driver, +y 12
o'clock, +x the driver's right, the grip centred on z = 0. The mount frame is that frame turned MOUNT_DEG about the
column (0: the motor at 3 o'clock). The carrier frame has its origin on the motor's front face, +z along the shaft
(here pointing out, away from the column), +y away from the teeth (here towards the dash), x across; placed in the
mount frame by R_POP and (R_FACE_P, 0, z_axis). Swinging off turns the carrier by -lift about x through the hinge.
"""
import math

import numpy as np
from manifold3d import CrossSection, Manifold

import faceparts as FP
import gears as GR
import mountparts as MP
from cadlib import box, clean, cyl, cyl_x, cyl_y, extrude_x, prism_x, revolve, sector, union
from params import (
  BACKLASH,
  CD_EXTRA,
  M3_CLEAR,
  M3_PILOT,
  M5_CLEAR,
  M5_NUT_AF,
  MOTOR_PLATE_T,
  NEMA,
  NEMA_BOSS,
  NEMA_HOLES,
  NEMA_LEN,
  SHAFT_ACROSS_FLAT,
  SHAFT_D,
  SHAFT_FLAT_LEN,
  SHAFT_LEN,
  SPOKE_BACK_Z,
  WALL,
)

# ***** the car, as measured on 10 October (photos and tape) where this mount differs from the estimates *****

WHEEL_OD_P = 372.0        # across the wheel: your tape across the middle (the cover makers' 365-368 was a little small)
GRIP_P = 35.4             # 4.25 to 4.5 in round the grip: 34.4 to 36.4 mm thick; the channel takes 35.4 plus the tape
MOUNT_DEG = -10.0         # the motor at about 3:20: between the wiper stalk pushed all the way down (3 notches, taken as
                          # 36 degrees until measured) and the key
MOUNT_ADJ = (3.0, 6.0)    # the whole mount (back teeth, motor and hinge block) can be turned this many degrees down
                          # (towards the key) and up (towards the stalk) when fitting it: about 3:26 to 3:08. The hinge
                          # block's slots and the back teeth's notch over the spoke allow it, so the stalk and the key
                          # can be cleared in the car. (Further down the key is in the way.)

# ***** the motor and its gear along the shaft *****

R_FACE_P = FP.R_F - 13.0      # 153: the motor's front face, this far from the column's axis (inside the grip's circle)
FGP_TEETH = (7.0, 19.0)       # the gear's teeth along the shaft from the motor's front face: radius 160 to 172 ...
FGP_ROLLER = (20.0, 24.0)     # ... and its roller at the shaft's end, radius 173 to 177: the same teeth and rolling band
                              # as the back-teeth mount (FP.FACE_BAND, FP.ROLL_BAND)
SPOKE_CLEAR = 8.0             # the motor's side towards you stays this far behind the spokes' back face (5, plus 3 because
                              # the spokes' depth is read off photos)
FLAT_CLEAR_P = 5.0            # inside the teeth the channel's back stands this far clear of the carrier plate's edge (the
                              # motor's side clears it by 3.85 too, and by 1 dropped past the teeth's ends)
Z_AXIS_P = math.floor((SPOKE_BACK_Z - NEMA / 2 - SPOKE_CLEAR) * 2.0) / 2.0     # -59.5: the motor's axis

# carrier frame -> mount frame: carrier x -> -y, carrier y -> -z (towards the dash), carrier z -> +x (out)
R_POP = np.array([[0.0, 0.0, 1.0], [-1.0, 0.0, 0.0], [0.0, -1.0, 0.0]])

# ***** the hinge and the springs (carrier frame, y and z) *****

HINGE_P = (50.0, -50.0)       # the hinge's axis, over the motor's board, along x
KNUCKLE_R = 6.5               # the carrier's knuckle (between the hinge block's two)
KNUCKLE_X = 15.0
BLOCK_KNUCKLE_X = (KNUCKLE_X + MP.GAP, KNUCKLE_X + MP.GAP + 7.0)
BLOCK_KNUCKLE_R = 7.5
LIFT_OFF = 75.0               # swung off: the stop
LIFT_DROP = -3.0              # wheel turned past the teeth: the carrier drops this far, onto the other stop
DEAD_DEG = 50.0               # the springs pass the hinge's line here: below it they pull the gear on, above it off
WEB_LEAD = 95.0               # the carrier's web between its knuckle and its top: its faces, degrees round the hinge
WEB_TRAIL = 150.0             # from +y (towards the dash) towards +z (out); swinging off turns the carrier's angles down
SPRING_X = 33.0               # the two springs, each side of the carrier

# The springs: McMaster-Carr 5108N591, spring steel, loop ends: 2.75 in (69.85 mm) long, 0.5 in (12.7 mm) outside,
# 0.075 in (1.9 mm) wire, 2.75 lbf (12.2 N) to start stretching, 23.2 lbf/in (4.06 N/mm), 30.51 lbf (135.7 N) at most,
# 3.95 in (100.3 mm) long at that (McMaster's table). McMaster's table doesn't say whether its length is inside the loops
# or over them: the bolts are placed for inside; over them, each spring pulls 15 N more. Either way the snap point
# stretches it to at most 1/1.44 of the most it takes and uses at most 66 % of its stretch, and the springs hold the
# gear in at least 1.5 times what lane keeping's hardest push needs. (27749N488, 2.5 in stainless, was 1.20 short.)
SPRING_PART = "McMaster-Carr 5108N591"
SPRING_OD_P, SPRING_WIRE_P = 12.7, 1.905
SPRING_FREE_P, SPRING_IT_P, SPRING_RATE_P, SPRING_MAX_P, SPRING_MAX_LEN_P = 69.85, 12.23, 4.063, 135.7, 100.3
PIN_D = 5.0                   # the loops go over M5 bolts
SPRING_PULL_ON = 47.8         # each spring's pull with the gear on the teeth (N), the length measured inside the loops
SPRING_R = None               # set below: both bolts this far from the hinge


def _spring_radius() -> float:
  """Both bolts the same distance r from the hinge; at the springs' angle apart with the gear on (180 - DEAD_DEG), the
  bolts are 2 r sin(..) apart: set so each spring pulls SPRING_PULL_ON with its length inside the loops."""
  inside = SPRING_FREE_P + (SPRING_PULL_ON - SPRING_IT_P) / SPRING_RATE_P
  pins = inside - PIN_D
  return pins / (2.0 * math.sin(math.radians((180.0 - DEAD_DEG) / 2.0)))


SPRING_R = _spring_radius()
BETA_C = 117.0                # the carrier's bolt, degrees round the hinge (from +y towards +z): through the block over
                              # the motor; both bolts sit behind the wiper stalk and the key
BETA_B = BETA_C + 180.0 - DEAD_DEG     # the hinge block's bolt: towards the column from the hinge


def polar_hinge(r: float, beta_deg: float) -> np.ndarray:
  hy, hz = HINGE_P
  return np.array([hy + r * math.cos(math.radians(beta_deg)), hz + r * math.sin(math.radians(beta_deg))])


C_BOLT = polar_hinge(SPRING_R, BETA_C)
B_BOLT = polar_hinge(SPRING_R, BETA_B)


def b_bolt(hole: int = 0) -> np.ndarray:
  return B_BOLT


def turn(p_yz, lift: float) -> np.ndarray:
  """A carrier-frame (y, z) point turned with the carrier swung off by lift degrees."""
  hy, hz = HINGE_P
  t = math.radians(-lift)
  y, z = p_yz[0] - hy, p_yz[1] - hz
  return np.array([hy + y * math.cos(t) - z * math.sin(t), hz + y * math.sin(t) + z * math.cos(t)])


def spring_length_pins(lift: float, hole: int = 0) -> float:
  return float(np.linalg.norm(turn(C_BOLT, lift) - b_bolt(hole)))


def spring_force(lift: float, hole: int = 0, inside_loops: bool = True) -> float:
  """Each spring's pull (N) with the carrier swung off by lift degrees. inside_loops: McMaster's length measured inside
  the loops (else over them)."""
  free_inside = SPRING_FREE_P if inside_loops else SPRING_FREE_P - 2 * SPRING_WIRE_P
  stretch = spring_length_pins(lift, hole) + PIN_D - free_inside
  return SPRING_IT_P + SPRING_RATE_P * max(0.0, stretch)


def spring_torque(lift: float, hole: int = 0, inside_loops: bool = True) -> float:
  """Both springs' turning force about the hinge (N mm); positive turns the gear onto the teeth."""
  c = turn(C_BOLT, lift)
  b = b_bolt(hole)
  rc = c - np.array(HINGE_P)
  u = (b - c) / np.linalg.norm(b - c)
  f = spring_force(lift, hole, inside_loops)
  # +x turns +y towards +z (swinging off is the other way)
  return 2.0 * f * float(rc[0] * u[1] - rc[1] * u[0])


# ***** the back teeth *****

class PopTeeth(FP.FaceTeeth):
  """The back teeth for the motor inside the grip's circle: the same teeth and rolling band as the back-teeth mount, a
  thick back (its depth set by the motor's axis), and the flat that clears the carrier's plate inside the teeth."""

  def __init__(self, wheel_od: float = WHEEL_OD_P, grip: float = GRIP_P, spoke_deg: tuple = None,
               n_teeth: int = FP.N_TEETH_SHORT, z_axis: float = Z_AXIS_P, mount_deg: float = MOUNT_DEG):
    from params import PAD, RIGHT_SPOKE_DEG
    spoke_deg = spoke_deg if spoke_deg is not None else RIGHT_SPOKE_DEG
    self.wheel_od, self.grip, self.n_teeth, self.mount_deg = wheel_od, grip, n_teeth, mount_deg
    self.rr = wheel_od / 2.0 - grip / 2.0
    self.rho = grip / 2.0 + PAD
    self.c1 = self.rho * (math.sqrt(2.0) - 1.0)
    self.z_bridge = -self.rho
    self.z_axis = z_axis
    self.z_p = z_axis + FP.R_P + CD_EXTRA
    self.z_root = self.z_p + GR.DEDENDUM * GR.MODULE
    self.z_tip = self.z_p - GR.ADDENDUM * GR.MODULE
    self.back_t = self.z_bridge - self.z_root
    self.z_band = z_axis + FP.ROLLER_R_F
    self.z_flat = z_axis - MP.PLATE_BOTTOM + FLAT_CLEAR_P      # inside the teeth: clear of the carrier plate's edge
    self.r_flat = R_FACE_P + MOTOR_PLATE_T + 0.5               # ... out to here
    self.w_out = self.rr + self.rho + WALL
    self.w_in = self.rr - self.rho - WALL
    self.k_o = self.rr + self.c1 + self.rho + FP.CORNER_T * math.sqrt(2.0)
    self.k_i = self.rr - self.c1 - self.rho - FP.CORNER_T * math.sqrt(2.0)
    self.pitch_deg = 360.0 / FP.FACE_TEETH
    self.teeth_half = n_teeth / 2 * self.pitch_deg
    self.roll_half = self.teeth_half + FP.ROLL_PAST_TEETH
    self.lead_end = self.roll_half + FP.END_LEAD_IN
    self.chamfer_deg = math.degrees(FP.END_CHAMFER / FP.ROLL_BAND[1])
    self.half = self.lead_end + self.chamfer_deg
    self.joint_deg = FP.JOINT_TEETH * self.pitch_deg if self.half > 40.0 else None
    # the right spoke's junction, in degrees from the mount's middle (the piece is centred on the motor)
    self.spoke = (spoke_deg[0] - mount_deg - FP.SPOKE_ROOM_DEG - MOUNT_ADJ[1],
                  spoke_deg[1] - mount_deg + FP.SPOKE_ROOM_DEG + MOUNT_ADJ[0])
    if self.back_t < 4.0:
      raise ValueError("the teeth would sit inside the channel")
    if not (self.w_in < self.r_flat - 5.0 and FP.ROLL_BAND[1] < self.w_out - 3.0):
      raise ValueError(f"a steering wheel {wheel_od} mm across and {grip} mm thick puts the grip off the teeth's radius")

  def profile(self):
    rr, rho, c1 = self.rr, self.rho, self.c1
    zb = self.z_root - 0.8          # the outer wall's foot: a small bevel to the root plane
    return [
      (rr - rho, FP.FRONT_Z), (rr - rho, -c1), (rr - c1, self.z_bridge), (rr + c1, self.z_bridge), (rr + rho, -c1),
      (rr + rho, FP.FRONT_Z), (self.w_out, FP.FRONT_Z), (self.w_out, zb + 0.01),
      (self.w_out - 0.8, self.z_root), (FP.ROLL_BAND[1], self.z_root), (FP.ROLL_BAND[1], self.z_band),
      (FP.ROLL_BAND[0], self.z_band), (FP.ROLL_BAND[0], self.z_root), (FP.FACE_BAND[1], self.z_root),
      (FP.FACE_BAND[1], self.z_tip), (FP.FACE_BAND[0], self.z_tip), (FP.FACE_BAND[0], self.z_root),
      (self.r_flat, self.z_root), (self.r_flat, self.z_flat), (self.w_in, self.z_flat), (self.w_in, FP.FRONT_Z),
    ]


def pop_ramps(t: PopTeeth) -> Manifold:
  """Past the rolling band at each end the back falls away towards the wheel, as on the back-teeth mount. Dropping, the
  carrier here brings the gear in towards the column, so the teeth's zone (inside) and the band's (outside) split at
  the gear's dropped outer end."""
  zt_end = t.z_root + FP.TEETH_END_DROP
  zb_end = t.z_band + FP.BAND_END_DROP
  z_last = t.z_bridge - 2.0
  r_split = FP.ROLL_BAND[0] - 1.8          # dropped 3 degrees the gear's teeth reach out to about 170.6, the roller's
  fast = 0.45 * FP.END_LEAD_IN            # inner edge comes in to about 171.4
  overlap = 0.05
  cuts = []
  for sgn in (1, -1):
    def band_z(u, s=sgn):
      a = s * u
      if a <= t.lead_end:
        return t.z_band + (zb_end - t.z_band) * min(1.0, (a - t.roll_half) / FP.END_LEAD_IN)
      return zb_end + (z_last - zb_end) * min(1.0, (a - t.lead_end) / t.chamfer_deg)

    def teeth_z(u, s=sgn):
      a = s * u
      if a <= t.lead_end:
        z = t.z_root + (zt_end - t.z_root) * min(1.0, (a - t.roll_half) / fast)
      else:
        z = zt_end + (z_last - zt_end) * min(1.0, (a - t.lead_end) / t.chamfer_deg)
      return max(z, band_z(u, s))

    a0, a1 = t.roll_half, t.half + 0.5
    lo, hi = (a0, a1) if sgn > 0 else (-a1, -a0)
    cuts.append(FP.polar_ramp_cut(t.r_flat - 3.0, r_split + overlap, lo, hi, teeth_z, t.z_tip - 3.0))
    cuts.append(FP.polar_ramp_cut(r_split - overlap, t.w_out + 1.0, lo, hi, band_z, t.z_tip - 3.0))
  return union(cuts)


def pop_spoke_notch(t: PopTeeth) -> Manifold:
  return FP.polar_box(0.0, FP.NOTCH_R, t.spoke[0], t.spoke[1], -80.0, 20.0)


INNER_CHAMFER = 3.0            # the teeth's tips cut back 45 degrees at their inner end this much (the motor's front edge
                               # passes there as it swings off)


def inner_chamfer(t: PopTeeth) -> Manifold:
  c = INNER_CHAMFER
  return revolve([(FP.FACE_BAND[0] + c + 0.5, t.z_tip - 0.5), (FP.FACE_BAND[0] - 0.5, t.z_tip - 0.5),
                  (FP.FACE_BAND[0] - 0.5, t.z_tip + c + 0.5)], -t.half - 1.0, t.half + 1.0)


def pop_solid(t: PopTeeth) -> Manifold:
  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2
  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \
    inner_chamfer(t) - pop_ramps(t) - pop_spoke_notch(t) - FP.centre_mark(t)
  return clean(body)


def pop_dowel_holes(t: PopTeeth) -> Manifold:
  zc = (t.z_bridge + t.z_root) / 2.0
  spots = [(t.w_in + 2.5, -t.c1 - 4.0), (t.w_out - 2.5, -t.c1 - 4.0), (FP.FACE_BAND[0] + 3.0, zc), (FP.FACE_BAND[1], zc)]
  holes = [cyl_y(FP.DOWEL_D / 2.0, -FP.DOWEL_DEPTH, FP.DOWEL_DEPTH, x=r, z=z, segments=24) for r, z in spots]
  return union(holes).rotate((0, 0, t.joint_deg))


def pop_pieces(t: PopTeeth, whole: Manifold | None = None) -> dict:
  whole = whole if whole is not None else pop_solid(t)
  slots = FP.tie_slots(t)
  if t.joint_deg is None:
    return {"one-piece": clean(whole - slots)}
  big = 260.0
  up = FP.polar_box(0.0, big, t.joint_deg, t.half + 2.0, -90.0, 40.0)
  down = FP.polar_box(0.0, big, -t.half - 2.0, t.joint_deg, -90.0, 40.0)
  dw = pop_dowel_holes(t)
  return {"upper": clean((whole ^ up) - slots - dw), "lower": clean((whole ^ down) - slots - dw),
          "one-piece": clean(whole - slots)}


# ***** the motor gear *****

def pop_motor_gear() -> Manifold:
  """Gear frame: z = 0 at the motor's front face, the shaft along +z. Teeth, then a short hub, then the roller at the
  shaft's end; a D bore on the shaft's flat and an M3 x 10 set screw through a tooth gap onto the flat."""
  zt0, zt1 = FGP_TEETH
  zr0, zr1 = FGP_ROLLER
  teeth = GR.gear_outline(FP.FACE_MOTOR_TEETH, BACKLASH).extrude(zt1 - zt0).translate((0, 0, zt0))
  hub = cyl(FP.R_P - GR.DEDENDUM * GR.MODULE, zt1 - 0.01, zr0 + 0.01, segments=96)
  roller = cyl(FP.ROLLER_R_F, zr0, zr1, segments=360)
  part = (teeth + hub + roller).rotate((0, 0, FP.FG_PHASE))
  r = SHAFT_D / 2 + 0.12
  flat_y = SHAFT_ACROSS_FLAT - SHAFT_D / 2 + 0.12
  d_shape = CrossSection.circle(r, 96) - CrossSection.square((2 * r + 2, 2 * r)).translate((-r - 1, flat_y))
  flat_from = SHAFT_LEN - SHAFT_FLAT_LEN
  part = part - d_shape.extrude(zr1 + 1 - max(flat_from, zt0 - 1)).translate((0, 0, max(flat_from, zt0 - 1)))
  part = part - Manifold.cylinder(1.0, r + 0.8, r, 48).translate((0, 0, zt0))
  z_set = (zt0 + zt1) / 2.0
  hole = cyl_y(M3_PILOT / 2, 0.0, FP.R_P + 4, z=z_set, segments=32)
  return clean(part - hole)


def pop_gear_teeth_only() -> Manifold:
  zt0, zt1 = FGP_TEETH
  return GR.gear_outline(FP.FACE_MOTOR_TEETH, BACKLASH).extrude(zt1 - zt0).translate((0, 0, zt0)).rotate((0, 0, FP.FG_PHASE))


def pop_roller() -> Manifold:
  return cyl(FP.ROLLER_R_F, FGP_ROLLER[0], FGP_ROLLER[1], segments=360)


# ***** the motor and its board (for the checks and the pictures) *****

def motor_and_board() -> dict:
  """The motor turned so its own cable plug and the board's car plug face the dash (+y), the board's motor plug faces
  12 o'clock (carrier -x) and its unused debug plug the key (carrier +x): nothing points at the spokes."""
  h = NEMA / 2
  body = box(-h, h, -h, h, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
  board = box(-h, h, -h, h, -NEMA_LEN - 14.0, -NEMA_LEN)
  plugs = box(-6, 6, h, h + 14, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0) + \
    box(-h - 14, -h, -6, 6, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0) + box(h, h + 5, -6, 6, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0)
  motor_plug = box(-8, 8, h, h + 12, -NEMA_LEN + 2.0, -NEMA_LEN + 18.0)
  return {"body": body, "board": board, "plugs": plugs + motor_plug}


# ***** the carrier *****

TOP_Y = MP.TOP_Y                    # the block over the motor, on its dash side
SIDE_X = MP.SIDE_X
TOP_BACK = -NEMA_LEN + 1.0          # it stops short of the board
PLUG_SLOT = (-9.5, 9.5, -NEMA_LEN - 1.0, -NEMA_LEN + 20.0)   # x and z: room for the motor's own cable plug
WEB_X = (9.5, KNUCKLE_X)            # the two webs from the knuckle to the block over the motor, each side of the car plug
LOBE = (-4.5, 4.5)                  # the switch's lobe on the knuckle, x
LOBE_R = 10.5
SW_BETA = 270.0                     # the switch's roller meets the knuckle here (towards the column), hinge block frame
LOBE_ON = (LIFT_DROP - 2.0, 2.5)    # the lobe holds the switch pressed from these lifts


def _sector_yz(r_in: float, r_out: float, b0: float, b1: float, step: float = 2.0) -> CrossSection:
  """An annular sector round the hinge in the (y, z) plane, angles from +y towards +z."""
  hy, hz = HINGE_P
  bs = np.linspace(b0, b1, max(2, int(abs(b1 - b0) / step) + 1))
  pts = [(hy + r_out * math.cos(math.radians(b)), hz + r_out * math.sin(math.radians(b))) for b in bs]
  pts += [(hy + r_in * math.cos(math.radians(b)), hz + r_in * math.sin(math.radians(b))) for b in bs[::-1]]
  cs = CrossSection([pts])
  return cs if cs.area() > 0 else CrossSection([pts[::-1]])


def _ray_poly(r_max: float, b0: float, b1: float) -> CrossSection:
  """The wedge between two rays from the hinge (angles b0 to b1), out to r_max."""
  hy, hz = HINGE_P
  pts = [(hy, hz)] + [(hy + r_max * math.cos(math.radians(b)), hz + r_max * math.sin(math.radians(b)))
                      for b in np.linspace(b0, b1, 24)]
  cs = CrossSection([pts])
  return cs if cs.area() > 0 else CrossSection([pts[::-1]])


LOBE_RAMP = 12.0


def _lobe_outline() -> CrossSection:
  hy, hz = HINGE_P
  b0, b1 = SW_BETA + LOBE_ON[0], SW_BETA + LOBE_ON[1]

  def r_at(b):
    if b < b0:
      return KNUCKLE_R + (LOBE_R - KNUCKLE_R) * (b - (b0 - LOBE_RAMP)) / LOBE_RAMP
    if b > b1:
      return KNUCKLE_R + (LOBE_R - KNUCKLE_R) * ((b1 + LOBE_RAMP) - b) / LOBE_RAMP
    return LOBE_R

  bs = np.linspace(b0 - LOBE_RAMP, b1 + LOBE_RAMP, 81)
  pts = [(hy + r_at(b) * math.cos(math.radians(b)), hz + r_at(b) * math.sin(math.radians(b))) for b in bs]
  pts += [(hy + (KNUCKLE_R - 1.0) * math.cos(math.radians(b)), hz + (KNUCKLE_R - 1.0) * math.sin(math.radians(b)))
          for b in bs[::-1]]
  cs = CrossSection([pts])
  return cs if cs.area() > 0 else CrossSection([pts[::-1]])


def pop_carrier() -> Manifold:
  t = MOTOR_PLATE_T
  # plate and finger guard as the back-teeth mount's carrier (guard open 72 degrees either side of the teeth)
  outline = CrossSection.square((2 * MP.PLATE_HALF, 2 * MP.PLATE_HALF), center=True) + CrossSection.circle(MP.GUARD_OUT, 180)
  outline = outline ^ CrossSection.square((200, 200)).translate((-100, MP.PLATE_BOTTOM))
  plate = outline.extrude(t)
  shell = cyl(MP.GUARD_OUT, t, MP.GUARD_FRONT, segments=180) - cyl(MP.GUARD_IN, t - 1, MP.GUARD_FRONT + 1, segments=180)
  lip = cyl(MP.GUARD_OUT, MP.GUARD_FRONT - 1.6, MP.GUARD_FRONT, segments=180) - \
    cyl(MP.GUARD_LIP_IN, MP.GUARD_FRONT - 3, MP.GUARD_FRONT + 1, segments=180)
  gw = FP.GUARD_WINDOW_F
  window = sector(MP.GUARD_OUT + 6, 270.0 - gw, 270.0 + gw).extrude(MP.GUARD_FRONT + 4).translate((0, 0, t - 2))
  guard = (shell + lip) - window
  for sgn in (-1, 1):
    a = math.radians(270.0 + sgn * gw)
    rm = (MP.GUARD_IN + MP.GUARD_OUT) / 2
    guard = guard + cyl((MP.GUARD_OUT - MP.GUARD_IN) / 2 + 0.6, t, MP.GUARD_FRONT, rm * math.cos(a), rm * math.sin(a), 24)
  # the block over the motor (its dash side) and the walls beside its dash-side half
  top = box(-SIDE_X[1], SIDE_X[1], TOP_Y[0], TOP_Y[1], TOP_BACK, t)
  walls = union([box(SIDE_X[0], SIDE_X[1], 0.0, TOP_Y[1], TOP_BACK, t), box(-SIDE_X[1], -SIDE_X[0], 0.0, TOP_Y[1], TOP_BACK, t)])
  # the springs' front bolt goes across through the block over the motor, thickened round it
  cy, cz = C_BOLT
  bar = Manifold.batch_hull([cyl_x(6.0, -SIDE_X[1], SIDE_X[1], y=cy, z=cz),
                             box(-SIDE_X[1], SIDE_X[1], TOP_Y[0], TOP_Y[1], cz - 6.0, cz + 6.0)]) ^ \
    box(-SIDE_X[1], SIDE_X[1], TOP_Y[0], 60.0, -60.0, 10.0)
  # the knuckle, and a web each side joining it to the block over the motor: the web's faces are rays from the hinge at
  # WEB_LEAD (the stop when off) and WEB_TRAIL (the stop when dropped)
  hy, hz = HINGE_P
  knuckle = cyl_x(KNUCKLE_R, -KNUCKLE_X, KNUCKLE_X, y=hy, z=hz)
  web_cs = (_ray_poly(80.0, WEB_LEAD, WEB_TRAIL) ^ CrossSection.square((60.0, 80.0)).translate((TOP_Y[0], -80.0)))
  web_cs = web_cs ^ CrossSection.batch_hull([CrossSection.circle(KNUCKLE_R, 48).translate((hy, hz)),
                                             CrossSection.square((TOP_Y[1] - TOP_Y[0], 12.0)).translate((TOP_Y[0], TOP_BACK)),
                                             CrossSection.circle(6.0, 48).translate((cy, cz))])
  webs = union([extrude_x(web_cs, WEB_X[0], WEB_X[1]), extrude_x(web_cs, -WEB_X[1], -WEB_X[0])])
  # the switch's lobe: a raised arc on the knuckle where the switch's roller rests while the motor is on, sloping down
  # to the knuckle over LOBE_RAMP degrees at each end so the roller rolls on and off
  lobe = extrude_x(_lobe_outline(), *LOBE)
  part = union([plate, guard, top, walls, bar, knuckle, webs, lobe])
  # holes and room
  part = part - cyl_x(M5_CLEAR / 2, -60.0, 60.0, y=cy, z=cz, segments=32)       # the springs' front bolt
  part = part - cyl_x(2.75, -40.0, 40.0, y=hy, z=hz, segments=32)                # M5 hinge bolt
  part = part - box(PLUG_SLOT[0], PLUG_SLOT[1], NEMA / 2 - 1.0, TOP_Y[1] + 1.0, PLUG_SLOT[2], PLUG_SLOT[3])
  part = part - cyl(NEMA_BOSS / 2 + 0.4, -3, t + 1, segments=128)
  for sx in (-1, 1):
    for sy in (-1, 1):
      x, y = sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2
      part = part - cyl(M3_CLEAR / 2, -1, t + 1, x, y, 32) - cyl(3.4, t - MP.MOTOR_SCREW_CBORE, t + 1, x, y, 32)
  part = part - box(-NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA_LEN - 20, 0.0)
  # the plate's lower edge on the gear side cut back at 45 degrees, as the back-teeth mount's
  a, y0 = FP.PLATE_CHAMFER, MP.PLATE_BOTTOM
  part = part - prism_x([(y0 - 1.0, t - a - 1.0), (y0 + a + 1.0, t + 1.0), (y0 - 1.0, t + 1.0)], -60.0, 60.0)
  return clean(part)


# ***** placing parts *****

def rot_z(deg: float) -> np.ndarray:
  a = math.radians(deg)
  return np.array([[math.cos(a), -math.sin(a), 0.0], [math.sin(a), math.cos(a), 0.0], [0.0, 0.0, 1.0]])


def mount_to_wheel() -> tuple:
  return rot_z(MOUNT_DEG), np.zeros(3)


def carrier_to_mount(z_axis: float = Z_AXIS_P) -> tuple:
  return R_POP, np.array([R_FACE_P, 0.0, z_axis])


def carrier_to_wheel(z_axis: float = Z_AXIS_P) -> tuple:
  Rm, _ = mount_to_wheel()
  Rc, Tc = carrier_to_mount(z_axis)
  return Rm @ Rc, Rm @ Tc


def place(m: Manifold, R: np.ndarray, T) -> Manifold:
  return m.transform([[float(R[i, 0]), float(R[i, 1]), float(R[i, 2]), float(T[i])] for i in range(3)])


def swung(m: Manifold, lift: float) -> Manifold:
  """A carrier-frame part swung off by lift degrees about the hinge (still in the carrier frame)."""
  if not lift:
    return m
  hy, hz = HINGE_P
  return m.translate((0.0, -hy, -hz)).rotate((-lift, 0.0, 0.0)).translate((0.0, hy, hz))


def to_wheel(m: Manifold, lift: float = 0.0, z_axis: float = Z_AXIS_P) -> Manifold:
  R, T = carrier_to_wheel(z_axis)
  return place(swung(m, lift), R, T)


def carrier_point_to_wheel(p, z_axis: float = Z_AXIS_P) -> np.ndarray:
  R, T = carrier_to_wheel(z_axis)
  return R @ np.asarray(p, dtype=float) + T


# ***** the springs (bought parts, for the checks and the pictures) *****

def spring_solid(lift: float, hole: int = 0) -> Manifold:
  """Both springs (coils and end loops), carrier frame, the carrier swung off by lift (the back bolt doesn't move). Each
  loop's inside rests on the far side of its bolt."""
  c = turn(C_BOLT, lift)
  b = b_bolt(hole)
  r_out = SPRING_OD_P / 2
  r_in = r_out - SPRING_WIRE_P
  out = []
  for s in (1, -1):
    a3 = np.array([s * SPRING_X, c[0], c[1]])
    b3 = np.array([s * SPRING_X, b[0], b[1]])
    d = b3 - a3
    L = float(np.linalg.norm(d))
    z = d / L
    x = np.array([1.0, 0.0, 0.0])
    y = np.cross(z, x)
    R = np.stack([x, y, z], axis=1)
    lc0 = -PIN_D / 2 + r_in + r_out             # the loop's middle, then where the coils start
    ring = (cyl_x(r_out, -SPRING_WIRE_P / 2, SPRING_WIRE_P / 2, segments=40) -
            cyl_x(r_in, -SPRING_WIRE_P, SPRING_WIRE_P, segments=40))
    loop_a = ring.translate((0, 0, -PIN_D / 2 + r_in))
    loop_b = ring.translate((0, 0, L + PIN_D / 2 - r_in))
    coil = cyl(r_out, lc0 - 0.5, L - lc0 + 0.5, segments=40)
    out.append(place(coil + loop_a + loop_b, R, a3))
  return union(out)


# ***** the hinge block *****

PAD_R = (8.0, 14.0)           # the two stops' pads, this far from the hinge, between the web and the knuckles
PARK_PAD = (2.0, WEB_LEAD - LIFT_OFF)          # degrees round the hinge: the web's leading face meets it swung off
DROP_PAD = (WEB_TRAIL - LIFT_DROP, 170.0)      # ... and its trailing face, dropped
CHEEK_X = (BLOCK_KNUCKLE_X[0], 25.5)           # the block's two cheeks, each side (the springs pass just outside)
B_BOSS_R = 7.5
SW_ROLLER_R = 2.4                              # the switch's roller (Omron SS-5GL2: 4.8 mm across)
SW_PRESS_P = 0.9                               # on, the lobe holds the roller this far past where the switch clicks
SW_HOLES_R = LOBE_R + MP.SW_OP - SW_PRESS_P    # the switch's holes' line, this far from the hinge along SW_BETA
SW_CAGE_X = (MP.SW_THICK / 2 + 0.4, MP.SW_THICK / 2 + 3.4)
SW_BODY_R = (LOBE_R, SW_HOLES_R + 6.0)         # the switch, its roller to its back
# The hinge block bolts to a flange on the column plate: two M5 bolts along the column, each through a slot across the
# block's flange (its own x, which turns with the mount) and an upright slot (y) in the plate's. The block's flange is
# part of the block, so it turns with the mount when that is set (MOUNT_ADJ); the plate's slots are long enough for that
# and for the cover's underside sitting higher or lower than estimated. The plate itself slides along the column and
# across on its screw tabs, so the block sets where the plate ends up.
FLANGE_T = 5.0
BLOCK_FLANGE_DZ = (-72.5, -66.0)     # the block's flange along the column, from the motor's axis
_FL0_DEG = -7.5                      # the flange's shape, as the 3:15 build had it in the steering wheel frame


def _to_mount(pts, deg: float = _FL0_DEG):
  """Steering wheel (x, y) points at mount angle deg -> mount frame."""
  c, s_ = math.cos(math.radians(-deg)), math.sin(math.radians(-deg))
  return tuple((float(c * x - s_ * y), float(s_ * x + c * y)) for x, y in pts)


BLOCK_FLANGE_M = _to_mount(((62.0, -34.0), (104.0, -34.0), (104.0, -2.0), (62.0, -2.0)))
FLANGE_BOLTS_M = _to_mount(((72.0, -26.0), (94.0, -12.0)))
SLOT_X = 12.0                 # the block's slots: +- this across
SLOT_Y = 26.0                 # the plate's slots: +- this up and down


def block_flange_z(z_axis: float = Z_AXIS_P) -> tuple:
  return (z_axis + BLOCK_FLANGE_DZ[0], z_axis + BLOCK_FLANGE_DZ[1])


def flange_bolts_wheel(mount_deg: float = None) -> list:
  """The two flange bolts (x, y) in the steering wheel frame with the mount at mount_deg."""
  deg = MOUNT_DEG if mount_deg is None else mount_deg
  c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
  return [(c * x - s_ * y, s_ * x + c * y) for x, y in FLANGE_BOLTS_M]


def mount_to_carrier(p_m, z_axis: float = Z_AXIS_P) -> np.ndarray:
  x, y, z = p_m
  return np.array([-y, z_axis - z, x - R_FACE_P])


def carrier_to_mount_pt(p_c, z_axis: float = Z_AXIS_P) -> np.ndarray:
  x, y, z = p_c
  return np.array([R_FACE_P + z, -x, z_axis - y])


def _hinge_pt(r: float, beta: float) -> tuple:
  p = polar_hinge(r, beta)
  return (float(p[0]), float(p[1]))


def pop_hinge_block() -> Manifold:
  """Carrier frame, the carrier on (lift 0)."""
  hy, hz = HINGE_P
  by, bz = B_BOLT
  parts = []
  # the knuckles
  for s0, s1 in ((BLOCK_KNUCKLE_X[0], BLOCK_KNUCKLE_X[1]), (-BLOCK_KNUCKLE_X[1], -BLOCK_KNUCKLE_X[0])):
    parts.append(cyl_x(BLOCK_KNUCKLE_R, s0, s1, y=hy, z=hz))
  # the cheeks: from the knuckles round behind the hinge to the springs' back bolt and the switch's cage, kept to the
  # angles the carrier never swings into (from 175 round through 270 to 10 degrees)
  sw_back = SW_BODY_R[1] + 4.0
  cheek_pts = [CrossSection.circle(BLOCK_KNUCKLE_R, 48).translate((hy, hz)),
               CrossSection.circle(B_BOSS_R, 48).translate((by, bz)),
               CrossSection.circle(4.0, 24).translate(_hinge_pt(sw_back, SW_BETA - 12.0)),
               CrossSection.circle(4.0, 24).translate(_hinge_pt(sw_back, SW_BETA + 25.0))]
  cheek_cs = CrossSection.batch_hull(cheek_pts) ^ (_ray_poly(200.0, 178.0, 368.0) + CrossSection.circle(BLOCK_KNUCKLE_R, 48).translate((hy, hz)))
  for s0, s1 in ((CHEEK_X[0], CHEEK_X[1]), (-CHEEK_X[1], -CHEEK_X[0])):
    parts.append(extrude_x(cheek_cs, s0, s1))
  # the bridge between the cheeks behind the switch, and the switch's cage walls
  bridge_cs = _sector_yz(SW_BODY_R[1] + 0.5, sw_back + 4.0, SW_BETA - 14.0, SW_BETA + 27.0, 1.0)
  parts.append(extrude_x(bridge_cs, -CHEEK_X[1], CHEEK_X[1]))
  cage_cs = _sector_yz(SW_BODY_R[0] + 1.5, SW_BODY_R[1] + 1.0, SW_BETA - 22.0, SW_BETA + 22.0, 1.0)
  for s0, s1 in (SW_CAGE_X, (-SW_CAGE_X[1], -SW_CAGE_X[0])):
    parts.append(extrude_x(cage_cs, s0, s1))
  # the stops' pads, from the knuckles' inside faces in towards the web
  for b0, b1 in (PARK_PAD, DROP_PAD):
    pad = _sector_yz(BLOCK_KNUCKLE_R - 1.0, PAD_R[1], b0, b1, 0.5)
    for s0, s1 in ((WEB_X[0], BLOCK_KNUCKLE_X[1]), (-BLOCK_KNUCKLE_X[1], -WEB_X[0])):
      parts.append(extrude_x(pad, s0, s1))
  # the flange that bolts to the column plate's post (built in the steering wheel frame)
  body = union(parts)
  part = body + _block_flange()
  # holes: hinge bolt, the springs' back bolt, the switch's screws (slots along the switch's travel, nuts in one wall)
  part = part - cyl_x(2.75, -60.0, 60.0, y=hy, z=hz, segments=32)
  part = part - cyl_x(M5_CLEAR / 2, -60.0, 60.0, y=by, z=bz, segments=32)
  # room for the carrier's knuckle and lobe between the block's knuckles
  part = part - cyl_x(KNUCKLE_R + MP.CHANNEL_GAP, -KNUCKLE_X - MP.GAP, KNUCKLE_X + MP.GAP, y=hy, z=hz, segments=96)
  part = part - _switch_screw_slots()
  return clean(part)


def _switch_frame():
  """The switch's place: its holes' line SW_HOLES_R from the hinge along SW_BETA; returns (centre (y, z), radial unit,
  along unit) with radial pointing away from the hinge."""
  rad = np.array([math.cos(math.radians(SW_BETA)), math.sin(math.radians(SW_BETA))])
  along = np.array([-rad[1], rad[0]])
  return np.array(HINGE_P), rad, along


def _switch_screw_slots() -> Manifold:
  h, rad, along = _switch_frame()
  out = []
  for d in (-MP.SW_PITCH / 2, MP.SW_PITCH / 2):
    pts = []
    for s in (-MP.SW_SLOT, MP.SW_SLOT):
      c = h + rad * (SW_HOLES_R + s) + along * d
      pts.append(cyl_x(MP.M2_CLEAR / 2, -SW_CAGE_X[1] - 1, SW_CAGE_X[1] + 1, y=float(c[0]), z=float(c[1]), segments=20))
      # nut trap in the -x wall's outside face
      out.append(prism_hex_x(MP.M2_NUT_AF, -SW_CAGE_X[1] - 1.0, -SW_CAGE_X[1] + MP.M2_NUT_T, float(c[0]), float(c[1])))
    out.append(Manifold.batch_hull(pts))
  return union(out)


def prism_hex_x(af: float, x0: float, x1: float, y: float, z: float) -> Manifold:
  r = af / math.sqrt(3)
  pts = [(y + r * math.cos(math.radians(60 * i)), z + r * math.sin(math.radians(60 * i))) for i in range(6)]
  return extrude_x(CrossSection([pts]), x0, x1)


def switch_body_pop() -> Manifold:
  """The room the power switch takes (body, lever and roller), carrier frame on the hinge block."""
  h, rad, along = _switch_frame()
  r0, r1 = SW_BODY_R
  pts = []
  for r in (r0, r1):
    for s in (-MP.SW_LEN / 2, MP.SW_LEN / 2):
      c = h + rad * r + along * s
      pts.append((float(c[0]), float(c[1])))
  cs = CrossSection([[pts[0], pts[1], pts[3], pts[2]]])
  cs = cs if cs.area() > 0 else CrossSection([[pts[0], pts[2], pts[3], pts[1]]])
  return extrude_x(cs, -MP.SW_THICK / 2, MP.SW_THICK / 2)


def wheel_to_carrier(m: Manifold, z_axis: float = Z_AXIS_P) -> Manifold:
  R, T = carrier_to_wheel(z_axis)
  Rt = R.T
  off = -Rt @ T
  return m.transform([[float(Rt[i, 0]), float(Rt[i, 1]), float(Rt[i, 2]), float(off[i])] for i in range(3)])


def _xy_poly(pts) -> CrossSection:
  cs = CrossSection([list(pts)])
  return cs if cs.area() > 0 else CrossSection([list(pts)[::-1]])


def mount_solid_to_carrier(m: Manifold, z_axis: float = Z_AXIS_P) -> Manifold:
  """A mount-frame solid -> carrier frame (the inverse of carrier_to_mount)."""
  Rt = R_POP.T
  off = -Rt @ np.array([R_FACE_P, 0.0, z_axis])
  return m.transform([[float(Rt[i, 0]), float(Rt[i, 1]), float(Rt[i, 2]), float(off[i])] for i in range(3)])


def _block_flange() -> Manifold:
  """The block's flange, built in the mount frame (so it turns with the mount), with a slot across at each bolt."""
  z0, z1 = block_flange_z()
  fl = _xy_poly(BLOCK_FLANGE_M).extrude(z1 - z0).translate((0, 0, z0))
  for bx, by in FLANGE_BOLTS_M:
    fl = fl - Manifold.batch_hull([cyl(M5_CLEAR / 2, z0 - 1, z1 + 1, bx + s, by, 32) for s in (-SLOT_X, SLOT_X)])
  return mount_solid_to_carrier(fl)


# ***** the column plate and its screw tabs *****
#
# The plate is a U round the adjustment tab (the steering column's tilt and reach lever): a leg each side of the tab's
# paddle, joined behind the tab's pivot where nothing moves when you pull it. The right leg carries the upright flange
# the hinge block bolts to. It hangs from the lower column cover's own screws through swivel tabs.
#
# The cover's three screws (Honda's parts list: two 4 x 16 self-tapping, 90101-S2K-000, and one M5 x 12 screw-washer,
# 93891-05012-08). Honda's remote starter instructions (AII 42271, step 12) draw where they go: the two self-tapping
# screws near the cover's steering wheel end into the column's bracket there, one under the key cylinder (the round cup
# in your photos, right of the paddle) and one in line with the tab's slot (behind the paddle, so it can't be used); the
# M5 beside the tab's slot further back, into the tilt lock's bracket. No source gives distances: their places here are
# read off the drawing and your photos, and each tab reaches anywhere 18 to 40 mm from its screw, turned any way, onto
# one of the plate's long slots, so the plate fits them wherever they really are. Each tab holds an M5 x 20 hex bolt
# hanging down from a channel along its top (the cover above keeps it there): the plate goes up onto the bolts and a
# washer and lock nut under it hold it.

TAB_T = 8.0                   # a tab's thickness: the plate's top sits this far below the cover's underside
TAB_W = 16.0                  # its arm's width
# Two kinds of tab: "cup", for the self-tapping screw in the round cup under the key cylinder (its round end bridges the
# cup; the screw's pan head and a washer sit in a counterbore underneath), and "slim", for the M5 right beside the
# tab's slot (a socket-head M5 in a smaller counterbore, so its end stays clear of the tab's arm).
TAB_KINDS = {"cup": {"end_r": 12.5, "head": (6.6, 4.0)}, "slim": {"end_r": 7.0, "head": (4.6, 5.0)}}
TAB_END_R = TAB_KINDS["cup"]["end_r"]
TAB_L = 40.0                  # its screw to the far end of its slot
TAB_SLOT = (18.0, 40.0)       # the slot along it for the bolt to the plate, with a channel on top for the bolt's head
TAB_BOSS = (5.5, 3.0)         # a short boss into the cover's screw cup that centres it: radius, height

NUT_CHANNEL_T = 5.5           # the channel for the bolt's hex head (8 mm across flats, 3.5 mm tall): it can slide, not turn
PL_T_U = 8.0                  # the plate's thickness
PL_RIGHT_X = (12.0, 70.0)     # the right leg across (its inner edge 9 mm right of the paddle)
PL_LEFT_X = (-64.0, -50.0)    # the left leg (its inner edge 9 mm left of the paddle)
PL_FRONT_Z = -92.0            # the right leg's front end (behind the key cylinder's bulge) ...
PL_NOTCH = (44.0, -114.0)     # ... except outside x 44, where it starts at z -114: the springs' bolt on the hinge block
                              # and the springs' loops on it hang just above there
PL_LEFT_FRONT_Z = -124.0      # the left leg's front end
PL_BRIDGE_Z = (-208.0, -194.0)   # the bridge behind the tab's pivot; the plate's back edge
# the slots the tabs' bolts go through: (x0, z0, x1, z1)
PL_SLOTS = ((54.0, -122.0, 54.0, -186.0), (28.0, -136.0, 28.0, -186.0), (-40.0, -201.0, 4.0, -201.0),
            (-57.0, -132.0, -57.0, -184.0), (18.0, -117.0, 40.0, -117.0), (19.0, -100.0, 35.0, -100.0))
PL_TIE_Z_U = (-148.0, -176.0)  # notches across the left leg's underside for a zip tie round the covers, if wanted
PAD_T = 10.0                   # foam strip on the left leg's top (EPDM weatherstrip 10 x 10 mm), squeezed to TAB_T
FLANGE_PAD = 9.0               # the plate's flange beyond its slots' ends
SHELF_X1 = 86.0               # the shelf under the flange, out to here


def plate_top_y_u(cover_bottom: float = None) -> float:
  from params import COVER_BOTTOM
  return (COVER_BOTTOM if cover_bottom is None else cover_bottom) - TAB_T


def plate_flange_z() -> tuple:
  z0 = block_flange_z()[0]
  return (z0 - FLANGE_T, z0)


def plate_flange_outline() -> list:
  """The plate's flange (x, y), steering wheel frame, round both bolts' slots at the nominal mount."""
  b = flange_bolts_wheel()
  xs, ys = [p[0] for p in b], [p[1] for p in b]
  y_lo = min(ys) - SLOT_Y - FLANGE_PAD
  x_lo = min(min(xs) - FLANGE_PAD, PL_RIGHT_X[1] - 8.0)
  x_hi = max(xs) + FLANGE_PAD + 2.0
  # its lower outer corner cut away: the lower spring sweeps past there as the motor pops off
  cx = max(xs) - 4.0
  cy = max(min(ys), y_lo + 10.0)
  return [(x_lo, y_lo), (cx, y_lo), (x_hi, cy), (x_hi, max(ys) + SLOT_Y + FLANGE_PAD), (x_lo, max(ys) + SLOT_Y + FLANGE_PAD)]


def _slot_y(x0, z0, x1, z1, y0, y1, r=M5_CLEAR / 2) -> Manifold:
  return Manifold.batch_hull([cyl_y(r, y0, y1, x=x0, z=z0, segments=32), cyl_y(r, y0, y1, x=x1, z=z1, segments=32)])


def _round_corner(part: Manifold, x: float, z: float, sx: int, sz: int, r: float, y0: float, y1: float) -> Manifold:
  """Rounds the plate's corner at (x, z), the plate lying towards +sx in x and +sz in z from it."""
  cut = box(min(x, x + sx * r) - 0.01, max(x, x + sx * r) + 0.01, y0 - 1.0, y1 + 1.0, min(z, z + sz * r) - 0.01, max(z, z + sz * r) + 0.01)
  return part - (cut - cyl_y(r, y0 - 2.0, y1 + 2.0, x=x + sx * r, z=z + sz * r, segments=40))


def pop_column_plate(cover_bottom: float = None) -> Manifold:
  """Steering wheel frame. The U: right leg, bridge, left leg (its top TAB_T below the cover's underside); the tabs'
  slots; at the right leg's outer edge the upright flange the hinge block bolts to (upright slots), held by a wall
  along the leg's edge, a shelf under it and a gusset behind it."""
  y1 = plate_top_y_u()
  y0 = y1 - PL_T_U
  zb0, zb1 = PL_BRIDGE_Z
  right = box(PL_RIGHT_X[0], PL_RIGHT_X[1], y0, y1, zb0, PL_FRONT_Z)
  left = box(PL_LEFT_X[0], PL_LEFT_X[1], y0, y1, zb0, PL_LEFT_FRONT_Z)
  bridge = box(PL_LEFT_X[0], PL_RIGHT_X[0] + 1.0, y0, y1, zb0, zb1)
  part = union([right, left, bridge])
  part = part - box(PL_NOTCH[0], PL_RIGHT_X[1] + 1.0, y0 - 1.0, y1 + 1.0, PL_NOTCH[1], PL_FRONT_Z + 1.0)
  # round the corners you might touch
  part = _round_corner(part, PL_RIGHT_X[0], PL_FRONT_Z, 1, -1, 8.0, y0, y1)
  part = _round_corner(part, PL_NOTCH[0], PL_FRONT_Z, -1, -1, 6.0, y0, y1)
  part = _round_corner(part, PL_LEFT_X[0], PL_LEFT_FRONT_Z, 1, -1, 7.0, y0, y1)
  part = _round_corner(part, PL_LEFT_X[1], PL_LEFT_FRONT_Z, -1, -1, 7.0, y0, y1)
  part = _round_corner(part, PL_LEFT_X[0], zb0, 1, 1, 8.0, y0, y1)
  # a rib under each leg's edge by the tab, for stiffness
  ribs = [box(PL_RIGHT_X[0], PL_RIGHT_X[0] + 4.0, y0 - 6.0, y0 + 0.01, zb0, PL_FRONT_Z - 8.0),
          box(PL_LEFT_X[1] - 4.0, PL_LEFT_X[1], y0 - 6.0, y0 + 0.01, zb0, PL_LEFT_FRONT_Z - 7.0),
          box(PL_LEFT_X[0] + 8.0, PL_RIGHT_X[0] + 4.0, y0 - 6.0, y0 + 0.01, zb1 - 4.0, zb1)]
  part = union([part] + ribs)
  # the flange, its wall along the leg's edge, the shelf under it and the gusset behind
  fz0, fz1 = plate_flange_z()
  fo = plate_flange_outline()
  fy0, fy1 = fo[0][1], fo[2][1]
  flange = _xy_poly(fo).extrude(fz1 - fz0).translate((0, 0, fz0))
  wall = box(PL_RIGHT_X[1] - 8.0, PL_RIGHT_X[1], y0, fy1, fz0 - 30.0, fz1)
  low = min(y0, fy0)
  shelf = box(PL_RIGHT_X[1] - 8.0, SHELF_X1, low, y0 + 6.0, fz0 - 16.0, fz1)
  gusset = prism_x([(y0 + 5.0, fz0), (fy1 - 4.0, fz0), (y0 + 5.0, fz0 - 26.0)], PL_RIGHT_X[1] - 8.0, PL_RIGHT_X[1])
  part = union([part, flange, wall, shelf, gusset])
  # the tabs' slots
  for x0, z0, x1, z1 in PL_SLOTS:
    part = part - _slot_y(x0, z0, x1, z1, y0 - 8.0, y1 + 1.0)
  # zip-tie notches across the left leg's underside
  for z in PL_TIE_Z_U:
    part = part - box(PL_LEFT_X[0] - 1.0, PL_LEFT_X[1] + 1.0, y0 - 7.0, y0 + 1.5, z - 4.0, z + 4.0)
  # the flange's slots (upright)
  for bx, by in flange_bolts_wheel():
    part = part - Manifold.batch_hull([cyl(M5_CLEAR / 2, fz0 - 17.0, fz1 + 1.0, bx, by + s, 32) for s in (-SLOT_Y, SLOT_Y)])
  return clean(part)


def plate_pad(cover_bottom: float = None) -> Manifold:
  """The foam strip on the left leg's top, squeezed between it and the cover."""
  y1 = plate_top_y_u(cover_bottom)
  return box(PL_LEFT_X[0] + 1.0, PL_LEFT_X[1] - 1.0, y1, y1 + TAB_T, PL_BRIDGE_Z[0] + 4.0, PL_LEFT_FRONT_Z - 4.0)


def pop_screw_tab(kind: str = "cup") -> Manifold:
  """Tab frame: its screw at the origin, its slot along +x from TAB_SLOT[0] to TAB_SLOT[1], +z towards the cover (its
  top face z = 0). The plate's bolt hangs from its hex head in a channel along the slot's top and can slide along it."""
  t = TAB_T
  k = TAB_KINDS[kind]
  end = cyl(k["end_r"], -t, 0.0, 0.0, 0.0, 64)
  arm = Manifold.batch_hull([cyl(TAB_W / 2, -t, 0.0, 6.0, 0.0, 48), cyl(TAB_W / 2, -t, 0.0, TAB_L + 3.0, 0.0, 48)])
  boss = cyl(TAB_BOSS[0], 0.0, TAB_BOSS[1], segments=48)
  part = end + arm + boss
  part = part - cyl(M5_CLEAR / 2, -t - 1.0, TAB_BOSS[1] + 1.0, segments=32)
  part = part - cyl(k["head"][0], -t - 1.0, -t + k["head"][1], segments=48)
  part = part - Manifold.batch_hull([cyl(M5_CLEAR / 2, -t - 1.0, 1.0, x, 0.0, 32) for x in TAB_SLOT])
  # the bolt head's channel from the top: its flats against the channel's sides so it can't turn
  ch = box(TAB_SLOT[0] - M5_NUT_AF * 0.6, TAB_SLOT[1] + M5_NUT_AF * 0.6, -(M5_NUT_AF + 0.3) / 2, (M5_NUT_AF + 0.3) / 2,
           -NUT_CHANNEL_T, 0.5)
  part = part - ch
  return clean(part)


def place_tab(screw_xz: tuple, toward_xz: tuple, cover_bottom: float = None) -> tuple:
  """Where a tab sits: its screw at screw_xz (on the cover's underside), turned towards toward_xz. Returns (R, T) tab
  frame -> steering wheel frame and toward_xz."""
  from params import COVER_BOTTOM
  yc = COVER_BOTTOM if cover_bottom is None else cover_bottom
  sx, sz = screw_xz
  d = np.array([toward_xz[0] - sx, toward_xz[1] - sz], dtype=float)
  d /= np.linalg.norm(d)
  ex = np.array([d[0], 0.0, d[1]])
  ez = np.array([0.0, 1.0, 0.0])
  ey = np.cross(ez, ex)
  R = np.stack([ex, ey, ez], axis=1)
  T = np.array([sx, yc, sz])
  return R, T, toward_xz


def tab_bolts_on_slot(screw_xz: tuple, slot: tuple, n: int = 9) -> list:
  """Points on a plate slot (x0, z0, x1, z1) a tab from screw_xz can put its bolt (18 to 40 mm away), sampled."""
  x0, z0, x1, z1 = slot
  out = []
  L = math.hypot(x1 - x0, z1 - z0)
  ux, uz = (x1 - x0) / L, (z1 - z0) / L
  for i in range(int(L) + 1):
    u = min(L, float(i))
    if u < 3.0 or u > L - 3.0:
      continue
    px, pz = x0 + ux * u, z0 + uz * u
    d = math.hypot(px - screw_xz[0], pz - screw_xz[1])
    if TAB_SLOT[0] + 1.0 <= d <= TAB_SLOT[1] - 1.0:
      out.append((px, pz))
  return out

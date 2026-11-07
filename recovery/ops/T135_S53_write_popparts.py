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
MOUNT_DEG = -7.5          # the motor at about 3:15: the most room between the wiper stalk pushed down and the key

# ***** the motor and its gear along the shaft *****

R_FACE_P = FP.R_F - 13.0      # 153: the motor's front face, this far from the column's axis (inside the grip's circle)
FGP_TEETH = (7.0, 19.0)       # the gear's teeth along the shaft from the motor's front face: radius 160 to 172 ...
FGP_ROLLER = (20.0, 24.0)     # ... and its roller at the shaft's end, radius 173 to 177: the same teeth and rolling band
                              # as the back-teeth mount (FP.FACE_BAND, FP.ROLL_BAND)
SPOKE_CLEAR = 5.0             # the motor's side towards you stays this far behind the spokes' back face
Z_AXIS_P = math.floor((SPOKE_BACK_Z - NEMA / 2 - SPOKE_CLEAR) * 2.0) / 2.0     # -56.5: the motor's axis

# carrier frame -> mount frame: carrier x -> -y, carrier y -> -z (towards the dash), carrier z -> +x (out)
R_POP = np.array([[0.0, 0.0, 1.0], [-1.0, 0.0, 0.0], [0.0, -1.0, 0.0]])

# ***** the hinge and the springs (carrier frame, y and z) *****

HINGE_P = (45.0, -50.0)       # the hinge's axis, over the motor's board, along x
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

# The springs: McMaster-Carr 27749N488, 302 stainless steel, loop ends: 2.5 in (63.5 mm) long, 0.5 in (12.7 mm)
# outside, 0.075 in (1.9 mm) wire, 2.29 lbf (10.19 N) to start stretching, 22.41 lbf/in (3.924 N/mm), 25.41 lbf
# (113.0 N) at most, 3.53 in (89.7 mm) long at that (McMaster's table). McMaster's table doesn't say whether its length
# is inside the loops or overall; the hinge block has two holes for the back bolt, one for each (see SPRING_HOLES).
SPRING_PART = "McMaster-Carr 27749N488"
SPRING_OD_P, SPRING_WIRE_P = 12.7, 1.905
SPRING_FREE_P, SPRING_IT_P, SPRING_RATE_P, SPRING_MAX_P, SPRING_MAX_LEN_P = 63.5, 10.19, 3.924, 113.0, 89.7
PIN_D = 5.0                   # the loops go over M5 bolts
SPRING_PULL_ON = 55.0         # each spring's pull with the gear on the teeth (N), the length measured inside the loops
SPRING_R = None               # set below: both bolts this far from the hinge


def _spring_radius() -> float:
  """Both bolts the same distance r from the hinge; at the springs' angle apart with the gear on (180 - DEAD_DEG), the
  bolts are 2 r sin(..) apart: set so each spring pulls SPRING_PULL_ON with its length inside the loops."""
  inside = SPRING_FREE_P + (SPRING_PULL_ON - SPRING_IT_P) / SPRING_RATE_P
  pins = inside - PIN_D
  return pins / (2.0 * math.sin(math.radians((180.0 - DEAD_DEG) / 2.0)))


SPRING_R = _spring_radius()
BETA_C = 100.0                # the carrier's bolt, degrees round the hinge (from +y towards +z): above the motor's front
BETA_B = BETA_C + 180.0 - DEAD_DEG     # the hinge block's bolt: behind the board
SPRING_HOLES = (0.0, -(2 * SPRING_WIRE_P))   # the back bolt's second hole sits closer by this much, along the spring:
                                             # for McMaster's length being measured over the loops


def polar_hinge(r: float, beta_deg: float) -> np.ndarray:
  hy, hz = HINGE_P
  return np.array([hy + r * math.cos(math.radians(beta_deg)), hz + r * math.sin(math.radians(beta_deg))])


C_BOLT = polar_hinge(SPRING_R, BETA_C)
B_BOLT = polar_hinge(SPRING_R, BETA_B)


def b_bolt(hole: int = 0) -> np.ndarray:
  """The hinge block's spring bolt: hole 0, or hole 1 a little closer to the carrier's bolt along the spring."""
  d = C_BOLT - B_BOLT
  return B_BOLT + SPRING_HOLES[hole] * -d / np.linalg.norm(d)


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
    from params import RIGHT_SPOKE_DEG
    spoke_deg = spoke_deg if spoke_deg is not None else RIGHT_SPOKE_DEG
    # the parent's checks are for the back-teeth mount's depths; its angles are taken from the mount's middle here
    rel = (spoke_deg[0] - mount_deg, spoke_deg[1] - mount_deg)
    super().__init__(wheel_od, grip, rel, n_teeth)
    self.mount_deg = mount_deg
    self.z_axis = z_axis
    self.z_p = z_axis + FP.R_P + CD_EXTRA
    self.z_root = self.z_p + GR.DEDENDUM * GR.MODULE
    self.z_tip = self.z_p - GR.ADDENDUM * GR.MODULE
    self.back_t = self.z_bridge - self.z_root
    self.z_band = z_axis + FP.ROLLER_R_F
    self.z_flat = z_axis - MP.PLATE_BOTTOM + FP.FLAT_CLEAR     # inside the teeth: clear of the carrier plate's edge
    self.r_flat = R_FACE_P + MOTOR_PLATE_T + 0.5               # ... out to here
    if self.back_t < 4.0:
      raise ValueError("the teeth would sit inside the channel")

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


def pop_solid(t: PopTeeth) -> Manifold:
  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2
  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \
    pop_ramps(t) - pop_spoke_notch(t) - FP.centre_mark(t)
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
PLUG_SLOT = (-9.5, 9.5, -NEMA_LEN - 1.0, -NEMA_LEN + 21.0)   # x and z: room for the motor's own cable plug
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
  # the springs' front bolt: a bar across above the motor's front half
  cy, cz = C_BOLT
  bar = Manifold.batch_hull([cyl_x(6.0, -SIDE_X[1], SIDE_X[1], y=cy, z=cz),
                             box(-SIDE_X[1], SIDE_X[1], TOP_Y[1] - 1.0, TOP_Y[1], cz - 8.0, cz + 8.0)])
  # the knuckle, and a web each side joining it to the block over the motor: the web's faces are rays from the hinge at
  # WEB_LEAD (the stop when off) and WEB_TRAIL (the stop when dropped)
  hy, hz = HINGE_P
  knuckle = cyl_x(KNUCKLE_R, -KNUCKLE_X, KNUCKLE_X, y=hy, z=hz)
  web_cs = (_ray_poly(80.0, WEB_LEAD, WEB_TRAIL) ^ CrossSection.square((60.0, 80.0)).translate((TOP_Y[0], -80.0)))
  web_cs = web_cs ^ CrossSection.batch_hull([CrossSection.circle(KNUCKLE_R, 48).translate((hy, hz)),
                                             CrossSection.square((TOP_Y[1] - TOP_Y[0], 12.0)).translate((TOP_Y[0], TOP_BACK)),
                                             CrossSection.circle(6.0, 48).translate((cy, cz))])
  webs = union([extrude_x(web_cs, WEB_X[0], WEB_X[1]), extrude_x(web_cs, -WEB_X[1], -WEB_X[0])])
  # the switch's lobe: a raised arc on the knuckle, where the switch's roller rests while the motor is on
  lobe_cs = _sector_yz(KNUCKLE_R - 0.5, LOBE_R, SW_BETA + LOBE_ON[0], SW_BETA + LOBE_ON[1], 0.5)
  # a ramp each end, so the roller climbs on smoothly
  ramp_a = _sector_yz(KNUCKLE_R - 0.5, LOBE_R, SW_BETA + LOBE_ON[1], SW_BETA + LOBE_ON[1] + 1.0, 0.25)
  lobe = extrude_x(lobe_cs, *LOBE)
  part = union([plate, guard, top, walls, bar, knuckle, webs, lobe])
  part = part - extrude_x(ramp_a, LOBE[0] - 1, LOBE[1] + 1) * 0  # placeholder for a later smoother ramp
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
  """Both springs' coils, carrier frame, the carrier swung off by lift (the back bolt doesn't move)."""
  c = turn(C_BOLT, lift)
  b = b_bolt(hole)
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
    coil = cyl(SPRING_OD_P / 2, 0.0, L, segments=40)
    loops = cyl_y(SPRING_OD_P / 2 - SPRING_WIRE_P / 2, -SPRING_WIRE_P / 2, SPRING_WIRE_P / 2, segments=32)
    body = coil ^ box(-20, 20, -20, 20, SPRING_OD_P / 2 + PIN_D / 2, L - SPRING_OD_P / 2 - PIN_D / 2)
    out.append(place(body + loops.translate((0, 0, PIN_D / 2 + SPRING_OD_P / 2 - SPRING_WIRE_P)) +
                     loops.translate((0, 0, L - PIN_D / 2 - SPRING_OD_P / 2 + SPRING_WIRE_P)), R, a3))
  return union(out)

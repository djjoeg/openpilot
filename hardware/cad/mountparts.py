"""
The parts that hold the motor over the steering wheel:

  motor carrier  - the motor bolts to its plate; the finger guard wraps the motor gear; it turns on the hinge block's
                   hinge, so the motor gear can be lifted off the steering wheel teeth
  lever bracket  - screws onto the top of the motor carrier at its front, so it moves with the carrier. Its two legs
                   come up through the hinge block and hold the lift lever's bolt. In front it holds the power switch
                   under the lift lever's handle, and the catch the handle clicks onto when it is pulled down.
  lift lever     - on the driver's side. Down (on): the handle points at you, rests on the lever bracket clicked onto
                   its catch, and holds the power switch pressed; the motor gear sits on the steering wheel teeth.
                   Flipped up (off): the switch lets go first, then the lever's rounded end presses on the hinge block's
                   top and lifts the lever bracket and the carrier with it, taking the motor gear off the teeth. Up, it
                   rests on a flat on that rounded end, just past its highest point, so the spring holds it up until it
                   is pulled back down.
  hinge block    - holds the carrier's hinge and the spring that presses the motor gear onto the teeth; the lever
                   bracket's legs pass through two slots in it and the lift lever presses on its top between them; the
                   arm bolts to its ears at an adjustable angle
  arm            - from the dash clamp to the hinge block; printed in several lengths, each slides +-15 mm
  dash clamp     - grips the edge of the cover over the gauges; holds the arm at an adjustable angle
  clamp pad      - swivel pad on the end of the dash clamp's screw
  setup gauge    - a 12 mm block used once while adjusting: sets the gap between the carrier and the hinge block

Frames (millimetres):
  carrier: origin at the centre of the motor's front face, +z along the shaft (towards the driver), +y away from the
           steering wheel's centre (the steering wheel's 12 o'clock direction), x across. The hinge block is drawn in
           the same frame, as it sits with the motor gear on the teeth. The lever bracket is drawn in this frame too
           (it is screwed to the carrier and moves with it).
  lever:   origin on the lift lever's bolt (the x axis), handle along +z, its top face +y. On the lever bracket it is
           turned by -alpha, alpha being how far it has been lifted from down (degrees).
  arm:     z along the arm from the dash clamp's bolt (middle of its slide) to the hinge block's bolt at z = length.
  clamp:   origin at the top front corner of the cover's edge; +y up from the cover's top face, +z towards the driver.

Angles in (y, z) planes are measured from +z towards +y. Turning a part by +a about x moves +y towards +z, the same
as Manifold.rotate((a, 0, 0)).
"""
import math

import numpy as np
from manifold3d import CrossSection, Manifold

from cadlib import box, circle_yz, clean, cyl, cyl_x, cyl_y, extrude_x, hex_prism_y, prism_x, rect_yz, sector, union
from params import (ARM_SLIDE, ARM_T, ARM_W, CLAMP_DEPTH, HOOD_EDGE_MAX, HOOD_EDGE_MIN, M3_CLEAR, M3_PILOT, M4_CLEAR,
                    M5_CLEAR, M6_CLEAR, M6_NUT_AF, M6_NUT_T, MOTOR_PLATE_T, NEMA, NEMA_BOSS, NEMA_HOLES, NEMA_LEN,
                    Z_GEAR_TEETH, Z_MOTOR_FACE)

GAP = 0.4                     # running clearance between parts that turn against each other


def rot2(deg: float) -> np.ndarray:
  """Turns (y, z) vectors by deg about x (+y towards +z)."""
  a = math.radians(deg)
  return np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])


def place_yz(m: Manifold, deg: float, y: float, z: float) -> Manifold:
  """Turns a part by deg about x, then moves its origin to (y, z)."""
  return m.rotate((deg, 0, 0)).translate((0.0, y, z))


# ***** motor carrier *****

PLATE_HALF = NEMA / 2 + 2.5           # square plate half width
PLATE_BOTTOM = -20.0                  # plate's lower edge below the motor's axis
GUARD_IN = 26.5                       # finger guard inner radius: clears the motor screws' heads
MOTOR_SCREW_CBORE = 2.6               # the motor screws' heads sit this deep in the plate's gear side
GUARD_OUT = 28.5
GUARD_LIP_IN = 25.5                   # guard's front lip: fingers can't get past it to the teeth
GUARD_WINDOW = 60.0                   # guard open +- this many degrees around straight down (where the gears meet)
GUARD_FRONT = (Z_GEAR_TEETH[1] - Z_MOTOR_FACE) + 2.0
TOP_Y = (NEMA / 2 + 0.5, NEMA / 2 + 8.5)      # block over the motor (y range): its top face is TOP_Y[1]
SIDE_X = (NEMA / 2 + 0.5, NEMA / 2 + 3.4)     # walls beside the motor's upper half (x range each side)
BLOCK_BACK = -46.0                    # the block over the motor reaches back this far (under the hinge)
WALL_BACK = -NEMA_LEN + 1.0           # the walls beside the motor stop just short of its back, clear of the board's plugs
HINGE_R = 7.5
HINGE = (TOP_Y[1] + HINGE_R + 0.5, -40.0)     # carrier hinge axis (y, z); the hinge block's knuckles clear the
                                              # carrier's top by 0.5 mm at any angle
CARRIER_KNUCKLE = 15.0                # carrier's knuckle spans x +-this
CARRIER_KNUCKLE_R = 6.5               # carrier's knuckle radius (it turns in a channel of radius HINGE_R + CHANNEL_GAP)
BLOCK_KNUCKLE = (CARRIER_KNUCKLE + GAP, CARRIER_KNUCKLE + GAP + 7.0)   # hinge block's knuckles, x range each side

# Spring that presses the motor gear onto the steering wheel teeth: Lee Spring LC 055F 08 S (stainless steel, 0.42 in
# (10.67 mm) outside, 0.31 in (7.87 mm) inside, 0.055 in (1.40 mm) wire, 1.75 in (44.45 mm) long +-0.05 in (1.27 mm),
# 20.0 lb/in (3.502 N/mm) +-10%, 0.765 in (19.43 mm) fully squashed, which takes 88.93 N; it needs an 0.438 in
# (11.13 mm) hole). Lee Spring sizes its stock springs so that squashing them fully is the most they can take, so that
# load is the spring's limit. The spring never gets that far here (the parts report gives its lengths). It is strong
# enough that the motor gear stays in the teeth without grease (see margins.py).
SPRING_OD, SPRING_ID, SPRING_FREE, SPRING_RATE, SPRING_SOLID, SPRING_MAX_N = 10.67, 7.87, 44.45, 3.502, 19.43, 88.93
SPRING_WIRE = 1.40
SPRING_FREE_TOL, SPRING_RATE_TOL = 1.27, 0.10        # Lee Spring's tolerances on its free length (mm) and rate
SPRING_PART = "Lee Spring LC 055F 08 S"
SPRING_Z = -4.0                       # spring's axis, in front of the hinge
SPRING_ARM = SPRING_Z - HINGE[1]      # its distance from the hinge axis
SPRING_SEAT_R = 5.75                  # hole through the carrier's top block (11.5 mm; the spring needs 11.13): the
SPRING_SEAT_D = TOP_Y[1] - NEMA / 2   # spring's lower end rests on the motor's top, 8.5 mm below the carrier's top
SPRING_POCKET_R = 5.9                 # pocket in the hinge block's underside for its upper end
SPRING_POCKET_D = 12.9                # deep enough for the spring's working length of 33.4 mm
POCKET_ROOF = 3.0                     # the hinge block above the pocket, where the lift lever's rounded end bears
SPRING_SHIM_T = 1.0                   # an M5 washer (10 mm across) under the spring adds this much push, if the grip
                                      # test in the car setup asks for it
SETUP_GAP = 12.0                      # carrier top to hinge block underside with the motor gear on the teeth
SPRING_LEN = SETUP_GAP + SPRING_POCKET_D + SPRING_SEAT_D   # spring's length with the motor gear on the teeth

# How far the carrier turns (degrees; positive lifts the motor gear)
LIFT_DEG = 8.0          # lift lever up: the motor gear clears the steering wheel teeth by about 5 mm
DROP_DEG = 3.0          # with the steering wheel turned past the teeth, the carrier drops this much, until the lift
                        # lever's rounded end meets the hinge block (the motor gear's roller stays above the ends of the
                        # teeth's rolling band)


def spring_force(theta_deg: float) -> float:
  """Spring force (N) with the carrier turned up by theta."""
  return SPRING_RATE * (SPRING_FREE - SPRING_LEN + SPRING_ARM * math.sin(math.radians(theta_deg)))


def spring_torque(theta_deg: float) -> float:
  """Spring's turning force (N mm) on the carrier about the hinge."""
  return spring_force(theta_deg) * SPRING_ARM * math.cos(math.radians(theta_deg))


# ***** hinge block *****

HB_BOTTOM = TOP_Y[1] + SETUP_GAP      # hinge block underside
HB_T = SPRING_POCKET_D + POCKET_ROOF   # 15.9 mm thick
HB_TOP = HB_BOTTOM + HB_T
HB_FRONT = 4.0
HB_HALF = BLOCK_KNUCKLE[1]
HB_BODY_BACK = HINGE[1] - HINGE_R - 3.0          # back end of the main body (just behind the hinge)
CHANNEL_GAP = 0.6                     # the carrier's knuckle turns in a channel this much bigger than it
KNUCKLE_CHIN_Y = HINGE[0] - 5.35      # the hinge block's knuckles have 45 degree slopes in front from here up

# Angle joint between the hinge block and the arm. The arm's bolt sits behind the lift lever, so the lever's rounded
# end clears the arm's end with the lever down.
EAR_X = (ARM_W / 2 + GAP, ARM_W / 2 + GAP + 6.0)   # ears either side of the arm's end
EAR_HINGE_ROOM = 5.6         # the ears are cut back round the hinge bolt's axis: room for its head, nut or a washer
EAR_CUT_Z, EAR_CUT_TOP = -4.0, HB_TOP + 21.35   # the ears' front corner above the block is cut away (45 degrees from here up to
                                      # this height) so the lift lever's bolt goes in from the side
PIVOT = (HB_TOP + ARM_T / 2 + 1.5, -29.0)        # the arm's bolt (y, z)
LOCK_R = 22.0                                    # the arm's locking bolt, this far along the arm from its bolt
LOCK_RANGE = 37.5                                # the joint adjusts +- this many degrees ...
ARM_NOMINAL = 62.5                               # ... around the arm at this angle to the steering column


def arm_direction(a_deg: float) -> np.ndarray:
  """Unit (y, z) vector from the hinge block's arm bolt along the arm towards the dash clamp, for the arm at a_deg
  to the steering column."""
  return np.array([math.sin(math.radians(a_deg)), -math.cos(math.radians(a_deg))])


# ***** lever bracket and lift lever *****

LEVER_PIVOT = (HB_TOP + 9.15, 0.0)    # (y, z): the lift lever's bolt, held by the lever bracket's legs
LEVER_HALF = 7.1                      # the lever's rounded end spans x +- this, between the bracket's legs
BR_PLATE_T = 4.0
BR_PLATE_Y = (TOP_Y[1], TOP_Y[1] + BR_PLATE_T)   # the bracket's base plate lies on the carrier's top
BR_BACK = -16.0                       # the base plate's back edge (under the hinge block)
BR_LEG_X = (LEVER_HALF + GAP, LEVER_HALF + GAP + 5.0)    # legs, x range each side
BR_LEG_Z = (-5.0, 5.0)
BR_LEG_TOP = LEVER_PIVOT[0] + 6.0
BR_SCREWS = ((-6.0, -13.0), (6.0, -13.0))         # (x, z): M3 x 10 screws down into the carrier's top
BR_SCREW_DEPTH = 7.0                  # their holes in the carrier (the motor is 8.5 mm below the carrier's top)
# slots in the hinge block for the legs: room for the legs to move as the carrier turns (up to LIFT_DEG and a little
# more, and down DROP_DEG)
LEG_SLOT_X = (BR_LEG_X[0] - GAP, BR_LEG_X[1] + GAP)
_LEG_REACH = HB_TOP + 1.0 - HINGE[0]   # the highest point of a leg inside the hinge block, above the hinge axis
LEG_SLOT_Z = (BR_LEG_Z[0] - _LEG_REACH * math.sin(math.radians(10.0)) - 0.35,   # lifted 10 degrees (the most is 9)
              BR_LEG_Z[1] + _LEG_REACH * math.sin(math.radians(4.0)) + 0.55)    # dropped 4 degrees (the most is 3)

# The lift lever's rounded end (lever frame). Angles are degrees from straight down towards the back; a direction b
# degrees from down points straight down once the lever is lifted b degrees.
NOSE_R = 4.0            # the nose that pushes the lever's bolt up is this round
CAM_PEAK_AT = 65.0      # the nose is under the bolt with the lever lifted about this far ...
CAM_PEAK_LIFT = 9.0     # ... and then holds the carrier lifted this many degrees
A_OFF = 77.0            # lever up: it rests on the flat here, with the carrier at LIFT_DEG
HEEL_W, HEEL_R = 4.5, 2.0   # the flat runs this far past the bolt to a rounded heel, which stops the lever going further

# Handle
HANDLE_T = 8.0
HANDLE_LEN = 47.0       # bolt to the end of the handle (longer than the first 39 mm: the stronger spring needs more lift)
HANDLE_WIDE_FROM = 8.0  # past the bracket's legs the handle widens to HANDLE_X, so it covers the switch's roller
HANDLE_X = (-13.0, LEVER_HALF)
REST_GAP = 0.05         # the handle's underside to the switch cage's tops, lever down

# Power switch: subminiature roller-lever microswitch, 19.8 x 6.4 x 10.2 mm with two holes 9.5 mm apart, such as the
# Omron SS-5GL2 (roller works at 14.5 +-0.8 mm from the holes' line, free at up to 19.3 mm; up to 1.2 mm between
# switching on and letting go). It lies across under the handle, roller up; the handle presses it when the lever is down.
SW_LEN, SW_THICK, SW_H = 19.8, 6.4, 10.2
SW_PITCH = 9.5
SW_OP, SW_OP_TOL, SW_FP, SW_MD = 14.5, 0.8, 19.3, 1.2
SW_PRESS = 0.6                        # the handle presses the roller this far past where it clicks
SW_D = 16.0                           # the switch's middle, this far in front of the lever's bolt
SW_X = -3.5                           # and this far across
SW_HOLES = LEVER_PIVOT[0] - HANDLE_T / 2 - (SW_OP - SW_PRESS)   # the holes' line (y)
SW_SLOT = 2.0                         # the switch's screws slide +- this to set where it clicks
CAGE_BACK = (9.5, 12.5)               # the switch's walls (z ranges) ...
CAGE_FRONT = (19.5, 23.0)
CAGE_X = (-14.5, LEVER_HALF + 0.5)    # ... and their x range
REST_Y = LEVER_PIVOT[0] - HANDLE_T / 2 - REST_GAP
M2_CLEAR, M2_NUT_AF, M2_NUT_T = 2.4, 4.3, 1.8

# The click: a thin springy tab under the handle's end (lever frame) hooks under a small ridge on the catch, a rib on
# the front of the switch walls whose face is a circle round the lever's bolt. Lifting, the tab bends 0.5 mm out to
# pass the ridge; pulling down, it bends again and snaps under it. Lever up, the tab is clear of everything, so it
# doesn't stay bent (printed plastic slowly gives way under a constant load, more so in a hot car).
CATCH_R = 30.0                        # the catch's face, this far from the lever's bolt
CATCH_X = (3.5, LEVER_HALF + 0.5)
RIDGE_H = 0.75                        # the ridge stands this far out from the catch's face
FINGER_X = (4.0, LEVER_HALF)          # the tab's width
FINGER_GAP = 1.0                      # the tab's inside face to the catch's face (it clears the ridge by 0.25)
FINGER_T = 1.75
FINGER_TIP = 31.9                     # the tab ends this many degrees below the handle's line
BUMP_H = 0.75                         # the tab's hook stands this far in from its inside face (it clears
                                      # the catch's face by 0.25)
CLICK_CLEAR = 0.2                     # lever down: room between the hook and the ridge
RAMP_ON, RAMP_OFF = 30.0, 45.0        # slopes the hook meets the ridge at, pulling down and lifting
FINGER_E = 1810.0                     # PETG's stiffness along its layers, N/mm^2 (Bambu Lab PETG HF data sheet: 1810
                                      # MPa in X-Y; the tab is printed flat, so it bends along its layers)
RUB = 0.35                            # rubbing (friction) between dry printed PETG parts, an estimate


# ----- lift lever's rounded end -----

def pad_plane(theta_deg: float):
  """The hinge block's top, where the lift lever presses, in the carrier frame with the carrier lifted theta degrees:
  a point on it and its upward normal, (y, z)."""
  hy, hz = HINGE
  r = rot2(theta_deg)
  c = r @ np.array([HB_TOP - hy, 0.0 - hz]) + np.array([hy, hz])
  return c, r @ np.array([1.0, 0.0])


def pivot_height(theta_deg: float) -> float:
  """How far the lift lever's bolt is above the hinge block's top with the carrier lifted theta degrees."""
  c, n = pad_plane(theta_deg)
  return float((np.array(LEVER_PIVOT) - c) @ n)


def down_dir(b_deg: float) -> np.ndarray:
  """Lever-frame unit vector b degrees from straight down towards the back."""
  return np.array([-math.cos(math.radians(b_deg)), -math.sin(math.radians(b_deg))])


CAM_DWELL_R = pivot_height(-DROP_DEG)    # the round part under the bolt: it meets the hinge block with the carrier
                                         # dropped DROP_DEG, and clears it by DROP_GAP with the motor gear on the teeth
DROP_GAP = pivot_height(0.0) - CAM_DWELL_R


def cam_outline(segments: int = 360) -> CrossSection:
  """The lift lever's rounded end (lever frame): a circle round the bolt, a nose that pushes the bolt up as the lever
  turns, and the flat it rests on when up, ending in a heel."""
  e = pivot_height(CAM_PEAK_LIFT) - NOSE_R
  nose_c = e * down_dir(CAM_PEAK_AT + CAM_PEAK_LIFT)
  f = down_dir(A_OFF + LIFT_DEG)                 # the flat faces the hinge block's top when up
  t = down_dir(A_OFF + LIFT_DEG + 90.0)          # along the flat, away from the nose
  h_up = pivot_height(LIFT_DEG)
  heel_c = (h_up - HEEL_R) * f + (HEEL_W + HEEL_R) * t
  hull = CrossSection.batch_hull([CrossSection.circle(CAM_DWELL_R, segments),
                                  CrossSection.circle(NOSE_R, segments).translate((float(nose_c[0]), float(nose_c[1]))),
                                  CrossSection.circle(HEEL_R, segments).translate((float(heel_c[0]), float(heel_c[1])))])
  ang = math.degrees(math.atan2(f[1], f[0]))
  beyond = CrossSection.square((200.0, 400.0)).translate((h_up, -200.0)).rotate(ang)
  return hull - beyond


def cam_points() -> np.ndarray:
  return np.array([p for poly in cam_outline(720).to_polygons() for p in poly])


def lever_to_carrier(points_yz: np.ndarray, alpha: float) -> np.ndarray:
  """Lever-frame (y, z) points to the carrier frame with the lever lifted alpha degrees."""
  return np.asarray(points_yz) @ rot2(-alpha).T + np.array(LEVER_PIVOT)


def cam_lift(alpha: float, cam_pts=None) -> float:
  """The carrier lift (degrees) the lift lever's rounded end holds at lever angle alpha, -DROP_DEG or more."""
  pts = lever_to_carrier(cam_pts if cam_pts is not None else cam_points(), alpha)

  def clear(th):
    c, n = pad_plane(th)
    return float(((pts - c) @ n).min())

  lo, hi = -DROP_DEG - 2.0, LIFT_DEG + 12.0
  if clear(lo) >= 0:
    return lo
  for _ in range(50):
    mid = (lo + hi) / 2
    if clear(mid) >= 0:
      hi = mid
    else:
      lo = mid
  return hi


def cam_contact(alpha: float, theta: float, cam_pts=None) -> np.ndarray:
  """Where the rounded end touches the hinge block's top (carrier frame) at lever angle alpha, carrier lift theta."""
  pts = lever_to_carrier(cam_pts if cam_pts is not None else cam_points(), alpha)
  c, n = pad_plane(theta)
  return pts[int(np.argmin((pts - c) @ n))]


def lever_lift_table(step: float = 1.0, end: float = A_OFF + 6.0):
  """(lever angle, carrier lift, push in N at the end of the handle from the spring alone, the same with rubbing
  added) from down to past up. The carrier never sits lower than the motor gear on the teeth (lift 0). A negative
  push means the lever moves on by itself and must be held back."""
  pts = cam_points()
  rows = []
  prev = None
  for a in np.arange(0.0, end + 1e-9, step):
    th = max(0.0, cam_lift(a, pts))
    force = rub = 0.0
    if prev is not None and (th > 0.0 or prev[1] > 0.0):
      dth = math.radians(th - prev[1])
      dal = math.radians(a - prev[0])
      tq = spring_torque((th + prev[1]) / 2)
      force = tq * dth / dal / HANDLE_LEN
      # rubbing at the rounded end: the hinge block pushes on it with N (the spring's turning force over how far the
      # touching point is from the hinge, along the hinge block's top); rubbing opposes the turn by RUB * N times the
      # bolt's height above the hinge block
      p = cam_contact(a, th, pts)
      c, n = pad_plane(th)
      along = rot2(th) @ np.array([0.0, 1.0])
      arm = abs(float((p - np.array(HINGE)) @ along))
      normal = tq / max(arm, 1.0)
      rub = RUB * normal * pivot_height(th) / HANDLE_LEN
    rows.append((float(a), th, force, rub))
    prev = (a, th)
  return rows


# ----- lift lever -----

def handle_outline(z0: float, z1: float) -> CrossSection:
  ht = HANDLE_T / 2
  cs = rect_yz(-ht, ht, z0, min(z1, HANDLE_LEN - ht))
  if z1 >= HANDLE_LEN - ht:
    cs = cs + circle_yz(ht, 0.0, HANDLE_LEN - ht, 48)
  return cs


def knob_outline() -> CrossSection:
  """A raised grip on top of the handle's end."""
  ht = HANDLE_T / 2
  return circle_yz(5.0, 2.0, HANDLE_LEN - 6.0, 48) ^ rect_yz(-ht, 20.0, 0.0, HANDLE_LEN + 5)


def polar_yz(r: float, below_deg: float) -> tuple:
  """(y, z) of the point r from the lever's bolt, below_deg below the handle's line (lever frame), or below the
  bolt's level in the carrier frame with the lever down."""
  a = math.radians(below_deg)
  return (-r * math.sin(a), r * math.cos(a))


def finger_angles():
  """(hook's top angle, ridge's peak angle) in degrees below the handle's line, lever down."""
  r_in = CATCH_R + FINGER_GAP
  bump_peak = FINGER_TIP - math.degrees(BUMP_H / math.tan(math.radians(RAMP_ON)) / r_in)
  # the hook's lifting slope and the ridge's are parallel; CLICK_CLEAR between them where they overlap
  r_mid = CATCH_R + RIDGE_H - (RIDGE_H + BUMP_H - FINGER_GAP) / 2
  ridge_peak = bump_peak - math.degrees((RIDGE_H + BUMP_H - FINGER_GAP + CLICK_CLEAR) / r_mid)
  return bump_peak, ridge_peak


def finger_outline() -> CrossSection:
  """The springy tab under the handle's end, with its hook at the tip (lever frame)."""
  r_in = CATCH_R + FINGER_GAP
  r_out = r_in + FINGER_T
  root = math.degrees(math.asin((HANDLE_T / 2 - 1.0) / r_out))
  bump_peak, _ = finger_angles()
  hook_top = bump_peak - math.degrees(BUMP_H / math.tan(math.radians(RAMP_OFF)) / r_in)
  pts = [polar_yz(r_out, a) for a in np.linspace(root, FINGER_TIP, 40)]
  pts += [polar_yz(r_in, FINGER_TIP), polar_yz(r_in - BUMP_H, bump_peak), polar_yz(r_in, hook_top)]
  pts += [polar_yz(r_in, a) for a in np.linspace(hook_top, root, 30)]
  cs = CrossSection([pts])
  return cs if cs.area() > 0 else CrossSection([pts[::-1]])


def lift_lever(with_finger: bool = True) -> Manifold:
  """Lever frame: bolt on the x axis, handle along +z. Prints on its side, the +x face on the bed: every piece starts
  from that face."""
  hole = circle_yz(M4_CLEAR / 2, segments=48)
  end = extrude_x((cam_outline() + handle_outline(0.0, HANDLE_WIDE_FROM + 0.5)) - hole, -LEVER_HALF, LEVER_HALF)
  wide = extrude_x(handle_outline(HANDLE_WIDE_FROM, HANDLE_LEN) + knob_outline(), HANDLE_X[0], HANDLE_X[1])
  parts = [end, wide]
  if with_finger:
    parts.append(extrude_x(finger_outline(), FINGER_X[0], FINGER_X[1]))
  return clean(union(parts))


def lever_tab() -> Manifold:
  """Just the click's springy tab (lever frame), for checking the click."""
  return extrude_x(finger_outline(), FINGER_X[0], FINGER_X[1])


def lever_in_carrier(lever: Manifold, alpha: float = 0.0) -> Manifold:
  """The lever where it sits on the lever bracket (carrier frame), lifted alpha degrees from down."""
  return place_yz(lever, -alpha, *LEVER_PIVOT)


def finger_force() -> dict:
  """Estimates for the click: the tab bends RIDGE_H + BUMP_H - FINGER_GAP to pass the ridge."""
  r_mid = CATCH_R + FINGER_GAP + FINGER_T / 2
  root = math.degrees(math.asin((HANDLE_T / 2 - 1.0) / (CATCH_R + FINGER_GAP + FINGER_T)))
  length = math.radians(FINGER_TIP - root) * r_mid
  width = FINGER_X[1] - FINGER_X[0]
  stiffness = 3 * FINGER_E * (width * FINGER_T ** 3 / 12) / length ** 3
  bend = RIDGE_H + BUMP_H - FINGER_GAP
  push = stiffness * bend
  rub = math.degrees(math.atan(RUB))
  to_lift = push * math.tan(math.radians(RAMP_OFF + rub)) * r_mid / HANDLE_LEN
  to_click = push * math.tan(math.radians(RAMP_ON + rub)) * r_mid / HANDLE_LEN
  strain = 1.5 * FINGER_T * bend / length ** 2
  return {"bend_mm": round(bend, 2), "tab_force_N": round(push, 2), "to_unclick_at_handle_end_N": round(to_lift, 1),
          "to_click_at_handle_end_N": round(to_click, 1), "tab_strain_percent": round(100 * strain, 2)}


# ----- lever bracket -----

def switch_body() -> Manifold:
  """Room the power switch takes (body, and its lever and roller up to the handle), carrier frame."""
  return box(SW_X - SW_LEN / 2, SW_X + SW_LEN / 2, SW_HOLES - 6.0, REST_Y - 0.05,
             SW_D - SW_THICK / 2, SW_D + SW_THICK / 2)


def catch_outline() -> CrossSection:
  """The catch's side outline (y, z) in the carrier frame: from the switch walls' front out to a face round the lever's
  bolt, with the ridge the lever's tab clicks under."""
  vy, vz = LEVER_PIVOT
  top = math.degrees(math.asin((HANDLE_T / 2 + REST_GAP) / CATCH_R))
  bottom = math.degrees(math.acos((CAGE_FRONT[1] - 0.5 - vz) / CATCH_R))
  _, ridge = finger_angles()
  up = math.degrees(RIDGE_H / math.tan(math.radians(RAMP_ON)) / CATCH_R)
  down = math.degrees(RIDGE_H / math.tan(math.radians(RAMP_OFF)) / CATCH_R)

  def at(r, a):
    y, z = polar_yz(r, a)
    return (y + vy, z + vz)

  pts = [at(CATCH_R, a) for a in np.linspace(top, ridge - up, 20)]
  pts += [at(CATCH_R + RIDGE_H, ridge)]
  pts += [at(CATCH_R, a) for a in np.linspace(ridge + down, bottom, 20)]
  pts += [(pts[-1][0], CAGE_FRONT[1] - 0.5), (pts[0][0], CAGE_FRONT[1] - 0.5)]
  cs = CrossSection([pts])
  return cs if cs.area() > 0 else CrossSection([pts[::-1]])


def lever_bracket() -> Manifold:
  """Carrier frame. Prints base plate down."""
  vy, vz = LEVER_PIVOT
  y0, y1 = BR_PLATE_Y
  lx0, lx1 = BR_LEG_X
  plate = box(-lx1, lx1, y0, y1, BR_BACK, CAGE_FRONT[1]) + box(CAGE_X[0], -lx1 + 0.01, y0, y1, CAGE_BACK[0] - 2.0, CAGE_FRONT[1])
  # legs: rounded tops round the lever's bolt
  leg_cs = CrossSection.batch_hull([rect_yz(y1 - 0.01, vy, BR_LEG_Z[0], BR_LEG_Z[1]),
                                    circle_yz((BR_LEG_Z[1] - BR_LEG_Z[0]) / 2, vy, vz, 48),
                                    rect_yz(y1 - 0.01, BR_LEG_TOP - 3.0, BR_LEG_Z[0], BR_LEG_Z[1])])
  legs = [extrude_x(leg_cs, lx0, lx1), extrude_x(leg_cs, -lx1, -lx0)]
  # the switch's walls, their tops the rest for the handle, and the catch in front
  walls = [box(CAGE_X[0], CAGE_X[1], y1 - 0.01, REST_Y, CAGE_BACK[0], CAGE_BACK[1]),
           box(CAGE_X[0], CAGE_X[1], y1 - 0.01, REST_Y, CAGE_FRONT[0], CAGE_FRONT[1])]
  catch = extrude_x(catch_outline(), CATCH_X[0], CATCH_X[1])
  part = union([plate] + legs + walls + [catch])
  # holes: the spring passes through to its seat in the carrier; two screws into the carrier; the lever's bolt
  part = part - cyl_y(SPRING_OD / 2 + 1.0, y0 - 1, y1 + 1, z=SPRING_Z, segments=64)
  for x, z in BR_SCREWS:
    part = part - cyl_y(M3_CLEAR / 2, y0 - 1, y1 + 1, x=x, z=z, segments=24)
  part = part - cyl_x(M4_CLEAR / 2, -lx1 - 1, lx1 + 1, y=vy, z=vz, segments=32)
  # the switch's two M2 screws: slots through both walls (the switch slides +-SW_SLOT to set where it clicks), heads
  # on the front, nuts held in slots in the back wall's back face
  for dx in (-SW_PITCH / 2, SW_PITCH / 2):
    x = SW_X + dx
    hole = Manifold.batch_hull([cyl(M2_CLEAR / 2, CAGE_BACK[0] - 1, CAGE_FRONT[1] + 1, x=x, y=SW_HOLES + s, segments=20)
                                for s in (-SW_SLOT, SW_SLOT)])
    nut = Manifold.batch_hull([hex_prism_z_at(M2_NUT_AF, CAGE_BACK[0] - 1.0, CAGE_BACK[0] + M2_NUT_T, x, SW_HOLES + s)
                               for s in (-SW_SLOT, SW_SLOT)])
    part = part - hole - nut
  return clean(part)


def hex_prism_z_at(af: float, z0: float, z1: float, x: float, y: float) -> Manifold:
  r = af / math.sqrt(3)
  pts = [(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i))) for i in range(6)]
  return CrossSection([pts]).extrude(z1 - z0).translate((0, 0, z0))


# ----- hinge block -----

def hinge_block(arm_nominal: float = ARM_NOMINAL, ears: bool = True) -> Manifold:
  """arm_nominal: the arm's angle to the steering column in the middle of the joint's range (ARM_NOMINAL for the dash
  mount; the column mount's arm runs closer to the column, so its hinge block has the slot centred lower). ears:
  False leaves off the ears on top (the back-teeth mount's hinge block carries its arm's joint underneath instead)."""
  hy, hz = HINGE
  py, pz = PIVOT
  body = box(-HB_HALF, HB_HALF, HB_BOTTOM, HB_TOP, HB_BODY_BACK, HB_FRONT)
  kn = []
  for sgn in (-1, 1):
    x0, x1 = (BLOCK_KNUCKLE[0], BLOCK_KNUCKLE[1]) if sgn > 0 else (-BLOCK_KNUCKLE[1], -BLOCK_KNUCKLE[0])
    chin = prism_x([(KNUCKLE_CHIN_Y, hz + HINGE_R - 0.01), (HB_BOTTOM + 0.5, hz + HINGE_R - 0.01),
                    (HB_BOTTOM + 0.5, hz + HINGE_R + HB_BOTTOM + 0.5 - KNUCKLE_CHIN_Y)], x0, x1)
    kn.append(cyl_x(HINGE_R, x0, x1, y=hy, z=hz) + box(x0, x1, hy, HB_BOTTOM + 0.5, hz - HINGE_R, hz + HINGE_R) + chin)

  # ears either side of the arm's end: the arm's bolt, and a curved slot for its locking bolt
  slot_pts = [np.array([py, pz]) + LOCK_R * arm_direction(a)
              for a in np.linspace(arm_nominal - LOCK_RANGE, arm_nominal + LOCK_RANGE, 15)]
  ear_cs = CrossSection.batch_hull([circle_yz(10.0, py, pz), rect_yz(HB_BOTTOM, py + 10.0, pz - 14.0, HB_FRONT)] +
                                   [circle_yz(7.0, float(q[0]), float(q[1])) for q in slot_pts])
  ears = [extrude_x(ear_cs, EAR_X[0], EAR_X[1]), extrude_x(ear_cs, -EAR_X[1], -EAR_X[0])] if ears else []
  part = union([body] + kn + ears)
  # room in the ears for bolts that go in from the sides: the hinge bolt's head and nut (the ears reach out past the
  # knuckles), and the lift lever's bolt, which goes in through the ears' front corner above the block (cut back at
  # 45 degrees so the ears still print without supports there), with room for a socket on its nut
  for sgn in (-1, 1):
    x0, x1 = (BLOCK_KNUCKLE[1], 60.0) if sgn > 0 else (-60.0, -BLOCK_KNUCKLE[1])
    part = part - cyl_x(EAR_HINGE_ROOM, x0, x1, y=hy, z=hz, segments=48)
    ex0, ex1 = (EAR_X[0] - 0.01, EAR_X[1] + 1.0) if sgn > 0 else (-EAR_X[1] - 1.0, -EAR_X[0] + 0.01)
    y0, y1 = HB_TOP + 0.5, EAR_CUT_TOP
    part = part - prism_x([(y0, HB_FRONT + 1.0), (y0, EAR_CUT_Z), (y1, EAR_CUT_Z - (y1 - y0)), (y1, HB_FRONT + 1.0)], ex0, ex1)

  # the carrier's knuckle turns in a channel in the underside
  rc = HINGE_R + CHANNEL_GAP
  part = part - (cyl_x(rc, -CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, y=hy, z=hz, segments=96) +
                 box(-CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, hy - 20.0, hy, hz - rc, hz + rc))
  part = part - cyl_x(2.75, -60, 60, y=hy, z=hz, segments=32)                    # M5 hinge bolt
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=py, z=pz, segments=32)            # the arm's bolt
  part = part - union([cyl_x(M5_CLEAR / 2, -60, 60, y=float(q[0]), z=float(q[1]), segments=20)
                       for q in [np.array([py, pz]) + LOCK_R * arm_direction(a)
                                 for a in np.linspace(arm_nominal - LOCK_RANGE, arm_nominal + LOCK_RANGE, 71)]])
  # slots for the lever bracket's legs (open at the front); the lift lever presses on the top between them
  for sgn in (-1, 1):
    x0, x1 = LEG_SLOT_X if sgn > 0 else (-LEG_SLOT_X[1], -LEG_SLOT_X[0])
    part = part - box(x0, x1, HB_BOTTOM - 1.0, HB_TOP + 1.0, LEG_SLOT_Z[0], LEG_SLOT_Z[1])
  part = part - cyl_y(SPRING_POCKET_R, HB_BOTTOM - 1.0, HB_BOTTOM + SPRING_POCKET_D, z=SPRING_Z, segments=64)
  return clean(part)


# ***** arm *****

ARM_LOCK_R = 24.0          # the dash clamp's locking bolt, this far along the arm from the clamp's pivot bolt


def arm(length: float) -> Manifold:
  """Arm frame: z along the arm from the dash clamp's pivot bolt (middle of the slide) to the hinge block's bolt at
  z = length. The bolts run across the arm (along x). One slot at the dash clamp end takes both of the clamp's bolts,
  so the arm slides +-ARM_SLIDE before they are tightened."""
  ht, w = ARM_T / 2, ARM_W / 2
  z_top = -ARM_SLIDE - 12.0
  bar = box(-w, w, -ht, ht, z_top, length) + cyl_x(ht, -w, w, z=length, segments=64) + cyl_x(ht, -w, w, z=z_top, segments=64)
  slot = Manifold.batch_hull([cyl_x(M5_CLEAR / 2, -w - 1, w + 1, z=-ARM_SLIDE, segments=32),
                              cyl_x(M5_CLEAR / 2, -w - 1, w + 1, z=ARM_LOCK_R + ARM_SLIDE, segments=32)])
  holes = cyl_x(M5_CLEAR / 2, -w - 1, w + 1, z=length, segments=32) + \
    cyl_x(M5_CLEAR / 2, -w - 1, w + 1, z=length - LOCK_R, segments=32)
  if length - LOCK_R - M5_CLEAR / 2 < ARM_LOCK_R + ARM_SLIDE + M5_CLEAR / 2 + 3.0:
    raise ValueError(f"arm {length} mm is too short")
  return clean(bar - slot - holes)


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
ARM_PIVOT = (PLATE_T + ARM_T / 2 + 3.0, LIP_GAP + LIP_T + 12.0)   # (y, z) clamp frame
ARM_ANGLES = (0.0, 80.0)       # the arm can point from level to 80 degrees below level


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
  # the arm turns between the side plates
  part = part - (cyl_x(ARM_T / 2 + 1.0, -SIDE_PLATE_X[0], SIDE_PLATE_X[0], y=py, z=pz) +
                 box(-SIDE_PLATE_X[0], SIDE_PLATE_X[0], JAW_Y0 + JAW_T + 0.5, py + 40, zf + 0.01, pz + 60))
  return clean(part)


# ***** small parts *****

def clamp_pad() -> Manifold:
  """Swivel pad for the end of the M6 clamp screw. Stick rubber on top."""
  return cyl(11.0, 0, 5.0, segments=96) - cyl(3.4, -1, 3.0, segments=32)


GAUGE_X = (BR_LEG_X[1] + 1.0, HB_HALF - 0.5)      # the setup gauge sits here, beside the lever bracket ...
GAUGE_Z = (-19.0, 3.0)                             # ... between the carrier's knuckle and the hinge block's front


def setup_gauge() -> Manifold:
  """A block SETUP_GAP thick (less 0.2) that slides in from the side between the carrier's top and the hinge block,
  beside the lever bracket, with a grip that sticks out past the hinge block (carrier frame, right-hand side)."""
  y0, y1 = TOP_Y[1] + 0.1, HB_BOTTOM - 0.1
  block = box(GAUGE_X[0], GAUGE_X[1], y0, y1, GAUGE_Z[0], GAUGE_Z[1])
  grip = box(GAUGE_X[1] - 0.01, GAUGE_X[1] + 14.0, y0, y1, GAUGE_Z[0] + 4.0, GAUGE_Z[1] - 4.0)
  return clean(block + grip)


# ***** motor carrier *****

def motor_carrier(guard_window: float = GUARD_WINDOW) -> Manifold:
  """guard_window: the finger guard is open this many degrees either side of straight down, where the gears meet
  (GUARD_WINDOW for the dash mount; the column mount's carrier opens a little wider, so the guard's rounded ends
  clear the ring's rolling band when the carrier drops at the ring's ends)."""
  t = MOTOR_PLATE_T
  outline = CrossSection.square((2 * PLATE_HALF, 2 * PLATE_HALF), center=True) + CrossSection.circle(GUARD_OUT, 180)
  # nothing below PLATE_BOTTOM: stays clear of the steering wheel when the carrier drops (wheel turned far)
  outline = outline ^ CrossSection.square((200, 200)).translate((-100, PLATE_BOTTOM))
  plate = outline.extrude(t)

  # finger guard: a shell around the motor gear, open below where it meets the steering wheel teeth
  shell = cyl(GUARD_OUT, t, GUARD_FRONT, segments=180) - cyl(GUARD_IN, t - 1, GUARD_FRONT + 1, segments=180)
  lip = cyl(GUARD_OUT, GUARD_FRONT - 1.6, GUARD_FRONT, segments=180) - cyl(GUARD_LIP_IN, GUARD_FRONT - 3, GUARD_FRONT + 1, segments=180)
  window = sector(GUARD_OUT + 6, 270.0 - guard_window, 270.0 + guard_window).extrude(GUARD_FRONT + 4).translate((0, 0, t - 2))
  guard = (shell + lip) - window
  for sgn in (-1, 1):   # rounded lower ends: a hand that meets the guard pushes it up instead of catching an edge
    a = math.radians(270.0 + sgn * guard_window)
    rm = (GUARD_IN + GUARD_OUT) / 2
    guard = guard + cyl((GUARD_OUT - GUARD_IN) / 2 + 0.6, t, GUARD_FRONT, rm * math.cos(a), rm * math.sin(a), 24)

  # block over the motor, walls beside its upper half, the hinge knuckle. The knuckle has 45 degree slopes in front
  # so the carrier prints finger guard down
  block = box(-SIDE_X[1], SIDE_X[1], TOP_Y[0], TOP_Y[1], BLOCK_BACK, t)
  walls = union([box(SIDE_X[0], SIDE_X[1], 0.0, TOP_Y[1], WALL_BACK, t), box(-SIDE_X[1], -SIDE_X[0], 0.0, TOP_Y[1], WALL_BACK, t)])
  hy, hz = HINGE
  kr = CARRIER_KNUCKLE_R
  knuckle = cyl_x(kr, -CARRIER_KNUCKLE, CARRIER_KNUCKLE, y=hy, z=hz) + \
    box(-CARRIER_KNUCKLE, CARRIER_KNUCKLE, TOP_Y[1] - 1.0, hy, hz - kr, hz + kr)
  # a pointed front (it stays below the hinge block at any lift) and a slope down to the carrier's top, so the
  # carrier prints finger guard down without supports here
  tip = (hy, hz + kr * math.sqrt(2.0))
  side = (hy + kr / math.sqrt(2.0), hz + kr / math.sqrt(2.0))
  knuckle = knuckle + prism_x([(hy - kr / math.sqrt(2.0), side[1]), side, tip], -CARRIER_KNUCKLE, CARRIER_KNUCKLE)
  rise = tip[0] - TOP_Y[1] + 0.5
  knuckle = knuckle + prism_x([(TOP_Y[1] - 0.5, hz + kr - 0.01), (tip[0], hz + kr - 0.01), tip,
                               (TOP_Y[1] - 0.5, tip[1] + 1.2 * rise)], -CARRIER_KNUCKLE, CARRIER_KNUCKLE)
  part = plate + guard + block + walls + knuckle
  part = part - cyl_y(SPRING_SEAT_R, TOP_Y[1] - SPRING_SEAT_D, TOP_Y[1] + 1.0, z=SPRING_Z, segments=64)
  part = part - cyl_x(2.75, -40, 40, y=hy, z=hz, segments=32)        # M5 hinge bolt
  for x, z in BR_SCREWS:                                               # the lever bracket's screws
    part = part - cyl_y(M3_PILOT / 2, TOP_Y[1] - BR_SCREW_DEPTH, TOP_Y[1] + 1.0, x=x, z=z, segments=24)
  # motor screws (heads recessed on the gear side) and the motor's boss
  part = part - cyl(NEMA_BOSS / 2 + 0.4, -3, t + 1, segments=128)
  for sx in (-1, 1):
    for sy in (-1, 1):
      x, y = sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2
      part = part - cyl(M3_CLEAR / 2, -1, t + 1, x, y, 32) - cyl(3.4, t - MOTOR_SCREW_CBORE, t + 1, x, y, 32)
  # the motor body stays clear
  part = part - box(-NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA_LEN - 20, 0.0)
  return clean(part)


# ***** screws and bolts (bought parts), for the fit checks and the bolt lengths *****

M3_BUTTON = (5.7, 1.65)      # ISO 7380 M3 button head: across, tall (the motor screws)
M3_SOCKET = (5.5, 3.0)       # ISO 4762 M3 socket head
M5_WASHER_T, M5_NYLOC_T = 1.0, 5.2
M4_WASHER_T, M4_NYLOC_T, M4_NYLOC_AF = 0.8, 5.0, 7.0
MOTOR_HOLE_DEPTH = 4.5       # the motor's front M3 holes: usual NEMA 17 depth, not confirmed for this motor


def motor_screw_heads(head=M3_BUTTON) -> Manifold:
  """The four motor screws' heads in their counterbores on the plate's gear side (carrier frame)."""
  dk, k = head
  z0 = MOTOR_PLATE_T - MOTOR_SCREW_CBORE
  return union([cyl(dk / 2, z0, z0 + k, sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2, 48) for sx in (-1, 1) for sy in (-1, 1)])


def switch_screws(length: float = 16.0, dy: float = 0.0) -> Manifold:
  """The switch's two M2 screws: heads on the front wall's face, tips out past the rear wall (carrier frame). dy: where
  they sit in their slots (the switch slides +-SW_SLOT to set where it clicks)."""
  parts = []
  for sx in (-1, 1):
    x = SW_X + sx * SW_PITCH / 2
    parts.append(cyl(1.0, CAGE_FRONT[1] - length, CAGE_FRONT[1], x, SW_HOLES + dy, 24) +
                 cyl(1.9, CAGE_FRONT[1], CAGE_FRONT[1] + 2.0, x, SW_HOLES + dy, 24))
  return union(parts)


def lever_bolt(length: float = 35.0) -> Manifold:
  """The lift lever's M4 bolt through the bracket's legs, a washer each side and the lock nut (carrier frame)."""
  y, z = LEVER_PIVOT
  half = BR_LEG_X[1]
  w = M4_WASHER_T
  x_head = -half - w
  return (cyl_x(2.0, x_head, x_head + length, y=y, z=z, segments=24) +
          cyl_x(3.5, x_head - 4.0, x_head, y=y, z=z, segments=24) +
          cyl_x(4.5, -half - w, -half, y=y, z=z, segments=24) + cyl_x(4.5, half, half + w, y=y, z=z, segments=24) +
          cyl_x(M4_NYLOC_AF / 2 / math.cos(math.pi / 6), half + w, half + w + M4_NYLOC_T, y=y, z=z, segments=6))


def hinge_bolt(washers: bool = True) -> Manifold:
  """The M5 hinge bolt's head and lock nut on the hinge block's knuckles (with a washer under each, if used)."""
  hy, hz = HINGE
  k = BLOCK_KNUCKLE[1]
  w = M5_WASHER_T if washers else 0.0
  return union([cyl_x(4.25, -k - w - 5.0, -k - w, y=hy, z=hz, segments=32),
                cyl_x(5.0, -k - w, -k, y=hy, z=hz, segments=32) if w else cyl_x(2.5, -k - 0.01, -k, y=hy, z=hz),
                cyl_x(5.0, k, k + w, y=hy, z=hz, segments=32) if w else cyl_x(2.5, k, k + 0.01, y=hy, z=hz),
                cyl_x(8.0 / 2 / math.cos(math.pi / 6), k + w, k + w + M5_NYLOC_T, y=hy, z=hz, segments=6)])


def lever_bolt_tools() -> Manifold:
  """Room to put in and tighten the lift lever's bolt from the sides: a 3 mm hex key in its head, a 7 mm socket on
  its nut (carrier frame, lever down)."""
  y, z = LEVER_PIVOT
  half = BR_LEG_X[1] + M4_WASHER_T
  return (cyl_x(1.6, -60.0, -half - 4.0, y=y, z=z, segments=16) +
          cyl_x(6.0, half, 60.0, y=y, z=z, segments=32))


def spring_body() -> Manifold:
  """Room the spring takes, seat to pocket, with the motor gear on the teeth (carrier frame)."""
  return cyl_y(SPRING_OD / 2, TOP_Y[1] - SPRING_SEAT_D, HB_BOTTOM + SPRING_POCKET_D, z=SPRING_Z, segments=48)


def fastener_table() -> list:
  """Each bolt and screw: what it goes through, and how much length that leaves (mm)."""
  rows = []

  def nut_bolt(name, use, length, stack, washers, nut):
    spare = length - stack - washers - nut
    rows.append({"bolt": name, "use": use, "length": length, "through_mm": round(stack + washers, 1), "nut_mm": nut,
                 "past_the_nut_mm": round(spare, 1), "ok": spare >= 1.5})

  nut_bolt("M5 x 55", "hinge: the hinge block's knuckles and the carrier's between them, lock nut", 55.0,
           2 * BLOCK_KNUCKLE[1], 0.0, M5_NYLOC_T)
  nut_bolt("M5 x 60", "arm to hinge block: both ears and the arm, a washer each side, lock nut", 60.0,
           2 * EAR_X[1], 2 * M5_WASHER_T, M5_NYLOC_T)
  nut_bolt("M5 x 60", "arm to dash clamp: both side plates and the arm, a washer each side, lock nut", 60.0,
           2 * SIDE_PLATE_X[1], 2 * M5_WASHER_T, M5_NYLOC_T)
  nut_bolt("M4 x 35", "lift lever: both bracket legs and the lever, a washer each side, lock nut", 35.0,
           2 * BR_LEG_X[1], 2 * M4_WASHER_T, M4_NYLOC_T)
  # screws that cut their own thread or go into the motor
  into = 10.0 - BR_PLATE_T
  rows.append({"bolt": "M3 x 10", "use": "lever bracket into the carrier", "length": 10.0, "through_mm": BR_PLATE_T,
               "thread_in_mm": into, "hole_depth_mm": BR_SCREW_DEPTH, "ok": 4.0 <= into < BR_SCREW_DEPTH})
  under = MOTOR_PLATE_T - MOTOR_SCREW_CBORE
  into = 6.0 - under
  rows.append({"bolt": "M3 x 6 button head", "use": "carrier plate into the motor", "length": 6.0, "through_mm": under,
               "thread_in_mm": round(into, 1), "hole_depth_mm": MOTOR_HOLE_DEPTH, "ok": 3.0 <= into < MOTOR_HOLE_DEPTH})
  stack = CAGE_FRONT[1] - CAGE_BACK[0]
  rows.append({"bolt": "M2 x 16", "use": "switch: front wall, switch and rear wall, nut in the rear wall", "length": 16.0,
               "through_mm": stack, "past_the_wall_mm": round(16.0 - stack, 1), "ok": 16.0 - stack >= M2_NUT_T})
  # the dash clamp's screw: from under the jaw, through its nut, up to the pad under the cover's edge
  pad_socket = 3.0
  need_thin = -HOOD_EDGE_MIN - 5.0 + pad_socket - JAW_Y0
  need_thick = -HOOD_EDGE_MAX - 5.0 + pad_socket - JAW_Y0
  rows.append({"bolt": "M6 x 40", "use": f"dash clamp: under the jaw up to the pad, for a cover edge {HOOD_EDGE_MIN:.0f} to "
               f"{HOOD_EDGE_MAX:.0f} mm thick", "length": 40.0, "needs_mm": [round(need_thick, 1), round(need_thin, 1)],
               "ok": need_thin <= 40.0})
  return rows


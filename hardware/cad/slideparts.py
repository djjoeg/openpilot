"""
The slide mount: the motor at about 5:20 behind the wheel, its gear on the back teeth exactly as on the pop-off mount,
but it comes off the teeth by sliding straight back along the steering column instead of swinging away.

  slide carrier  - the motor bolts to its plate (finger guard round the gear, as before); on its 4 o'clock side a wall
                   holds the two 6 mm steel rods it slides on, the latch lever's bolt and the tongue that works the
                   power switch
  slide block    - fixed: bolts to the column plate; two linear bearings for each rod, the latch's spring-loaded
                   pusher, the power switch
  latch lever    - on the carrier's 4 o'clock side. Swing its handle forward (towards you): its cam pushes against the
                   block's pusher, the motor slides on and the pusher's spring keeps the gear pressed in. A flat on the
                   cam sits on the pusher, so it stays there. Swing it back: the motor is free and two springs on the
                   rods' back ends pull it 5.5 mm back, clear of the teeth.
  board cap      - covers the controller board on the motor's back

The carrier frame is popparts.py's (origin on the motor's front face, +z out along the shaft, +y towards the dash, x
across: +x towards 6 o'clock at this mount), with the motor on the teeth. Sliding off moves the carrier +STROKE in y.
Bought parts are drawn too, for the checks and the pictures.
"""
import math

import manifold3d
import numpy as np
from manifold3d import CrossSection, Manifold

import faceparts as FP
import mountparts as MP
import popparts as PP
from cadlib import box, clean, cyl, cyl_x, cyl_y, extrude_x, sector, union
from params import M3_CLEAR, M3_PILOT, M5_CLEAR, MOTOR_PLATE_T, NEMA, NEMA_BOSS, NEMA_HOLES, NEMA_LEN

H = NEMA / 2

# ***** where it sits *****
MOUNT_DEG_S = -70.0          # the motor at about 5:20 (0 = 3 o'clock, + up)
MOUNT_ADJ_S = (3.0, 3.0)     # the mount can be turned this far down (towards 6) and up (towards 4) when fitting it
STROKE = 8.25               # slid off: the carrier this far forward (towards the nose), which takes the motor, the gear
                             # and the carrier 1.5 mm out of the room your fingers need round the grip (popassembly.FINGERS)

# ***** the rods: two 6 mm hardened steel linear rods, 100 mm, fixed in the carrier; they slide in the block *****
ROD_D, ROD_LEN = 6.0, 100.0
RODS = ((-31.0, -15.0), (-31.0, 15.0))     # (x, z) of each rod
ROD_HOLE = 5.95                            # pressed into the carrier, and a grub screw each (the rods' front ends: below)
WALL_X = (-40.0, -21.6)                    # the carrier's wall on the motor's 4 o'clock side
WALL_Y = (-12.0, 23.5)                     # ... its front and back (its back stops against the block, slid off)
WALL_Z = (-23.0, 24.0)

# ***** the block *****
BLOCK_Y = (WALL_Y[1] + STROKE, WALL_Y[1] + STROKE + 42.0)
LM6UU = (12.0, 19.0)                       # the linear bearings: 12 mm across, 19 long (two on each rod)
BRG_SEAT = 12.0                            # pressed in
BRG_Y = ((BLOCK_Y[0] + 1.5, BLOCK_Y[0] + 20.5), (BLOCK_Y[0] + 21.5, BLOCK_Y[0] + 40.5))
HOUSING_R = 9.0

# ***** the latch: lever with a cam on the carrier, spring-loaded pusher in the block *****
LEVER_X = (-50.0, -44.0)                   # the lever's thickness (x)
PIVOT = (12.0, 0.0)                        # (y, z) its bolt (M5 x 35 and a lock nut), on the carrier
PIVOT_BOSS_X = (-44.0, -40.0)              # the boss on the carrier's wall the bolt goes through (lever outside it)
CAM_MIN = 8.0                              # the cam round the bolt (it faces the pusher with the lever off)
CAM_FLAT_HALF = 3.6                        # the flat that sits on the pusher with the lever on: +- this wide
CAM_RATE = 7.5                             # mm per radian at most: where the cam touches the pusher's nose stays within
                                           # this of the nose's middle (its flat face reaches 8.5)
CAM_BLEND = 0.15                           # radians: the cam's side eases into the round part over this much
PUSHER_X = -47.0                           # the pusher's axis (x); it points at the bolt (z = PIVOT[1])
NOSE_HALF = (3.3, 9.0)                     # the pusher's square nose that the cam pushes: +- across (x), +- up/down (z)
NOSE_EDGE = 0.5                            # its edges are rounded this much: the cam pushes only within the rest
SLOT_HALF = (3.6, 11.3)                    # the slot in the block's front wall the nose slides in: +- x, +- z (the cam's
SLOT_DEEP = 1.0                            # side swings into it, 10.7 from the middle at most, when the teeth meet tip to
                                           # tip), this far past the wall; a collar round it keeps 2 mm of wall
PUSHER_BODY_D = 14.0                       # its body behind the block's front wall; the spring behind it
PUSHER_BORE = 14.4
CLEAR_OFF = 0.5                            # slid off with the lever off, the cam clears the pusher by this much
FRONT_WALL_T = 2.5                         # the block's wall in front of the pusher's body
HANDLE_ON = (-20.0, -8.0)                  # (y, z) the handle's end from the bolt, lever on: forward, a little in (short
                                           # enough to pass the back teeth, 2.7 clear, as it swings with the motor on)
PAD_R = 5.5                                # the round pad at the handle's end, for your finger
SWING_SIGN = -1.0                          # turning the lever off swings the handle out (away from the column)
# The pusher's spring: Lee Spring LC 072G 05 M (music wire, 12.19 mm outside, 1.83 mm wire, 25.4 mm long, 18.214 N/mm,
# 198.65 N at its solid height of 14.53 mm). Pre-loaded to PUSH_STOP in the block; the lever on presses it to PUSH_ON
# (with the gear on the teeth), so the gear stays pressed in while the teeth piece wobbles as the wheel turns.
PSPRING = {"part": "Lee Spring LC 072G 05 M", "od": 12.19, "wire": 1.83, "free": 25.4, "rate": 18.214, "solid": 14.53,
           "max": 198.65}
PUSH_STOP = 30.0                           # N: the pusher's spring with the pusher out against the block's front wall (it
                                           # also limits how far the carrier follows the roller past the teeth: 1.1 mm)
PUSH_ON = 50.0                             # N: ... with the lever on and the gear on the teeth


def _spring_len(force: float) -> float:
  return PSPRING["free"] - force / PSPRING["rate"]


PUSH_TRAVEL_ON = _spring_len(PUSH_STOP) - _spring_len(PUSH_ON)           # the pusher goes back this far with the lever on
CAM_FLAT = CAM_MIN + CLEAR_OFF + STROKE + PUSH_TRAVEL_ON                # the flat's distance from the bolt
PUSH_FACE_STOP = PIVOT[0] + STROKE + CAM_MIN + CLEAR_OFF                 # the pusher's nose (y), out against its stop
# The cam's shape, as how far it reaches along the pusher (p) at each angle short of on (a, radians): the flat's corner
# (the high point) until the touching point would get CAM_RATE off the nose's middle, then an even fall of CAM_RATE per
# radian, eased over CAM_BLEND into the round part.
_CAM_C = math.hypot(CAM_FLAT, CAM_FLAT_HALF)
_CAM_AC = math.atan2(CAM_FLAT_HALF, CAM_FLAT)
_CAM_A1 = _CAM_AC + math.asin(CAM_RATE / _CAM_C)
_CAM_P1 = _CAM_C * math.cos(_CAM_A1 - _CAM_AC)
_CAM_P2 = CAM_MIN + CAM_RATE * CAM_BLEND / 2.0
_CAM_A2 = _CAM_A1 + (_CAM_P1 - _CAM_P2) / CAM_RATE
_CAM_A3 = _CAM_A2 + CAM_BLEND
LEVER_SWING = math.ceil(math.degrees(_CAM_A3)) + 1.0                     # degrees from off to on
PUSH_BODY_Y = BLOCK_Y[0] + FRONT_WALL_T                                  # the body's front face, at the stop
PUSH_BODY_LEN = 10.0
PSPRING_Y0 = PUSH_BODY_Y + PUSH_BODY_LEN                                 # the spring's front end, at the stop
PSPRING_Y1 = PSPRING_Y0 + _spring_len(PUSH_STOP)                         # ... its back end, against the plug
PLUG_Y = (PSPRING_Y1, PSPRING_Y1 + 4.0)                                  # a printed plug closes the bore (two M3)

# ***** the release springs on the rods' back ends, and their collars *****
# Two compression springs over the rods behind the block, each against a 6 mm shaft collar clamped at the rod's end:
# with the carrier on they are squeezed more and pull the carrier back.
# Lee Spring LC 022D 08 S: stainless, 7.62 mm outside, 6.50 inside (on a rod up to 6.10), 0.56 mm wire, 25.4 mm long,
# 0.403 N/mm, 9.27 N at its solid height of 4.6 mm (leespring.com). RSPRING_ON: each spring's length with the carrier on.
RSPRING = {"part": "Lee Spring LC 022D 08 S", "od": 7.62, "wire": 0.56, "free": 25.4, "rate": 0.403, "solid": 4.6,
           "max": 9.27}
RSPRING_ON = 10.5
END_HOLE_D = 6.8                           # the rods' holes in the block's end walls: the springs bear on the wall round them
COLLAR = (12.0, 7.0)                       # 6 mm bore shaft collar: 12 across, 7 wide (set screw)
COLLAR_Y = BLOCK_Y[1] + RSPRING_ON          # the collars' front faces, with the carrier on
ROD_FRONT = COLLAR_Y + COLLAR[1] - ROD_LEN  # the rods' front ends (in the carrier's wall), with the collars at their back ends

# ***** the power switch (as before: Omron SS-5GL2, push-on terminals) *****
# It lies flat behind the motor, its roller pointing across at the carrier's tongue, which has a land on its side: with
# the motor on the land holds the roller pressed; a millimetre off it starts down a 45 degree ramp and the switch lets go
# by 3 mm off (the teeth meeting tip to tip leave it 4.5 mm off: no power until the gear drops in). The switch's two
# screws sit in slots across (+- SW_SLOT): with the motor on, push it towards the tongue until it clicks, 0.6 mm more.
TONGUE_X = (-36.0, -30.0)                  # the carrier's tongue that works it, between the rods
TONGUE_Z = (-3.0, 3.0)
TONGUE_Y1 = 58.0                           # its back end (carrier on)
SW_ROLL_Y = 48.0                           # the switch's roller sits here (y), pressing the tongue's +x face
LAND_H = 4.0                               # the land on the tongue: this much proud ...
LAND_TOP_FROM = SW_ROLL_Y - 1.0            # ... from here back to the tongue's end (carrier on), a 45 degree ramp before it
SW_HOLES_X = TONGUE_X[1] + LAND_H + MP.SW_OP - MP.SW_PRESS   # the switch's holes' line (x), its roller towards -x
SW_SLOT = 2.0


# ***** the motor plate (as the pop-off carrier's) *****

def _motor_plate() -> Manifold:
  t = MOTOR_PLATE_T
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
  return plate + guard


def _plate_holes() -> Manifold:
  t = MOTOR_PLATE_T
  out = [cyl(NEMA_BOSS / 2 + 0.4, -3, t + 1, segments=128)]
  for sx in (-1, 1):
    for sy in (-1, 1):
      x, y = sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2
      out.append(cyl(M3_CLEAR / 2, -1, t + 1, x, y, 32) + cyl(3.4, t - MP.MOTOR_SCREW_CBORE, t + 1, x, y, 32))
  a, y0 = FP.PLATE_CHAMFER, MP.PLATE_BOTTOM
  from cadlib import prism_x
  out.append(prism_x([(y0 - 1.0, t - a - 1.0), (y0 + a + 1.0, t + 1.0), (y0 - 1.0, t + 1.0)], -60.0, 60.0))
  return union(out)


# ***** the cam *****
# With the lever on, the cam's flat sits square on the pusher's nose CAM_FLAT from the bolt; the flat's corners are the
# high point the lever passes over just before (and just after) on, so it stays on until you push the handle back. Its
# sides fall evenly from there to the round part round the bolt, which faces the pusher with the lever off. The sides
# are shaped so the cam always touches the nose's flat face, never its edge.

def cam_reach(a: float) -> tuple:
  """(p, dp/da): the cam's reach along the pusher and its rate, a radians short of on (a >= 0)."""
  if a <= _CAM_A1:
    return _CAM_C * math.cos(a - _CAM_AC), -_CAM_C * math.sin(a - _CAM_AC)
  if a <= _CAM_A2:
    return _CAM_P1 - CAM_RATE * (a - _CAM_A1), -CAM_RATE
  if a <= _CAM_A3:
    s = a - _CAM_A2
    return _CAM_P2 - CAM_RATE * s + CAM_RATE * s * s / (2.0 * CAM_BLEND), -CAM_RATE + CAM_RATE * s / CAM_BLEND
  return CAM_MIN, 0.0


_SUPPORT = {}


def cam_support(short_deg: float) -> float:
  """How far the cam reaches towards the pusher (along +y from the bolt) with the lever short_deg degrees short of on,
  where it can touch the pusher's nose (within its height, less the rounded edges). Far from on the flat's corner
  swings past the nose's end, and the cam's side does the pushing."""
  key = round(abs(short_deg), 4)
  if key not in _SUPPORT:
    h = NOSE_HALF[1] - NOSE_EDGE
    strip = CrossSection.square((100.0, 2.0 * h)).translate((-50.0, -h))
    _SUPPORT[key] = max(CAM_MIN, (cam_outline().rotate(SWING_SIGN * key) ^ strip).bounds()[2])
  return _SUPPORT[key]


def cam_peak() -> tuple:
  """(degrees short of on, reach) of the flat's corner, the lever's high point."""
  return math.degrees(math.atan2(CAM_FLAT_HALF, CAM_FLAT)), math.hypot(CAM_FLAT, CAM_FLAT_HALF)


def cam_outline() -> CrossSection:
  """In the lever's frame with the lever on: u along the pusher (+y), v = +z. Each point is where the pusher's face
  touches it at one angle (the same both ways from on)."""
  pts = []
  for deg in np.arange(-180.0, 180.0, 0.5):
    phi = math.radians(deg)
    p, dp = cam_reach(abs(phi))
    dp = dp if phi >= 0 else -dp
    c, s = math.cos(phi), math.sin(phi)
    pts.append((p * c - dp * s, p * s + dp * c))
  return CrossSection([pts]).simplify(0.002)


def cam_state(short_deg: float, tip_to_tip: float = 0.0) -> dict:
  """The carrier's place (how far it still is from on, mm), the pusher's force (N) and the turning force the handle
  needs (N mm) with the lever short_deg short of on. tip_to_tip: the gear stopped this far short by the teeth meeting
  tip to tip."""
  reach = cam_support(short_deg)
  gap = reach - (CAM_MIN + CLEAR_OFF)               # how far the cam has pushed the carrier and the pusher apart
  if gap <= 0:
    return {"carrier_off": STROKE, "force": 0.0, "torque": 0.0}
  carrier_off = max(tip_to_tip, STROKE - gap)
  pusher_back = max(0.0, gap - (STROKE - carrier_off))
  rel = release_force(carrier_off)
  force = max(rel, PUSH_STOP + PSPRING["rate"] * pusher_back) if pusher_back > 0 else rel
  dd = 0.25
  slope = abs(cam_support(short_deg + dd) - cam_support(short_deg - dd)) / math.radians(2 * dd)
  return {"carrier_off": carrier_off, "force": force, "torque": force * slope}


def handle_len() -> float:
  return math.hypot(*HANDLE_ON)


def cam_table(step: float = 5.0) -> list:
  rows = []
  for t2t in (0.0, 4.5):
    for d in np.arange(LEVER_SWING, -0.01, -step):
      st = cam_state(float(d), t2t)
      rows.append({"tip_to_tip": t2t, "short_deg": round(float(d), 1), "carrier_off": round(st["carrier_off"], 2),
                   "force_N": round(st["force"], 1), "handle_N": round(st["torque"] / handle_len(), 1)})
  return rows


def slide_lever(swing: float = 0.0) -> Manifold:
  """The latch lever in the carrier frame, swung swing degrees from on (0 on; SWING_SIGN * LEVER_SWING off)."""
  hu, hv = HANDLE_ON
  L = math.hypot(hu, hv)
  ang = math.degrees(math.atan2(hv, hu))
  arm = CrossSection.batch_hull([CrossSection.circle(6.5, 48), CrossSection.circle(5.0, 48).translate((L - 3.0, 0.0))])
  pad = CrossSection.circle(PAD_R, 48).translate((L - 3.5, 0.0))
  handle = (arm + pad).rotate(ang)
  lever = (cam_outline() + handle) - CrossSection.circle(M5_CLEAR / 2, 48)
  m = extrude_x(lever, LEVER_X[0], LEVER_X[1]).translate((0.0, PIVOT[0], PIVOT[1]))
  if swing:
    m = m.translate((0.0, -PIVOT[0], -PIVOT[1])).rotate((swing, 0.0, 0.0)).translate((0.0, PIVOT[0], PIVOT[1]))
  return clean(m)


def release_force(carrier_off: float) -> float:
  """Both release springs' pull (N) with the carrier carrier_off mm back from on."""
  length_on = COLLAR_Y - BLOCK_Y[1]
  per = RSPRING["rate"] * max(0.0, RSPRING["free"] - (length_on + carrier_off))
  return 2.0 * per


# ***** the carrier *****

def slide_carrier() -> Manifold:
  wall = box(WALL_X[0], WALL_X[1], WALL_Y[0], WALL_Y[1], WALL_Z[0], WALL_Z[1])
  socks = union([cyl_y(ROD_D / 2 + 4.5, WALL_Y[0], WALL_Y[1], x=x, z=z, segments=48) for x, z in RODS])
  boss = cyl_x(7.0, PIVOT_BOSS_X[0], WALL_X[0] + 0.5, y=PIVOT[0], z=PIVOT[1], segments=48)
  tongue = box(TONGUE_X[0], TONGUE_X[1], WALL_Y[1] - 0.5, TONGUE_Y1, TONGUE_Z[0], TONGUE_Z[1])
  land = box(TONGUE_X[1] - 0.5, TONGUE_X[1] + LAND_H, LAND_TOP_FROM, TONGUE_Y1, TONGUE_Z[0], TONGUE_Z[1])
  ramp = Manifold.batch_hull([box(TONGUE_X[1] - 0.5, TONGUE_X[1] + 0.01, LAND_TOP_FROM - LAND_H, LAND_TOP_FROM - LAND_H + 0.01,
                                  TONGUE_Z[0], TONGUE_Z[1]),
                              box(TONGUE_X[1] - 0.5, TONGUE_X[1] + LAND_H, LAND_TOP_FROM, LAND_TOP_FROM + 0.01,
                                  TONGUE_Z[0], TONGUE_Z[1])])
  part = union([_motor_plate(), wall, socks, boss, tongue, land, ramp])
  part = part - _plate_holes()
  part = part - box(-H - 0.3, H + 0.3, -H - 0.3, H + 0.3, -NEMA_LEN - 20, 0.0)
  for x, z in RODS:
    part = part - cyl_y(ROD_HOLE / 2, WALL_Y[0] - 1.0, WALL_Y[1] + 1.0, x=x, z=z, segments=48)
    # an M3 x 6 grub screw into each rod, cut into the plastic from outside (top for the upper rod, bottom the lower)
    if z > 0:
      part = part - cyl(M3_PILOT / 2, z, WALL_Z[1] + 1.0, x=x, y=0.0, segments=24)
    else:
      part = part - cyl(M3_PILOT / 2, WALL_Z[0] - 1.0, z, x=x, y=0.0, segments=24)
  # the lever's bolt: through the boss into the wall, its lock nut slid in from the wall's front along a slot
  part = part - cyl_x(M5_CLEAR / 2, PIVOT_BOSS_X[0] - 1.0, WALL_X[1] - 3.0, y=PIVOT[0], z=PIVOT[1], segments=32)
  nut_x = (-33.0, -33.0 + 6.4)
  part = part - box(nut_x[0], nut_x[1], WALL_Y[0] - 1.0, PIVOT[0] + 4.8, PIVOT[1] - 4.25, PIVOT[1] + 4.25)
  return clean(part)


# ***** the block *****

def slide_block() -> Manifold:
  y0, y1 = BLOCK_Y
  hs = union([cyl_y(HOUSING_R, y0, y1, x=x, z=z, segments=64) for x, z in RODS])
  web = box(RODS[0][0] - HOUSING_R, RODS[0][0] + HOUSING_R, y0, y1, RODS[0][1], RODS[1][1])
  pusher = cyl_y(PUSHER_BORE / 2 + 3.0, y0, PLUG_Y[1], x=PUSHER_X, z=PIVOT[1], segments=64)
  collar = cyl_y(math.hypot(*SLOT_HALF) + 2.0, y0, PUSH_BODY_Y + SLOT_DEEP + 2.0, x=PUSHER_X, z=PIVOT[1], segments=64)
  join = box(PUSHER_X, RODS[0][0], y0, PLUG_Y[1], PIVOT[1] - 8.0, PIVOT[1] + 8.0)
  sw_plate = box(-28.0, SW_HOLES_X + 6.0, SW_ROLL_Y - 14.0, SW_ROLL_Y + 14.0, -9.0, -3.6)
  part = union([hs, web, pusher, collar, join, sw_plate,
                box(FLANGE_X[0], -20.0, FLANGE_Y[0], FLANGE_Y[1], FLANGE_Z[0], FLANGE_Z[1])])
  # the rods' bearings and the tongue's slot
  for (b0, b1) in BRG_Y:
    for x, z in RODS:
      part = part - cyl_y(BRG_SEAT / 2, b0, b1, x=x, z=z, segments=64)
  for x, z in RODS:
    part = part - cyl_y(END_HOLE_D / 2, y0 - 1.0, y1 + 1.0, x=x, z=z, segments=48)
  part = part - box(TONGUE_X[0] - 0.6, TONGUE_X[1] + LAND_H + 0.8, y0 - 1.0, y1 + 1.0, TONGUE_Z[0] - 0.6, TONGUE_Z[1] + 0.6)
  # the pusher's bore: the nose's slot through the front wall, the body and spring behind, open at the back for the plug
  part = part - box(PUSHER_X - SLOT_HALF[0], PUSHER_X + SLOT_HALF[0], y0 - 1.0, PUSH_BODY_Y + SLOT_DEEP,
                    PIVOT[1] - SLOT_HALF[1], PIVOT[1] + SLOT_HALF[1])
  part = part - cyl_y(PUSHER_BORE / 2, PUSH_BODY_Y, PLUG_Y[1] + 1.0, x=PUSHER_X, z=PIVOT[1], segments=64)
  # the switch's window
  part = part - box(TONGUE_X[1], SW_HOLES_X - 4.0, SW_ROLL_Y - 6.0, SW_ROLL_Y + 6.0, -3.2, 3.2)
  part = part + block_flange()
  return clean(part)


def pusher() -> Manifold:
  """The latch's pusher, out against its stop (carrier frame): the nose the cam pushes, the body, a spigot for the spring."""
  nose = box(PUSHER_X - NOSE_HALF[0], PUSHER_X + NOSE_HALF[0], PUSH_FACE_STOP, PUSH_BODY_Y + 0.01,
             PIVOT[1] - NOSE_HALF[1], PIVOT[1] + NOSE_HALF[1])
  body = cyl_y(PUSHER_BODY_D / 2, PUSH_BODY_Y, PSPRING_Y0, x=PUSHER_X, z=PIVOT[1], segments=64)
  spigot = cyl_y(4.0, PSPRING_Y0, PSPRING_Y0 + 5.0, x=PUSHER_X, z=PIVOT[1], segments=32)
  return nose + body + spigot


def plug() -> Manifold:
  return cyl_y(PUSHER_BORE / 2 - 0.15, PLUG_Y[0], PLUG_Y[1], x=PUSHER_X, z=PIVOT[1], segments=64)


CAP_CHAMFER_Y0 = 19.0                      # the board cap's 45 degree cut starts here on its column side (y)


# ***** bought parts (for the checks and the pictures) *****

def rods(dy: float = 0.0) -> Manifold:
  return union([cyl_y(ROD_D / 2, ROD_FRONT + dy, ROD_FRONT + ROD_LEN + dy, x=x, z=z, segments=32) for x, z in RODS])


def collars(dy: float = 0.0) -> Manifold:
  return union([cyl_y(COLLAR[0] / 2, COLLAR_Y + dy, COLLAR_Y + COLLAR[1] + dy, x=x, z=z, segments=32) for x, z in RODS])


def release_springs(dy: float = 0.0) -> Manifold:
  r = RSPRING["od"] / 2
  return union([cyl_y(r, BLOCK_Y[1], COLLAR_Y + dy, x=x, z=z, segments=32) - cyl_y(r - RSPRING["wire"], BLOCK_Y[1] - 1,
                                                                                   COLLAR_Y + dy + 1, x=x, z=z, segments=32)
                for x, z in RODS])


def bearings() -> Manifold:
  return union([cyl_y(LM6UU[0] / 2, b0, b1, x=x, z=z, segments=48) - cyl_y(ROD_D / 2, b0 - 1, b1 + 1, x=x, z=z, segments=32)
                for b0, b1 in BRG_Y for x, z in RODS])


def switch_body() -> Manifold:
  """The switch lying flat behind the motor, its roller towards -x on the tongue (body, lever and roller)."""
  return box(SW_HOLES_X - 5.1, SW_HOLES_X + 5.1, SW_ROLL_Y - MP.SW_LEN / 2, SW_ROLL_Y + MP.SW_LEN / 2, -3.2, 3.2) + \
    box(TONGUE_X[1] + LAND_H, SW_HOLES_X - 5.0, SW_ROLL_Y - 2.4, SW_ROLL_Y + 2.4, -1.5, 1.5)


def motor_board(dash: str = "car"):
  """The motor, its board flat on its back (parts and plugs towards the column) under the cap, the board's car plug
  towards the dash and its motor plug towards 4 o'clock, the motor's own plug on its dash side."""
  h = H
  # the board with its side tabs broken off: 40.1 x 40.8 and the small tab its motor plug sits on
  core = CrossSection.square((40.1, 40.8)).translate((-20.05, -20.4))
  tab = CrossSection.square((15.9, 2.6)).translate((-8.3, -22.94))
  cs = (core + tab).mirror((0, 1)).rotate(90.0)
  cap = cs.offset(3.0, manifold3d.JoinType.Round, circular_segments=32).extrude(10.5).translate((0, 0, -50.5)) ^ \
    box(-30, 30, -30, 30, -50.5, -40.0)
  # its edge towards the dash and the column cut back 45 degrees (the column cover's lower front edge is there, slid off)
  from cadlib import prism_x
  cap = cap - prism_x([(CAP_CHAMFER_Y0, -51.0), (30.0, -51.0), (30.0, -51.0 + 30.0 - CAP_CHAMFER_Y0)], -30.0, 30.0)
  plug = 10.0
  return {"motor": box(-h, h, -h, h, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0), "board+cap": cap,
          "car plug": box(-1.7, 13.3, 20.05, 20.05 + plug, -47.6, -41.6),
          "motor plug": box(-22.94 - plug, -22.94, -8.7, 6.3, -47.6, -41.6),
          "motor's own plug": box(-8.0, 8.0, h, h + plug, -38.0, -22.0)}


# ***** the back teeth for this mount *****
# The same teeth piece as the pop-off mount's short set, centred on the motor at 5:20. The right lower spoke (the silver
# bar) meets the grip right there, so the channel is cut away over its junction (only the back and the outside wall run
# across it, as over the right spoke at 3 o'clock) and the zip ties go either side of it, the upper ones in the lead-in.

BAR_DEG = (-74.0, -56.0)       # the silver bar meets the grip between these angles (carref.RIGHT_BAR_DEG)
BAR_TOL_DEG = 3.0              # read off one photo


class SlideTeeth(PP.PopTeeth):
  def __init__(self, mount_deg: float = MOUNT_DEG_S, **kw):
    super().__init__(mount_deg=mount_deg, **kw)
    lo = BAR_DEG[0] - (mount_deg + MOUNT_ADJ_S[1]) - BAR_TOL_DEG - FP.SPOKE_ROOM_DEG
    hi = BAR_DEG[1] - (mount_deg - MOUNT_ADJ_S[0]) + BAR_TOL_DEG + FP.SPOKE_ROOM_DEG
    self.spoke = (lo, hi)


def slide_tie_angles(t: SlideTeeth) -> list:
  """Zip tie slots every FP.SLOT_EVERY_DEG, outwards from the bar's notch on both sides, as far as the lead-in's end."""
  w = math.degrees(FP.TIE_W / 2.0 / t.rr) + 1.0
  out = []
  a = t.spoke[1] + w + 0.25
  while a + w <= t.lead_end:
    out.append(a)
    a += FP.SLOT_EVERY_DEG
  a = t.spoke[0] - w - 0.25
  while a - w >= -t.lead_end:
    out.append(a)
    a -= FP.SLOT_EVERY_DEG
  return sorted(out)


def slide_ramps(t: SlideTeeth) -> Manifold:
  """Past the rolling band at each end the back falls away towards the wheel, as on the pop-off mount; but here the
  carrier follows the roller straight along the column, so the gear's teeth keep their full reach out (radius 172) and
  the teeth's zone and the band's split just outside it."""
  zt_end = t.z_root + FP.TEETH_END_DROP
  zb_end = t.z_band + FP.BAND_END_DROP
  z_last = t.z_bridge - 2.0
  r_split = FP.ROLL_BAND[0] - 0.9
  fast = 0.45 * FP.END_LEAD_IN
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


def slide_solid(t: SlideTeeth) -> Manifold:
  from cadlib import revolve
  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2
  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \
    PP.inner_chamfer(t) - slide_ramps(t) - PP.pop_spoke_notch(t) - FP.centre_mark(t)
  return clean(body)


def slide_teeth(t: SlideTeeth = None) -> Manifold:
  t = t or SlideTeeth()
  return clean(slide_solid(t) - FP.tie_slots(t, slide_tie_angles(t)))


# ***** the block's flange: bolts to the column plate's upright flange (two M5 x 25 along the column) *****
FLANGE_Y = (BLOCK_Y[1] - 4.5, BLOCK_Y[1])
FLANGE_X = (WALL_X[1] - 0.5, 12.0)
FLANGE_Z = (-18.0, 8.0)
FLANGE_BOLTS = ((-11.0, -9.0), (5.0, -1.0))   # (x, z)
FLANGE_SLOT = 8.0                              # each bolt's slot runs +- this across (x): the mount's +-3 degrees and the
                                               # plate's place


def block_flange() -> Manifold:
  fl = box(FLANGE_X[0], FLANGE_X[1], FLANGE_Y[0], FLANGE_Y[1], FLANGE_Z[0], FLANGE_Z[1])
  for x, z in FLANGE_BOLTS:
    fl = fl - Manifold.batch_hull([cyl_y(M5_CLEAR / 2, FLANGE_Y[0] - 1, FLANGE_Y[1] + 1, x=x + s, z=z, segments=32)
                                   for s in (-FLANGE_SLOT, FLANGE_SLOT)])
  return fl


# ***** the column plate: the pop-off mount's U round the adjustment tab, moved down with the column cover (carscene.py),
# with an upright flange the block bolts to *****
# The U, its slots for the screw tabs and its pad are the pop-off mount's (popparts.py), placed with the tab and the
# cover's screws (all three move with the cover). The flange hangs from the right leg, square to the column, behind
# the block's flange; its two slots run up and down (+- PL_FLANGE_SLOT) for the cover's height. The plate is made for one
# key depth D (your photo of the key sets it); its tabs slide along their slots for the rest.

PL_FLANGE_T = 5.0
PL_FLANGE_SLOT = 10.0
PL_FLANGE_PAD = 8.0


def flange_bolts_wheel(mount_deg: float = MOUNT_DEG_S) -> list:
  """The block's flange bolts (x, y) in the steering wheel frame, the mount at mount_deg (slots' middles)."""
  a = math.radians(mount_deg)
  out = []
  for xc, zc in FLANGE_BOLTS:
    r, t = PP.R_FACE_P + zc, -xc
    out.append((r * math.cos(a) - t * math.sin(a), r * math.sin(a) + t * math.cos(a)))
  return out


def flange_z() -> tuple:
  """The plate's flange (z), right behind the block's."""
  z1 = PP.Z_AXIS_P - FLANGE_Y[1]
  return (z1 - PL_FLANGE_T, z1)


def slide_column_plate(D: float = None) -> Manifold:
  """Steering wheel frame, for key depth D."""
  import carscene as CS
  sc = CS.CarScene(D if D is not None else CS.D_REF)
  dy, dz = sc.shift[1], sc.shift[2]
  y1 = PP.plate_top_y_u()
  y0 = y1 - PP.PL_T_U
  zb0, zb1 = PP.PL_BRIDGE_Z
  right = box(PP.PL_RIGHT_X[0], PP.PL_RIGHT_X[1], y0, y1, zb0, PP.PL_FRONT_Z)
  left = box(PP.PL_LEFT_X[0], PP.PL_LEFT_X[1], y0, y1, zb0, PP.PL_LEFT_FRONT_Z)
  bridge = box(PP.PL_LEFT_X[0], PP.PL_RIGHT_X[0] + 1.0, y0, y1, zb0, zb1)
  part = union([right, left, bridge])
  part = PP._round_corner(part, PP.PL_RIGHT_X[0], PP.PL_FRONT_Z, 1, -1, 8.0, y0, y1)
  part = PP._round_corner(part, PP.PL_LEFT_X[0], PP.PL_LEFT_FRONT_Z, 1, -1, 7.0, y0, y1)
  part = PP._round_corner(part, PP.PL_LEFT_X[1], PP.PL_LEFT_FRONT_Z, -1, -1, 7.0, y0, y1)
  part = PP._round_corner(part, PP.PL_LEFT_X[0], zb0, 1, 1, 8.0, y0, y1)
  ribs = [box(PP.PL_RIGHT_X[0], PP.PL_RIGHT_X[0] + 4.0, y0 - 6.0, y0 + 0.01, zb0, PP.PL_FRONT_Z - 8.0),
          box(PP.PL_LEFT_X[1] - 4.0, PP.PL_LEFT_X[1], y0 - 6.0, y0 + 0.01, zb0, PP.PL_LEFT_FRONT_Z - 7.0),
          box(PP.PL_LEFT_X[0] + 8.0, PP.PL_RIGHT_X[0] + 4.0, y0 - 6.0, y0 + 0.01, zb1 - 4.0, zb1)]
  part = union([part] + ribs)
  for x0, z0, x1, z1 in PP.PL_SLOTS:
    part = part - PP._slot_y(x0, z0, x1, z1, y0 - 8.0, y1 + 1.0)
  for z in PP.PL_TIE_Z_U:
    part = part - box(PP.PL_LEFT_X[0] - 1.0, PP.PL_LEFT_X[1] + 1.0, y0 - 7.0, y0 + 1.5, z - 4.0, z + 4.0)
  # the flange, in the plate's own frame (the cover's estimate it was drawn for): the block's bolts, less the move
  fz0, fz1 = flange_z()
  fz0, fz1 = fz0 - dz, fz1 - dz
  bolts = [(x, y - dy) for x, y in flange_bolts_wheel()]
  xs = [b[0] for b in bolts]
  ys = [b[1] for b in bolts]
  fx0 = min(xs) - PL_FLANGE_PAD - FLANGE_SLOT * 0.4
  fx1 = max(max(xs) + PL_FLANGE_PAD, PP.PL_RIGHT_X[1])
  fy0 = min(ys) - PL_FLANGE_SLOT - PL_FLANGE_PAD
  flange = box(fx0, fx1, fy0, y1, fz0, fz1)
  # a gusset behind it, along the leg's outer edge, and the leg made long enough to reach it
  reach = box(PP.PL_RIGHT_X[1] - 14.0, PP.PL_RIGHT_X[1], y0, y1, fz0, PP.PL_FRONT_Z)
  gusset = box(fx1 - 6.0, fx1, fy0 + 8.0, y1, fz0 - 22.0, fz1)
  gusset = gusset - _wedge_cut(fx1 - 7.0, fx1 + 1.0, fy0 + 7.0, y0, fz0 - 23.0, fz0)
  part = union([part, flange, reach, gusset])
  for (bx, by) in bolts:
    part = part - Manifold.batch_hull([cyl(M5_CLEAR / 2, fz0 - 1.0, fz1 + 1.0, bx, by + s, 32) for s in (-PL_FLANGE_SLOT, PL_FLANGE_SLOT)])
  # the plate keeps 1.5 mm clear of the block in front of its flange, and of the rods' back ends, their collars and
  # springs everywhere they go (the mount turned anywhere in its +-3 degrees)
  part = part - block_keepout(1.5).translate((0.0, -dy, -dz))
  return clean(part.translate((0.0, dy, dz)))


def _mount_angles() -> tuple:
  return (MOUNT_DEG_S - MOUNT_ADJ_S[0], MOUNT_DEG_S, MOUNT_DEG_S + MOUNT_ADJ_S[1])


def _to_wheel_at(m: Manifold, mount_deg: float) -> Manifold:
  Rm = PP.rot_z(mount_deg)
  return PP.place(m, Rm @ PP.R_POP, Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P]))


def block_keepout(clear: float) -> Manifold:
  """Steering wheel frame: everywhere the block can be (the mount turned anywhere in its +-3 degrees), grown by clear,
  in front of the column plate's flange; and everywhere the rods' back ends, their collars and springs go."""
  blk = slide_block()
  placed = [_to_wheel_at(blk, m) for m in _mount_angles()]
  grown = Manifold.batch_hull([p.translate((sx, sy, sz)) for p in placed
                               for sx, sy, sz in ((clear, 0, 0), (-clear, 0, 0), (0, clear, 0), (0, -clear, 0), (0, 0, clear))])
  out = grown ^ box(-500.0, 500.0, -500.0, 500.0, flange_z()[1], 500.0)
  r = COLLAR[0] / 2 + clear
  for x, z in RODS:
    tube = cyl_y(r, BLOCK_Y[1] - 1.0, ROD_FRONT + ROD_LEN + STROKE + 1.0, x=x, z=z, segments=32)
    out = out + Manifold.batch_hull([_to_wheel_at(tube, m) for m in _mount_angles()])
  return out


def _wedge_cut(x0, x1, y_lo, y_hi, z_back, z_front) -> Manifold:
  """Cuts the gusset's lower back corner away at a slope (from (y_lo, z_front) to (y_hi, z_back))."""
  from cadlib import prism_x
  return prism_x([(y_lo, z_front), (y_lo, z_back), (y_hi, z_back)], x0, x1)


# ***** the board cap *****
# A printed cover over the controller board's parts side (the board lies flat on the motor's back, its parts and plugs
# facing the column). Its open end sits against the motor's back; four tongues run up the motor's sides and a zip tie
# round the motor holds them. Openings let the two plugs out; its edge towards the dash and the column is cut back (the
# column cover's lower front edge is there with the motor slid off).
CAP_WALL, CAP_GAP = 2.0, 1.0
CAP_DEPTH = 10.5                            # from the motor's back face to the cap's outside
CAP_TONGUE = (10.0, 8.0, 1.6)               # each tongue: width, how far up the motor, thickness
TIE_SLOT = (4.0, 1.2)                       # the zip tie's groove across each tongue (width along the motor, depth)


def _board_cs() -> CrossSection:
  core = CrossSection.square((40.1, 40.8)).translate((-20.05, -20.4))
  tab = CrossSection.square((15.9, 2.6)).translate((-8.3, -22.94))
  return (core + tab).mirror((0, 1)).rotate(90.0)


def board_cap() -> Manifold:
  """Carrier frame, as fitted."""
  from cadlib import prism_x
  z_back = -NEMA_LEN
  cs = _board_cs()
  outer = cs.offset(CAP_GAP + CAP_WALL, manifold3d.JoinType.Round, circular_segments=32)
  inner = cs.offset(CAP_GAP, manifold3d.JoinType.Round, circular_segments=32)
  shell = outer.extrude(CAP_DEPTH).translate((0, 0, z_back - CAP_DEPTH)) - \
    inner.extrude(CAP_DEPTH - CAP_WALL + 0.01).translate((0, 0, z_back - CAP_DEPTH + CAP_WALL))
  # the tongues up the motor's four sides (clear of the plugs' openings), each with a groove for the tie
  w, up, th = CAP_TONGUE
  x0, y0, x1, y1 = outer.bounds()
  z_in = z_back - CAP_DEPTH + CAP_WALL
  tongues = []
  for side, along in (("+x", 0.0), ("-x", 15.0), ("+y", -14.0), ("-y", 0.0)):
    if side == "+x":
      tg = box(H, H + th, along - w / 2, along + w / 2, z_back, z_back + up) + box(H - 0.5, x1, along - w / 2, along + w / 2, z_in, z_back)
      tg = tg - box(H + th - TIE_SLOT[1], x1 + 1, along - w / 2 - 1, along + w / 2 + 1, z_back + up - 2 - TIE_SLOT[0], z_back + up - 2)
    elif side == "-x":
      tg = box(-H - th, -H, along - w / 2, along + w / 2, z_back, z_back + up) + box(x0, -H + 0.5, along - w / 2, along + w / 2, z_in, z_back)
      tg = tg - box(x0 - 1, -H - th + TIE_SLOT[1], along - w / 2 - 1, along + w / 2 + 1, z_back + up - 2 - TIE_SLOT[0], z_back + up - 2)
    elif side == "+y":
      tg = box(along - w / 2, along + w / 2, H, H + th, z_back, z_back + up) + box(along - w / 2, along + w / 2, H - 0.5, y1, z_in, z_back)
      tg = tg - box(along - w / 2 - 1, along + w / 2 + 1, H + th - TIE_SLOT[1], y1 + 1, z_back + up - 2 - TIE_SLOT[0], z_back + up - 2)
    else:
      tg = box(along - w / 2, along + w / 2, -H - th, -H, z_back, z_back + up) + box(along - w / 2, along + w / 2, y0, -H + 0.5, z_in, z_back)
      tg = tg - box(along - w / 2 - 1, along + w / 2 + 1, y0 - 1, -H - th + TIE_SLOT[1], z_back + up - 2 - TIE_SLOT[0], z_back + up - 2)
    tongues.append(tg)
  part = union([shell] + tongues)
  # the plugs' openings: the car plug towards the dash, the motor plug towards 4 o'clock
  part = part - box(-2.7, 14.3, 18.0, 30.0, -48.6, z_back + 0.01)
  part = part - box(-30.0, -20.0, -9.7, 7.3, -48.6, z_back + 0.01)
  part = part - prism_x([(CAP_CHAMFER_Y0, -51.0), (30.0, -51.0), (30.0, -51.0 + 30.0 - CAP_CHAMFER_Y0)], -30.0, 30.0)
  return clean(part)

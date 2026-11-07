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
                   rods' back ends pull it 6 mm back, clear of the teeth.
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
from cadlib import box, clean, cyl, cyl_x, cyl_y, extrude_x, hex_prism_x, hex_prism_y, sector, union
from params import M3_CLEAR, M3_PILOT, M5_CLEAR, MOTOR_PLATE_T, NEMA, NEMA_BOSS, NEMA_HOLES, NEMA_LEN

H = NEMA / 2

# ***** where it sits *****
MOUNT_DEG_S = -70.0          # the motor at about 5:20 (0 = 3 o'clock, + up)
MOUNT_ADJ_S = (3.0, 3.0)     # the mount can be turned this far down (towards 6) and up (towards 4) when fitting it
STROKE = 6.0                 # slid off: the carrier this far back towards the dash (the gear then clears the teeth by 2.5)

# ***** the rods: two 6 mm hardened steel linear rods, 100 mm, fixed in the carrier; they slide in the block *****
ROD_D, ROD_LEN = 6.0, 100.0
RODS = ((-31.0, -15.0), (-31.0, 15.0))     # (x, z) of each rod
ROD_FRONT = -12.0                          # the rods' front ends (in the carrier)
ROD_HOLE = 5.95                            # pressed into the carrier, and a grub screw each
WALL_X = (-40.0, -21.6)                    # the carrier's wall on the motor's 4 o'clock side
WALL_Y = (-12.0, 22.0)                     # ... its front and back (its back stops against the block, slid off)
WALL_Z = (-23.0, 24.0)

# ***** the block *****
BLOCK_Y = (28.0, 70.0)
LM6UU = (12.0, 19.0)                       # the linear bearings: 12 mm across, 19 long (two on each rod)
BRG_SEAT = 12.0                            # pressed in
BRG_Y = ((29.5, 48.5), (49.5, 68.5))
HOUSING_R = 9.0

# ***** the latch: lever with a cam on the carrier, spring-loaded pusher in the block *****
LEVER_X = (-50.0, -44.0)                   # the lever's thickness (x)
PIVOT = (12.0, 0.0)                        # (y, z) its bolt (M5 x 30), on the carrier
PIVOT_BOSS_X = (-44.0, -40.0)              # the boss on the carrier's wall the bolt goes through (lever outside it)
CAM_MIN = 6.0                              # the cam's smallest radius (faces the pusher with the lever off)
CAM_FLAT_HALF = 3.6                        # the flat that sits on the pusher with the lever on: +- this wide
LEVER_SWING = 70.0                         # degrees from off to on
CAM_RISE = (62.0, 14.0)                    # the cam rises between these angles before on (degrees)
PUSHER_X = -47.0                           # the pusher's axis (x); its y axis passes through the bolt (z = PIVOT[1])
PUSHER_NOSE_D = 9.6                        # the nose that the cam pushes, through a 10 mm hole in the block's front
PUSHER_BODY_D = 12.6                       # its body behind the block's front wall; the spring behind it
PUSHER_BORE = 13.0
CLEAR_OFF = 0.5                            # slid off with the lever off, the cam clears the pusher by this much
FRONT_WALL_T = 2.5                         # the block's wall in front of the pusher's body
HANDLE_LEN = 31.6                          # bolt to the end of the handle
HANDLE_ON_DIR = (-30.0, -10.0)             # (y, z) the handle points this way with the lever on: forward, a little in
# The pusher's spring: Lee Spring LC 072G 05 M (music wire, 12.19 mm outside, 1.83 mm wire, 25.4 mm long, 18.214 N/mm,
# 198.65 N at its solid height of 14.53 mm). Pre-loaded to PUSH_STOP in the block; the lever on presses it PUSH_ON
# (with the gear on the teeth), so the gear stays pressed in while the teeth piece wobbles as the wheel turns.
PSPRING = {"part": "Lee Spring LC 072G 05 M", "od": 12.19, "wire": 1.83, "free": 25.4, "rate": 18.214, "solid": 14.53,
           "max": 198.65}
PUSH_STOP = 15.0                           # N: the pusher's spring with the pusher out against the block's front wall
PUSH_ON = 50.0                             # N: ... with the lever on and the gear on the teeth


def _spring_len(force: float) -> float:
  return PSPRING["free"] - force / PSPRING["rate"]


PUSH_TRAVEL_ON = _spring_len(PUSH_STOP) - _spring_len(PUSH_ON)           # the pusher goes back this far with the lever on
CAM_FLAT = CAM_MIN + CLEAR_OFF + STROKE + PUSH_TRAVEL_ON                # the flat's distance from the bolt
PUSH_FACE_STOP = PIVOT[0] + STROKE + CAM_MIN + CLEAR_OFF                 # the pusher's nose (y), out against its stop
PUSH_BODY_Y = BLOCK_Y[0] + FRONT_WALL_T                                  # the body's front face, at the stop
PUSH_BODY_LEN = 10.0
PSPRING_Y0 = PUSH_BODY_Y + PUSH_BODY_LEN                                 # the spring's front end, at the stop
PSPRING_Y1 = PSPRING_Y0 + _spring_len(PUSH_STOP)                         # ... its back end, against the plug
PLUG_Y = (PSPRING_Y1, PSPRING_Y1 + 3.0)                                  # a printed plug closes the bore (two M3)

# ***** the release springs on the rods' back ends, and their collars *****
# Two compression springs over the rods behind the block, each against a 6 mm shaft collar clamped at the rod's end:
# with the carrier on they are squeezed more and pull the carrier back.
RSPRING = {"part": "to be chosen", "od": 10.0, "wire": 0.8, "free": 20.0, "rate": 0.55, "solid": 8.0}
COLLAR = (12.0, 7.0)                       # 6 mm bore shaft collar: 12 across, 7 wide (set screw)
COLLAR_Y = ROD_FRONT + ROD_LEN - COLLAR[1]  # the collars' front faces, with the carrier on

# ***** the power switch (as before: Omron SS-5GL2, push-on terminals) *****
TONGUE_X = (-34.0, -28.0)                  # the carrier's tongue that works it, between the rods
TONGUE_Z = (-3.0, 3.0)
TONGUE_Y1 = 58.0                           # its back end (carrier on)
SW_ROLL_Y = 48.0                           # the switch's roller sits here (y), pressing the tongue's +x face
LAND_H = 2.5                               # the land on the tongue: this much proud, from 1.5 mm in front of the roller
LAND_FROM = SW_ROLL_Y - 1.5                # (carrier on) back to the tongue's end: the switch opens 1.5 mm off
SW_HOLES_X = TONGUE_X[1] + LAND_H + MP.SW_OP - MP.SW_PRESS   # the switch's holes' line (x), its roller towards -x


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

def cam_support(dtheta_deg: float) -> float:
  """The cam's reach towards the pusher (its flat face) with the lever dtheta degrees short of on: the base radius off,
  a smooth rise, then the flat's corner (the lever passes over it) and the flat itself."""
  d = abs(dtheta_deg)
  a0, a1 = CAM_RISE
  flat = CAM_FLAT * math.cos(math.radians(d)) + CAM_FLAT_HALF * math.sin(math.radians(d))
  corner = math.degrees(math.atan2(CAM_FLAT_HALF, CAM_FLAT))
  if d <= corner:
    return flat
  peak = math.hypot(CAM_FLAT, CAM_FLAT_HALF)
  if d >= a0:
    return CAM_MIN
  if d <= a1:
    # from the rise's end to the corner: blend into the flat's corner
    u = (d - corner) / (a1 - corner)
    return peak + (flat - peak) * 0.0 * u if False else max(flat, peak - (peak - _rise(a1)) * u)
  return _rise(d)


def _rise(d: float) -> float:
  a0, a1 = CAM_RISE
  peak = math.hypot(CAM_FLAT, CAM_FLAT_HALF)
  s = (a0 - d) / (a0 - a1)                     # 0 at the rise's start, 1 at its end
  s = max(0.0, min(1.0, s))
  return CAM_MIN + (peak - 0.15 - CAM_MIN) * (0.5 - 0.5 * math.cos(math.pi * s))


def cam_outline(step: float = 0.5) -> CrossSection:
  """The cam in the lever's frame with the lever on (the pusher's direction is +y): the intersection of the half-planes
  p . u(d) <= support(d) over the lever's swing, where u(d) is the pusher's direction seen from the lever d degrees short
  of on; round the rest of the bolt it's the base circle."""
  big = 200.0
  cs = CrossSection.circle(CAM_FLAT + CAM_FLAT_HALF + 4.0, 128)
  for d in np.arange(-30.0, LEVER_SWING + 25.0 + 1e-9, step):
    h = cam_support(d)
    a = math.radians(90.0 + d)                 # the pusher's direction in the lever's frame: turning on turns it to +y
    ux, uy = math.cos(a), math.sin(a)
    # half-plane u . p <= h as a big square
    sq = CrossSection.square((2 * big, 2 * big), center=True).translate((0.0, -big + h))
    cs = cs ^ sq.rotate(d)
  return cs + CrossSection.circle(CAM_MIN, 64)


def cam_torque_table(step: float = 2.0) -> list:
  """(degrees short of on, the cam's reach, the pusher's force N, turning force on the lever N mm) along the swing:
  normal (the gear seats) and with the teeth tip to tip (the carrier stops 4.5 mm short)."""
  rows = []
  for short in (0.0, 4.5):
    for d in np.arange(LEVER_SWING, -0.01, -step):
      h = cam_support(d)
      # the gap the cam fills: the carrier slides on until its gear seats (release springs ~12 N), then the pusher goes back
      travel = h - CAM_MIN - CLEAR_OFF                 # how far the cam has pushed the carrier and pusher apart
      pusher_back = max(0.0, travel - (STROKE - short))
      f = PUSH_STOP + PSPRING["rate"] * pusher_back if pusher_back > 0 else 12.0
      dh = (cam_support(max(0.0, d - 0.5)) - cam_support(d + 0.5)) / math.radians(1.0)
      rows.append((short, round(float(d), 1), round(h, 2), round(f, 1), round(f * abs(dh), 0)))
  return rows


def slide_lever(swing: float = 0.0) -> Manifold:
  """The latch lever in the carrier frame; swing = degrees short of on (0 on, LEVER_SWING off)."""
  cs = cam_outline()
  # the handle: from the bolt out along HANDLE_ON_DIR, 9 mm wide, its end rounded into a finger pad
  hy, hz = HANDLE_ON_DIR
  L = math.hypot(hy, hz)
  ang = math.degrees(math.atan2(hz, hy))
  arm = CrossSection.batch_hull([CrossSection.circle(6.0, 48), CrossSection.circle(5.5, 48).translate((HANDLE_LEN - 2.0, 0.0))])
  pad = CrossSection.circle(7.0, 48).translate((HANDLE_LEN - 4.0, 0.0))
  handle = (arm + pad).rotate(ang)
  lever = (cs + handle) - CrossSection.circle(M5_CLEAR / 2, 48)
  # the lever's own frame has the pusher along +y; the carrier's (y, z) plane: lever (u, v) -> carrier (y = v?..)
  m = extrude_x(lever.rotate(-90.0), LEVER_X[0], LEVER_X[1])      # u (pusher) -> +y
  m = m.translate((0.0, PIVOT[0], PIVOT[1]))
  if swing:
    m = m.translate((0.0, -PIVOT[0], -PIVOT[1])).rotate((swing, 0.0, 0.0)).translate((0.0, PIVOT[0], PIVOT[1]))
  return clean(m)


# ***** the carrier *****

def slide_carrier() -> Manifold:
  wall = box(WALL_X[0], WALL_X[1], WALL_Y[0], WALL_Y[1], WALL_Z[0], WALL_Z[1])
  socks = union([cyl_y(ROD_D / 2 + 4.5, WALL_Y[0], WALL_Y[1], x=x, z=z, segments=48) for x, z in RODS])
  boss = cyl_x(7.0, PIVOT_BOSS_X[0], WALL_X[0] + 0.5, y=PIVOT[0], z=PIVOT[1], segments=48)
  tongue = box(TONGUE_X[0], TONGUE_X[1], WALL_Y[1] - 0.5, TONGUE_Y1, TONGUE_Z[0], TONGUE_Z[1])
  land = box(TONGUE_X[1] - 0.5, TONGUE_X[1] + LAND_H, LAND_FROM + LAND_H, TONGUE_Y1, TONGUE_Z[0], TONGUE_Z[1])
  ramp = Manifold.batch_hull([box(TONGUE_X[1] - 0.5, TONGUE_X[1] + 0.01, LAND_FROM, LAND_FROM + 0.01, TONGUE_Z[0], TONGUE_Z[1]),
                              box(TONGUE_X[1] - 0.5, TONGUE_X[1] + LAND_H, LAND_FROM + LAND_H, LAND_FROM + LAND_H + 0.01,
                                  TONGUE_Z[0], TONGUE_Z[1])])
  part = union([_motor_plate(), wall, socks, boss, tongue, land, ramp])
  part = part - _plate_holes()
  part = part - box(-H - 0.3, H + 0.3, -H - 0.3, H + 0.3, -NEMA_LEN - 20, 0.0)
  for x, z in RODS:
    part = part - cyl_y(ROD_HOLE / 2, WALL_Y[0] - 1.0, WALL_Y[1] + 1.0, x=x, z=z, segments=48)
    # grub screw from the top (z) into each rod: M3 nut trap
    part = part - cyl(M3_CLEAR / 2, z, WALL_Z[1] + 1, x=x, y=0.0, segments=24) if z > 0 else \
      part - cyl(M3_CLEAR / 2, WALL_Z[0] - 1, z, x=x, y=0.0, segments=24)
  part = part - cyl_x(M5_CLEAR / 2, PIVOT_BOSS_X[0] - 1.0, WALL_X[1] - 4.0, y=PIVOT[0], z=PIVOT[1], segments=32)
  part = part - hex_prism_x(MP.M2_NUT_AF * 0 + 8.3, WALL_X[1] - 9.0, WALL_X[1] - 4.0, y=PIVOT[0], z=PIVOT[1])   # M5 nut
  return clean(part)


# ***** the block *****

def slide_block() -> Manifold:
  y0, y1 = BLOCK_Y
  hs = union([cyl_y(HOUSING_R, y0, y1, x=x, z=z, segments=64) for x, z in RODS])
  web = box(RODS[0][0] - HOUSING_R, RODS[0][0] + HOUSING_R, y0, y1, RODS[0][1], RODS[1][1])
  pusher = cyl_y(PUSHER_BORE / 2 + 3.0, y0, PLUG_Y[1], x=PUSHER_X, z=PIVOT[1], segments=64)
  join = box(PUSHER_X, RODS[0][0], y0, PLUG_Y[1], PIVOT[1] - 8.0, PIVOT[1] + 8.0)
  sw_plate = box(-28.0, SW_HOLES_X + 6.0, SW_ROLL_Y - 14.0, SW_ROLL_Y + 14.0, -9.0, -3.6)
  part = union([hs, web, pusher, join, sw_plate])
  # the rods' bearings and the tongue's slot
  for (b0, b1) in BRG_Y:
    for x, z in RODS:
      part = part - cyl_y(BRG_SEAT / 2, b0, b1, x=x, z=z, segments=64)
  for x, z in RODS:
    part = part - cyl_y(ROD_D / 2 + 0.8, y0 - 1.0, y1 + 1.0, x=x, z=z, segments=48)
  part = part - box(TONGUE_X[0] - 0.6, TONGUE_X[1] + LAND_H + 0.8, y0 - 1.0, y1 + 1.0, TONGUE_Z[0] - 0.6, TONGUE_Z[1] + 0.6)
  # the pusher's bore: nose hole through the front wall, the body and spring behind, open at the back for the plug
  part = part - cyl_y(5.0, y0 - 1.0, PUSH_BODY_Y + 0.01, x=PUSHER_X, z=PIVOT[1], segments=48)
  part = part - cyl_y(PUSHER_BORE / 2, PUSH_BODY_Y, PLUG_Y[1] + 1.0, x=PUSHER_X, z=PIVOT[1], segments=64)
  # the switch's window
  part = part - box(TONGUE_X[1], WALL_X[1] + 12.0, SW_ROLL_Y - 6.0, SW_ROLL_Y + 6.0, -3.2, 3.2)
  return clean(part)


def pusher() -> Manifold:
  """The latch's pusher, out against its stop (carrier frame): the nose the cam pushes, the body, a spigot for the spring."""
  nose = cyl_y(PUSHER_NOSE_D / 2, PUSH_FACE_STOP, PUSH_BODY_Y, x=PUSHER_X, z=PIVOT[1], segments=48)
  body = cyl_y(PUSHER_BODY_D / 2, PUSH_BODY_Y, PSPRING_Y0, x=PUSHER_X, z=PIVOT[1], segments=64)
  spigot = cyl_y(4.0, PSPRING_Y0, PSPRING_Y0 + 5.0, x=PUSHER_X, z=PIVOT[1], segments=32)
  return nose + body + spigot


def plug() -> Manifold:
  return cyl_y(PUSHER_BORE / 2 - 0.15, PLUG_Y[0], PLUG_Y[1], x=PUSHER_X, z=PIVOT[1], segments=64)


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
  plug = 10.0
  return {"motor": box(-h, h, -h, h, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0), "board+cap": cap,
          "car plug": box(-1.7, 13.3, 20.05, 20.05 + plug, -47.6, -41.6),
          "motor plug": box(-22.94 - plug, -22.94, -8.7, 6.3, -47.6, -41.6),
          "motor's own plug": box(-8.0, 8.0, h, h + plug, -38.0, -22.0)}

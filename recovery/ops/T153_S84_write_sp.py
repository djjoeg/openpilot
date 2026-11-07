"""Draft of the slide mount's parts (carrier frame, the motor engaged): for laying out the space. Not the final parts."""
import math
import sys

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np  # noqa: E402
from manifold3d import CrossSection, Manifold  # noqa: E402

import faceparts as FP  # noqa: E402
import mountparts as MP  # noqa: E402
import popparts as PP  # noqa: E402
from cadlib import box, clean, cyl, cyl_x, cyl_y, extrude_x, sector, union  # noqa: E402
from params import M3_CLEAR, MOTOR_PLATE_T, NEMA, NEMA_BOSS, NEMA_HOLES, NEMA_LEN  # noqa: E402

MOUNT = -70.0
STROKE = 6.0
H = NEMA / 2
ROD_D = 6.0
RODS = ((-31.0, -18.0), (-31.0, 12.0))      # (x_c, z_c)
ROD_FRONT = -12.0                            # the rods' front ends in the carrier (engaged)
ROD_LEN = 100.0
SOCKET_Y = (-12.0, 14.0)                     # the rods' sockets in the carrier's side
WALL_X = (-40.0, -21.4)                      # the carrier's side wall (beside the motor's 4 o'clock face)
BLOCK_Y = (28.0, 70.0)
BRG_R = 6.0                                   # LM6UU: 12 mm across, 19 long
HOUSING_R = BRG_R + 3.0


def motor_plate() -> Manifold:
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
  return plate + guard


def carrier() -> Manifold:
  wall = box(WALL_X[0], WALL_X[1], SOCKET_Y[0], SOCKET_Y[1], RODS[0][1] - 9.0, MOTOR_PLATE_T)
  socks = union([cyl_y(ROD_D / 2 + 4.0, SOCKET_Y[0], SOCKET_Y[1], x=x, z=z) for x, z in RODS])
  part = motor_plate() + wall + socks
  part = part - box(-H - 0.3, H + 0.3, -H - 0.3, H + 0.3, -NEMA_LEN - 20, 0.0)
  return part


def rods(dy: float = 0.0) -> Manifold:
  return union([cyl_y(ROD_D / 2, ROD_FRONT + dy, ROD_FRONT + ROD_LEN + dy, x=x, z=z, segments=32) for x, z in RODS])


def block() -> Manifold:
  hs = union([cyl_y(HOUSING_R, BLOCK_Y[0], BLOCK_Y[1], x=x, z=z) for x, z in RODS])
  web = box(RODS[0][0] - HOUSING_R, RODS[0][0] + HOUSING_R, BLOCK_Y[0], BLOCK_Y[1], RODS[0][1], RODS[1][1])
  return hs + web


def motor_board():
  import study90 as S
  return S.radial_parts(MOUNT, "car")

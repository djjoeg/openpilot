"""
The side-slide mount: the motor at about 5:20 behind the steering wheel, its shaft pointing out at the steering wheel
and its gear on the back teeth, slides along its own shaft in towards the middle of the steering wheel to come off the
teeth. A spring pulls it in; you pull it back out until the latch clicks, and pull the latch's knob to let it go.

  mounting plate  - fixed. Carries the rail, the latch (a bought spring plunger with a knob), the power switch and
                    the spring's spool. How it fixes to the car is not drawn yet (see the report's questions).
  motor bracket   - the motor bolts to its face (finger guard round the gear, as before); a flange along the motor's
                    4 o'clock side bolts to the rail's block; beside it the latch's ear, with the hole the plunger's
                    pin drops into, and the end that presses the switch; on the motor's dash side the tab the spring's
                    strip is clamped to
  gear            - 16 teeth, no roller, the teeth's outer ends pointed so they find the gaps between the steering
                    wheel teeth as it slides in
  spool           - the spring's drum, turning on an M4 screw
  board cover     - the pop-off/slide mount's cover over the controller board, turned a quarter: the car plug points
                    at 6 o'clock, the motor plug at the dash
  steering wheel teeth - the slide mount's short teeth, the inner end of every tooth pointed to match the gear

Bought: an MGN12H block on a 100 mm MGN12 rail; a KIPP K0338.11105 spring plunger (M10 x 1, 5 mm pin) and an
M10 x 1 thin nut; a Lee Spring LCF 040 08 050S constant force spring; the Omron SS-5GL2 power switch (as before).

The carrier frame is popparts.py's: origin on the motor's front face on the shaft, +z out along the shaft (away from
the column), +y towards the dash, x across (+x towards 6 o'clock at this mount). Everything here is drawn with the motor
on the teeth; slid in s mm, the moving parts are at z - s.
"""
import math

import manifold3d
import numpy as np
from manifold3d import CrossSection, Manifold

import faceparts as FP
import gears as GR
import mountparts as MP
import popparts as PP
import slideparts as SP
from cadlib import box, clean, cyl, cyl_x, cyl_y, hex_prism_x, prism_x, sector, union
from params import (
  BACKLASH,
  M3_CLEAR,
  M3_PILOT,
  MOTOR_PLATE_T,
  NEMA,
  NEMA_BOSS,
  NEMA_HOLES,
  NEMA_LEN,
  SHAFT_ACROSS_FLAT,
  SHAFT_D,
  SHAFT_FLAT_LEN,
  SHAFT_LEN,
)

H = NEMA / 2
MOUNT_DEG = SP.MOUNT_DEG_S        # -70: the motor at about 5:20
STROKE = 40.0                     # slid in this far, the gear, the guard and the shaft's end are 13 mm inside the steering
                                  # wheel's inside edge (12.5 frees the gear from the teeth)

# ***** bought: HIWIN MGN12H block on an MGN12 rail (HIWIN's catalogue) *****
RAIL_W, RAIL_H = 12.0, 8.0
RAIL_LEN = 100.0
RAIL_PITCH, RAIL_E = 25.0, 12.5   # holes every 25 mm; a 100 mm rail has its end holes 12.5 from its ends (the plate's
RAIL_SLOT = 3.0                   # slots take +- this, for rails cut with other end distances)
RAIL_CBORE = (6.0, 3.5, 4.5)      # the rail's counterbored holes: head, hole, depth
BLOCK_W, BLOCK_L, BLOCK_H, BLOCK_H1 = 27.0, 47.6, 13.0, 3.0   # width, length, rail's foot to block's top, rail's foot
BLOCK_HOLES = 20.0                                             # to block's underside; 4 x M3 x 3.5 deep, 20 x 20

# ***** the stack across (x), motor side to plate *****
FLANGE_GAP = 2.65                 # the bracket's flange stands this far off the motor's side
FLANGE_T = 6.0
X_FL = (-H - FLANGE_GAP - FLANGE_T, -H - FLANGE_GAP)          # the flange (-29.8, -23.8)
X_BLOCK_TOP = X_FL[0]
X_RAIL_BOT = X_BLOCK_TOP - BLOCK_H                             # -42.8: the rail's foot, the plate's inner face
X_BLOCK_BOT = X_RAIL_BOT + BLOCK_H1
X_RAIL_TOP = X_RAIL_BOT + RAIL_H
PLATE_T = 6.0
X_PL = (X_RAIL_BOT - PLATE_T, X_RAIL_BOT)                      # the plate (-48.8, -42.8)

# ***** along the shaft (z) and across the other way (y) *****
Y_RAIL = -5.0                     # the rail's middle: off the motor's middle towards the driver, to leave room beside it
Z_RAIL = (-96.0, RAIL_LEN - 96.0)  # the rail's ends
Z_BLOCK = -28.0                   # the block's middle, motor on
BLOCK_Z = (Z_BLOCK - BLOCK_L / 2, Z_BLOCK + BLOCK_L / 2)
FL_Y = (Y_RAIL - 15.0, Y_RAIL + 15.0)            # the flange, across
FL_Z = (BLOCK_Z[0] - 0.5, MOTOR_PLATE_T)         # ... and along: from just past the block to the bracket's face
GUARD_FRONT = 24.5                # the finger guard reaches this far out (the shaft ends at 23)

# ***** the latch: KIPP K0338.11105 spring plunger (Zoro's listing of KIPP's data) *****
KIPP = {"part": "KIPP K0338.11105", "thread_d": 10.0, "thread_len": 15.0, "pin_d": 5.0, "pin_out": 5.0,
        "body_d": 13.0, "body_len": 38.5, "knob_d": 21.0, "knob_len": 15.9, "len": 43.5, "push_N": (5.0, 12.0)}
NUT_M10 = (17.0, 5.0)             # M10 x 1 thin nut: across flats, thick
PIN_Y = 20.0                      # the plunger's axis (y)
BOSS_OUT = 0.8                    # a boss on the plate's outer face under the plunger's collar
X_COLLAR = X_PL[0] - BOSS_OUT                                  # -49.6
X_THREAD_END = X_COLLAR + KIPP["thread_len"]                    # -34.6
X_PIN_TIP = X_THREAD_END + KIPP["pin_out"]                      # -29.6: the pin's tip, out
PIN_IN = 3.5                      # the pin goes this far into the ear's hole
X_EAR = (X_PIN_TIP - PIN_IN, X_FL[1])                           # the ear (-33.1, -23.8)
EAR_Y = (FL_Y[1], 30.0)
EAR_Z = (-25.0, 0.0)              # its outer end (+z) presses the switch and meets the stop
BEVEL_DEG = 30.0                  # the ramp at the ear's outer end that pushes the pin back as it comes in
BEVEL_TOP = X_PIN_TIP + 0.5
BEVEL_LEN = (BEVEL_TOP - X_EAR[0]) / math.tan(math.radians(BEVEL_DEG))
BEVEL_Y = (PIN_Y - 3.5, PIN_Y + 3.5)
EAR_FLAT = 3.0                    # flat between the ramp and the hole
PIN_HOLE_D = 5.3
PIN_Z = EAR_Z[1] - BEVEL_LEN - EAR_FLAT - PIN_HOLE_D / 2        # the plunger's axis (z)
STOP_GAP = 0.2                    # pulled out against the stop, the ear is this far past where the pin holds it

# ***** the power switch: Omron SS-5GL2 (mountparts.py), pressed end on by the ear's outer end *****
SW_X = (-29.7, -29.7 + MP.SW_THICK)        # its thickness (x): the roller over the ear's end everywhere
SW_Y0 = 18.0                               # its length runs along y from here (the roller over the ear: see the guide)
SW_HOLES_Z = EAR_Z[1] + MP.SW_OP - MP.SW_PRESS   # the holes' line: the ear presses the roller 0.6 past its click
SW_SLOT = 2.0                              # the screws slide +- this along z to set it
HOLDER_X = (SW_X[0] - 3.5, SW_X[0])        # the wall it hangs on
HOLDER_Y = (16.5, SW_Y0 + MP.SW_LEN + 1.5)
HOLDER_Z = (EAR_Z[1] + STOP_GAP, SW_HOLES_Z + MP.SW_H / 2 + 2.0)
M2_CLEAR, M2_NUT_AF, M2_NUT_T = MP.M2_CLEAR, MP.M2_NUT_AF, MP.M2_NUT_T

# ***** the spring: Lee Spring LCF 040 08 050S constant force spring (Lee Spring's catalogue) *****
CF = {"part": "Lee Spring LCF 040 08 050S", "load_N": 11.70, "w": 12.70, "t": 0.20, "id": 14.99, "length": 762.0,
      "initial_defl": 31.50, "working_defl": 610.0, "life": 4000}
DRUM_D = 17.5                     # 17% over the spring's inside (Lee: 10 to 20%)
SPOOL_Y = (31.0, 44.2)            # the drum between its flanges
SPOOL_FLANGE = (25.0, 1.2)
SPOOL_Z = -76.0                   # the spool's axle (an M4 x 25 screw along y), on the plate
STRIP_X = -18.3                   # the strip leaves the coil here and runs out along the motor's dash side
CLAMP_Z = -2.5                    # its end is clamped to the bracket's tab here (motor on)
TAB = ((STRIP_X, -12.0), (26.0, 49.0), (-10.0, MOTOR_PLATE_T))   # the bracket's tab the strip is clamped to: x, y, z
CLAMP_Y = ((SPOOL_Y[0] + SPOOL_Y[1]) / 2 - CF["w"] / 2 - 2.2, (SPOOL_Y[0] + SPOOL_Y[1]) / 2 + CF["w"] / 2 + 2.2)
M4_PILOT = 3.4
POST = ((X_RAIL_BOT, -24.0), (24.0, SPOOL_Y[0] - SPOOL_FLANGE[1] - 0.4), (SPOOL_Z - 8.0, SPOOL_Z + 8.0))


def coil_outer_r(extended: float) -> float:
  """The coil's outside radius on the drum with this much strip pulled out (its cross-section: the strip still wound)."""
  wound = CF["length"] - extended
  return math.sqrt((DRUM_D / 2) ** 2 + wound * CF["t"] / math.pi)


SPOOL_X = STRIP_X - coil_outer_r(CLAMP_Z - STROKE - SPOOL_Z)     # the axle (x): the strip leaves the coil at STRIP_X

# ***** the stops *****
BUMPER_Z = (Z_RAIL[0] - 2.0, FL_Z[0] - STROKE - 0.2)            # slid in, the flange's end stops on this
BUMPER = ((X_RAIL_TOP + 0.6, X_FL[1] - 0.4), (Y_RAIL - 9.0, Y_RAIL + 9.0))

# ***** the gear *****
GEAR_TEETH_Z = (7.0, 19.5)        # along the shaft from the motor's face: radius 160 to 172.5 (the teeth: 160.5 to 171.5)
GEAR_HUB = (8.0, 22.5)            # a hub out to the shaft's end: radius, end
ROOF_DEG = 40.0                   # the pointed ends: each side sloped this much off square


def prism_y(points_xz, y0, y1) -> Manifold:
  """Extrudes an (x, z) outline along Y from y0 to y1 (either winding)."""
  cs = CrossSection([list(points_xz)])
  if cs.area() < 1e-9:
    cs = CrossSection([list(points_xz)[::-1]])
  # extruded points are (u=x, v=z, w); map (u, v, w) -> (u, w + y0, v): a reflection, so flip the winding back
  m = cs.extrude(y1 - y0).transform([[1, 0, 0, 0], [0, 0, 1, y0], [0, 1, 0, 0]])
  return m if m.volume() > 0 else Manifold.compose([m])


def _box_poly(pts_xz, y0, y1) -> Manifold:
  return Manifold.batch_hull([box(x - 1e-3, x + 1e-3, y0, y1, z - 1e-3, z + 1e-3) for x, z in pts_xz])


# ***** the gear *****

def gear_roofs(z1: float, u_max: float = 2.3, rho=(13.3, 18.6)) -> Manifold:
  """Cuts that point each tooth's outer end: in the plane across the tooth, its end falls ROOF_DEG off square on each
  side of the tooth's middle (gear frame before FG_PHASE: tooth 0 on +x)."""
  tb = math.tan(math.radians(ROOF_DEG))
  half = [Manifold.batch_hull([box(rho[0], rho[1], s * u, s * u + 1e-3, z1 - u * tb, z1 + 1.0) for u in (0.0, u_max)])
          for s in (1, -1)]
  one = half[0] + half[1]
  return union([one.rotate((0, 0, k * 360.0 / FP.FACE_MOTOR_TEETH)) for k in range(FP.FACE_MOTOR_TEETH)])


def side_gear() -> Manifold:
  """Gear frame: z = 0 at the motor's front face, the shaft along +z. Teeth (outer ends pointed), a hub to the shaft's
  end, a D bore on the shaft's flat and an M3 x 8 set screw through a tooth gap onto the flat."""
  zt0, zt1 = GEAR_TEETH_Z
  teeth = GR.gear_outline(FP.FACE_MOTOR_TEETH, BACKLASH).extrude(zt1 - zt0).translate((0, 0, zt0))
  teeth = teeth - gear_roofs(zt1)
  hub = cyl(GEAR_HUB[0], zt1 - 0.5, GEAR_HUB[1], segments=96)
  part = (teeth + hub).rotate((0, 0, FP.FG_PHASE))
  r = SHAFT_D / 2 + 0.12
  flat_y = SHAFT_ACROSS_FLAT - SHAFT_D / 2 + 0.12
  d_shape = CrossSection.circle(r, 96) - CrossSection.square((2 * r + 2, 2 * r)).translate((-r - 1, flat_y))
  flat_from = SHAFT_LEN - SHAFT_FLAT_LEN
  part = part - d_shape.extrude(GEAR_HUB[1] + 1 - max(flat_from, zt0 - 1)).translate((0, 0, max(flat_from, zt0 - 1)))
  part = part - Manifold.cylinder(1.0, r + 0.8, r, 48).translate((0, 0, zt0))
  z_set = (zt0 + zt1) / 2.0
  hole = cyl_y(M3_PILOT / 2, 0.0, FP.R_P + 4, z=z_set, segments=32)
  return clean(part - hole)


def side_gear_teeth_only() -> Manifold:
  zt0, zt1 = GEAR_TEETH_Z
  teeth = GR.gear_outline(FP.FACE_MOTOR_TEETH, BACKLASH).extrude(zt1 - zt0).translate((0, 0, zt0)) - gear_roofs(zt1)
  return teeth.rotate((0, 0, FP.FG_PHASE))


# ***** the steering wheel teeth *****

class SideTeeth(SP.SlideTeeth):
  """The slide mount's short back teeth, centred on the motor at 5:20."""


def face_roofs(t: SideTeeth, u_max: float = 3.3) -> Manifold:
  """Cuts that point each steering wheel tooth's inner end (where the gear comes in): in the plane of the steering
  wheel, its end falls ROOF_DEG off square on each side of the tooth's middle. Only the teeth themselves (between their
  tips and the root plane) are cut."""
  tb = math.tan(math.radians(ROOF_DEG))
  r0 = FP.FACE_BAND[0]
  z0, z1 = t.z_tip - 1.0, t.z_root
  pts = [(r0 - 1.5, 0.0), (r0, 0.0), (r0 + u_max * tb, u_max), (r0 - 1.5, u_max)]
  wedge = CrossSection([pts]) + CrossSection([[(x, -y) for x, y in pts[::-1]]])
  one = wedge.extrude(z1 - z0).translate((0, 0, z0))
  n = t.n_teeth // 2
  return union([one.rotate((0, 0, (j + 0.5) * t.pitch_deg)) for j in range(-n, n)])


def side_teeth_solid(t: SideTeeth) -> Manifold:
  return clean(SP.slide_solid(t) - face_roofs(t))


def side_teeth(t: SideTeeth = None) -> Manifold:
  t = t or SideTeeth()
  return clean(side_teeth_solid(t) - FP.tie_slots(t, SP.slide_tie_angles(t)))


# ***** the motor bracket *****

def _face_plate() -> Manifold:
  t = MOTOR_PLATE_T
  outline = CrossSection.square((2 * MP.PLATE_HALF, 2 * MP.PLATE_HALF), center=True) + CrossSection.circle(MP.GUARD_OUT, 180)
  outline = outline ^ CrossSection.square((200, 200)).translate((-100, MP.PLATE_BOTTOM))
  # out to the flange, and the tab's root on the dash side
  outline = outline + CrossSection.square((X_FL[1] + 0.5 - X_FL[0], FL_Y[1] - FL_Y[0])).translate((X_FL[0], FL_Y[0]))
  outline = outline + CrossSection.square((TAB[0][1] - TAB[0][0], TAB[1][0] + 0.5 - MP.PLATE_HALF + 1.0)).translate(
    (TAB[0][0], MP.PLATE_HALF - 1.0))
  # clear of the switch and the stop (fixed) beside the guard
  outline = outline - CrossSection.square((40.0, 40.0)).translate((-22.3 - 40.0, HOLDER_Y[0] - 0.5))
  return outline.extrude(t)


def _guard() -> Manifold:
  t = MOTOR_PLATE_T
  shell = cyl(MP.GUARD_OUT, t - 0.01, GUARD_FRONT, segments=180) - cyl(MP.GUARD_IN, t - 1, GUARD_FRONT + 1, segments=180)
  lip = cyl(MP.GUARD_OUT, GUARD_FRONT - 1.6, GUARD_FRONT, segments=180) - \
    cyl(MP.GUARD_LIP_IN, GUARD_FRONT - 3, GUARD_FRONT + 1, segments=180)
  gw = FP.GUARD_WINDOW_F
  window = sector(MP.GUARD_OUT + 6, 270.0 - gw, 270.0 + gw).extrude(GUARD_FRONT + 4).translate((0, 0, t - 2))
  guard = (shell + lip) - window
  for sgn in (-1, 1):
    a = math.radians(270.0 + sgn * gw)
    rm = (MP.GUARD_IN + MP.GUARD_OUT) / 2
    guard = guard + cyl((MP.GUARD_OUT - MP.GUARD_IN) / 2 + 0.6, t - 0.01, GUARD_FRONT, rm * math.cos(a), rm * math.sin(a), 24)
  return guard


def ear_bevel() -> Manifold:
  """The ramp at the ear's outer end, over the pin's band: it pushes the pin back as the ear comes in under it."""
  pts = [(X_EAR[0] - 1.0, EAR_Z[1] - BEVEL_LEN - 0.01), (X_EAR[0], EAR_Z[1] - BEVEL_LEN), (BEVEL_TOP, EAR_Z[1]),
         (BEVEL_TOP, EAR_Z[1] + 1.0), (X_EAR[0] - 1.0, EAR_Z[1] + 1.0)]
  return prism_y(pts, BEVEL_Y[0], BEVEL_Y[1])


def side_bracket() -> Manifold:
  plate = _face_plate()
  guard = _guard()
  flange = box(X_FL[0], X_FL[1], FL_Y[0], FL_Y[1], FL_Z[0], FL_Z[1])
  ear = box(X_EAR[0], X_EAR[1], EAR_Y[0] - 0.5, EAR_Y[1], EAR_Z[0], EAR_Z[1])
  tab = box(TAB[0][0], TAB[0][1], TAB[1][0], TAB[1][1], TAB[2][0], TAB[2][1])
  part = union([plate, guard, flange, ear, tab])
  # the motor: its boss and its four screws (heads in the gear side, as before), and its body's room
  part = part - cyl(NEMA_BOSS / 2 + 0.4, -3, MOTOR_PLATE_T + 1, segments=128)
  for sx in (-1, 1):
    for sy in (-1, 1):
      x, y = sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2
      part = part - cyl(M3_CLEAR / 2, -1, MOTOR_PLATE_T + 1, x, y, 32) - \
        cyl(3.4, MOTOR_PLATE_T - MP.MOTOR_SCREW_CBORE, MOTOR_PLATE_T + 1, x, y, 32)
  part = part - box(-H - 0.3, H + 0.3, -H - 0.3, H + 0.3, -NEMA_LEN - 20, 0.0)
  # the plate's edge towards the driver cut back 45 degrees, as before
  a, y0 = FP.PLATE_CHAMFER, MP.PLATE_BOTTOM
  part = part - prism_x([(y0 - 1.0, MOTOR_PLATE_T - a - 1.0), (y0 + a + 1.0, MOTOR_PLATE_T + 1.0), (y0 - 1.0, MOTOR_PLATE_T + 1.0)],
                        -60.0, 60.0)
  # the block's four M3 x 6 screws, heads sunk in the flange's motor side
  for y in (Y_RAIL - BLOCK_HOLES / 2, Y_RAIL + BLOCK_HOLES / 2):
    for z in (Z_BLOCK - BLOCK_HOLES / 2, Z_BLOCK + BLOCK_HOLES / 2):
      part = part - cyl_x(M3_CLEAR / 2, X_FL[0] - 1.0, X_FL[1] + 1.0, y=y, z=z, segments=32)
      part = part - cyl_x(3.1, X_FL[1] - 3.2, X_FL[1] + 1.0, y=y, z=z, segments=32)
  # the latch: the pin's hole, and the ramp before it
  part = part - cyl_x(PIN_HOLE_D / 2, X_EAR[0] - 1.0, X_EAR[1] + 1.0, y=PIN_Y, z=PIN_Z, segments=48)
  part = part - ear_bevel()
  # the strip's two clamp screws (M3 x 6, washers on the strip), cut their own thread into the tab
  for y in CLAMP_Y:
    part = part - cyl_x(M3_PILOT / 2, TAB[0][0] - 1.0, TAB[0][1] + 1.0, y=y, z=CLAMP_Z, segments=24)
  return clean(part)


# ***** the mounting plate *****

def plate_outline_boxes() -> list:
  """The plate's parts (y, z ranges): along the rail; round the latch's nut; under the switch's holder; down to the
  spool's post."""
  return [((-16.0, 12.0), (BUMPER_Z[0], -16.0)), ((-13.0, 12.0), (-16.0, Z_RAIL[1])),
          ((8.0, 33.0), (PIN_Z - 13.0, Z_RAIL[1])), ((HOLDER_Y[0], HOLDER_Y[1]), (-2.0, HOLDER_Z[1])),
          ((12.0, POST[1][1]), (POST[2][0], PIN_Z - 12.0))]


def side_plate() -> Manifold:
  x0, x1 = X_PL
  parts = [box(x0, x1, y0, y1, z0, z1) for (y0, y1), (z0, z1) in plate_outline_boxes()]
  # the plunger's boss on the outside
  parts.append(cyl_x(8.5, X_COLLAR, x0 + 0.01, y=PIN_Y, z=PIN_Z, segments=64))
  # the switch's holder: the wall it hangs on, joined to the plate over its top; a stop beside it in the pin's band
  hx, hy, hz = HOLDER_X, HOLDER_Y, HOLDER_Z
  parts.append(box(hx[0], hx[1], hy[0], hy[1], hz[0], hz[1]))
  parts.append(box(x1 - 0.01, hx[0] + 0.01, hy[0], hy[1], hz[1] - 2.0, hz[1]))
  parts.append(box(hx[1] - 0.01, BEVEL_TOP + 4.6, hy[0], SW_Y0 - 0.3, hz[0], hz[0] + 7.0))
  # the spool's post
  (px0, px1), (py0, py1), (pz0, pz1) = POST
  parts.append(box(px0, px1, py0, py1, pz0, pz1))
  # the stop at the inner end: a bridge over the rail's end, its feet each side of the rail
  (bx0, bx1), (by0, by1) = BUMPER
  parts.append(box(bx0, bx1, by0, by1, BUMPER_Z[0], BUMPER_Z[1]))
  for ya, yb in ((by0, Y_RAIL - RAIL_W / 2 - 0.6), (Y_RAIL + RAIL_W / 2 + 0.6, by1)):
    parts.append(box(x1 - 0.01, bx0 + 0.01, ya, yb, BUMPER_Z[0], BUMPER_Z[1]))
  part = union(parts)
  # the rail's four M3 x 12 screws: slots along the rail, nuts sunk in the outer face
  for k in range(4):
    z = Z_RAIL[1] - RAIL_E - k * RAIL_PITCH
    part = part - Manifold.batch_hull([cyl_x(M3_CLEAR / 2, x0 - 1.0, x1 + 1.0, y=Y_RAIL, z=z + s, segments=24)
                                       for s in (-RAIL_SLOT, RAIL_SLOT)])
    part = part - Manifold.batch_hull([hex_prism_x(5.9, x0 - 1.0, x0 + 2.6, y=Y_RAIL, z=z + s) for s in (-RAIL_SLOT, RAIL_SLOT)])
  # the plunger: through the boss and the plate; its nut goes on the inside
  part = part - cyl_x(5.2, X_COLLAR - 1.0, x1 + 1.0, y=PIN_Y, z=PIN_Z, segments=64)
  # the switch's two M2 screws: slots along z through the wall, nuts in a hex slot on its plate side
  for dy in (MP.SW_LEN / 2 - MP.SW_PITCH / 2, MP.SW_LEN / 2 + MP.SW_PITCH / 2):
    y = SW_Y0 + dy
    part = part - Manifold.batch_hull([cyl_x(M2_CLEAR / 2, hx[0] - 1.0, hx[1] + 1.0, y=y, z=SW_HOLES_Z + s, segments=20)
                                       for s in (-SW_SLOT, SW_SLOT)])
    part = part - Manifold.batch_hull([hex_prism_x(M2_NUT_AF, hx[0] - 1.0, hx[0] + M2_NUT_T, y=y, z=SW_HOLES_Z + s)
                                       for s in (-SW_SLOT, SW_SLOT)])
  # the spool's M4 screw: cuts its own thread into the post
  part = part - cyl_y(M4_PILOT / 2, POST[1][0] - 1.0, POST[1][1] + 1.0, x=SPOOL_X, z=SPOOL_Z, segments=24)
  return clean(part)


# ***** the spool *****

def side_spool() -> Manifold:
  """Spool frame: its axle along y, y as fitted."""
  d, (y0, y1) = DRUM_D, SPOOL_Y
  fd, ft = SPOOL_FLANGE
  hub = cyl_y(d / 2, y0 - 0.01, y1 + 0.01, segments=96)
  fl = cyl_y(fd / 2, y0 - ft, y0, segments=96) + cyl_y(fd / 2, y1, y1 + ft, segments=96)
  return clean((hub + fl) - cyl_y(2.2, y0 - ft - 1.0, y1 + ft + 1.0, segments=32))


# ***** the board cover, turned a quarter *****

def side_board_cap() -> Manifold:
  """The slide mount's board cover without its cut-back corner, turned so its car plug points +x (6 o'clock) and its
  motor plug +y (the dash)."""
  z_back = -NEMA_LEN
  cs = SP._board_cs()
  outer = cs.offset(SP.CAP_GAP + SP.CAP_WALL, manifold3d.JoinType.Round, circular_segments=32)
  inner = cs.offset(SP.CAP_GAP, manifold3d.JoinType.Round, circular_segments=32)
  shell = outer.extrude(SP.CAP_DEPTH).translate((0, 0, z_back - SP.CAP_DEPTH)) - \
    inner.extrude(SP.CAP_DEPTH - SP.CAP_WALL + 0.01).translate((0, 0, z_back - SP.CAP_DEPTH + SP.CAP_WALL))
  w, up, th = SP.CAP_TONGUE
  x0, y0, x1, y1 = outer.bounds()
  z_in = z_back - SP.CAP_DEPTH + SP.CAP_WALL
  ts = SP.TIE_SLOT
  tongues = []
  for side, along in (("+x", 0.0), ("-x", 15.0), ("+y", -14.0), ("-y", 0.0)):
    if side == "+x":
      tg = box(H, H + th, along - w / 2, along + w / 2, z_back, z_back + up) + box(H - 0.5, x1, along - w / 2, along + w / 2, z_in, z_back)
      tg = tg - box(H + th - ts[1], x1 + 1, along - w / 2 - 1, along + w / 2 + 1, z_back + up - 2 - ts[0], z_back + up - 2)
    elif side == "-x":
      tg = box(-H - th, -H, along - w / 2, along + w / 2, z_back, z_back + up) + box(x0, -H + 0.5, along - w / 2, along + w / 2, z_in, z_back)
      tg = tg - box(x0 - 1, -H - th + ts[1], along - w / 2 - 1, along + w / 2 + 1, z_back + up - 2 - ts[0], z_back + up - 2)
    elif side == "+y":
      tg = box(along - w / 2, along + w / 2, H, H + th, z_back, z_back + up) + box(along - w / 2, along + w / 2, H - 0.5, y1, z_in, z_back)
      tg = tg - box(along - w / 2 - 1, along + w / 2 + 1, H + th - ts[1], y1 + 1, z_back + up - 2 - ts[0], z_back + up - 2)
    else:
      tg = box(along - w / 2, along + w / 2, -H - th, -H, z_back, z_back + up) + box(along - w / 2, along + w / 2, y0, -H + 0.5, z_in, z_back)
      tg = tg - box(along - w / 2 - 1, along + w / 2 + 1, y0 - 1, -H - th + ts[1], z_back + up - 2 - ts[0], z_back + up - 2)
    tongues.append(tg)
  part = union([shell] + tongues)
  part = part - box(-2.7, 14.3, 18.0, 30.0, -48.6, z_back + 0.01)
  part = part - box(-30.0, -20.0, -9.7, 7.3, -48.6, z_back + 0.01)
  return clean(part.rotate((0, 0, -90.0)))


# ***** bought parts and the motor, for the checks and the pictures *****

def motor_board() -> dict:
  """The motor (its own plug on its dash side) and the board, cover and plugs turned with the cover."""
  mb = SP.motor_board()
  rot = lambda m: m.rotate((0, 0, -90.0))
  return {"motor": mb["motor"], "board+cap": side_board_cap(), "car plug": rot(mb["car plug"]),
          "motor plug": rot(mb["motor plug"]), "motor's own plug": mb["motor's own plug"]}


def rail() -> Manifold:
  return box(X_RAIL_BOT, X_RAIL_TOP, Y_RAIL - RAIL_W / 2, Y_RAIL + RAIL_W / 2, Z_RAIL[0], Z_RAIL[1])


def block() -> Manifold:
  """The block, motor on (it rides the rail: its middle is cut away round the rail)."""
  b = box(X_BLOCK_BOT, X_BLOCK_TOP, Y_RAIL - BLOCK_W / 2, Y_RAIL + BLOCK_W / 2, BLOCK_Z[0], BLOCK_Z[1])
  return b - box(X_RAIL_BOT - 1.0, X_RAIL_TOP + 0.3, Y_RAIL - RAIL_W / 2 - 0.3, Y_RAIL + RAIL_W / 2 + 0.3, BLOCK_Z[0] - 1, BLOCK_Z[1] + 1)


def plunger(pin_back: float = 0.0) -> dict:
  """The plunger in the plate: its collar, thread and nut (fixed), and its pin pushed back pin_back mm (the knob comes
  out as far)."""
  k = KIPP
  x_body0 = X_COLLAR - (k["body_len"] - k["thread_len"] - k["knob_len"])
  fixed = union([cyl_x(k["thread_d"] / 2, X_COLLAR, X_THREAD_END, y=PIN_Y, z=PIN_Z, segments=48),
                 cyl_x(k["body_d"] / 2, x_body0, X_COLLAR, y=PIN_Y, z=PIN_Z, segments=48),
                 hex_prism_x(NUT_M10[0], X_PL[1], X_PL[1] + NUT_M10[1], y=PIN_Y, z=PIN_Z)])
  pin = cyl_x(k["pin_d"] / 2, X_THREAD_END - 0.01, X_PIN_TIP - pin_back, y=PIN_Y, z=PIN_Z, segments=32)
  knob = cyl_x(k["knob_d"] / 2, x_body0 - k["knob_len"] - pin_back, x_body0 - pin_back, y=PIN_Y, z=PIN_Z, segments=48)
  return {"fixed": fixed, "pin": pin, "knob": knob}


def switch(roller_down: float = 0.0) -> dict:
  """The switch in its holder: body, and the room its lever and roller take anywhere along its length (its roller sits
  near one end: fitted over the ear). roller_down: how far past where the ear's end is (motor on) the roller reaches."""
  body = box(SW_X[0], SW_X[1], SW_Y0, SW_Y0 + MP.SW_LEN, SW_HOLES_Z - MP.SW_H / 2, SW_HOLES_Z + MP.SW_H / 2)
  rc = (SW_X[0] + SW_X[1]) / 2
  lever = box(rc - 1.6, rc + 1.6, SW_Y0, SW_Y0 + MP.SW_LEN, EAR_Z[1] - roller_down, SW_HOLES_Z - MP.SW_H / 2 + 0.01)
  heads = union([cyl_x(1.9, SW_X[1], SW_X[1] + 1.6, y=SW_Y0 + dy, z=SW_HOLES_Z, segments=20)
                 for dy in (MP.SW_LEN / 2 - MP.SW_PITCH / 2, MP.SW_LEN / 2 + MP.SW_PITCH / 2)])
  return {"body": body + heads, "lever": lever}


def spring_parts(slide: float = 0.0) -> dict:
  """The spool's coil (fixed), the strip from it to the clamp (moving with the bracket: slid in `slide`), the clamp's
  washers and screw heads (moving), the axle screw (fixed)."""
  ext = CLAMP_Z - slide - SPOOL_Z
  ro = coil_outer_r(ext)
  coil = cyl_y(ro, SPOOL_Y[0], SPOOL_Y[1], x=SPOOL_X, z=SPOOL_Z, segments=64)
  y0 = (SPOOL_Y[0] + SPOOL_Y[1]) / 2 - CF["w"] / 2
  strip = box(STRIP_X - 0.2, STRIP_X, y0, y0 + CF["w"], SPOOL_Z, CLAMP_Z + 5.0 - slide)
  clamp = union([cyl_x(3.5, STRIP_X - 0.7, STRIP_X - 0.2, y=y, z=CLAMP_Z - slide, segments=24) +
                 cyl_x(2.75, STRIP_X - 3.7, STRIP_X - 0.7, y=y, z=CLAMP_Z - slide, segments=24) for y in CLAMP_Y])
  axle = cyl_y(2.0, POST[1][0], SPOOL_Y[1] + SPOOL_FLANGE[1] + 0.8, x=SPOOL_X, z=SPOOL_Z, segments=24) + \
    cyl_y(3.5, SPOOL_Y[1] + SPOOL_FLANGE[1] + 0.8, SPOOL_Y[1] + SPOOL_FLANGE[1] + 4.8, x=SPOOL_X, z=SPOOL_Z, segments=24) + \
    cyl_y(4.5, SPOOL_Y[1] + SPOOL_FLANGE[1], SPOOL_Y[1] + SPOOL_FLANGE[1] + 0.8, x=SPOOL_X, z=SPOOL_Z, segments=24)
  return {"coil": coil, "strip": strip, "clamp": clamp, "axle": axle}


def block_screws() -> Manifold:
  return union([cyl_x(2.75, X_FL[1] - 3.2, X_FL[1] - 0.01, y=y, z=z, segments=24)
                for y in (Y_RAIL - BLOCK_HOLES / 2, Y_RAIL + BLOCK_HOLES / 2)
                for z in (Z_BLOCK - BLOCK_HOLES / 2, Z_BLOCK + BLOCK_HOLES / 2)])


# ***** placing *****

def to_wheel(m: Manifold, mount_deg: float = MOUNT_DEG) -> Manifold:
  Rm = PP.rot_z(mount_deg)
  return PP.place(m, Rm @ PP.R_POP, Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P]))


def slid(m: Manifold, s: float) -> Manifold:
  """A moving part (drawn motor on) slid in s mm."""
  return m.translate((0.0, 0.0, -s)) if s else m


def pin_back_at(s: float) -> float:
  """How far the ear holds the plunger's pin back with the bracket slid in s mm (0: in its hole, or out past the ear)."""
  rel = PIN_Z + s                            # where the pin is along the ear (ear's frame, motor on)
  hole0, hole1 = PIN_Z - PIN_HOLE_D / 2, PIN_Z + PIN_HOLE_D / 2
  pin_r = KIPP["pin_d"] / 2
  top = EAR_Z[1]
  if rel - pin_r >= top:
    return 0.0                               # past the ear's end: out
  # the ear's face under the pin: the most it holds the pin back over the pin's width
  def face_back(z):
    if hole0 < z < hole1:
      return 0.0
    if z < EAR_Z[0] or z > top:
      return 0.0
    if z > top - BEVEL_LEN:
      return max(0.0, (BEVEL_TOP - (BEVEL_TOP - X_EAR[0]) * (top - z) / BEVEL_LEN) * -1.0 + X_PIN_TIP) if False else \
        max(0.0, X_PIN_TIP - (BEVEL_TOP - (BEVEL_TOP - X_EAR[0]) * (top - z) / BEVEL_LEN))
    return X_PIN_TIP - X_EAR[0]
  zs = np.linspace(rel - pin_r, rel + pin_r, 21)
  if hole0 <= rel - pin_r and rel + pin_r <= hole1:
    return 0.0
  return float(max(face_back(z) for z in zs))

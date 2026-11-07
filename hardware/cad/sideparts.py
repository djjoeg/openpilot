"""
The side-slide mount: the motor at about 5:20 behind the steering wheel, its shaft pointing out at the steering wheel
and its gear on the back teeth, slides along its own shaft in towards the middle of the steering wheel to come off the
teeth. A lever on the motor's bracket sticks out through an L-shaped slot in the mounting plate (where the latch's knob
was). Pull the lever out along the slot and the motor slides out onto the teeth; at the slot's outer end, pull it
towards you into the notch and it is latched. Push it away from you, out of the notch, and the spring pulls the motor in;
if the spring doesn't, push the lever in along the slot. A second notch at the slot's inner end parks it there.

  mounting plate  - fixed. Carries the rail, the lever's slot and its two notches, the power switch and the spring's
                    spool. A tongue at its dash end carries the foot: a flat plate that lies under the lower column
                    cover's underside and is held by the cover's own screw under the key cylinder (a longer one of the
                    same thread), through a window that takes the screw wherever it falls
  motor bracket   - the motor bolts to its face (finger guard round the gear, as before); a flange along the motor's
                    4 o'clock side bolts to the rail's block; beside it the ear, a fork round the lever's hub, whose
                    outer end presses the switch; on the motor's dash side the tab the spring's strip is clamped to
  lever           - turns on an M4 x 25 screw across the ear's fork (its head sunk in the inner lug, its thread cut
                    into the outer one); its arm runs out through the plate's slot to a knob
  foot pad        - a flat plate under the foot that bridges the window: the cover's screw goes through its slot
  foot shim       - the same outline, 2 mm thick; one to three between the foot and the cover's underside
  strip clamp     - a small bar that pinches the spring's strip against the tab (two M3 screws)
  gear            - 16 teeth, no roller, the teeth's outer ends pointed so they find the gaps between the steering
                    wheel teeth as it slides in
  spool           - the spring's drum, turning on an M4 screw
  board cover     - the pop-off/slide mount's cover over the controller board, turned a quarter: the car plug points
                    at 6 o'clock, the motor plug at the dash
  steering wheel teeth - three sets, the same piece with 10, 14 or 18 teeth (10.8, 15.2 or 19.5 degrees each way); the
                    inner end of every tooth pointed to match the gear

Bought: an MGN12H block on a 100 mm MGN12 rail; a Lee Spring LCF 040 08 050S constant force spring; the Omron SS-5GL2
power switch (as before); screws.

The carrier frame is popparts.py's: origin on the motor's front face on the shaft, +z out along the shaft (away from
the column), +y towards the dash, x across (+x towards 6 o'clock at this mount). Everything here is drawn with the motor
on the teeth; slid in s mm, the moving parts are at z - s.
"""
import itertools
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
PLATE_T = 6.8
X_PL = (X_RAIL_BOT - PLATE_T, X_RAIL_BOT)                      # the plate (-49.6, -42.8)

# ***** along the shaft (z) and across the other way (y) *****
Y_RAIL = -5.0                     # the rail's middle: off the motor's middle towards the driver, to leave room beside it
Z_RAIL = (-96.0, RAIL_LEN - 96.0)  # the rail's ends
Z_BLOCK = -28.0                   # the block's middle, motor on
BLOCK_Z = (Z_BLOCK - BLOCK_L / 2, Z_BLOCK + BLOCK_L / 2)
FL_Y = (Y_RAIL - 15.0, Y_RAIL + 15.0)            # the flange, across
FL_Z = (BLOCK_Z[0] - 0.5, MOTOR_PLATE_T)         # ... and along: from just past the block to the bracket's face
FLANGE_TRIM_Z = math.sqrt(160.0 ** 2 - (H + FLANGE_GAP + FLANGE_T) ** 2) - PP.R_FACE_P - 0.3   # see side_bracket
GUARD_FRONT = 24.5                # the finger guard reaches this far out (the shaft ends at 23)

# ***** the lever: on a screw across the bracket's ear, out through an L-shaped slot in the plate *****
# Its arm leaves the ear towards 4 o'clock, through the plate to a knob outside it. It runs along the slot swung SLOT_DEG
# towards the dash. Pulled out against the stop, it swings back towards you, straight out, into the notch at the slot's
# outer end; the spring then pulls its arm onto the notch's floor, which sets where the motor sits on the teeth. So the
# knob is nearest you when latched. The notch at the inner end takes it the same way, slid in, so the motor stays in
# without the spring. Drawn here as latched: motor out, the lever straight out.
X_EAR = (-36.0, -22.5)            # the ear, across: a fork round the lever's hub, on the flange's dash end
EAR_Y = (FL_Y[1], 30.0)
EAR_Z = (-26.5, 0.0)              # its outer end (+z) presses the switch and meets the stop
LUG_IN_Y1 = 28.0                  # the inner lug stops short of the spool's post towards the dash (slid in, they're level)
LEVER_Z = (-18.5, -6.5)           # the lever's thickness, along the shaft (motor out)
LUG_GAP = 0.3                     # each side of its hub, between the fork's two lugs
PIVOT = (-29.25, 20.0)            # the screw's axis (x, y), along the shaft
HUB_R = 6.0
# The pivot is an M4 x 20 socket head screw (ISO 4762: head 7 across, 4 tall) in from the ear's inner end: its head
# sunk in the inner lug, its shank through the lug and the lever, into an M4 nut in a pocket in the outer lug's inner
# face (the lever's hub covers the pocket), so the ear's outer face (the switch's roller rides on it) stays whole. The
# screw carries no pull: snug, not tight, so the lever swings freely.
PIVOT_SCREW_LEN, PIVOT_HEAD_D, PIVOT_HEAD_H = 20.0, 7.0, 4.0
PIVOT_CBORE = (PIVOT_HEAD_D + 0.6, PIVOT_HEAD_H + 0.2)            # the head's counterbore: across, deep
PIVOT_HEAD_Z = (EAR_Z[0] + 0.2, EAR_Z[0] + 0.2 + PIVOT_HEAD_H)    # the head sits here
PIVOT_END_Z = PIVOT_HEAD_Z[1] + PIVOT_SCREW_LEN                   # the screw's end: short of the ear's outer face
PIVOT_CLEAR_D, LEVER_BORE_D = 4.4, 4.3                            # clearance through the lugs, the lever's bore
M4_NUT_AF, M4_NUT_T = 7.0, 3.2                                    # ISO 4032 M4 nut: across flats, thick
PIVOT_NUT_Z = (LEVER_Z[1] + LUG_GAP, LEVER_Z[1] + LUG_GAP + M4_NUT_T + 0.2)   # its pocket, from the outer lug's inner face
SHANK_W = 9.0                     # the lever's arm, across (y)
KNOB_D, KNOB_R = 50.0, 12.0       # the knob's middle from the pivot, its radius
SLOT_DEG = 42.0                   # in the slot the lever is swung this far towards the dash; in a notch, straight out
SLOT_CLEAR = 0.4                  # round the arm in the slot and the notches, but on the notches' load faces
BRIDGE = ((-30.0, X_EAR[1]), (HUB_R + 0.6 + PIVOT[1], EAR_Y[1]))   # joins the lugs past the hub, on the motor's side
STOP_GAP = 0.2                    # pulled out against the stop, the ear is this far past where the notch holds it
PLATE_SLOT_Y = 42.0               # the plate reaches this far towards the dash round the notches
PLATE_SLOT_Z = -62.0              # ... and this far in, past the inner notch
LEVER_USE_N = 20.0                # pulling the lever out or pushing it in, every time: about 2 kg (more than it needs)
LEVER_YANK_N = 100.0              # a hard yank on the knob: about 10 kg (an estimate on the high side)

# ***** the power switch: Omron SS-5GL2 (mountparts.py), pressed end on by the ear's outer end *****
SW_X = (-30.0, -30.0 + MP.SW_THICK)        # its thickness (x): the roller over the ear's end everywhere
SW_Y0 = 18.0                               # its length runs along y from here (the roller over the ear: see the guide)
SW_HOLES_Z = EAR_Z[1] + MP.SW_OP - MP.SW_PRESS   # the holes' line: the ear presses the roller 0.6 past its click
SW_SLOT = 2.0                              # the screws slide +- this along z to set it
HOLDER_X = (X_RAIL_BOT, SW_X[0])           # the block it hangs on, out from the plate
HOLDER_Y = (16.5, SW_Y0 + MP.SW_LEN + 1.5)
HOLDER_Z = (EAR_Z[1] + STOP_GAP, SW_HOLES_Z + MP.SW_H / 2 + 2.0)
STOP_X = (SW_X[0], -24.5)                  # the stop beside the switch that the ear's end meets, pulled out
M2_CLEAR, M2_NUT_AF, M2_NUT_T = MP.M2_CLEAR, MP.M2_NUT_AF, MP.M2_NUT_T
SW_SCREW_LEN = 12.0                        # M2 x 12: through the switch into a nut in a slot in the block
SW_NUT_X = (SW_X[1] - SW_SCREW_LEN + 0.2, SW_X[1] - SW_SCREW_LEN + 0.2 + M2_NUT_T)

# ***** the spring: Lee Spring LCF 040 08 050S constant force spring (Lee Spring's catalogue) *****
CF = {"part": "Lee Spring LCF 040 08 050S", "load_N": 11.70, "w": 12.70, "t": 0.20, "id": 14.99, "length": 762.0,
      "initial_defl": 31.50, "working_defl": 610.0, "life": 4000}
DRUM_D = 17.5                     # 17% over the spring's inside (Lee: 10 to 20%)
SPOOL_Y = (30.4, 43.6)            # the drum: the post's face on one side, the spool's flange on the other
SPOOL_FLANGE = (25.0, 1.2)
SPOOL_Z = -76.0                   # the spool's axle (an M4 x 20 screw along y, through a washer), on the plate
AXLE_LEN = 20.0                   # ... it cuts its own thread 4.8 mm into the post
STRIP_X = -18.3                   # the strip leaves the coil here and runs out along the motor's dash side
CLAMP_Z = -2.5                    # its end is clamped to the bracket's tab here (motor on)
TAB = ((STRIP_X, -12.0), (26.0, 49.0), (-10.0, MOTOR_PLATE_T))   # the bracket's tab the strip is clamped to: x, y, z
CLAMP_Y = ((SPOOL_Y[0] + SPOOL_Y[1]) / 2 - CF["w"] / 2 - 2.2, (SPOOL_Y[0] + SPOOL_Y[1]) / 2 + CF["w"] / 2 + 2.2)
# The strip's end is pinched between the tab and a small printed bar by two M3 x 10 screws beside its edges. The screws
# go in from the tab's 6 o'clock side (the latch's ear is in the way on the other) and cut their own thread in the bar.
CLAMP_BAR = ((STRIP_X - 0.2 - 4.0, STRIP_X - 0.2), (CLAMP_Y[0] - 3.5, CLAMP_Y[1] + 3.5), (CLAMP_Z - 4.0, CLAMP_Z + 4.0))
M4_PILOT = 3.4
POST = ((X_RAIL_BOT, -24.0), (22.0, SPOOL_Y[0] - 0.4), (SPOOL_Z - 8.0, SPOOL_Z + 8.0))
POST_NARROW = (26.5, -25.5)       # below this y the post stops short at this x: the board cover passes beside it, slid in
POST_FACE = 13.5                  # the post's face round the axle (radius) that guides the coil's side


def coil_outer_r(extended: float) -> float:
  """The coil's outside radius on the drum with this much strip pulled out (its cross-section: the strip still wound)."""
  wound = CF["length"] - extended
  return math.sqrt((DRUM_D / 2) ** 2 + wound * CF["t"] / math.pi)


SPOOL_X = STRIP_X - coil_outer_r(CLAMP_Z - STROKE - SPOOL_Z)     # the axle (x): the strip leaves the coil at STRIP_X

# ***** the stops *****
BUMPER_Z = (Z_RAIL[0] - 2.0, FL_Z[0] - STROKE - 0.2)            # slid in, the flange's end stops on this
BUMPER = ((X_RAIL_TOP + 0.6, X_FL[1] - 0.4), (Y_RAIL - 9.0, Y_RAIL + 9.0))

# ***** the plate's fixing: the foot under the lower column cover, on the cover's own screw under the key cylinder *****
#
# Steering wheel frame (mm): z along the column towards you, 0 at the middle of the round part you hold; y up; x to your
# right. The lower column cover's underside is a level plane at COVER_Y (carscene.py: -100.5 to -106.9 over the range of
# D the design is drawn for), its screw under the key cylinder at CUP_X, CUP_Z (65.9 to 72, -120.5 to -137.6, each 4 mm
# either way). The plate's tongue runs on towards the dash along the plate's own plane, and the foot stands out from it
# level, 8 mm thick, its top FOOT_Y[1] just under the lowest underside; shims make up the rest. The window takes the
# screw wherever it falls (with the mount turned up to 3 degrees either way), and the foot bar under the foot bridges
# the window: the screw's head sits on the bar. The foot starts 2 mm behind where the bracket's tab reaches, slid in.
D_FOOT = (107.0, 125.0)           # the range of carscene.D the foot is drawn for (the cover's front edge at least 70 mm
                                  # behind the back of the round part you hold)
FOOT_Y = (-116.0, -108.0)         # the foot: its underside and its top
FOOT_X = (46.0, 92.0)             # ... across: its left end clear of the cover on the back of the steering wheel, its
                                  # right end flush with the plate's outer face (so the plate prints on that face)
FOOT_Z = (-150.0, -110.5)         # ... along the column: from 2 mm behind the bracket's tab, slid in, to well past the screw
WINDOW_X, WINDOW_Z = (54.0, 84.0), (-144.0, -116.0)   # the screw's window
TONGUE_R = (136.0, 160.0)         # the tongue: the plate's plane, this band of radius, out to the foot's far end
BAR = (40.0, 12.0, 16.0)          # the foot bar: across (x), along (z), thick; its slot along x takes the screw. Thick,
                                  # because the screw's clamp bends it across the window
BAR_SLOT_W = 4.5
SHIM_T = 2.0                      # a shim: the foot's outline and window, this thick
COVER_SCREW = ("a 4.2 x 45 mm (#8 x 1 3/4 in) pan head sheet metal screw with an M4 washer, in place of the cover's own 4 x 16 "
               "tapping screw under the key cylinder (the same pitch, 1.41 mm; it goes through the bar, the foot and the shims)")
FOOT_CLAMP_N = 600.0              # the screw's clamp on the foot: an estimate on the low side (a 4.2 mm screw into steel,
                                  # tightened with a screwdriver by hand, reaches about 1000 N)

# ***** the gear *****
GEAR_TEETH_Z = (7.0, 19.5)        # along the shaft from the motor's face: radius 160 to 172.5 (the teeth: 160.5 to 171.5)
GEAR_HUB = (8.0, 22.5)            # a hub out to the shaft's end: radius, end
ROOF_DEG = 40.0                   # the pointed ends: each side sloped this much off square


def prism_y(points_xz, y0, y1) -> Manifold:
  """Extrudes an (x, z) outline along Y from y0 to y1 (either winding)."""
  cs = CrossSection([list(points_xz)])
  if cs.area() < 1e-9:
    cs = CrossSection([list(points_xz)[::-1]])
  # extruded points are (u=x, v=z, w); map (u, v, w) -> (u, y1 - w, v), a proper rotation
  return cs.extrude(y1 - y0).transform([[1, 0, 0, 0], [0, 0, -1, y1], [0, 1, 0, 0]])


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

TEETH_SETS = {10: "straight roads", 14: "highway", 18: "winding roads"}   # teeth on the piece: 10.8, 15.2, 19.5 degrees each way
N_PIECE_MIN = FP.N_TEETH_SHORT    # a set with fewer teeth keeps the 14-tooth piece's length: its zip tie slots need it


class SideTeeth(SP.SlideTeeth):
  """The slide mount's back teeth, centred on the motor at 5:20: n_teeth of them (10, 14 or 18). The piece's length past
  the teeth (the smooth run-out, the ramps and the zip tie slots) is that of a piece with at least 14 teeth."""

  def __init__(self, n_teeth: int = FP.N_TEETH_SHORT, **kw):
    super().__init__(n_teeth=n_teeth, **kw)
    n_piece = max(n_teeth, N_PIECE_MIN)
    self.roll_half = n_piece / 2 * self.pitch_deg + FP.ROLL_PAST_TEETH
    self.lead_end = self.roll_half + FP.END_LEAD_IN
    self.half = self.lead_end + self.chamfer_deg
    self.joint_deg = None
    self.reach_deg = round(self.teeth_half, 1)


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


# the set's number (its reach in degrees, the car setup's answer) cut 0.6 mm into the channel's outer wall, just past
# the middle towards 4 o'clock (over the lower bar's junction, where no zip tie goes): 3 x 5 pixel digits, 2 mm pixels
DIGITS = {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111", "4": "101101111001001",
          "5": "111100111001111", "6": "111100111101111", "7": "111001001001001", "8": "111101111101111", "9": "111101111001111"}
MARK_PX, MARK_DEPTH, MARK_Z0, MARK_DEG0 = 2.0, 0.6, -29.0, 3.0


def number_mark(t: "SideTeeth") -> Manifold:
  """The digits of the set's reach, cut into the outer wall: read from outside the steering wheel, the piece on the car
  (the front edge up, 4 o'clock to the left)."""
  text = str(round(t.teeth_half))
  w = math.degrees(MARK_PX / t.w_out)
  cuts = []
  a = MARK_DEG0 + (4 * len(text) - 1) * w        # seen from outside, 4 o'clock is to the left: the text runs down in angle
  for ch in text:
    px = DIGITS[ch]
    for row in range(5):
      for col in range(3):
        if px[row * 3 + col] == "1":
          a1 = a - col * w
          z1 = MARK_Z0 + (5 - row) * MARK_PX
          cuts.append(FP.polar_box(t.w_out - MARK_DEPTH, t.w_out + 1.0, a1 - w, a1, z1 - MARK_PX, z1, step_deg=0.3))
    a -= 4 * w
  return union(cuts)


def side_teeth(t: SideTeeth = None) -> Manifold:
  t = t or SideTeeth()
  return clean(side_teeth_solid(t) - FP.tie_slots(t, SP.slide_tie_angles(t)) - number_mark(t))


# ***** the motor bracket *****

def _face_plate() -> Manifold:
  t = MOTOR_PLATE_T
  outline = CrossSection.square((2 * MP.PLATE_HALF, 2 * MP.PLATE_HALF), center=True) + gothic(MP.GUARD_OUT)
  outline = outline ^ CrossSection.square((200, 200)).translate((-100, MP.PLATE_BOTTOM))
  # out to the flange, and the tab's root on the dash side
  outline = outline + CrossSection.square((X_FL[1] + 0.5 - X_FL[0], FL_Y[1] - FL_Y[0])).translate((X_FL[0], FL_Y[0]))
  outline = outline + CrossSection.square((TAB[0][1] - TAB[0][0], TAB[1][0] + 0.5 - MP.PLATE_HALF + 1.0)).translate(
    (TAB[0][0], MP.PLATE_HALF - 1.0))
  # clear of the switch and the stop (fixed) beside the guard
  outline = outline - CrossSection.square((40.0, 40.0)).translate((-22.3 - 40.0, HOLDER_Y[0] - 0.5))
  return outline.extrude(t)


def gothic(r: float, segments: int = 180) -> CrossSection:
  """A circle of radius r with a 45 degree point on its +y side (towards the dash): printed lying on its -y side, its
  top needs no support."""
  k = r / math.sqrt(2.0)
  return CrossSection.circle(r, segments) + CrossSection([[(-k, k), (k, k), (0.0, r * math.sqrt(2.0))]])


def teardrop_x(r: float, x0: float, x1: float, y: float, z: float) -> Manifold:
  """A hole along x with a 45 degree point on its +y side (printed with +y up)."""
  return gothic(r, 48).extrude(x1 - x0).transform([[0, 0, 1, x0], [0, 1, 0, y], [-1, 0, 0, z]])


def teardrop_z(r: float, z0: float, z1: float, x: float, y: float) -> Manifold:
  """A hole along z with a 45 degree point on its +y side (printed with +y up)."""
  return gothic(r, 48).extrude(z1 - z0).translate((x, y, z0))


def _guard() -> Manifold:
  t = MOTOR_PLATE_T
  shell = gothic(MP.GUARD_OUT).extrude(GUARD_FRONT - t + 0.01).translate((0, 0, t - 0.01)) - \
    gothic(MP.GUARD_IN).extrude(GUARD_FRONT - t + 2).translate((0, 0, t - 1))
  lip = gothic(MP.GUARD_OUT).extrude(1.6).translate((0, 0, GUARD_FRONT - 1.6)) - \
    gothic(MP.GUARD_LIP_IN).extrude(4.0).translate((0, 0, GUARD_FRONT - 3))
  gw = FP.GUARD_WINDOW_F
  window = sector(MP.GUARD_OUT + 6, 270.0 - gw, 270.0 + gw).extrude(GUARD_FRONT + 4).translate((0, 0, t - 2))
  guard = (shell + lip) - window
  for sgn in (-1, 1):
    a = math.radians(270.0 + sgn * gw)
    rm = (MP.GUARD_IN + MP.GUARD_OUT) / 2
    guard = guard + cyl((MP.GUARD_OUT - MP.GUARD_IN) / 2 + 0.6, t - 0.01, GUARD_FRONT, rm * math.cos(a), rm * math.sin(a), 24)
  return guard


def side_bracket() -> Manifold:
  plate = _face_plate()
  guard = _guard()
  flange = box(X_FL[0], X_FL[1], FL_Y[0], FL_Y[1], FL_Z[0], FL_Z[1])
  # the ear: a fork of two lugs round the lever's hub, joined past the hub on the motor's side
  lug_in = box(X_EAR[0], X_EAR[1], EAR_Y[0] - 0.5, LUG_IN_Y1, EAR_Z[0], LEVER_Z[0] - LUG_GAP)
  lug_out = box(X_EAR[0], X_EAR[1], EAR_Y[0] - 0.5, EAR_Y[1], LEVER_Z[1] + LUG_GAP, EAR_Z[1])
  bridge = box(BRIDGE[0][0], BRIDGE[0][1], BRIDGE[1][0], BRIDGE[1][1], LEVER_Z[0] - LUG_GAP - 0.01, LEVER_Z[1] + LUG_GAP + 0.01)
  ear = lug_in + lug_out + bridge
  tab = box(TAB[0][0], TAB[0][1], TAB[1][0], TAB[1][1], TAB[2][0], TAB[2][1])
  part = union([plate, guard, flange, ear, tab])
  # the motor: its boss and its four screws (heads in the gear side, as before), and its body's room
  part = part - gothic(NEMA_BOSS / 2 + 0.4, 128).extrude(MOTOR_PLATE_T + 4).translate((0, 0, -3))
  for sx in (-1, 1):
    for sy in (-1, 1):
      x, y = sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2
      part = part - cyl(M3_CLEAR / 2, -1, MOTOR_PLATE_T + 1, x, y, 32) - \
        cyl(3.4, MOTOR_PLATE_T - MP.MOTOR_SCREW_CBORE, MOTOR_PLATE_T + 1, x, y, 32)
  part = part - box(-H - 0.3, H + 0.3, -H - 0.3, H + 0.3, -NEMA_LEN - 20, 0.0)
  # the plate's edge towards the driver cut back 45 degrees, as before; beyond the motor's side the flange's end is
  # trimmed too, so it stays inside the teeth's inner edge (radius 160) where it passes under them
  a, y0 = FP.PLATE_CHAMFER, MP.PLATE_BOTTOM
  part = part - prism_x([(y0 - 1.0, MOTOR_PLATE_T - a - 1.0), (y0 + a + 1.0, MOTOR_PLATE_T + 1.0), (y0 - 1.0, MOTOR_PLATE_T + 1.0)],
                        -60.0, 60.0)
  part = part - box(X_FL[0] - 1.0, -MP.PLATE_HALF, y0 - 2.0, -13.0, FLANGE_TRIM_Z, MOTOR_PLATE_T + 1.0)
  # the block's four M3 x 6 screws, heads sunk in the flange's motor side
  for y in (Y_RAIL - BLOCK_HOLES / 2, Y_RAIL + BLOCK_HOLES / 2):
    for z in (Z_BLOCK - BLOCK_HOLES / 2, Z_BLOCK + BLOCK_HOLES / 2):
      part = part - cyl_x(M3_CLEAR / 2, X_FL[0] - 1.0, X_FL[1] + 1.0, y=y, z=z, segments=32)
      part = part - cyl_x(3.1, X_FL[1] - 3.2, X_FL[1] + 1.0, y=y, z=z, segments=32)
  # the lever's screw: its head sunk in the inner lug's inner end, a clearance hole through the lug, a pilot hole it cuts
  # its thread into in the outer lug (blind, so the ear's outer face, which the switch's roller rides on, stays whole);
  # room for the lever's hub and arm swinging into either notch
  part = part - teardrop_z(PIVOT_CBORE[0] / 2, EAR_Z[0] - 1.0, EAR_Z[0] + PIVOT_CBORE[1], PIVOT[0], PIVOT[1])
  part = part - teardrop_z(PIVOT_CLEAR_D / 2, EAR_Z[0] - 1.0, LEVER_Z[0] - LUG_GAP + 0.5, PIVOT[0], PIVOT[1])
  part = part - teardrop_z(PIVOT_CLEAR_D / 2, LEVER_Z[1] + LUG_GAP - 0.5, PIVOT_END_Z + 0.8, PIVOT[0], PIVOT[1])
  nut_r = (M4_NUT_AF + 0.3) / 2 / math.cos(math.radians(30.0))
  part = part - Manifold.cylinder(PIVOT_NUT_Z[1] - PIVOT_NUT_Z[0] + 0.5, nut_r, nut_r, 6).translate(
    (PIVOT[0], PIVOT[1], PIVOT_NUT_Z[0] - 0.5))
  part = part - lever_swing_room(0.5)
  # the strip's two clamp screws, in from the tab's 6 o'clock side
  for y in CLAMP_Y:
    part = part - cyl_x(M3_CLEAR / 2, TAB[0][0] - 1.0, TAB[0][1] + 1.0, y=y, z=CLAMP_Z, segments=24)
  # slots through the finger guard's dash side, so a hex key reaches the power switch's screws from 6 o'clock with the
  # motor out on the teeth (to set the switch)
  for dy in (MP.SW_LEN / 2 - MP.SW_PITCH / 2, MP.SW_LEN / 2 + MP.SW_PITCH / 2):
    part = part - Manifold.batch_hull([cyl_x(2.6, -MP.GUARD_OUT - 15.0, MP.GUARD_OUT + 15.0, y=SW_Y0 + dy, z=SW_HOLES_Z + s,
                                             segments=24) for s in (-SW_SLOT, SW_SLOT)])
  return clean(part)


# ***** the mounting plate *****

def plate_outline_boxes() -> list:
  """The plate's parts (y, z ranges): along the rail; round the lever's slot and its notches; under the switch's holder;
  down to the spool's post."""
  return [((-16.0, 12.0), (BUMPER_Z[0], -26.0)), ((-13.0, 12.0), (-26.0, Z_RAIL[1])),
          ((8.0, PLATE_SLOT_Y), (PLATE_SLOT_Z, Z_RAIL[1])), ((HOLDER_Y[0], HOLDER_Y[1]), (-2.0, HOLDER_Z[1])),
          ((12.0, POST[1][1]), (POST[2][0], PLATE_SLOT_Z + 1.0))]


def side_plate() -> Manifold:
  x0, x1 = X_PL
  parts = [box(x0, x1, y0, y1, z0, z1) for (y0, y1), (z0, z1) in plate_outline_boxes()]
  # the switch's holder: a block out from the plate, with a stop beside the switch in the pin's band
  hx, hy, hz = HOLDER_X, HOLDER_Y, HOLDER_Z
  parts.append(box(hx[0] - 0.01, hx[1], hy[0], hy[1], hz[0], hz[1]))
  parts.append(box(hx[1] - 0.01, STOP_X[1], hy[0], SW_Y0 - 0.3, hz[0], hz[0] + 7.0))
  # the spool's post, with a round face that guides the coil's side
  (px0, px1), (py0, py1), (pz0, pz1) = POST
  parts.append(box(px0, px1, POST_NARROW[0], py1, pz0, pz1))
  parts.append(box(px0, POST_NARROW[1], py0, POST_NARROW[0] + 0.01, pz0, pz1))
  parts.append(cyl_y(POST_FACE, py1 - 1.6, py1, x=SPOOL_X, z=SPOOL_Z, segments=96))
  # the stop at the inner end: a bridge over the rail's end, its feet each side of the rail
  (bx0, bx1), (by0, by1) = BUMPER
  parts.append(box(bx0, bx1, by0, by1, BUMPER_Z[0], BUMPER_Z[1]))
  for ya, yb in ((by0, Y_RAIL - RAIL_W / 2 - 0.6), (Y_RAIL + RAIL_W / 2 + 0.6, by1)):
    parts.append(box(x1 - 0.01, bx0 + 0.01, ya, yb, BUMPER_Z[0], BUMPER_Z[1]))
  # the tongue towards the dash, in the plate's plane, and the foot standing out from it under the column cover
  parts.append(box(x0, x1, PLATE_SLOT_Y - 0.01, PP.Z_AXIS_P - FOOT_Z[0], TONGUE_R[0] - PP.R_FACE_P, TONGUE_R[1] - PP.R_FACE_P))
  parts.append(foot_block())
  part = union(parts)
  part = part - from_wheel(box(WINDOW_X[0], WINDOW_X[1], FOOT_Y[0] - 1.0, FOOT_Y[1] + 1.0, WINDOW_Z[0], WINDOW_Z[1]))
  # the rail's four M3 x 12 screws: slots along the rail, nuts sunk in the outer face
  for k in range(4):
    z = Z_RAIL[1] - RAIL_E - k * RAIL_PITCH
    part = part - Manifold.batch_hull([cyl_x(M3_CLEAR / 2, x0 - 1.0, x1 + 1.0, y=Y_RAIL, z=z + s, segments=24)
                                       for s in (-RAIL_SLOT, RAIL_SLOT)])
    part = part - Manifold.batch_hull([hex_prism_x(5.9, x0 - 1.0, x0 + 2.6, y=Y_RAIL, z=z + s) for s in (-RAIL_SLOT, RAIL_SLOT)])
  # the lever's slot and its two notches
  part = part - lever_cutter()
  # the switch's two M2 x 12 screws: slots along z (it slides +- SW_SLOT to set it), each into a nut that slides in a
  # hex slot open at the block's top
  for dy in (MP.SW_LEN / 2 - MP.SW_PITCH / 2, MP.SW_LEN / 2 + MP.SW_PITCH / 2):
    y = SW_Y0 + dy
    part = part - Manifold.batch_hull([cyl_x(M2_CLEAR / 2, SW_NUT_X[0] - 1.0, hx[1] + 1.0, y=y, z=SW_HOLES_Z + s, segments=20)
                                       for s in (-SW_SLOT, SW_SLOT)])
    part = part - box(SW_NUT_X[0], SW_NUT_X[1], y - M2_NUT_AF / 2, y + M2_NUT_AF / 2, SW_HOLES_Z - SW_SLOT - 2.6, hz[1] + 1.0)
  # the spool's M4 screw: cuts its own thread into the post
  part = part - cyl_y(M4_PILOT / 2, POST[1][0] - 1.0, POST[1][1] + 1.0, x=SPOOL_X, z=SPOOL_Z, segments=24)
  return clean(part)


def foot_block() -> Manifold:
  """The foot (carrier frame): a level slab under the column cover, drawn in the steering wheel frame."""
  return from_wheel(box(FOOT_X[0], FOOT_X[1], FOOT_Y[0], FOOT_Y[1], FOOT_Z[0], FOOT_Z[1]))


def foot_bar(z_screw: float | None = None) -> Manifold:
  """The foot bar (steering wheel frame): under the foot, across the window, at the screw's z (the window's middle if
  not given); its slot along x takes the screw anywhere across the window."""
  bw, bl, bt = BAR
  zs = z_screw if z_screw is not None else sum(WINDOW_Z) / 2
  xm = sum(WINDOW_X) / 2
  bar = box(xm - bw / 2, xm + bw / 2, FOOT_Y[0] - bt, FOOT_Y[0], zs - bl / 2, zs + bl / 2)
  slot = Manifold.batch_hull([cyl_y(BAR_SLOT_W / 2, FOOT_Y[0] - bt - 1.0, FOOT_Y[0] + 1.0, x=x, z=zs, segments=24)
                              for x in WINDOW_X])
  return clean(bar - slot)


def foot_bar_sweep() -> Manifold:
  """Everywhere the foot bar can be (carrier frame): the screw anywhere along the window."""
  bw, bl, bt = BAR
  xm = sum(WINDOW_X) / 2
  return from_wheel(box(xm - bw / 2, xm + bw / 2, FOOT_Y[0] - bt, FOOT_Y[0], WINDOW_Z[0] - bl / 2, WINDOW_Z[1] + bl / 2))


def foot_shim() -> Manifold:
  """A shim (steering wheel frame): the foot's outline and window, SHIM_T thick, on the foot's top."""
  sh = box(FOOT_X[0], FOOT_X[1], FOOT_Y[1], FOOT_Y[1] + SHIM_T, FOOT_Z[0], FOOT_Z[1])
  return clean(sh - box(WINDOW_X[0], WINDOW_X[1], FOOT_Y[1] - 1.0, FOOT_Y[1] + SHIM_T + 1.0, WINDOW_Z[0], WINDOW_Z[1]))


def cover_screw(x: float, z: float, cover_y: float) -> Manifold:
  """The cover's screw as fitted (steering wheel frame): its shank from the bar up into the cover, its head under the bar."""
  bt = BAR[2]
  return cyl_y(2.1, FOOT_Y[0] - bt - 0.01, cover_y + 10.0, x=x, z=z, segments=24) + \
    cyl_y(4.0, FOOT_Y[0] - bt - 2.8, FOOT_Y[0] - bt, x=x, z=z, segments=24)


# ***** the lever *****

def lever_room(clear: float = 0.0, z_clear: float = 0.0) -> Manifold:
  """The lever's hub and arm (no knob) as fitted, motor out, latched; grown by `clear` across and round, and by
  `z_clear` along the shaft."""
  px, py = PIVOT
  z0, z1 = LEVER_Z[0] - z_clear, LEVER_Z[1] + z_clear
  arm = box(px - KNOB_D, px, py - SHANK_W / 2 - clear, py + SHANK_W / 2 + clear, z0, z1)
  return arm + cyl(HUB_R + clear, z0, z1, x=px, y=py, segments=64)


def side_lever() -> Manifold:
  """Carrier frame, motor out, latched: the hub on the screw, the arm straight out towards 4 o'clock, the knob."""
  px, py = PIVOT
  z0, z1 = LEVER_Z
  part = lever_room() + cyl(KNOB_R, z0, z1, x=px - KNOB_D, y=py, segments=96)
  return clean(part - cyl(LEVER_BORE_D / 2, z0 - 1.0, z1 + 1.0, x=px, y=py, segments=48))


def lever_at(m: Manifold, s: float = 0.0, deg: float = 0.0) -> Manifold:
  """A part drawn with the lever (carrier frame) swung deg towards the dash about its pin, then slid in s."""
  if deg:
    px, py = PIVOT
    m = m.translate((-px, -py, 0.0)).rotate((0.0, 0.0, -deg)).translate((px, py, 0.0))
  return slid(m, s)


def lever_swing(m: Manifold, s_range, steps: int = 15) -> Manifold:
  """Everywhere `m` (drawn with the lever) goes swinging between the slot and a notch, slid in anywhere in s_range."""
  angles = np.linspace(0.0, SLOT_DEG, steps)
  return union([Manifold.batch_hull([lever_at(m, s, a) for s in s_range for a in (a0, a1)])
                for a0, a1 in itertools.pairwise(angles)])


def lever_swing_room(clear: float) -> Manifold:
  """The lever's hub and arm swinging between the slot and either notch (the bracket's room for them, with the
  bracket's own s): out to the lugs' faces along the shaft, so no sliver of the bridge is left between them."""
  return lever_swing(lever_room(clear, LUG_GAP + 0.02), (0.0,))


def lever_cutter() -> Manifold:
  """The plate's slot and notches: the arm in the slot (swung SLOT_DEG) from pulled out against the stop to slid in on
  the bumper, and swung back into each notch. The notches' load faces are exactly where the arm rests on them: the outer
  notch's floor where the spring pulls it (motor fully out), the inner notch's outer face where the motor's weight pulls
  it (slid in)."""
  arm = lever_room(SLOT_CLEAR)
  straight = Manifold.batch_hull([lever_at(arm, s, SLOT_DEG) for s in (-0.6, STROKE + 0.6)])
  cut = straight + lever_swing(arm, (-0.6, 0.0)) + lever_swing(arm, (STROKE, STROKE + 0.6))
  return cut ^ box(X_PL[0] - 1.0, X_PL[1] + 1.0, -100.0, 100.0, -200.0, 100.0)


def lever_screw() -> Manifold:
  """The M4 x 20 pivot screw and its nut as fitted: head, shank, nut (carrier frame, motor out)."""
  px, py = PIVOT
  nut_r = M4_NUT_AF / 2 / math.cos(math.radians(30.0))
  return cyl(PIVOT_HEAD_D / 2, PIVOT_HEAD_Z[0], PIVOT_HEAD_Z[1], x=px, y=py, segments=32) + \
    cyl(2.0, PIVOT_HEAD_Z[1] - 0.01, PIVOT_END_Z, x=px, y=py, segments=32) + \
    Manifold.cylinder(M4_NUT_T, nut_r, nut_r, 6).translate((px, py, PIVOT_NUT_Z[0]))


# ***** the spool *****

def side_spool() -> Manifold:
  """Spool frame: its axle along y, y as fitted. One flange, on the screw head's side (on the print bed); the post's face
  guides the coil's other side."""
  d, (y0, y1) = DRUM_D, SPOOL_Y
  fd, ft = SPOOL_FLANGE
  hub = cyl_y(d / 2, y0, y1 + 0.01, segments=96)
  fl = cyl_y(fd / 2, y1, y1 + ft, segments=96)
  return clean((hub + fl) - cyl_y(2.2, y0 - 1.0, y1 + ft + 1.0, segments=32))


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

  def rot(m: Manifold) -> Manifold:
    return m.rotate((0, 0, -90.0))

  return {"motor": mb["motor"], "board+cap": side_board_cap(), "car plug": rot(mb["car plug"]),
          "motor plug": rot(mb["motor plug"]), "motor's own plug": mb["motor's own plug"]}


def rail() -> Manifold:
  return box(X_RAIL_BOT, X_RAIL_TOP, Y_RAIL - RAIL_W / 2, Y_RAIL + RAIL_W / 2, Z_RAIL[0], Z_RAIL[1])


def block() -> Manifold:
  """The block, motor on (it rides the rail: its middle is cut away round the rail)."""
  b = box(X_BLOCK_BOT, X_BLOCK_TOP, Y_RAIL - BLOCK_W / 2, Y_RAIL + BLOCK_W / 2, BLOCK_Z[0], BLOCK_Z[1])
  return b - box(X_RAIL_BOT - 1.0, X_RAIL_TOP + 0.3, Y_RAIL - RAIL_W / 2 - 0.3, Y_RAIL + RAIL_W / 2 + 0.3, BLOCK_Z[0] - 1, BLOCK_Z[1] + 1)


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
  heads = union([cyl_x(2.75, TAB[0][1], TAB[0][1] + 3.0, y=y, z=CLAMP_Z - slide, segments=24) for y in CLAMP_Y])
  clamp = slid(strip_clamp(), slide) + heads
  y_head = SPOOL_Y[1] + SPOOL_FLANGE[1] + 0.8                     # the washer under the head, then the head
  axle = cyl_y(2.0, y_head - AXLE_LEN, y_head, x=SPOOL_X, z=SPOOL_Z, segments=24) + \
    cyl_y(3.5, SPOOL_Y[1] + SPOOL_FLANGE[1] + 0.8, SPOOL_Y[1] + SPOOL_FLANGE[1] + 4.8, x=SPOOL_X, z=SPOOL_Z, segments=24) + \
    cyl_y(4.5, SPOOL_Y[1] + SPOOL_FLANGE[1], SPOOL_Y[1] + SPOOL_FLANGE[1] + 0.8, x=SPOOL_X, z=SPOOL_Z, segments=24)
  return {"coil": coil, "strip": strip, "clamp": clamp, "axle": axle}


def strip_clamp() -> Manifold:
  """The bar that pinches the spring's strip against the bracket's tab (carrier frame, motor on)."""
  (x0, x1), (y0, y1), (z0, z1) = CLAMP_BAR
  bar = box(x0, x1, y0, y1, z0, z1)
  for y in CLAMP_Y:
    bar = bar - cyl_x(M3_PILOT / 2, x0 - 1.0, x1 + 1.0, y=y, z=CLAMP_Z, segments=24)
  return clean(bar)


def block_screws() -> Manifold:
  return union([cyl_x(2.75, X_FL[1] - 3.2, X_FL[1] - 0.01, y=y, z=z, segments=24)
                for y in (Y_RAIL - BLOCK_HOLES / 2, Y_RAIL + BLOCK_HOLES / 2)
                for z in (Z_BLOCK - BLOCK_HOLES / 2, Z_BLOCK + BLOCK_HOLES / 2)])


# ***** placing *****

def to_wheel(m: Manifold, mount_deg: float = MOUNT_DEG) -> Manifold:
  Rm = PP.rot_z(mount_deg)
  return PP.place(m, Rm @ PP.R_POP, Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P]))


def from_wheel(m: Manifold, mount_deg: float = MOUNT_DEG) -> Manifold:
  """The inverse of to_wheel: a steering-wheel-frame part into the carrier frame."""
  Rm = PP.rot_z(mount_deg)
  R = Rm @ PP.R_POP
  T = Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P])
  return PP.place(m, R.T, -(R.T @ T))


def wheel_point(x: float, y: float, z: float, mount_deg: float = MOUNT_DEG) -> np.ndarray:
  """A carrier-frame point in the steering wheel frame."""
  Rm = PP.rot_z(mount_deg)
  return Rm @ PP.R_POP @ np.array([x, y, z]) + Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P])


def slid(m: Manifold, s: float) -> Manifold:
  """A moving part (drawn motor on) slid in s mm."""
  return m.translate((0.0, 0.0, -s)) if s else m

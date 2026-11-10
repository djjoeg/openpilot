"""
The right arm mount (1 Nov 2026, from your note; v3 2 Nov 2026; v4 3 Nov 2026): the motor sits OUTSIDE the steering
wheel's rim on the right, at about 4 o'clock, its shaft pointing in at the wheel's middle, the gear on the teeth from
outside.

v6, the fit print (3 Nov, your note: more travel for the first print, and every slide the same way): both slides
are a groove in the outer piece and a wing bolt through it into a nut in the inner one, tightened to pull the inner
piece against the outer's wall. The motor's slide up the tower now has 31 mm of travel (the teeth piece may sit 12
mm nearer you or further than drawn); the arm's slide in the receiver 17.5 mm either way across. For a nut in it and
for stiffness, the arm's bar in the receiver is 20 x 30 (was 10 x 30), so the frame plate is v5: its receiver's bore
20 wide, the arm's groove in the wall on your side (v4's pinch bolt was on the dash side, where the photo estimates
put its wings in the dash), its labels cut in. Once the car shows where they sit, a later print can have shorter
slides.

v5 (3 Nov, after a stiffness check of v4, and your idea for the slide): the arm 50 mm deep along the column from
just outside the receiver to the tower, so it no longer twists under the motor's push (v4's 10 mm bar let the gear
move 1 to 2 mm in and out of the teeth); and the slide is one wing bolt in a groove up the tower's outer wall,
screwed into a nut in the carrier's bar: loosen it, slide the motor up into the teeth or down out of them, tighten.
It is the lock, the depth setting and the on and off; the groove's ends keep the carrier in. No M4 stop any more.

v4 (3 Nov, from the v3 print in your hand): the tower's channel is closed into a square tube, so the motor carrier
can't come out of it; the carrier's bar has no lug, so it slides into the tube from the tower's top end (off the car,
before the arm goes into the receiver); an M4 bolt screwed into the bar's end below the tower, a fender washer under
its head, is the stop (and what keeps the carrier in), locked with a jam nut. And the gear moved 4 degrees up the
rim, to the middle of the gap between the spokes (measured on photos of the same wheel: 6 to 46 degrees below
3 o'clock), so the 20 teeth fit between them.

v3 was two printed pieces and two slides:

  frame plate v4  - unchanged: on the column cover's two screws; the receiver under it runs across the car, one wing
                    bolt pinches the arm in it
  arm             - a 10 x 30 bar across the car (slide it in or out of the receiver: how far right the motor sits),
                    with a tower at its end: a channel along the column, open on the side towards the motor
  motor carrier   - the motor bolts to its plate (four M3, the shaft through the big hole pointing in at the wheel's
                    middle); its bar slides along the column in the tower's channel. A wing bolt through the tower's
                    outer wall pushes the bar tight. A wing bolt up through the lug at the bar's bottom end is the stop,
                    locked with a jam nut: slid up against it, the gear is in the teeth (lane keeping on); slid 6 mm or
                    more down the column, out of them (off; the motor has power whenever the car is on)
  gear            - the side-slide gear (you have it)

v2 (a foot, a bar, a flag and a bracket, for up and down and the angle) is gone: too many joints, and its motor
carrier could not have been put into the bracket's sleeve, which was closed at both ends.

Steering wheel frame (mm): z along the column towards you, 0 at the middle of the grip; y up; x to your right.
THETA is where the gear meets the teeth, degrees from 3 o'clock (-30 is 4 o'clock); R_FACE_OUT the motor's face
from the wheel's middle (the gear's teeth reach in to the same radius as before, 160.5 to 173).

Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, THETA. Adjustable: the arm 17.5 mm either way across, by
its groove in the receiver; the motor along the column, anywhere in the tower's groove (how deep the gear sits, and on
and off). Not adjustable: up and down, and the angle; where the gear sits along the teeth is set by the arm across and
by the gear's place on its shaft.

  python3 rightarm.py   # writes ../stl/right-arm/*.stl, ../plates/plate-11-frame-plate-v5.3mf, plate-12-right-arm.3mf
                        # and ../report/right-arm.png, column-frame-plate-v5.png
"""
import math
import os
import sys

import numpy as np
from manifold3d import CrossSection, Manifold

import armmount as AM
import frameplate as FR
import sideparts as S
from cadlib import (
  box,
  clean,
  cyl,
  cyl_x,
  cyl_y,
  on_bed,
  union,
  write_stl,
)
from params import NEMA, NEMA_LEN

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "..", "stl", "right-arm")
REPORT_DIR = os.path.join(HERE, "..", "report")

# ***** the car (rough) *****
COVER_Y, CUP_X, CUP_Z = AM.COVER_Y, AM.CUP_X, AM.CUP_Z       # -107, 73, -145

# ***** the motor: outside the rim, shaft pointing in *****
THETA = -26.0                    # where the gear meets the teeth: the middle of the gap between the spoke joins on the
                                 # back of the grip (-6 to -46, measured 3 Nov on photos of the same wheel), 4 degrees
                                 # above 4 o'clock (your note: the column's underside height would be -40; a tangent 20
                                 # degrees off upright would be -20; v3 had -30)
R_FACE_OUT = 182.5               # the motor's face from the wheel's middle: the face plate (5 mm, just inside it) clears the
                                 # teeth piece's outer band (radius 177); the gear's teeth then reach in to radius 163
Z_AXIS = S.PP.Z_AXIS_P           # -59.5: the motor's axis, along the column (as the side-slide mount)
U = np.array([math.cos(math.radians(THETA)), math.sin(math.radians(THETA))])      # out from the wheel's middle
V = np.array([-math.sin(math.radians(THETA)), math.cos(math.radians(THETA))])     # along the rim, anticlockwise
H = NEMA / 2
FACE_T = 5.0
M5_HOLE = 5.4
M5_NUT_AF, M5_NUT_T = 8.0, 4.0
BOSS_HOLE, NEMA_HOLES = 22.5, 31.0

# ***** the frame plate v5 (plate frame: x towards the door, y towards the dash, 0 at the cup) *****
PLATE_T = 6.0
BLOCK = (-60.0, 28.0, -14.0, 50.0)       # v1's block, out to the receiver's far end on the key side
BAR, LEG, LEG_SLOT = AM.BAR, AM.LEG, AM.LEG_SLOT
BORE_Y = (20.0, 40.4)                    # the receiver's bore along the column, 20 wide (v4: 10), on the dash side of the cup
BORE_DEPTH = 30.4                        # the arm is 30 tall
TUBE_Y = (BORE_Y[0] - 5.0, BORE_Y[1] + 5.0)   # walls 5 each side; the arm's groove in the wheel-side one
TUBE_X = (-47.0, 3.0)                    # along the plate: 50 long, from just short of the cup's washer out to the key side
TUBE_FLOOR_T = 5.0
SLOT_W = 5.6                             # the tower's groove, across (an M5 wing bolt's shank, 0.35 a side)
RSLOT_H = 6.4                            # the receiver's groove, top to bottom: its top prints as a 42 mm bridge, which
                                         # may droop, and the arm has 0.4 of play up and down in the bore
ARM_SLIDE = 17.5                         # v6: the arm slides this far either way across from its nominal place
RG_MID = -22.0                           # plate x of the arm's nut at the nominal place, the receiver's middle
RGROOVE_X = (RG_MID - ARM_SLIDE - RSLOT_H / 2 - 0.5, RG_MID + ARM_SLIDE + RSLOT_H / 2 + 0.5)    # (-43.2, -0.8)
RG_STOP = ARM_SLIDE + 0.5 + (RSLOT_H / 2 - 2.45)    # 18.75: the wing bolt meets the groove's end
RG_Z = PLATE_T + BORE_DEPTH / 2 + 3.0    # 24.2: the groove's middle, 3 below the bore's middle (in the car), so a fender
                                         # washer under its wing bolt passes the cup screw's head with the arm slid in

# ***** the arm (steering wheel frame): across, in the receiver *****
ARM_Z = (CUP_Z - BORE_Y[1] + 0.2, CUP_Z - BORE_Y[0] - 0.2)      # (-185.2, -165.2)
ARM_Y = (COVER_Y - PLATE_T - 30.0, COVER_Y - PLATE_T)          # (-143, -113)
ARM_X = (CUP_X - TUBE_X[1] + 3.0, 150.0)                       # (73, 150): 47 in the receiver, nominal
ARM_NUT_X = CUP_X - RG_MID               # 95: the arm's nut along its bar, at the nominal place
ARM_BOLT_Y = COVER_Y - RG_Z + 0.2        # -131: the receiver's wing bolt's line in the bar (the bar drawn against the
                                         # plate, 0.2 above the middle of its 0.4 of play, so on average it's centred)
ARM_NUT_IN = 6.0                         # the nut this far in from the bar's wheel-side face (the bolt's end 3 past it)
ARM_NUT_Z = (ARM_Z[1] - ARM_NUT_IN - M5_NUT_T - 0.2, ARM_Z[1] - ARM_NUT_IN + 0.2)    # its slot along the column
ARM_HOLE_END = ARM_Z[1] - ARM_NUT_IN - M5_NUT_T - 4.0                                 # the bolt's hole's bottom
RECEIVER_MOUTH = CUP_X - TUBE_X[0]       # 120: the receiver's open end on the key side

# ***** the tower at the arm's end and the motor carrier, in the motor's frame: u out from the wheel's middle (along
# U), v along the rim (along V), z along the column *****
BAR_U, BAR_V = (205.0, 221.0), (-39.0, -23.0)    # the carrier's bar, 16 x 16, beside the motor on its 5 o'clock side
CH_U, CH_V0 = (204.75, 221.25), -39.25           # the tower's square tube round it
CH_V1 = BAR_V[1] + 0.3                           # v4: its fourth wall, on the motor's side (0.3 clear of the bar)
COVER_T = 5.0                                    # that wall's thickness
TOWER_U, TOWER_V = (194.75, 231.25), (-47.25, CH_V1 + COVER_T)   # the inner wall 10, the outer wall 10 (the push
                                                 # bolt's nut), the back 8, the cover 5 (below the motor and its board,
                                                 # which stay above the tower's top)
BORE_CHAMFER = 0.8               # the tube's two mouths: 45 degrees, so the bar goes in and the first layers don't pinch it
TOWER_Z = (ARM_Z[0], -102.0)            # v6: the top 8 lower, so the motor slides 8 further down
BAR_UV = ((BAR_U[0] + BAR_U[1]) / 2, (BAR_V[0] + BAR_V[1]) / 2)    # (213, -31): the bar's middle line
BAR_END_UP = 18.0                # the bar's bottom end this far up the tube at the drawn depth (level with the tube's
                                 # bottom slid all the way out, so it never reaches further towards the dash)
DZ_DEEP, DZ_SHALLOW = 12.0, -12.0   # where the gear may need to sit for the drawn depth (v6, the fit print): the teeth
                                 # piece 12 mm nearer you or further than drawn (the plate on the cover, the tape)
DZ_MAX = DZ_DEEP + 1.0           # the groove's top: the gear's tips reach the bottom of the teeth 1 mm past the drawn depth
# the motor's slide (your idea, v5): an M5 x 20 wing bolt and a fender washer, through a groove up the tower's outer
# wall along -u, into an M5 nut in a slot in the carrier's bar; tightened, it pulls the bar against the outer wall
SLIDE_Z0 = -123.0                # the wing bolt's height at the drawn depth
SLIDE_NUT_U = (213.6, 218.0)     # the nut's slot in the bar: 3 mm of bar outside it, the bolt's end 1 mm past the nut
SLIDE_NUT_W = M5_NUT_AF + 0.3    # the slot across the nut's flats, 8.3: even the smallest standard nut can't turn in it
WASHER_OD, WASHER_T = 25.0, 1.6  # the fender washer under the wing bolt (19 to 25 mm across; the checks use 25)
TICK_DZ = range(-18, 14)         # depth ticks on the bar's outer face, one a millimetre: the one at the tower's top
TICK_LONG = (-15, -10, -5, 0, 5, 10)   # edge reads the slide (0 the drawn depth; longer ticks every 5)
# the carrier's plate (the motor's face against its outside), the web joining it to the bar, the bar's length
PLATE_U = (R_FACE_OUT - FACE_T, R_FACE_OUT)
PLATE_V = (BAR_V[0], H + 0.35)
PLATE_Z = (Z_AXIS - H - 0.35, Z_AXIS + H)
WEB_Z0 = PLATE_Z[0] - 3.0        # the web's underside, below the motor's and the board's: it lands on the tower first
BAR_Z = (TOWER_Z[0] + BAR_END_UP, PLATE_Z[1])   # (-167.2, -38.35) at the nominal depth: the end is up in the tube
DZ_OUT = TOWER_Z[1] - WEB_Z0     # -18: slid all the way out, the web sits on the tower's top (6 mm is enough)
GROOVE_Z = (SLIDE_Z0 + DZ_OUT - SLOT_W / 2 - 0.5, SLIDE_Z0 + DZ_MAX + SLOT_W / 2 + 0.5)    # (-144.3, -106.7)
DEEP = 50.0                      # the arm this deep along the column, from DEEP_X0 to the tower (v5)
DEEP_X0 = RECEIVER_MOUTH + ARM_SLIDE + 2.0   # 139.5: 0.75 clear of the receiver's mouth when the wing bolt stops
                                             # the arm at the groove's end
PAD_R, PAD_T = 3.5, 1.0          # pads round the four M3 holes on the plate's inside: the motor's holes are 4.5 deep
                                 # (STEPPERONLINE's drawing for this motor family), so an M3 x 10 goes 4 into them


def rad(t_u: float, t_v: float) -> tuple:
  """A point at t_u out along U and t_v along V, in the steering wheel frame (x, y)."""
  p = t_u * U + t_v * V
  return float(p[0]), float(p[1])


# ----- the frame plate v5 (plate frame, labels up) -----

def frame_plate_v5() -> Manifold:
  """v4 with the receiver's bore 20 wide, the arm's groove along its wheel-side wall at the bore's mid-height, and
  no pinch bolt or nut trap."""
  T = PLATE_T
  body = box(BAR[0], BAR[1], BAR[2], BAR[3], 0.0, T) + box(LEG[0], LEG[1], LEG[2], LEG[3], 0.0, T) + \
    box(BLOCK[0], BLOCK[1], BLOCK[2], BLOCK[3], 0.0, T)
  body = body - AM.through_slot(0.0, 0.0, FR.SLOT_L, FR.SLOT_W, "x")
  xc, y0, y1 = LEG_SLOT
  body = body - AM.through_slot(xc, (y0 + y1) / 2, y1 - y0, FR.SLOT_W, "y")
  z1 = T + BORE_DEPTH + TUBE_FLOOR_T
  tube = box(TUBE_X[0], TUBE_X[1], TUBE_Y[0], TUBE_Y[1], T - 0.01, z1)
  tube = tube - box(TUBE_X[0] - 1.0, TUBE_X[1] + 1.0, BORE_Y[0], BORE_Y[1], T, T + BORE_DEPTH)
  r = RSLOT_H / 2
  ends = [cyl_y(r, TUBE_Y[0] - 1.0, BORE_Y[0] + 1.0, x=x, z=RG_Z, segments=32) for x in (RGROOVE_X[0] + r, RGROOVE_X[1] - r)]
  tube = tube - Manifold.batch_hull(ends)
  body = body + tube
  import slotplate as SL
  SL.FONT.setdefault("<", ("010", "100", "111", "100", "010"))
  labels = [FR.text("< KEY", TUBE_X[1] + 3.0, BLOCK[3] - 8.0, T), FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, T, pix=0.9),
            FR.text("1", xc - FR.text_width("1", 0.9) / 2, LEG[2] + 3.0, T, pix=0.9)]
  # v5: cut in, not raised, so the screws' washers sit flat and the arm slides over the plate past the tube's end
  return clean(body - union(labels).translate((0.0, 0.0, -SL.LABEL_H + 0.01)))


def plate_to_wheel(m: Manifold) -> Manifold:
  return m.transform([[-1.0, 0.0, 0.0, CUP_X], [0.0, 0.0, -1.0, COVER_Y], [0.0, -1.0, 0.0, CUP_Z]])


# ----- the arm and the motor carrier (steering wheel frame) -----

def uvz(u0, u1, v0, v1, z0, z1) -> Manifold:
  """A box in the motor's frame (u along U, v along V), placed in the steering wheel frame."""
  return box(u0, u1, v0, v1, z0, z1).rotate((0.0, 0.0, THETA))


def uv_cyl_z(r, u, v, z0, z1, segments=32) -> Manifold:
  """A cylinder along z at (u, v) in the motor's frame."""
  x, y = rad(u, v)
  return cyl(r, z0, z1, x=x, y=y, segments=segments)


def teardrop_x(r: float, x0: float, x1: float, y: float, z: float, flat: float = 2.0) -> Manifold:
  """A hole along x that prints without support with +y up: a circle with a 45 degree roof, cut flat `flat` above
  the circle."""
  c = cyl_x(r, x0, x1, y=y, z=z, segments=64)
  tip = cyl_x(0.01, x0, x1, y=y + r * math.sqrt(2.0), z=z, segments=8)
  return Manifold.batch_hull([c, tip]) ^ box(x0 - 1.0, x1 + 1.0, y - r - 1.0, y + r + flat, z - r - 1.0, z + r + 1.0)


def bore_mouths() -> Manifold:
  """The tube's two mouths cut back 45 degrees, BORE_CHAMFER deep: the bar's end finds its way in at the top, and the
  bottom's first layers (on the bed) can't pinch it."""
  c, e = BORE_CHAMFER, 0.5
  out = []
  for z_face, sgn in ((TOWER_Z[0], 1.0), (TOWER_Z[1], -1.0)):
    wide = uvz(CH_U[0] - c - e, CH_U[1] + c + e, CH_V0 - c - e, CH_V1 + c + e, z_face - sgn * e - 0.01, z_face - sgn * e + 0.01)
    bore = uvz(CH_U[0], CH_U[1], CH_V0, CH_V1, z_face + sgn * c - 0.01, z_face + sgn * c + 0.01)
    out.append(Manifold.batch_hull([wide, bore]))
  return union(out)


def groove() -> Manifold:
  """v5: the slide's groove, along the column through the tower's outer wall, round-ended, on the bar's middle line."""
  v = BAR_UV[1]
  r = SLOT_W / 2
  ends = [cyl_x(r, CH_U[1] - 1.0, TOWER_U[1] + 1.0, y=v, z=z, segments=32) for z in (GROOVE_Z[0] + r, GROOVE_Z[1] - r)]
  return Manifold.batch_hull(ends).rotate((0.0, 0.0, THETA))


def arm() -> Manifold:
  """The arm and the tower at its end, one piece (printed flat, the tower standing up): the arm runs into the
  tower's foot (the hull of the arm's end and the tower, as thick as the arm) and, v5, a 50 mm deep block from just
  outside the receiver to the tower, so the arm doesn't twist; up the tower, a square tube the motor carrier's bar
  slides in (closed on all four sides), with the slide's groove up its outer wall."""
  a = box(ARM_X[0], ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1])
  foot = Manifold.batch_hull([box(ARM_X[1] - 5.0, ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1]),
                              uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], ARM_Z[0], ARM_Z[1])])
  foot = foot ^ box(ARM_X[0], 400.0, -400.0, ARM_Y[1], ARM_Z[0] - 1.0, ARM_Z[1] + 1.0)   # no higher than the arm (v4: the
                                                 # tower's top corner now stands above it; slid in, it would meet the plate)
  z1 = ARM_Z[0] + DEEP
  deep = Manifold.batch_hull([box(DEEP_X0, ARM_X[1], ARM_Y[0], ARM_Y[1] - 1.0, ARM_Z[0], z1),
                              uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], ARM_Z[0], z1)])
  deep = deep ^ box(DEEP_X0, 400.0, -400.0, ARM_Y[1] - 1.0, ARM_Z[0] - 1.0, z1)    # 1 mm under the frame plate
  tower = uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], TOWER_Z[0], TOWER_Z[1])
  m = a + foot + deep + tower
  m = m - uvz(CH_U[0], CH_U[1], CH_V0, CH_V1, TOWER_Z[0] - 1.0, TOWER_Z[1] + 1.0) - bore_mouths()
  # v6: the receiver's slide. Its M5 nut drops into a slot in the bar's top (the frame plate above holds it in once
  # the bar is in the receiver), flats along the bar, the slot's bottom the nut's own shape so it sits on the bolt's
  # line; the wing bolt comes in from the wheel-side face, through the receiver's groove
  w = SLIDE_NUT_W
  r = w / math.sqrt(3)
  z0, z1 = ARM_NUT_Z
  hexp = CrossSection([[(ARM_NUT_X + r * math.cos(math.radians(90 + 60 * i)), ARM_BOLT_Y + r * math.sin(math.radians(90 + 60 * i)))
                        for i in range(6)]])                    # a corner down
  pocket = hexp.extrude(z1 - z0).translate((0.0, 0.0, z0))
  pocket = pocket + box(ARM_NUT_X - w / 2, ARM_NUT_X + w / 2, ARM_BOLT_Y, ARM_Y[1] + 1.0, z0, z1)
  hole = cyl(M5_HOLE / 2, ARM_HOLE_END, ARM_Z[1] + 1.0, x=ARM_NUT_X, y=ARM_BOLT_Y, segments=32)
  return clean(m - groove() - pocket - hole)


def teardrop_z(r: float, z0: float, z1: float, u: float, v: float, flat: float = 0.6) -> Manifold:
  """A hole along z at (u, v) of the motor's frame that prints without support lying on its side with +v up (the
  carrier): a circle with a 45 degree roof towards +v, cut flat `flat` above the circle."""
  c = cyl(r, z0, z1, x=u, y=v, segments=32)
  tip = cyl(0.01, z0, z1, x=u, y=v + r * math.sqrt(2.0), segments=8)
  m = Manifold.batch_hull([c, tip]) ^ box(u - r - 1.0, u + r + 1.0, v - r - 1.0, v + r + flat, z0 - 1.0, z1 + 1.0)
  return m.rotate((0.0, 0.0, THETA))


def carrier(dz: float = 0.0) -> Manifold:
  """The motor carrier, one piece (printed on its side towards 5 o'clock): the bar that slides in the tower's tube,
  plain to its bottom end (no lug) so it goes in from the tower's top; across it, v5, the slide's wing bolt hole and
  the slot its M5 nut drops into (from the motor's side, flats along the bar so it can't turn), and the depth ticks on
  its outer face; at its top the web and the plate the motor bolts to (perpendicular to U, the motor's face against its
  outside; pads round the four M3 holes inside; the big hole a teardrop so it prints). dz: slid along the column from
  the nominal depth (+ towards you, deeper into the teeth)."""
  m = uvz(BAR_U[0], BAR_U[1], BAR_V[0], BAR_V[1], BAR_Z[0], BAR_Z[1])
  m = m + uvz(PLATE_U[0], BAR_U[0] + 0.01, BAR_V[0], BAR_V[1], WEB_Z0, PLATE_Z[1])               # the web
  m = m + uvz(PLATE_U[0], PLATE_U[1], PLATE_V[0], PLATE_V[1], PLATE_Z[0], PLATE_Z[1])            # the plate
  r0, r1 = PLATE_U
  corners = [(b, c) for b in (-NEMA_HOLES / 2, NEMA_HOLES / 2) for c in (-NEMA_HOLES / 2, NEMA_HOLES / 2)]
  pads = [cyl_x(PAD_R, r0 - PAD_T, r0 + 0.01, y=b, z=Z_AXIS + c, segments=32) for b, c in corners]
  m = m + union(pads).rotate((0.0, 0.0, THETA))
  holes = [teardrop_x(BOSS_HOLE / 2, r0 - 1.0, r1 + 1.0, y=0.0, z=Z_AXIS)]
  holes += [cyl_x(1.7, r0 - PAD_T - 1.0, r1 + 1.0, y=b, z=Z_AXIS + c, segments=24) for b, c in corners]
  m = m - union(holes).rotate((0.0, 0.0, THETA))
  bv = BAR_UV[1]
  m = m - teardrop_x(M5_HOLE / 2, SLIDE_NUT_U[0] - 2.0, BAR_U[1] + 1.0, y=bv, z=SLIDE_Z0, flat=0.6).rotate((0.0, 0.0, THETA))
  # the nut's slot: dropped in from the motor's side, flats along the bar; its bottom the nut's own shape, a corner
  # down, so the nut sits centred on the bolt's line
  w = SLIDE_NUT_W
  r = w / math.sqrt(3)                                           # the hex pocket's corner radius
  hexp = CrossSection([[(0.0 + r * math.cos(math.radians(90 + 60 * i)), bv + r * math.sin(math.radians(90 + 60 * i)))
                        for i in range(6)]])                    # in (z, v), a corner along -v; then along u
  pocket = hexp.extrude(SLIDE_NUT_U[1] - SLIDE_NUT_U[0]).rotate((0.0, 90.0, 0.0))     # extrusion z -> x (u)
  pocket = pocket.translate((SLIDE_NUT_U[0], 0.0, SLIDE_Z0))
  m = m - (pocket + box(SLIDE_NUT_U[0], SLIDE_NUT_U[1], bv, BAR_V[1] + 1.0, SLIDE_Z0 - w / 2, SLIDE_Z0 + w / 2)).rotate(
    (0.0, 0.0, THETA))
  for d in TICK_DZ:                                             # the bar's point at the tower's top when slid d
    zt = TOWER_Z[1] - d
    w = 7.0 if d in TICK_LONG else 4.0
    m = m - uvz(BAR_U[1] - 0.6, BAR_U[1] + 1.0, bv - w, bv + w, zt - 0.25, zt + 0.25)
  return clean(m).translate((0.0, 0.0, dz))


def motor_and_gear(dz: float = 0.0) -> dict:
  """The motor's body, board and the side-slide gear: carrier frame (z out along the shaft from the face) -> here
  the shaft points in: carrier z -> -U, carrier y -> V, carrier x -> along the column. dz as for carrier()."""
  # the motor's own 6-pin socket (motor card: 16 mm wide, 6.5 mm out, the back 11 mm of the body) and its plug's
  # wires bending away, 12 mm more: facing along the column (+x here; -x passes too). Facing -V it hits the carrier.
  motor = (box(-H, H, -H, H, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
           + box(21.15, 21.15 + 6.5 + 12.0, -8.0, 8.0, -NEMA_LEN, -NEMA_LEN + 11.0))
  # the StepperServoCAN board as it came (9 Nov): 56.0 x 43.3 mm (its maker's PCB file), centred on the shaft along its
  # long side and 20.4 / 22.9 either side across it. Mounted with the long side around the wheel (along V): along
  # the column it hits the arm with the carrier slid 15 mm or more down. Its case is 8 mm high (Retropilot); 16 mm
  # kept here. Turned so its Motor socket is on the motor plug's side (+x): that plug and its wires reach 20 mm past
  # the board's edge; the Car socket's plug runs off its +V end, to 38 mm out (both ways round pass, 10 Nov).
  board = (box(-20.4, 22.9, -28.0, 28.0, -NEMA_LEN - 16.0, -NEMA_LEN)
           + box(22.9, 42.9, -7.7, 5.3, -NEMA_LEN - 7.5, -NEMA_LEN - 1.0)
           + box(-12.3, 0.7, 15.0, 38.0, -NEMA_LEN - 7.5, -NEMA_LEN - 1.0))
  c = R_FACE_OUT * U
  mat = [[0.0, V[0], -U[0], float(c[0])], [0.0, V[1], -U[1], float(c[1])], [1.0, 0.0, 0.0, Z_AXIS + dz]]
  return {"motor": motor.transform(mat), "board": board.transform(mat), "gear": S.side_gear().transform(mat)}


# ----- the print bed -----

def parts_on_bed() -> dict:
  """The plate labels up (the receiver standing on it); the arm flat, the tower standing up (the tube straight up,
  its top flat); the carrier on its side towards 5 o'clock (the bar, the web and the plate's edge all start at v -39),
  the plate standing up from it, the slide nut's slot open on top."""
  car = carrier().rotate((0.0, 0.0, -THETA))           # into the motor's frame: u along x, v along y
  return {"column-frame-plate-v5": on_bed(frame_plate_v5()),
          "right-arm": on_bed(arm()),
          "right-carrier": on_bed(car, rotate=(90.0, 0.0, 0.0))}   # y -> z: v -39 down, the teardrop's roof up


def build(out_dir: str = STL_DIR) -> dict:
  os.makedirs(out_dir, exist_ok=True)
  info = {}
  for stem, m in parts_on_bed().items():
    write_stl(m, os.path.join(out_dir, stem + ".stl"), stem)
    bb = m.bounding_box()
    info[stem] = {"size_mm": [round(bb[i + 3] - bb[i], 1) for i in range(3)], "grams_solid": round(m.volume() / 1000 * 1.28)}
  for stale in ("right-bar", "right-bracket", "column-frame-plate-v4"):          # v2's pieces, the v4 plate
    p = os.path.join(out_dir, stale + ".stl")
    if os.path.exists(p):
      os.remove(p)
  return info


def bambu_plates() -> list:
  import plates as P
  out = []
  pdir = os.path.join(HERE, "..", "plates")
  for stale in ("plate-11-frame-plate-v4.3mf", "plate-11-frame-plate-v4.png"):
    if os.path.exists(os.path.join(pdir, stale)):
      os.remove(os.path.join(pdir, stale))
  parts = {"column-frame-plate-v5": ("frame plate v5", 1, P.STANDARD)}
  out += P.build(out_dir=pdir, stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-11-frame-plate-v5", "11 frame plate v5", list(parts),
                              "Plate 11: the frame plate v5 (the receiver 20 wide, the arm's groove in it)")])
  parts = {"right-arm": ("arm", 1, P.SOLID), "right-carrier": ("motor carrier", 1, P.SOLID)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-12-right-arm", "12 right arm v6", list(parts),
                              "Plate 12: the right arm mount v6, the fit print: the arm and the motor carrier")])
  return out


# ----- pictures -----

def scene() -> list:
  import carscene as CS
  import midteeth as MT
  from cadlib import revolve
  sc = CS.CarScene(D=125.0)
  grip_r = S.FP.GRIP / 2.0
  rr = S.FP.WHEEL_OD / 2.0 - grip_r
  circle = [(rr + grip_r * math.cos(math.radians(a)), grip_r * math.sin(math.radians(a))) for a in range(0, 360, 10)]
  grip = revolve(circle, -180.0, 180.0, step_deg=2.0)
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=18)).rotate((0.0, 0.0, THETA))    # the 20 set, the one on the car
  mg = motor_and_gear()
  car, plate, app, green, dark, orange = (0.55, 0.55, 0.58), (0.80, 0.82, 0.85), (0.35, 0.55, 0.85), (0.45, 0.70, 0.45), \
    (0.25, 0.25, 0.28), (0.95, 0.65, 0.3)
  return [(sc.column_cover(back=130.0), car), (grip, car), (teeth, orange), (mg["gear"], orange), (mg["motor"], dark),
          (mg["board"], dark), (plate_to_wheel(frame_plate_v5()), plate), (arm(), app), (carrier(), green)]


def picture(path: str) -> None:
  import render as R
  parts = scene()
  bed = parts_on_bed()
  views = [(parts, R.look((0.9, -0.5, 0.8), (0, 1, 0))), (parts, R.look((0.0, 0.0, 1.0), (0, 1, 0))),
           (parts, R.look((0.0, -1.0, 0.0), (0, 0, 1))),
           ([(bed["column-frame-plate-v5"], (0.8, 0.82, 0.85))], R.view_matrix(-50, 35)),
           ([(bed["right-arm"], (0.35, 0.55, 0.85))], R.view_matrix(-50, 35)),
           ([(bed["right-carrier"], (0.45, 0.70, 0.45))], R.view_matrix(-50, 35))]
  R.save(path, views, cols=2, size=(1000, 650),
         titles=["on the car, from your right and below", "from your seat (the dash behind)",
                 "from below, the wheel at the top (as in your photos)", "frame plate v5, as printed",
                 "arm, as printed", "motor carrier, as printed"],
         suptitle="Right arm mount v6 on the frame plate v5: the motor outside the rim just above 4 o'clock, shaft pointing in. "
                  "The car grey, the plate light, the arm blue, the motor carrier green, the motor dark, the gear and the "
                  "teeth orange. Rough.")


def plate_drawing(path: str) -> None:
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  from matplotlib.patches import Circle, Rectangle
  fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=150)
  for r in (BLOCK, BAR, LEG):
    ax.add_patch(Rectangle((r[0], r[2]), r[1] - r[0], r[3] - r[2], fc="#cfd3d6", ec="#444", lw=1.0))
  for r in (BLOCK, BAR, LEG):
    ax.add_patch(Rectangle((r[0] + 0.5, r[2] + 0.5), r[1] - r[0] - 1.0, r[3] - r[2] - 1.0, fc="#cfd3d6", ec="none"))
  ax.add_patch(Rectangle((TUBE_X[0], TUBE_Y[0]), TUBE_X[1] - TUBE_X[0], TUBE_Y[1] - TUBE_Y[0], fc="#9aa4ad", ec="#444", lw=1.0))
  ax.add_patch(Rectangle((TUBE_X[0], BORE_Y[0]), TUBE_X[1] - TUBE_X[0], BORE_Y[1] - BORE_Y[0], fc="#e8ebee", ec="#444", lw=0.8))
  ax.add_patch(Rectangle((RGROOVE_X[0], TUBE_Y[0] + 1.0), RGROOVE_X[1] - RGROOVE_X[0], 3.0, fc="white", ec="#444"))
  ax.add_patch(Rectangle((-FR.SLOT_L / 2, -FR.SLOT_W / 2), FR.SLOT_L, FR.SLOT_W, fc="white", ec="#444"))
  xc, y0, y1 = LEG_SLOT
  ax.add_patch(Rectangle((xc - FR.SLOT_W / 2, y0), FR.SLOT_W, y1 - y0, fc="white", ec="#444"))
  ax.add_patch(Circle((0, 0), 6.25, fc="none", ec="#c0392b", ls="--", lw=1.5))
  ax.text(0, -12, "cup screw", ha="center", va="top", fontsize=8, color="#c0392b")
  ax.text(xc, -44, "2nd screw", ha="center", va="top", fontsize=8, color="#c0392b")
  ax.text(-22, 57, "receiver across the car: the arm\nslides in from the key side", ha="center", va="center", fontsize=7, color="#444")
  ax.text(RG_MID, 11, "the arm's groove (on your side)", ha="center", va="center", fontsize=7, color="#444")
  ax.set_aspect("equal")
  ax.set_xlim(125, -75)
  ax.set_ylim(78, -62)
  ax.set_xlabel("across the car, mm (0 = cup screw; the key side to the right)")
  ax.set_ylabel("along the column, mm (0 = cup screw; the wheel is up)")
  ax.set_title("Frame plate v5 seen from below, as in your photos: the wheel at the top, the key side on the right.\n"
               "The receiver across the car, its bore 20 wide; the arm's groove in the wall on your side; 6 mm thick.", fontsize=9)
  ax.grid(True, lw=0.3, alpha=0.5)
  fig.tight_layout()
  fig.savefig(path)
  plt.close(fig)


def main():
  info = build()
  for stem, i in info.items():
    print(f"{stem}: {i['size_mm']} mm, about {i['grams_solid']} g solid")
  for n, fname, plate_name, rows, size in bambu_plates():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")
  os.makedirs(REPORT_DIR, exist_ok=True)
  stale = os.path.join(REPORT_DIR, "column-frame-plate-v4.png")
  if os.path.exists(stale):
    os.remove(stale)
  plate_drawing(os.path.join(REPORT_DIR, "column-frame-plate-v5.png"))
  picture(os.path.join(REPORT_DIR, "right-arm.png"))


if __name__ == "__main__":
  sys.exit(main())

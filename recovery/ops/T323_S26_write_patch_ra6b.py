"""rightarm.py v6, second pass: the receiver's groove on the wheel side (reachable from the seat; the dash side is
within millimetres of the dash in the photo estimates), 6.4 tall (its top prints as a 42 mm bridge), the arm's nut
from the wheel side; the carrier's bar end flush with the tower's bottom when slid all the way out; the deep part
clear of the receiver at the groove's end."""
p = "/home/claude/deliver/hardware/cad/rightarm.py"
s = open(p, encoding="utf-8").read()
reps = [
  ("""are a groove in the outer piece and a wing bolt through it into a nut in the inner one, tightened to pull the inner
piece against the outer's wall. The motor's slide up the tower now has 31 mm of travel (the teeth piece may sit 12
mm nearer you or further than drawn); the arm's slide in the receiver 17.5 mm either way across. For a nut in it and
for stiffness, the arm's bar in the receiver is 20 x 30 (was 10 x 30), so the frame plate is v5: its receiver's bore
20 wide, the groove in its dash-side wall where the pinch bolt was. Once the car shows where they sit, a later print
can have shorter slides.""",
   """are a groove in the outer piece and a wing bolt through it into a nut in the inner one, tightened to pull the inner
piece against the outer's wall. The motor's slide up the tower now has 31 mm of travel (the teeth piece may sit 12
mm nearer you or further than drawn); the arm's slide in the receiver 17.5 mm either way across. For a nut in it and
for stiffness, the arm's bar in the receiver is 20 x 30 (was 10 x 30), so the frame plate is v5: its receiver's bore
20 wide, the arm's groove in the wall on your side (v4's pinch bolt was on the dash side, which the photo estimates
put within a few millimetres of the dash). Once the car shows where they sit, a later print can have shorter
slides."""),
  ("""M5_NUT_AF, M5_NUT_T = 8.0, 4.0
NUT_TRAP = (M5_NUT_AF + 0.4, M5_NUT_T + 0.4)
""", """M5_NUT_AF, M5_NUT_T = 8.0, 4.0
"""),
  ("""TUBE_Y = (BORE_Y[0] - 5.0, BORE_Y[1] + 5.0)   # walls 5 each side; the arm's groove in the dash-side one""",
   """TUBE_Y = (BORE_Y[0] - 5.0, BORE_Y[1] + 5.0)   # walls 5 each side; the arm's groove in the wheel-side one"""),
  ("""SLOT_W = 5.6                             # the slides' grooves, across (an M5 wing bolt's shank, 0.35 a side)
ARM_SLIDE = 17.5                         # v6: the arm slides this far either way across from its nominal place
RG_MID = -22.0                           # plate x of the arm's nut at the nominal place, the receiver's middle
RGROOVE_X = (RG_MID - ARM_SLIDE - SLOT_W / 2 - 0.5, RG_MID + ARM_SLIDE + SLOT_W / 2 + 0.5)    # (-42.8, -1.2)""",
   """SLOT_W = 5.6                             # the tower's groove, across (an M5 wing bolt's shank, 0.35 a side)
RSLOT_H = 6.4                            # the receiver's groove, top to bottom: its top prints as a 42 mm bridge, which
                                         # may droop, and the arm has 0.4 of play up and down in the bore
ARM_SLIDE = 17.5                         # v6: the arm slides this far either way across from its nominal place
RG_MID = -22.0                           # plate x of the arm's nut at the nominal place, the receiver's middle
RGROOVE_X = (RG_MID - ARM_SLIDE - RSLOT_H / 2 - 0.5, RG_MID + ARM_SLIDE + RSLOT_H / 2 + 0.5)    # (-43.2, -0.8)
RG_STOP = ARM_SLIDE + 0.5 + (RSLOT_H / 2 - 2.45)    # 18.75: the wing bolt meets the groove's end"""),
  ("""ARM_Z = (CUP_Z - BORE_Y[1] + 0.2, CUP_Z - BORE_Y[0] - 0.2)      # (-175.2, -165.2)""",
   """ARM_Z = (CUP_Z - BORE_Y[1] + 0.2, CUP_Z - BORE_Y[0] - 0.2)      # (-185.2, -165.2)"""),
  ("""ARM_NUT_IN = 6.0                         # the nut this far in from the bar's dash-side face (the bolt's end 3 past it)""",
   """ARM_NUT_IN = 6.0                         # the nut this far in from the bar's wheel-side face (the bolt's end 3 past it)
ARM_NUT_Z = (ARM_Z[1] - ARM_NUT_IN - M5_NUT_T - 0.2, ARM_Z[1] - ARM_NUT_IN + 0.2)    # its slot along the column
ARM_HOLE_END = ARM_Z[1] - ARM_NUT_IN - M5_NUT_T - 4.0                                 # the bolt's hole's bottom"""),
  ("""BAR_END_UP = 8.0                 # the bar's bottom end this far up the tube at the drawn depth (2 below it slid out)""",
   """BAR_END_UP = 18.0                # the bar's bottom end this far up the tube at the drawn depth (level with the tube's
                                 # bottom slid all the way out, so it never reaches further towards the dash)"""),
  ("""BAR_Z = (TOWER_Z[0] + BAR_END_UP, PLATE_Z[1])   # (-167.2, -38.35) at the nominal depth: the end is up in the tube""",
   """BAR_Z = (TOWER_Z[0] + BAR_END_UP, PLATE_Z[1])   # (-167.2, -38.35) at the nominal depth: the end is up in the tube"""),
  ("""DEEP_X0 = RECEIVER_MOUTH + ARM_SLIDE + 0.5   # 138: clear of the receiver with the arm slid all the way in""",
   """DEEP_X0 = RECEIVER_MOUTH + ARM_SLIDE + 2.0   # 139.5: 0.75 clear of the receiver's mouth when the wing bolt stops
                                             # the arm at the groove's end"""),
  ("""def frame_plate_v5() -> Manifold:
  \"\"\"v4 with the receiver's bore 20 wide and, where the pinch bolt and its nut were, the arm's groove along the
  dash-side wall at the bore's mid-height.\"\"\"""",
   """def frame_plate_v5() -> Manifold:
  \"\"\"v4 with the receiver's bore 20 wide, the arm's groove along its wheel-side wall at the bore's mid-height, and
  no pinch bolt or nut trap.\"\"\""""),
  ("""  r = SLOT_W / 2
  ends = [cyl_y(r, BORE_Y[1] - 1.0, TUBE_Y[1] + 1.0, x=x, z=pz, segments=32) for x in (RGROOVE_X[0] + r, RGROOVE_X[1] - r)]""",
   """  r = RSLOT_H / 2
  ends = [cyl_y(r, TUBE_Y[0] - 1.0, BORE_Y[0] + 1.0, x=x, z=pz, segments=32) for x in (RGROOVE_X[0] + r, RGROOVE_X[1] - r)]"""),
  ("""  # v6: the receiver's slide. Its M5 nut drops into a slot in the bar's top (the plate's underside holds it in once the
  # bar is in the receiver), flats along the bar, the slot's bottom the nut's own shape so it sits on the bolt's line;
  # the wing bolt comes in from the dash-side face
  w = SLIDE_NUT_W
  r = w / math.sqrt(3)
  z0 = ARM_Z[0] + ARM_NUT_IN - 0.2
  hexp = CrossSection([[(ARM_NUT_X + r * math.cos(math.radians(90 + 60 * i)), ARM_MID_Y + r * math.sin(math.radians(90 + 60 * i)))
                        for i in range(6)]])                    # a corner down
  pocket = hexp.extrude(M5_NUT_T + 0.4).translate((0.0, 0.0, z0))
  pocket = pocket + box(ARM_NUT_X - w / 2, ARM_NUT_X + w / 2, ARM_MID_Y, ARM_Y[1] + 1.0, z0, z0 + M5_NUT_T + 0.4)
  hole = cyl(M5_HOLE / 2, ARM_Z[0] - 1.0, ARM_Z[0] + ARM_NUT_IN + M5_NUT_T + 4.0, x=ARM_NUT_X, y=ARM_MID_Y, segments=32)""",
   """  # v6: the receiver's slide. Its M5 nut drops into a slot in the bar's top (the frame plate above holds it in once
  # the bar is in the receiver), flats along the bar, the slot's bottom the nut's own shape so it sits on the bolt's
  # line; the wing bolt comes in from the wheel-side face, through the receiver's groove
  w = SLIDE_NUT_W
  r = w / math.sqrt(3)
  z0, z1 = ARM_NUT_Z
  hexp = CrossSection([[(ARM_NUT_X + r * math.cos(math.radians(90 + 60 * i)), ARM_MID_Y + r * math.sin(math.radians(90 + 60 * i)))
                        for i in range(6)]])                    # a corner down
  pocket = hexp.extrude(z1 - z0).translate((0.0, 0.0, z0))
  pocket = pocket + box(ARM_NUT_X - w / 2, ARM_NUT_X + w / 2, ARM_MID_Y, ARM_Y[1] + 1.0, z0, z1)
  hole = cyl(M5_HOLE / 2, ARM_HOLE_END, ARM_Z[1] + 1.0, x=ARM_NUT_X, y=ARM_MID_Y, segments=32)"""),
  ("""  ax.add_patch(Rectangle((RGROOVE_X[0], TUBE_Y[1] - 4.0), RGROOVE_X[1] - RGROOVE_X[0], 3.0, fc="white", ec="#444"))""",
   """  ax.add_patch(Rectangle((RGROOVE_X[0], TUBE_Y[0] + 1.0), RGROOVE_X[1] - RGROOVE_X[0], 3.0, fc="white", ec="#444"))"""),
  ("""  ax.text(-30, 44, "receiver across the car: the arm\\nslides in from the key side", ha="center", va="center", fontsize=7, color="#444")
  ax.text(RG_MID, 12, "the arm's groove (dash side)", ha="center", va="center", fontsize=7, color="#444")""",
   """  ax.text(-22, 57, "receiver across the car: the arm\\nslides in from the key side", ha="center", va="center", fontsize=7, color="#444")
  ax.text(RG_MID, 11, "the arm's groove (on your side)", ha="center", va="center", fontsize=7, color="#444")"""),
  ("""               "The receiver across the car, its bore 20 wide; the arm's groove in its dash-side wall; 6 mm thick.", fontsize=9)""",
   """               "The receiver across the car, its bore 20 wide; the arm's groove in the wall on your side; 6 mm thick.", fontsize=9)"""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:90]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")

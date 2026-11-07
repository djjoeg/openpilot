"""rightarm.py -> the fit print: frame plate v5 (a 20 x 30 receiver with a groove slide), arm and carrier v6 (a longer
slide up the tower; the arm's slide in the receiver by a wing bolt into a nut in the bar)."""
p = "/home/claude/deliver/hardware/cad/rightarm.py"
s = open(p, encoding="utf-8").read()
reps = [
  # docstring
  ("""v5 (3 Nov, after a stiffness check of v4, and your idea for the slide): the arm 50 mm deep along the column from""",
   """v6, the fit print (3 Nov, your note: more travel for the first print, and every slide the same way): both slides
are a groove in the outer piece and a wing bolt through it into a nut in the inner one, tightened to pull the inner
piece against the outer's wall. The motor's slide up the tower now has 31 mm of travel (the teeth piece may sit 12
mm nearer you or further than drawn); the arm's slide in the receiver 17.5 mm either way across. For a nut in it and
for stiffness, the arm's bar in the receiver is 20 x 30 (was 10 x 30), so the frame plate is v5: its receiver's bore
20 wide, the groove in its dash-side wall where the pinch bolt was. Once the car shows where they sit, a later print
can have shorter slides.

v5 (3 Nov, after a stiffness check of v4, and your idea for the slide): the arm 50 mm deep along the column from"""),
  ("""Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, THETA. Adjustable: the arm 5 mm further in across (then
its deep part meets the receiver's end) and 25 out; the motor's slide along the column, anywhere in the groove (how
deep the gear sits). Not adjustable: up and down, and the angle; where the gear sits along the teeth is set by the arm
across and by the gear's place on its shaft.

  python3 rightarm.py   # writes ../stl/right-arm/*.stl, ../plates/plate-11-frame-plate-v4.3mf, plate-12-right-arm.3mf
                        # and ../report/right-arm.png, column-frame-plate-v4.png""",
   """Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, THETA. Adjustable: the arm 17.5 mm either way across, by
its groove in the receiver; the motor along the column, anywhere in the tower's groove (how deep the gear sits, and on
and off). Not adjustable: up and down, and the angle; where the gear sits along the teeth is set by the arm across and
by the gear's place on its shaft.

  python3 rightarm.py   # writes ../stl/right-arm/*.stl, ../plates/plate-11-frame-plate-v5.3mf, plate-12-right-arm.3mf
                        # and ../report/right-arm.png, column-frame-plate-v5.png"""),
  # the frame plate's receiver
  ("""# ***** the frame plate v4 (plate frame: x towards the door, y towards the dash, 0 at the cup) *****
PLATE_T = 6.0
BLOCK = (-60.0, 28.0, -14.0, 50.0)       # v1's block, out to the receiver's far end on the key side
BAR, LEG, LEG_SLOT = AM.BAR, AM.LEG, AM.LEG_SLOT
BORE_Y = (20.0, 30.4)                    # the receiver's bore along the column (10 wide), on the dash side of the cup
BORE_DEPTH = 30.4                        # the arm is 30 tall
TUBE_Y = (BORE_Y[0] - 5.0, BORE_Y[1] + 8.0)   # walls: 5 on the wheel side, 8 on the dash side (the nut trap)
TUBE_X = (-47.0, 3.0)                    # along the plate: 50 long, from just short of the cup's washer out to the key side
TUBE_FLOOR_T = 5.0
PINCH_X = -30.0                          # the wing bolt, through the dash-side wall""",
   """# ***** the frame plate v5 (plate frame: x towards the door, y towards the dash, 0 at the cup) *****
PLATE_T = 6.0
BLOCK = (-60.0, 28.0, -14.0, 50.0)       # v1's block, out to the receiver's far end on the key side
BAR, LEG, LEG_SLOT = AM.BAR, AM.LEG, AM.LEG_SLOT
BORE_Y = (20.0, 40.4)                    # the receiver's bore along the column, 20 wide (v4: 10), on the dash side of the cup
BORE_DEPTH = 30.4                        # the arm is 30 tall
TUBE_Y = (BORE_Y[0] - 5.0, BORE_Y[1] + 5.0)   # walls 5 each side; the arm's groove in the dash-side one
TUBE_X = (-47.0, 3.0)                    # along the plate: 50 long, from just short of the cup's washer out to the key side
TUBE_FLOOR_T = 5.0
SLOT_W = 5.6                             # the slides' grooves, across (an M5 wing bolt's shank, 0.35 a side)
ARM_SLIDE = 17.5                         # v6: the arm slides this far either way across from its nominal place
RG_MID = -22.0                           # plate x of the arm's nut at the nominal place, the receiver's middle
RGROOVE_X = (RG_MID - ARM_SLIDE - SLOT_W / 2 - 0.5, RG_MID + ARM_SLIDE + SLOT_W / 2 + 0.5)    # (-43.3, -0.7)"""),
  ("""ARM_X = (CUP_X - TUBE_X[1] + 3.0, 150.0)                       # (73, 150): 47 in the receiver, nominal""",
   """ARM_X = (CUP_X - TUBE_X[1] + 3.0, 150.0)                       # (73, 150): 47 in the receiver, nominal
ARM_NUT_X = CUP_X - RG_MID               # 95: the arm's nut along its bar, at the nominal place
ARM_MID_Y = (ARM_Y[0] + ARM_Y[1]) / 2    # -128: the receiver's wing bolt's line, the bar's mid-height
ARM_NUT_IN = 6.0                         # the nut this far in from the bar's dash-side face (the bolt's end 3 past it)
RECEIVER_MOUTH = CUP_X - TUBE_X[0]       # 120: the receiver's open end on the key side"""),
  # the tower's slide: longer
  ("""TOWER_Z = (ARM_Z[0], -94.0)""", """TOWER_Z = (ARM_Z[0], -102.0)            # v6: the top 8 lower, so the motor slides 8 further down"""),
  ("""DZ_DEEP, DZ_SHALLOW = 4.0, -4.0  # where the gear may need to sit for the drawn depth: the teeth piece 4 mm nearer you or
                                 # further than drawn (the plate on the cover, the tape under the teeth)""",
   """DZ_DEEP, DZ_SHALLOW = 12.0, -12.0   # where the gear may need to sit for the drawn depth (v6, the fit print): the teeth
                                 # piece 12 mm nearer you or further than drawn (the plate on the cover, the tape)"""),
  ("""# v5's slide (your idea): an M5 x 20 wing bolt and a fender washer, through a groove up the tower's outer wall along
# -u, into an M5 nut in a slot in the carrier's bar; tightened, it pulls the bar against the outer wall
SLIDE_Z0 = -108.0                # the wing bolt's height at the drawn depth
SLOT_W = 5.6                     # the groove, across
""",
   """# the motor's slide (your idea, v5): an M5 x 20 wing bolt and a fender washer, through a groove up the tower's outer
# wall along -u, into an M5 nut in a slot in the carrier's bar; tightened, it pulls the bar against the outer wall
SLIDE_Z0 = -123.0                # the wing bolt's height at the drawn depth
"""),
  ("""TICK_DZ = range(-10, 7)          # depth ticks on the bar's outer face, one a millimetre: the one at the tower's top
TICK_LONG = (-10, -5, 0, 5)      # edge reads the slide (0 the drawn depth; longer ticks every 5)""",
   """TICK_DZ = range(-18, 14)         # depth ticks on the bar's outer face, one a millimetre: the one at the tower's top
TICK_LONG = (-15, -10, -5, 0, 5, 10)   # edge reads the slide (0 the drawn depth; longer ticks every 5)"""),
  ("""DZ_OUT = TOWER_Z[1] - WEB_Z0     # -10: slid all the way out, the web sits on the tower's top (6 mm is enough)
GROOVE_Z = (SLIDE_Z0 + DZ_OUT - SLOT_W / 2 - 0.5, SLIDE_Z0 + DZ_MAX + SLOT_W / 2 + 0.5)    # (-121.3, -99.7)
DEEP = 50.0                      # v5: the arm this deep along the column, from DEEP_X0 to the tower
DEEP_X0 = ARM_X[0] + 47.0 + 5.5  # 125.5: 5.5 outside the receiver's mouth at the nominal place (5 mm left to slide in)""",
   """DZ_OUT = TOWER_Z[1] - WEB_Z0     # -18: slid all the way out, the web sits on the tower's top (6 mm is enough)
GROOVE_Z = (SLIDE_Z0 + DZ_OUT - SLOT_W / 2 - 0.5, SLIDE_Z0 + DZ_MAX + SLOT_W / 2 + 0.5)    # (-144.3, -106.7)
DEEP = 50.0                      # the arm this deep along the column, from DEEP_X0 to the tower (v5)
DEEP_X0 = RECEIVER_MOUTH + ARM_SLIDE + 0.5   # 138: clear of the receiver with the arm slid all the way in"""),
  # the frame plate function
  ("""# ----- the frame plate v4 (plate frame, labels up) -----

def frame_plate_v4() -> Manifold:""",
   """# ----- the frame plate v5 (plate frame, labels up) -----

def frame_plate_v5() -> Manifold:
  \"\"\"v4 with the receiver's bore 20 wide and, where the pinch bolt and its nut were, the arm's groove along the
  dash-side wall at the bore's mid-height.\"\"\""""),
  ("""  pz = T + BORE_DEPTH / 2
  tube = tube - cyl_y(M5_HOLE / 2, BORE_Y[1] - 1.0, TUBE_Y[1] + 1.0, x=PINCH_X, z=pz, segments=32)
  tw, tt = NUT_TRAP
  yn = (BORE_Y[1] + TUBE_Y[1]) / 2
  tube = tube - box(PINCH_X - tw / 2, PINCH_X + tw / 2, yn - tt / 2, yn + tt / 2, pz - tw / 2 / math.cos(math.radians(30)), z1 + 1.0)
  body = body + tube""",
   """  pz = T + BORE_DEPTH / 2
  r = SLOT_W / 2
  ends = [cyl_y(r, BORE_Y[1] - 1.0, TUBE_Y[1] + 1.0, x=x, z=pz, segments=32) for x in (RGROOVE_X[0] + r, RGROOVE_X[1] - r)]
  tube = tube - Manifold.batch_hull(ends)
  body = body + tube"""),
  ("""  labels = [FR.text("< KEY", -16.0, BLOCK[3] - 8.0, T), FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, T, pix=0.9),""",
   """  labels = [FR.text("< KEY", TUBE_X[1] + 3.0, BLOCK[3] - 8.0, T), FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, T, pix=0.9),"""),
  # the arm: its nut and the receiver's bolt hole
  ("""  m = m - uvz(CH_U[0], CH_U[1], CH_V0, CH_V1, TOWER_Z[0] - 1.0, TOWER_Z[1] + 1.0) - bore_mouths()
  return clean(m - groove())""",
   """  m = m - uvz(CH_U[0], CH_U[1], CH_V0, CH_V1, TOWER_Z[0] - 1.0, TOWER_Z[1] + 1.0) - bore_mouths()
  # v6: the receiver's slide. Its M5 nut drops into a slot in the bar's top (the plate's underside holds it in once the
  # bar is in the receiver), flats along the bar, the slot's bottom the nut's own shape so it sits on the bolt's line;
  # the wing bolt comes in from the dash-side face
  w = SLIDE_NUT_W
  r = w / math.sqrt(3)
  z0 = ARM_Z[0] + ARM_NUT_IN - 0.2
  hexp = CrossSection([[(ARM_NUT_X + r * math.cos(math.radians(90 + 60 * i)), ARM_MID_Y + r * math.sin(math.radians(90 + 60 * i)))
                        for i in range(6)]])                    # a corner down
  pocket = hexp.extrude(M5_NUT_T + 0.4).translate((0.0, 0.0, z0))
  pocket = pocket + box(ARM_NUT_X - w / 2, ARM_NUT_X + w / 2, ARM_MID_Y, ARM_Y[1] + 1.0, z0, z0 + M5_NUT_T + 0.4)
  hole = cyl(M5_HOLE / 2, ARM_Z[0] - 1.0, ARM_Z[0] + ARM_NUT_IN + M5_NUT_T + 4.0, x=ARM_NUT_X, y=ARM_MID_Y, segments=32)
  return clean(m - groove() - pocket - hole)"""),
  # the ticks: thinner, so there is plastic between them a millimetre apart
  ("""    m = m - uvz(BAR_U[1] - 0.6, BAR_U[1] + 1.0, bv - w, bv + w, zt - 0.4, zt + 0.4)""",
   """    m = m - uvz(BAR_U[1] - 0.6, BAR_U[1] + 1.0, bv - w, bv + w, zt - 0.25, zt + 0.25)"""),
  # the bed and the plates
  ("""  return {"column-frame-plate-v4": on_bed(frame_plate_v4()),""", """  return {"column-frame-plate-v5": on_bed(frame_plate_v5()),"""),
  ("""  for stale in ("right-bar", "right-bracket"):          # v2's pieces""",
   """  for stale in ("right-bar", "right-bracket", "column-frame-plate-v4"):          # v2's pieces, the v4 plate"""),
  ("""  parts = {"column-frame-plate-v4": ("frame plate v4", 1, P.STANDARD)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-11-frame-plate-v4", "11 frame plate v4", list(parts), "Plate 11: the frame plate v4 (the receiver across)")])""",
   """  pdir = os.path.join(HERE, "..", "plates")
  for stale in ("plate-11-frame-plate-v4.3mf", "plate-11-frame-plate-v4.png"):
    if os.path.exists(os.path.join(pdir, stale)):
      os.remove(os.path.join(pdir, stale))
  parts = {"column-frame-plate-v5": ("frame plate v5", 1, P.STANDARD)}
  out += P.build(out_dir=pdir, stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-11-frame-plate-v5", "11 frame plate v5", list(parts),
                              "Plate 11: the frame plate v5 (the receiver 20 wide, the arm's groove in it)")])"""),
  ("""                 plate_list=[("plate-12-right-arm", "12 right arm v5", list(parts),
                              "Plate 12: the right arm mount v5: the arm (deep, the groove up its tower) and the carrier")])""",
   """                 plate_list=[("plate-12-right-arm", "12 right arm v6", list(parts),
                              "Plate 12: the right arm mount v6, the fit print: the arm and the motor carrier")])"""),
  ("""          (mg["board"], dark), (plate_to_wheel(frame_plate_v4()), plate), (arm(), app), (carrier(), green)]""",
   """          (mg["board"], dark), (plate_to_wheel(frame_plate_v5()), plate), (arm(), app), (carrier(), green)]"""),
  ("""           ([(bed["column-frame-plate-v4"], (0.8, 0.82, 0.85))], R.view_matrix(-50, 35)),""",
   """           ([(bed["column-frame-plate-v5"], (0.8, 0.82, 0.85))], R.view_matrix(-50, 35)),"""),
  ("""                 "from below, the wheel at the top (as in your photos)", "frame plate v4, as printed",""",
   """                 "from below, the wheel at the top (as in your photos)", "frame plate v5, as printed","""),
  ("""         suptitle="Right arm mount v5 on the frame plate v4: the motor outside the rim just above 4 o'clock, shaft pointing in. \"""",
   """         suptitle="Right arm mount v6 on the frame plate v5: the motor outside the rim just above 4 o'clock, shaft pointing in. \""""),
  # the plate drawing
  ("""  ax.add_patch(Circle((PINCH_X, TUBE_Y[1] - 4.0), 2.7, fc="white", ec="#444"))""",
   """  ax.add_patch(Rectangle((RGROOVE_X[0], TUBE_Y[1] - 4.0), RGROOVE_X[1] - RGROOVE_X[0], 3.0, fc="white", ec="#444"))"""),
  ("""  ax.text(PINCH_X, 12, "wing bolt", ha="center", va="center", fontsize=7, color="#444")""",
   """  ax.text(RG_MID, 12, "the arm's groove (dash side)", ha="center", va="center", fontsize=7, color="#444")"""),
  ("""  ax.set_title("Frame plate v4 seen from below, as in your photos: the wheel at the top, the key side on the right.\\n"
               "v3 with the receiver turned across the car; 6 mm thick.", fontsize=9)""",
   """  ax.set_title("Frame plate v5 seen from below, as in your photos: the wheel at the top, the key side on the right.\\n"
               "The receiver across the car, its bore 20 wide; the arm's groove in its dash-side wall; 6 mm thick.", fontsize=9)"""),
  ("""  plate_drawing(os.path.join(REPORT_DIR, "column-frame-plate-v4.png"))""",
   """  stale = os.path.join(REPORT_DIR, "column-frame-plate-v4.png")
  if os.path.exists(stale):
    os.remove(stale)
  plate_drawing(os.path.join(REPORT_DIR, "column-frame-plate-v5.png"))"""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:90]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")

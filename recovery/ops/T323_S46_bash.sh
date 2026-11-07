python3 - <<'EOF'
import re
# ---- viewer3d.py ----
p = "viewer3d.py"
s = open(p, encoding="utf-8").read()
reps = [
("""The right arm mount v5 as a 3D model to turn round in a web page (3 Nov 2026). The printed parts are the CAD parts
exactly (the same shapes as the print files), where they go on the car: the frame plate v4, the arm, the motor
carrier and the teeth; with the motor, its four screws, the gear, the zip ties, the wing bolts, washer and nuts. Round""",
 """The right arm mount v6, the fit print, as a 3D model to turn round in a web page (3 Nov 2026). The printed parts are
the CAD parts exactly (the same shapes as the print files), where they go on the car: the frame plate v5, the arm,
the motor carrier and the teeth; with the motor, its four screws, the gear, the zip ties, the wing bolts, washers and
nuts. Round"""),
("""M_ARM = [mv(7, 0.0, 0.5, (80.0, 0.0, 0.0))]                       # into the receiver from the key side, all on it
M_UP = [mv(8, 0.0, 0.6, (0.0, 0.0, -10.0))]                       # the motor slid up the groove into the teeth""",
 """M_ARM = [mv(7, 0.35, 0.85, (80.0, 0.0, 0.0))]                     # into the receiver from the key side, all on it
M_UP = [mv(9, 0.0, 0.6, (0.0, 0.0, RA.DZ_OUT))]                   # the motor slid up the groove into the teeth"""),
("""  ("The arm, with all of that on it, into the frame plate's square tube from the key side. Push the nut up into the "
   "slot in the tube's far wall and turn its wing bolt in through that wall: it pinches the arm."),
  ("Loosen the slide's wing bolt, slide it up the groove till the gear is all the way into the teeth, back it down "
   "1 mm (one tick on the bar at the tower's top) and tighten: lane keeping on. Down till the carrier sits on the "
   "tower: off."),
]""",
 """  ("The arm's M5 nut into the slot in the top of its bar, flats along the bar (it only goes in that way). Then the "
   "arm, with all of that on it, into the frame plate's square tube from the key side."),
  ("The arm's wing bolt, a fender washer under its wings, in through the long groove in the tube's wall on your side "
   "and a few turns into the arm's nut. Now the arm can't come out. Slide the arm across by it till the gear lines up "
   "with the teeth, and tighten: it pulls the arm against the wall."),
  ("Loosen the motor's wing bolt, slide it up the groove till the gear is all the way into the teeth, back it down "
   "1 mm (one tick on the bar at the tower's top) and tighten: lane keeping on. Down till the carrier sits on the "
   "tower: off."),
]"""),
("""  "plate": ("166 x 96 x 41 mm. Hangs on the column cover's two screws (the cup slot on the key side, slot 1 on the "
            "other). The square tube underneath is the receiver: the arm slides in from the key side. The printed "
            "labels (KEY, WHEEL, 1) face down."),""",
 """  "plate": ("v5. 166 x 96 x 41 mm. Hangs on the column cover's two screws (the cup slot on the key side, slot 1 on "
            "the other). The square tube underneath is the receiver, its bore 20 wide: the arm slides in from the key "
            "side, held by a wing bolt through the long groove in the wall on your side. The labels (KEY, WHEEL, 1), "
            "cut into the plate, face down."),"""),
("""  "arm": ("v5. Its 10 x 30 bar goes into the frame plate's square tube (47 mm in; 5 mm further in or as far out as "
          "you like sets how far right the motor sits); just outside, the arm is 50 mm deep along the column so it "
          "doesn't twist. The tower at its end runs along the column: a square tube, closed all round, that the motor "
          "carrier's bar slides in, with the slide's groove up its outer wall."),
  "carrier": ("v5. The motor bolts to the outside of its plate. Its long bar slides along the column in the tower's "
              "tube, in from the top; the slide's M5 nut sits in a slot across it, and the ticks on its outer face, "
              "read at the tower's top, show how far up it is (the long one is the drawn depth)."),""",
 """  "arm": ("v6, the fit print. Its 20 x 30 bar goes into the frame plate's square tube (47 mm in as drawn, 17.5 "
          "further in or out by the groove: how far right the motor sits), its M5 nut in the slot in its top; just "
          "outside, the arm is 50 mm deep along the column so it doesn't twist. The tower at its end runs along the "
          "column: a square tube, closed all round, that the motor carrier's bar slides in, with the motor's groove "
          "up its outer wall."),
  "carrier": ("v6. The motor bolts to the outside of its plate. Its long bar slides along the column in the tower's "
              "tube, in from the top, 31 mm of travel; the slide's M5 nut sits in a slot across it, and the ticks on "
              "its outer face, read at the tower's top, show how far up it is (the long one in the middle is the drawn "
              "depth)."),"""),
("""  "rbolt": BOLT + "In through the square tube's far (dash-side) wall; it pinches the arm's bar.",
  "rnut": "In the slot in the square tube's far wall, pushed up into it from below.",""",
 """  "rbolt": (BOLT + "The arm's slide: in through the long groove in the square tube's wall on your side, screwed into "
            "the nut in the arm's bar. Loosen it and slide the arm across by it; tighten it to hold (it pulls the bar "
            "against the wall). The groove's ends keep the arm in."),
  "rwasher": "Fender washer under the arm's wing bolt, wider than the groove.",
  "rnut": "M5 nut in the slot in the top of the arm's bar, its flats along the bar so it can't turn; the frame plate above keeps it in.","""),
("""    ("plate", "Frame plate v4 (plate 11)", n["plate"], "plate", True,
     [(RA.plate_to_wheel(RA.frame_plate_v4()), PLATE, 1.0)], M_PLATE),""",
 """    ("plate", "Frame plate v5 (plate 11)", n["plate"], "plate", True,
     [(RA.plate_to_wheel(RA.frame_plate_v5()), PLATE, 1.0)], M_PLATE),"""),
("""    ("rbolt", "Receiver wing bolt", n["rbolt"], "bolts", True, [(hw["receiver bolt"], STEEL, 1.0)],
     M_PLATE + [mv(7, 0.75, 1.0, (0.0, 0.0, -25.0))]),
    ("rnut", "Receiver nut (M5)", n["rnut"], "bolts", True, [(hw["receiver nut"], STEEL, 1.0)],
     M_PLATE + [mv(7, 0.5, 0.75, (0.0, -20.0, 0.0))]),""",
 """    ("rbolt", "Arm wing bolt", n["rbolt"], "bolts", True, [(hw["receiver bolt"], STEEL, 1.0)],
     M_ARM + [mv(8, 0.0, 1.0, (0.0, 0.0, 25.0))]),
    ("rwasher", "Arm washer (fender washer)", n["rwasher"], "bolts", True, [(hw["receiver washer"], STEEL, 1.0)],
     M_ARM + [mv(8, 0.0, 1.0, (0.0, 0.0, 25.0))]),
    ("rnut", "Arm nut (M5)", n["rnut"], "bolts", True, [(hw["receiver nut"], STEEL, 1.0)],
     M_ARM + [mv(7, 0.0, 0.35, (0.0, 25.0, 0.0))]),"""),
("""    ("sbolt", "Slide wing bolt", n["sbolt"], "bolts", True, [(hw["slide bolt"], STEEL, 1.0)], slide_moves),
    ("swasher", "Slide washer (fender washer)", n["swasher"], "bolts", True, [(hw["slide washer"], STEEL, 1.0)], slide_moves),""",
 """    ("sbolt", "Motor wing bolt", n["sbolt"], "bolts", True, [(hw["slide bolt"], STEEL, 1.0)], slide_moves),
    ("swasher", "Motor washer (fender washer)", n["swasher"], "bolts", True, [(hw["slide washer"], STEEL, 1.0)], slide_moves),"""),
("""    ("snut", "Slide nut (M5)", n["snut"], "bolts", True, [(hw["slide nut"], STEEL, 1.0)],""",
 """    ("snut", "Motor nut (M5)", n["snut"], "bolts", True, [(hw["slide nut"], STEEL, 1.0)],"""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:70]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)

# ---- the page ----
p = "viewer3d_page.html"
s = open(p, encoding="utf-8").read()
for a, b in (("<h1>Right arm mount v5</h1>", "<h1>Right arm mount v6</h1>"),):
  assert s.count(a) == 1
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)

# ---- incar.py, carphoto.py ----
for p in ("incar.py", "carphoto.py"):
  s = open(p, encoding="utf-8").read()
  assert s.count("RA.frame_plate_v4()") == 1
  s = s.replace("RA.frame_plate_v4()", "RA.frame_plate_v5()")
  if p == "incar.py":
    a = """The parts are the CAD parts exactly, where the CAD puts them: the frame plate v4 on the column cover's screws, the arm
v5 and its tower, the motor carrier with the motor (slid up the groove, the gear in the teeth), the gear, the teeth"""
    b = """The parts are the CAD parts exactly, where the CAD puts them: the frame plate v5 on the column cover's screws, the arm
v6 and its tower, the motor carrier with the motor (slid up the groove, the gear in the teeth), the gear, the teeth"""
    assert s.count(a) == 1
    s = s.replace(a, b)
  open(p, "w", encoding="utf-8").write(s)

# ---- allinone.py ----
p = "allinone.py"
s = open(p, encoding="utf-8").read()
reps = [
("""One print for everything the right-arm build needs (2 Nov 2026; 3 Nov: the arm and carrier v5, the teeth v3): the
frame plate v4, the steering wheel teeth v3""",
 """One print for everything the right-arm build needs (2 Nov 2026; 3 Nov: the arm and carrier v6, the fit print, the
frame plate v5, the teeth v3): the frame plate v5, the steering wheel teeth v3"""),
("""  "column-frame-plate-v4": ("right-arm", "frame plate v4", P.STANDARD),""",
 """  "column-frame-plate-v5": ("right-arm", "frame plate v5", P.STANDARD),"""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:70]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
grep -n "column-frame-plate\|v4\|v5" allinone.py | head; grep -n "Together\|caption" viewer3d_page.html | head
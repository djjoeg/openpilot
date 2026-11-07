python3 - <<'EOF'
p = 'viewer3d.py'
s = open(p, encoding='utf-8').read()
reps = [
("""The right arm mount v4 as a 3D model to turn round in a web page (3 Nov 2026). The printed parts are the CAD parts
exactly (the same shapes as the print files), where they go on the car: the frame plate v4, the arm, the motor
carrier and the teeth; with the motor, its four screws, the gear, the zip ties and the wing bolts and nuts. Round""",
 """The right arm mount v5 as a 3D model to turn round in a web page (3 Nov 2026). The printed parts are the CAD parts
exactly (the same shapes as the print files), where they go on the car: the frame plate v4, the arm, the motor
carrier and the teeth; with the motor, its four screws, the gear, the zip ties, the wing bolts, washer and nuts. Round"""),
("""M_UP = [mv(8, 0.0, 0.6, (0.0, 0.0, -10.0))]                       # the motor slid up the column to the stop""",
 """M_UP = [mv(8, 0.0, 0.6, (0.0, 0.0, -10.0))]                       # the motor slid up the groove into the teeth"""),
("""  ("The nuts: the M4 nut into the slot near the end of the carrier's bar; the tower's M5 nut into the slot at the top "
   "of its outer wall, and the tower's wing bolt in through that wall a few turns."),
  ("The carrier's bar down the tower's tube from the top, all the way, till the carrier sits on the tower."),
  ("The stop: the M4 bolt, a fender washer under its head and the jam nut on it, a few turns into the end of the "
   "carrier's bar, below the tower."),""",
 """  ("The slide's M5 nut into the slot in the carrier's bar, from the motor's side, its flats along the bar."),
  ("The carrier's bar down the tower's tube from the top, all the way, till the carrier sits on the tower."),
  ("The slide's wing bolt, a fender washer under its wings, in through the groove up the tower's outer wall and a few "
   "turns into that nut. Now the carrier can't come out."),"""),
("""  ("Slide the motor up the column against the stop: the gear in the teeth. Tighten the tower's wing bolt. (README "
   "step 4 sets the stop: the M4 bolt a quarter turn at a time, then the jam nut.)"),""",
 """  ("Loosen the slide's wing bolt, slide it up the groove till the gear is all the way into the teeth, back it down "
   "1 mm (one tick on the bar at the tower's top) and tighten: lane keeping on. Down till the carrier sits on the "
   "tower: off."),"""),
("""M4 = "M4 x 30 bolt. "
""", ""),
("""  "arm": ("v4. Its 10 x 30 bar goes into the frame plate's square tube (47 mm in; slide it up to 25 mm either way to "
          "set how far right the motor sits). The tower at its end runs along the column: a square tube, closed all "
          "round, that the motor carrier's bar slides in."),
  "carrier": ("v4. The motor bolts to the outside of its plate. Its long bar slides along the column in the tower's "
              "tube, in from the top; the M4 stop bolt screws into its far end, its nut in the slot 4 mm in."),""",
 """  "arm": ("v5. Its 10 x 30 bar goes into the frame plate's square tube (47 mm in; 5 mm further in or as far out as "
          "you like sets how far right the motor sits); just outside, the arm is 50 mm deep along the column so it "
          "doesn't twist. The tower at its end runs along the column: a square tube, closed all round, that the motor "
          "carrier's bar slides in, with the slide's groove up its outer wall."),
  "carrier": ("v5. The motor bolts to the outside of its plate. Its long bar slides along the column in the tower's "
              "tube, in from the top; the slide's M5 nut sits in a slot across it, and the ticks on its outer face, "
              "read at the tower's top, show how far up it is (the long one is the drawn depth)."),"""),
("""  "gear": "On the motor's shaft, set screw on the flat. Slid up against the stop, it sits in the teeth.",""",
 """  "gear": "On the motor's shaft, set screw on the flat. Slid up the groove, it sits in the teeth.","""),
("""  "pbolt": (BOLT + "In through the tower's outer wall onto the carrier's bar. Loosen it to slide the motor (lane "
            "keeping on and off)."),
  "pnut": "Dropped into the slot at the top of the tower's outer wall.",
  "sbolt": (M4 + "Up the middle of the carrier's bar from its end, below the tower: the washer under its head lands "
            "on the tower's bottom and stops the carrier, so it can't come out, and how far it is screwed in sets how "
            "deep the gear sits in the teeth."),
  "swasher": "Fender washer under the stop bolt's head, wider than the tube: it lands on the tower's bottom face.",
  "snut": "M4 nut, dropped into the slot near the end of the carrier's bar; the stop bolt screws into it.",
  "jnut": "M4 jam nut on the stop bolt, tightened against the bar's end: it locks the stop.",""",
 """  "sbolt": (BOLT + "The slide: in the groove up the tower's outer wall, screwed into the nut in the carrier's bar. "
            "Loosen it and slide the motor by it along the column (lane keeping on and off, and how deep the gear "
            "sits); tighten it to hold. The groove's ends keep the carrier in."),
  "swasher": "Fender washer under the slide's wing bolt, wider than the groove.",
  "snut": "M5 nut in the slot across the carrier's bar, its flats along the bar so it can't turn; the slide's wing bolt screws into it.","""),
("""  hw = RC.hardware(0.0, RA.STOP_GAP)""", """  hw = RC.hardware(0.0)"""),
("""  stop_moves = M_ARM + M_UP + [mv(6, 0.0, 1.0, (0.0, 0.0, -30.0))]   # waits below the tower, then up into the bar""",
 """  slide_moves = M_ARM + M_UP + [mv(6, 0.0, 1.0, scale(25.0, U3))]   # waits outside the groove, then in along it"""),
("""    ("pbolt", "Tower wing bolt", n["pbolt"], "bolts", True, [(hw["push bolt"], STEEL, 1.0)],
     M_ARM + [mv(4, 0.6, 1.0, scale(28.0, U3)), mv(8, 0.6, 1.0, scale(8.0, U3))]),
    ("pnut", "Tower nut (M5)", n["pnut"], "bolts", True, [(hw["push nut"], STEEL, 1.0)],
     M_ARM + [mv(4, 0.35, 0.6, (0.0, 0.0, 25.0))]),
    ("snut", "Stop nut (M4)", n["snut"], "bolts", True, [(hw["stop nut"], STEEL, 1.0)],
     M_CARRIER + [mv(4, 0.0, 0.35, scale(20.0, V3))]),
    ("sbolt", "Stop bolt (M4 x 30)", n["sbolt"], "bolts", True, [(hw["stop bolt"], STEEL, 1.0)], stop_moves),
    ("swasher", "Stop washer (fender washer)", n["swasher"], "bolts", True, [(hw["stop washer"], STEEL, 1.0)], stop_moves),
    ("jnut", "Stop jam nut (M4)", n["jnut"], "bolts", True, [(hw["stop jam nut"], STEEL, 1.0)], stop_moves),""",
 """    ("snut", "Slide nut (M5)", n["snut"], "bolts", True, [(hw["slide nut"], STEEL, 1.0)],
     M_CARRIER + [mv(4, 0.0, 1.0, scale(20.0, V3))]),
    ("sbolt", "Slide wing bolt", n["sbolt"], "bolts", True, [(hw["slide bolt"], STEEL, 1.0)], slide_moves),
    ("swasher", "Slide washer (fender washer)", n["swasher"], "bolts", True, [(hw["slide washer"], STEEL, 1.0)], slide_moves),"""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
p = 'viewer3d_page.html'
s = open(p, encoding='utf-8').read()
a = "<h1>Right arm mount v4</h1>"
assert s.count(a) == 1
open(p, 'w', encoding='utf-8').write(s.replace(a, "<h1>Right arm mount v5</h1>"))
print('ok')
EOF
grep -n "STOP_GAP\|M4\|stop" viewer3d.py visuals.py | head
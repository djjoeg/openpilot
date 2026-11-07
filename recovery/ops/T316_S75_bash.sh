python3 - <<'EOF'
p='viewer3d.py'; s=open(p).read()
a0 = s.index("# the moves, in the order it goes together")
a1 = s.index("# display colours (screen RGB)")
s = s[:a0] + '''# the moves, in the order it goes together (README steps 1 to 4); a part on another part takes that part's moves too
M_PLATE = [mv(1, 0.0, 1.0, (0.0, -55.0, 0.0))]                    # up onto the cover's two screws
M_TEETH = [mv(2, 0.0, 0.6, (0.0, 0.0, -45.0))]                    # onto the back of the grip
M_ARM = [mv(7, 0.0, 0.5, (80.0, 0.0, 0.0))]                       # into the receiver from the key side, all on it
M_UP = [mv(8, 0.0, 0.6, (0.0, 0.0, -10.0))]                       # the motor slid up the column to the stop
M_CARRIER = M_ARM + M_UP + [mv(5, 0.0, 1.0, (0.0, 0.0, 150.0))]   # down the tower's tube from the top, off the car

STEPS = [
  ("Fit the frame plate on the column cover's two screws, with washers: the cup slot on the key side, slot 1 on the "
   "other. Its flat side goes up against the cover; the square tube hangs underneath, the printed labels facing down."),
  ("Fit the teeth on the grip just above 4 o'clock (one wrap of silicone tape under them), between the two spokes, "
   "two zip ties through the middle slot, heads tucked inside the rim."),
  ("Off the car: the motor on the carrier, against the outside of its plate: four M3 x 10 from the side with the "
   "four round pads, the motor's boss in the big hole. Then the gear on the shaft (set screw on the flat)."),
  ("The nuts: the M4 nut into the slot near the end of the carrier's bar; the tower's M5 nut into the slot at the top "
   "of its outer wall, and the tower's wing bolt in through that wall a few turns."),
  ("The carrier's bar down the tower's tube from the top, all the way, till the carrier sits on the tower."),
  ("The stop: the M4 bolt, a fender washer under its head and the jam nut on it, a few turns into the end of the "
   "carrier's bar, below the tower."),
  ("The arm, with all of that on it, into the frame plate's square tube from the key side. Push the nut up into the "
   "slot in the tube's far wall and turn its wing bolt in through that wall: it pinches the arm."),
  ("Slide the motor up the column against the stop: the gear in the teeth. Tighten the tower's wing bolt. (README "
   "step 4 sets the stop: the M4 bolt a quarter turn at a time, then the jam nut.)"),
]

''' + s[a1:]
rep = [
('''BOLT = "M5 x 20 stainless wing bolt. "''', '''BOLT = "M5 x 20 stainless wing bolt. "
M4 = "M4 x 30 bolt. "'''),
('''  "teeth": "On the grip at 4 o'clock, on one wrap of silicone tape; the gear meets them from outside the rim.",''',
'''  "teeth": ("v3: on the grip between the two spokes, just above 4 o'clock, on one wrap of silicone tape; the gear meets "
            "them from outside the rim. The ends stop just past the last teeth, clear of the spokes' joins."),'''),
('''  "arm": ("115 x 44 x 81 mm. Its 10 x 30 bar goes into the frame plate's square tube (47 mm in; slide it up to 25 mm "
          "either way to set how far right the motor sits). The tower at its end runs along the column; its channel, "
          "open towards the motor, takes the motor carrier's bar."),
  "carrier": ("44 x 148 x 61 mm. The motor bolts to the outside of its plate. Its long bar slides along the column in "
              "the tower's channel; the lug at the bar's far end takes the stop wing bolt, its nut in the hex pocket."),''',
'''  "arm": ("v4. Its 10 x 30 bar goes into the frame plate's square tube (47 mm in; slide it up to 25 mm either way to "
          "set how far right the motor sits). The tower at its end runs along the column: a square tube, closed all "
          "round, that the motor carrier's bar slides in."),
  "carrier": ("v4. The motor bolts to the outside of its plate. Its long bar slides along the column in the tower's "
              "tube, in from the top; the M4 stop bolt screws into its far end, its nut in the slot 4 mm in."),'''),
('''  "sbolt": (BOLT + "Up through the carrier's lug; its tip stops the carrier against the tower: how deep the gear sits "
            "in the teeth."),
  "snut": "In the hex pocket on the carrier's lug.",
  "jnut": "On the stop wing bolt under the lug: tightened up against the lug, it locks the stop.",''',
'''  "sbolt": (M4 + "Up the middle of the carrier's bar from its end, below the tower: the washer under its head lands "
            "on the tower's bottom and stops the carrier, so it can't come out, and how far it is screwed in sets how "
            "deep the gear sits in the teeth."),
  "swasher": "Fender washer under the stop bolt's head, wider than the tube: it lands on the tower's bottom face.",
  "snut": "M4 nut, dropped into the slot near the end of the carrier's bar; the stop bolt screws into it.",
  "jnut": "M4 jam nut on the stop bolt, tightened against the bar's end: it locks the stop.",'''),
('''  hw = RC.hardware(0.0, RA.STOP_P)''', '''  hw = RC.hardware(0.0, RA.STOP_GAP)'''),
('''  motor_moves = M_CARRIER + [mv(5, 0.0, 0.35, scale(35.0, U3))]''', '''  motor_moves = M_CARRIER + [mv(3, 0.0, 0.4, scale(35.0, U3))]
  stop_moves = M_ARM + M_UP + [mv(6, 0.0, 1.0, (0.0, 0.0, -30.0))]   # waits below the tower, then up into the bar'''),
('''    ("screws", "Motor screws (4 x M3 x 10)", n["screws"], "motor", True, [(heads, STEEL, 1.0)],
     M_CARRIER + [mv(5, 0.35, 0.6, scale(-15.0, U3))]),
    ("gear", "Gear", n["gear"], "motor", True, [(RA.motor_and_gear(0.0)["gear"], GEAR, 1.0)], M_CARRIER + [mv(5, 0.6, 1.0, scale(-25.0, U3))]),
    ("rbolt", "Receiver wing bolt", n["rbolt"], "bolts", True, [(hw["receiver bolt"], STEEL, 1.0)],
     M_PLATE + [mv(3, 0.75, 1.0, (0.0, 0.0, -25.0))]),
    ("rnut", "Receiver nut (M5)", n["rnut"], "bolts", True, [(hw["receiver nut"], STEEL, 1.0)],
     M_PLATE + [mv(3, 0.5, 0.75, (0.0, -20.0, 0.0))]),
    ("pbolt", "Tower wing bolt", n["pbolt"], "bolts", True, [(hw["push bolt"], STEEL, 1.0)],
     M_ARM + [mv(4, 0.4, 1.0, scale(28.0, U3)), mv(7, 0.75, 1.0, scale(8.0, U3))]),
    ("pnut", "Tower nut (M5)", n["pnut"], "bolts", True, [(hw["push nut"], STEEL, 1.0)],
     M_ARM + [mv(4, 0.0, 0.4, (0.0, 0.0, 25.0))]),
    ("sbolt", "Stop wing bolt", n["sbolt"], "bolts", True, [(hw["stop bolt"], STEEL, 1.0)],
     M_CARRIER + [mv(6, 0.35, 1.0, (0.0, 0.0, -30.0))]),
    ("snut", "Stop nut (M5)", n["snut"], "bolts", True, [(hw["stop nut"], STEEL, 1.0)],
     M_CARRIER + [mv(6, 0.0, 0.3, (0.0, 0.0, 15.0))]),
    ("jnut", "Stop jam nut (M5)", n["jnut"], "bolts", True, [(hw["stop jam nut"], STEEL, 1.0)],
     M_CARRIER + [mv(6, 0.35, 1.0, (0.0, 0.0, -30.0))]),
  ]''',
'''    ("screws", "Motor screws (4 x M3 x 10)", n["screws"], "motor", True, [(heads, STEEL, 1.0)],
     M_CARRIER + [mv(3, 0.4, 0.65, scale(-15.0, U3))]),
    ("gear", "Gear", n["gear"], "motor", True, [(RA.motor_and_gear(0.0)["gear"], GEAR, 1.0)],
     M_CARRIER + [mv(3, 0.65, 1.0, scale(-25.0, U3))]),
    ("rbolt", "Receiver wing bolt", n["rbolt"], "bolts", True, [(hw["receiver bolt"], STEEL, 1.0)],
     M_PLATE + [mv(7, 0.75, 1.0, (0.0, 0.0, -25.0))]),
    ("rnut", "Receiver nut (M5)", n["rnut"], "bolts", True, [(hw["receiver nut"], STEEL, 1.0)],
     M_PLATE + [mv(7, 0.5, 0.75, (0.0, -20.0, 0.0))]),
    ("pbolt", "Tower wing bolt", n["pbolt"], "bolts", True, [(hw["push bolt"], STEEL, 1.0)],
     M_ARM + [mv(4, 0.6, 1.0, scale(28.0, U3)), mv(8, 0.6, 1.0, scale(8.0, U3))]),
    ("pnut", "Tower nut (M5)", n["pnut"], "bolts", True, [(hw["push nut"], STEEL, 1.0)],
     M_ARM + [mv(4, 0.35, 0.6, (0.0, 0.0, 25.0))]),
    ("snut", "Stop nut (M4)", n["snut"], "bolts", True, [(hw["stop nut"], STEEL, 1.0)],
     M_CARRIER + [mv(4, 0.0, 0.35, scale(20.0, V3))]),
    ("sbolt", "Stop bolt (M4 x 30)", n["sbolt"], "bolts", True, [(hw["stop bolt"], STEEL, 1.0)], stop_moves),
    ("swasher", "Stop washer (fender washer)", n["swasher"], "bolts", True, [(hw["stop washer"], STEEL, 1.0)], stop_moves),
    ("jnut", "Stop jam nut (M4)", n["jnut"], "bolts", True, [(hw["stop jam nut"], STEEL, 1.0)], stop_moves),
  ]'''),
('''The right arm mount v3 as a 3D model to turn round in a web page (3 Nov 2026).''', '''The right arm mount v4 as a 3D model to turn round in a web page (3 Nov 2026).'''),
]
for a,b in rep:
  assert a in s, a[:70]; s=s.replace(a,b)
open(p,'w').write(s)

p='viewer3d_page.html'; s=open(p).read()
rep=[('<title>Right Arm Mount v3</title>', '<title>Right Arm Mount</title>'),
     ('<h1>Right arm mount v3</h1>', '<h1>Right arm mount v4</h1>'),
     ('''<p>2010 Accord, 4 o'clock on the steering wheel</p>''', '''<p>2010 Accord, just above 4 o'clock on the steering wheel</p>'''),
     ('''text.textContent = "Every piece apart, near where it goes. Press Next, or slide right, to put it together one step at a time.";''',
      '''text.textContent = "Every piece apart, near where it goes; the arm's pieces off to the right, where they go together off the car. Press Next, or slide right, to put it together one step at a time.";'''),
]
for a,b in rep:
  assert a in s, a[:50]; s=s.replace(a,b)
open(p,'w').write(s)
print("ok")
EOF
ruff check viewer3d.py --output-format concise | head -5
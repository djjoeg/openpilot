python3 - <<'EOF'
p='viewer3d.py'; s=open(p).read()
a = s.index('  bolt_note = "M5 x 20 stainless wing bolt."\n')
b = s.index('CHIPS = [')
new = '''  motor_moves = M_CARRIER + [mv(5, 0.0, 0.35, scale(45.0, U3))]
  n = NOTES
  return [
    ("cover", "Column cover (the car)", n["cover"], "car", False,
     [(CS.CarScene(D=125.0).column_cover(back=130.0), COVER, 0.26)], []),
    ("grip", "Steering wheel grip (the car)", n["grip"], "car", True, [(RC.grip(), GRIP, 1.0)], []),
    ("plate", "Frame plate v4 (plate 11)", n["plate"], "plate", True,
     [(RA.plate_to_wheel(RA.frame_plate_v4()), PLATE, 1.0)], M_PLATE),
    ("teeth", "Steering wheel teeth (plate 9)", n["teeth"], "teeth", True, [(teeth, TEETH, 1.0)], M_TEETH),
    ("zips", "Zip ties (2)", n["zips"], "teeth", True, [(zips, NYLON, 1.0)],
     M_TEETH + [mv(2, 0.6, 1.0, scale(30.0, U3))]),
    ("arm", "Arm with its tower (plate 12)", n["arm"], "arm", True, [(RA.arm(), BLUE, 1.0)], M_ARM),
    ("carrier", "Motor carrier (plate 12)", n["carrier"], "carrier", True, [(RA.carrier(), GREEN, 1.0)], M_CARRIER),
    ("motor", "Stepper motor (17HS15-1504S-X1)", n["motor"], "motor", True,
     [(motor, MOTOR, 1.0), (mp[4], STEEL, 1.0)], motor_moves),
    ("board", "Motor board (StepperServoCAN)", n["board"], "motor", True,
     [(mp[17], PCB, 1.0), (chips, CHIP, 1.0), (plugs, PLUG, 1.0), (board_steel, STEEL, 1.0)], motor_moves),
    ("screws", "Motor screws (4 x M3 x 10)", n["screws"], "motor", True, [(heads, STEEL, 1.0)],
     M_CARRIER + [mv(5, 0.35, 0.6, scale(-18.0, U3))]),
    ("gear", "Gear", n["gear"], "motor", True, [(gear, GEAR, 1.0)], M_CARRIER + [mv(5, 0.6, 1.0, scale(-30.0, U3))]),
    ("rbolt", "Receiver wing bolt", n["rbolt"], "bolts", True, [(hw["receiver bolt"], STEEL, 1.0)],
     M_PLATE + [mv(3, 0.75, 1.0, (0.0, 0.0, -30.0))]),
    ("rnut", "Receiver nut (M5)", n["rnut"], "bolts", True, [(hw["receiver nut"], STEEL, 1.0)],
     M_PLATE + [mv(3, 0.5, 0.75, (0.0, -25.0, 0.0))]),
    ("pbolt", "Tower wing bolt", n["pbolt"], "bolts", True, [(hw["push bolt"], STEEL, 1.0)],
     M_ARM + [mv(4, 0.4, 1.0, scale(32.0, U3)), mv(7, 0.75, 1.0, scale(8.0, U3))]),
    ("pnut", "Tower nut (M5)", n["pnut"], "bolts", True, [(hw["push nut"], STEEL, 1.0)],
     M_ARM + [mv(4, 0.0, 0.4, (0.0, 0.0, 30.0))]),
    ("sbolt", "Stop wing bolt", n["sbolt"], "bolts", True, [(hw["stop bolt"], STEEL, 1.0)],
     M_CARRIER + [mv(6, 0.35, 1.0, (0.0, 0.0, -35.0))]),
    ("snut", "Stop nut (M5)", n["snut"], "bolts", True, [(hw["stop nut"], STEEL, 1.0)],
     M_CARRIER + [mv(6, 0.0, 0.3, (0.0, 0.0, 20.0))]),
    ("jnut", "Stop jam nut (M5)", n["jnut"], "bolts", True, [(hw["stop jam nut"], STEEL, 1.0)],
     M_CARRIER + [mv(6, 0.35, 1.0, (0.0, 0.0, -35.0))]),
  ]


'''
s = s[:a] + new + s[b:]
# NOTES dict before parts()
notes = '''BOLT = "M5 x 20 stainless wing bolt. "
NOTES = {
  "cover": ("The car's column cover, drawn roughly from your photos and measurements. The frame plate hangs on its "
            "two screws."),
  "grip": "The grip, 367 mm across and 33 mm thick, the steering wheel straight.",
  "plate": ("166 x 96 x 41 mm. Hangs on the column cover's two screws (the cup slot on the key side, slot 1 on the "
            "other). The square tube underneath is the receiver: the arm slides in from the key side. The printed "
            "labels (KEY, WHEEL, 1) face down."),
  "teeth": "On the grip at 4 o'clock, on one wrap of silicone tape; the gear meets them from outside the rim.",
  "zips": "Two zip ties round the grip through the teeth's middle slot, heads tucked inside the rim.",
  "arm": ("115 x 44 x 81 mm. Its 10 x 30 bar goes into the frame plate's square tube (47 mm in; slide it up to 25 mm "
          "either way to set how far right the motor sits). The tower at its end runs along the column; its channel, "
          "open towards the motor, takes the motor carrier's bar."),
  "carrier": ("44 x 148 x 61 mm. The motor bolts to the outside of its plate. Its long bar slides along the column in "
              "the tower's channel; the lug at the bar's far end takes the stop wing bolt, its nut in the hex pocket."),
  "motor": ("42 x 42 x 40 mm, against the outside of the carrier's plate, the shaft through the big hole pointing in "
            "at the steering wheel's middle."),
  "board": "On the motor's back. Drawn as a placeholder: the real board's shape and parts differ.",
  "screws": "Button heads, in from the side with the four round pads, into the motor.",
  "gear": "On the motor's shaft, set screw on the flat. Slid up against the stop, it sits in the teeth.",
  "rbolt": BOLT + "In through the square tube's far (dash-side) wall; it pinches the arm's bar.",
  "rnut": "In the slot in the square tube's far wall, pushed up into it from below.",
  "pbolt": (BOLT + "In through the tower's outer wall onto the carrier's bar. Loosen it to slide the motor (lane "
            "keeping on and off)."),
  "pnut": "Dropped into the slot at the top of the tower's outer wall.",
  "sbolt": (BOLT + "Up through the carrier's lug; its tip stops the carrier against the tower: how deep the gear sits "
            "in the teeth."),
  "snut": "In the hex pocket on the carrier's lug.",
  "jnut": "On the stop wing bolt under the lug: tightened up against the lug, it locks the stop.",
}


def parts() -> list:'''
s = s.replace("def parts() -> list:", notes, 1)
s = s.replace('meshes.append({"nv": int(len(q)), "nt": int(len(t)), "po": po, "io": io})', 'meshes.append({"nv": len(q), "nt": len(t), "po": po, "io": io})')
s = s.replace('''  page = open(PAGE, encoding="utf-8").read()\n''', '''  with open(PAGE, encoding="utf-8") as f:\n    page = f.read()\n''')
open(p,'w').write(s)
EOF
ruff check viewer3d.py --output-format concise && export PYTHONPATH=/home/claude/pylib && timeout 600 python3 viewer3d.py
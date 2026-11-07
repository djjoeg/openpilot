python3 - <<'EOF'
p = "visuals.py"
s = open(p).read()
def rep(a, b):
  global s
  assert s.count(a) == 1, (a[:80], s.count(a))
  s = s.replace(a, b)
rep('''"""
Review pictures of everything to print for the right-arm build (2 Nov 2026): the apparatus close up with its wing
bolts and nuts drawn in, then each printed piece on its own, big, two views, with its size and what it does.
''', '''"""
Review pictures of everything to print for the right-arm build (2 Nov 2026, the arm v2: the motor slides in and out
of the teeth): the apparatus close up with its wing bolts and nuts drawn in, slid in and slid out, then each printed
piece on its own, big, two views, with its size and what it does.
''')
rep('''import midteeth as MT
import render as R
import rightarm as RA
import sideparts as S
''', '''import midteeth as MT
import render as R
import rightarm as RA
import rightcheck as RC
import sideparts as S
''')
start = s.index("def hardware() -> list:")
end = s.index("def grip_segment(")
s = s[:start] + '''def hardware(dz: float = 0.0) -> list:
  """The seven wing bolts and their nuts, in the steering wheel frame, the motor slid dz from its stop."""
  parts = []
  # the receiver's pinch bolt: in the plate frame it runs along -y through the dash-side wall at PINCH_X
  pz = RA.PLATE_T + RA.BORE_DEPTH / 2
  head_y = RA.TUBE_Y[1]
  bolt = wing_bolt_z(0.0, 0.0, 0.0, length=12.0)                       # along -z from the head's underside
  bolt = bolt.rotate((-90.0, 0.0, 0.0))                                 # -z -> -y
  bolt = bolt.translate((RA.PINCH_X, head_y, pz))
  yn = (RA.BORE_Y[1] + RA.TUBE_Y[1]) / 2
  nut = hex_prism_z(8.0, -2.0, 2.0, x=0.0, y=0.0).rotate((90.0, 0.0, 0.0)).translate((RA.PINCH_X, yn, pz))
  nut = nut - cyl_y(2.5, yn - 3.0, yn + 3.0, x=RA.PINCH_X, z=pz, segments=24)
  parts += [(RA.plate_to_wheel(bolt), STEEL), (RA.plate_to_wheel(nut), STEEL)]
  # the rest: the foot's two, the pivot and the arc bolt, the sleeve's pinch bolt, the stop (with its jam nut)
  for name, m in RC.hardware(dz, RA.STOP_P).items():
    parts.append((m, STEEL))
  return parts


''' + s[end:]
rep('''def assembly_parts(with_grip: bool = True) -> list:
  mg = RA.motor_and_gear()
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0.0, 0.0, RA.THETA))
  parts = [(RA.plate_to_wheel(RA.frame_plate_v4()), PLATE), (RA.arm(), BLUE), (RA.bar(), BLUE), (RA.bracket(), BLUE),
           (mg["motor"], DARK), (mg["board"], DARK), (mg["gear"], ORANGE), (teeth, ORANGE)] + hardware()''',
'''def assembly_parts(with_grip: bool = True, dz: float = 0.0) -> list:
  mg = RA.motor_and_gear(dz)
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0.0, 0.0, RA.THETA))
  parts = [(RA.plate_to_wheel(RA.frame_plate_v4()), PLATE), (RA.arm(), BLUE), (RA.bar(), BLUE), (RA.bracket(), BLUE),
           (RA.carrier(dz), CARRIER), (mg["motor"], DARK), (mg["board"], DARK), (mg["gear"], ORANGE), (teeth, ORANGE)] + \\
    hardware(dz)''')
rep('''BLUE = (0.35, 0.55, 0.85)''', '''BLUE = (0.35, 0.55, 0.85)
CARRIER = (0.45, 0.70, 0.45)''')
start = s.index("def assembly_picture(path: str) -> None:")
end = s.index("def part_sheet(")
s = s[:start] + '''def assembly_picture(path: str) -> None:
  parts = assembly_parts()
  views = [(parts, R.look((0.0, 0.0, 1.0), (0, 1, 0))), (parts, R.look((0.0, -1.0, 0.0), (0, 0, 1))),
           (parts, R.look((0.9, -0.5, 0.8), (0, 1, 0))), (parts, R.look((1.0, -0.15, 0.1), (0, 1, 0)))]
  R.save(path, views, cols=2, size=(1100, 800),
         titles=["from your seat: the motor outside the rim at 4 o'clock, shaft pointing at the wheel's middle",
                 "from below, the wheel at the top (as in your photos)",
                 "from your right and below", "from the passenger's side (the right)"],
         suptitle="The right arm mount v2, assembled, the motor slid up against its stop: gear in the teeth, lane keeping on. "
                  "Plate light grey (on the column cover, not drawn), arm, bar and bracket blue, the motor carrier green, "
                  "motor dark, gear and teeth orange, the wing bolts steel, a piece of the wheel grip grey.")


def slide_picture(path: str) -> None:
  """The slide close up, from the right (across the column) and from below: in, and slid out."""
  near = []
  for dz in (0.0, RA.DZ_OUT):
    p = [x for x in assembly_parts(dz=dz)]
    near.append(p)
  views = [(near[0], R.look((1.0, -0.6, 0.0), (0, 0, 1))), (near[1], R.look((1.0, -0.6, 0.0), (0, 0, 1))),
           (near[0], R.look((0.6, -1.0, 0.5), (0, 0, 1))), (near[1], R.look((0.6, -1.0, 0.5), (0, 0, 1)))]
  R.save(path, views, cols=2, size=(1100, 800),
         titles=["IN: slid up against the stop, the pinch bolt tight (the wheel is up, the dash down)",
                 "OUT: pinch bolt loosened, motor slid 10 mm down the column (6 mm is enough), tightened",
                 "IN, from below on the right", "OUT, from below on the right"],
         suptitle="On and off: loosen the pinch wing bolt on the sleeve's side, slide the motor along the column, tighten "
                  "it. The wing bolt down through the sleeve's top is the stop: it sets how deep the gear sits in the "
                  "teeth (set it once; a jam nut under its wings holds it).")


''' + s[end:]
# part sheets: add the carrier, update the bar and bracket notes
rep('''  part_sheet(os.path.join(REPORT_DIR, "review-4-bar.png"), bed["right-bar"], BLUE,
             "Plate 12, the bar", "The foot (two upright slots: 9 mm up or down) laps the arm's end on two wing bolts; the bar runs 70 "
             "mm back towards you; the flag at the back is a plate across the column with the pivot hole and the second hole for "
             "the bracket, nuts in hex pockets on its dash side.")
  part_sheet(os.path.join(REPORT_DIR, "review-5-bracket.png"), bed["right-bracket"], BLUE,
             "Plate 12, the bracket", "The flat tab laps the flag: the pivot hole and a curved slot (15 degrees each way) set the "
             "motor's angle on two wing bolts. The face plate stands up from it, 5 mm, with the motor's four M3 holes and the 22.5 "
             "mm hole for its boss; the shaft comes through it, the gear on the end.")''',
'''  part_sheet(os.path.join(REPORT_DIR, "review-4-bar.png"), bed["right-bar"], BLUE,
             "Plate 12, the bar (printed standing on its long edge)", "The foot (two upright slots: 9 mm up or down) laps the "
             "arm's end on two wing bolts; the bar stands on the foot's far end, past the bolts, and runs 47 mm back towards "
             "you; the flag at the back is a plate across the column with the pivot hole and the second hole for the bracket, "
             "nuts in hex pockets on its dash side.")
  part_sheet(os.path.join(REPORT_DIR, "review-5-bracket.png"), bed["right-bracket"], BLUE,
             "Plate 12, the bracket", "The flat tab laps the flag: the pivot hole and a curved slot (15 degrees each way) set the "
             "motor's angle on two wing bolts. The sleeve stands up from it: the motor carrier's tongue slides in it; the pinch "
             "wing bolt goes in through the thick side wall (its nut drops into the slot from the top), the stop wing bolt down "
             "through the top (its nut in the pocket on top).")
  part_sheet(os.path.join(REPORT_DIR, "review-5b-carrier.png"), bed["right-carrier"], CARRIER,
             "Plate 12, the motor carrier", "The motor bolts to it with four M3 x 10 from this side (the boss in the big hole, the "
             "shaft through it towards the wheel's middle). The thick block at the corner is the tongue that slides in the "
             "bracket's sleeve; the thin web joining it goes through the slot in the sleeve's side.")''')
rep('''  assembly_picture(os.path.join(REPORT_DIR, "review-1-assembly.png"))''',
'''  assembly_picture(os.path.join(REPORT_DIR, "review-1-assembly.png"))
  slide_picture(os.path.join(REPORT_DIR, "review-1b-slide.png"))''')
open(p, "w").write(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib timeout 1800 python3 visuals.py 2>&1 | tail -8; ls -la ../report/review-*
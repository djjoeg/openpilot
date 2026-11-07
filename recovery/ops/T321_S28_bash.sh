python3 - <<'EOF'
p = 'visuals.py'
s = open(p, encoding='utf-8').read()
reps = [
("""Review pictures of everything to print for the right-arm build (3 Nov 2026, the arm v4: two printed pieces, the
motor slides in and out of the teeth in a closed tube, an M4 bolt in the carrier's end the stop): the apparatus close
up with its bolts and nuts drawn in; slid in, slid out and going together; then each printed piece on its own, big,
two views, with its size and what it does.""",
 """Review pictures of everything to print for the right-arm build (3 Nov 2026, the arm v5: two printed pieces, the
arm 50 mm deep where it leaves the frame plate, the motor slides in and out of the teeth in a closed tube, one wing
bolt in a groove up the tower's outer wall the lock and the handle): the apparatus close up with its bolts and nuts
drawn in; slid in, slid out and going together; then each printed piece on its own, big, two views, with its size
and what it does."""),
("""def hardware(dz: float = 0.0, off=(0.0, 0.0, 0.0), stop_too: bool = True) -> list:
  \"\"\"The wing bolts, the stop and the nuts, in the steering wheel frame, the motor slid dz from its stop; the
  carrier's own (the M4 stop: bolt, washer and nuts) moved by off as well, unless stop_too is False (then it waits
  where it goes, below the tower).\"\"\"
  out = []
  for name, m in RC.hardware(dz, RA.STOP_GAP).items():
    out.append((m.translate(off) if name.startswith("stop") and stop_too else m, STEEL))
  return out""",
 """def hardware(dz: float = 0.0, off=(0.0, 0.0, 0.0), bolt_in: bool = True) -> list:
  \"\"\"The wing bolts, the washer and the nuts, in the steering wheel frame, the motor slid dz from the drawn depth;
  the slide's nut (in the carrier's bar) moved by off with the carrier; the slide's wing bolt and washer too, unless
  bolt_in is False (then they wait 15 mm out from the groove, not yet in).\"\"\"
  out = []
  wait = (15.0 * float(RA.U[0]), 15.0 * float(RA.U[1]), 0.0)
  for name, m in RC.hardware(dz).items():
    if name == "slide nut":
      m = m.translate(off)
    elif name.startswith("slide"):
      m = m.translate(off) if bolt_in else m.translate(wait)
    out.append((m, STEEL))
  return out"""),
("""def assembly_parts(with_grip: bool = True, dz: float = 0.0, off=(0.0, 0.0, 0.0), stop_too: bool = True) -> list:""",
 """def assembly_parts(with_grip: bool = True, dz: float = 0.0, off=(0.0, 0.0, 0.0), bolt_in: bool = True) -> list:"""),
("""    [(m.translate(off), c) for m, c in mov] + hardware(dz, off, stop_too)""",
 """    [(m.translate(off), c) for m, c in mov] + hardware(dz, off, bolt_in)"""),
("""         suptitle="The right arm mount v4, assembled, the motor slid up against its stop: gear in the teeth, lane keeping "
                  "on. Plate light grey (on the column cover, not drawn), the arm blue, the motor carrier green, motor "
                  "dark, gear and teeth orange, the bolts, nuts and washer steel, a piece of the wheel grip grey.")""",
 """         suptitle="The right arm mount v5, assembled, the motor slid up the groove: gear in the teeth, lane keeping on. "
                  "Plate light grey (on the column cover, not drawn), the arm blue, the motor carrier green, motor dark, "
                  "gear and teeth orange, the bolts, nuts and washer steel, a piece of the wheel grip grey.")"""),
("""  bench = [p for p in assembly_parts(with_grip=False, dz=RA.DZ_OUT, off=off, stop_too=False) if p[1] is not PLATE]""",
 """  bench = [p for p in assembly_parts(with_grip=False, dz=RA.DZ_OUT, off=off, bolt_in=False) if p[1] is not PLATE]"""),
("""         titles=["IN: slid up against the stop, the tower's wing bolt tight (the wheel is up, the dash down)",
                 (f"OUT: wing bolt loosened, motor slid down until the carrier sits on the tower ({-RA.DZ_OUT:.0f} mm; "
                  "6 is enough), tightened"),
                 "IN, from below on the right", "OUT, from below on the right",
                 "PUTTING IT TOGETHER, off the car: the carrier's bar goes down the tower's tube from the top",
                 "the same from the passenger's side; then the M4 stop into the bar's end below"],
         suptitle="On and off: loosen the wing bolt on the tower's outer side, slide the motor along the column, tighten "
                  "it. The M4 bolt in the bottom end of the carrier's bar, a fender washer under its head, is the stop: "
                  "it sets how deep the gear sits in the teeth (set it once; the jam nut on it holds it), and it keeps "
                  "the carrier in the tube.")""",
 """         titles=["IN: the wing bolt slid up the groove, the gear in the teeth, tightened (the wheel is up, the dash down)",
                 (f"OUT: loosened, slid down until the carrier sits on the tower ({-RA.DZ_OUT:.0f} mm; 6 is enough), "
                  "tightened"),
                 "IN, from below on the right", "OUT, from below on the right",
                 "PUTTING IT TOGETHER, off the car: the carrier's bar goes down the tower's tube from the top",
                 "the same from the passenger's side; then the wing bolt and washer in through the groove into its nut"],
         suptitle="On and off, and how deep: one wing bolt in the groove up the tower's outer side, screwed into a nut in "
                  "the carrier's bar. Loosen it, slide the motor along the column by it, tighten it. The groove's ends "
                  "keep the carrier in; the ticks on the bar, read at the tower's top, show how far up it is.")"""),
("""             "Plate 12, the arm v4 (printed flat, the tower standing up)", "The 10 x 30 bar goes in the receiver (47 mm "
             "in, nominal; slide it 25 mm either way). The tower at its end has a square tube up it, closed all round: "
             "the motor carrier's bar slides down into it from the top. The wing bolt goes in through the tower's outer "
             "wall and pushes the bar tight; its nut drops into the slot from the top.",""",
 """             "Plate 12, the arm v5 (printed flat, the tower standing up)", "The 10 x 30 bar goes in the receiver (47 mm "
             "in, nominal; 5 mm further in, or out as far as you like). Just outside the receiver the arm is 50 mm deep "
             "along the column, so it doesn't twist. The tower at its end has a square tube up it, closed all round: "
             "the motor carrier's bar slides down into it from the top. The slide's wing bolt runs in the groove up "
             "its outer wall.","""),
("""             "Plate 12, the motor carrier v4 (printed on its side)", "The motor bolts to the standing plate with four M3 "
             "x 10 from the side with the four round pads (the boss in the big hole, the shaft through it towards the "
             "wheel's middle). The long bar slides down the arm's tower; the M4 stop bolt screws into its plain far end "
             "(its nut dropped into the slot on top, 4 mm in).",""",
 """             "Plate 12, the motor carrier v5 (printed on its side)", "The motor bolts to the standing plate with four M3 "
             "x 10 from the side with the four round pads (the boss in the big hole, the shaft through it towards the "
             "wheel's middle). The long bar slides down the arm's tower; the slide's M5 nut drops into the slot on top "
             "(flats along the bar), the wing bolt comes in from the outer face. The ticks on that face read the slide.","""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
for p in ('incar.py', 'carphoto.py'):
    s = open(p, encoding='utf-8').read()
    a = "RC.hardware(0.0, RA.STOP_GAP).values()"
    assert s.count(a) == 1, p
    open(p, 'w', encoding='utf-8').write(s.replace(a, "RC.hardware(0.0).values()"))
print('ok')
EOF
grep -n "v3 and its tower\|v4\b\|stop" incar.py | head -8
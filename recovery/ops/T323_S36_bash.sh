python3 - <<'EOF'
p = "visuals.py"
s = open(p, encoding="utf-8").read()
reps = [
("""Review pictures of everything to print for the right-arm build (3 Nov 2026, the arm v5: two printed pieces, the
arm 50 mm deep where it leaves the frame plate, the motor slides in and out of the teeth in a closed tube, one wing
bolt in a groove up the tower's outer wall the lock and the handle): the apparatus close up with its bolts and nuts
drawn in; slid in, slid out and going together; then each printed piece on its own, big, two views, with its size
and what it does.""",
 """Review pictures of everything to print for the right-arm build (3 Nov 2026, the arm v6, the fit print, on the frame
plate v5: the arm 50 mm deep where it leaves the frame plate, the motor slides in and out of the teeth in a closed
tube, and both slides the same way, a wing bolt in a groove into a nut in the inner piece): the apparatus close up
with its bolts and nuts drawn in; the motor's slide in, out and going together; the arm's slide in the receiver;
then each printed piece on its own, big, two views, with its size and what it does."""),
("""def hardware(dz: float = 0.0, off=(0.0, 0.0, 0.0), bolt_in: bool = True) -> list:
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
  return out""",
 """def hardware(dz: float = 0.0, off=(0.0, 0.0, 0.0), bolt_in: bool = True, receiver_in: bool = True,
             arm_dx: float = 0.0) -> list:
  \"\"\"The wing bolts, the washers and the nuts, in the steering wheel frame, the motor slid dz from the drawn depth,
  the arm arm_dx across; the slide's nut (in the carrier's bar) moved by off with the carrier; the slide's wing bolt
  and washer too, unless bolt_in is False (then they wait 15 mm out from the groove, not yet in); the receiver's wing
  bolt and washer left out when receiver_in is False (they go in on the car).\"\"\"
  out = []
  wait = (15.0 * float(RA.U[0]), 15.0 * float(RA.U[1]), 0.0)
  for name, m in RC.hardware(dz, arm_dx=arm_dx).items():
    if name == "slide nut":
      m = m.translate(off)
    elif name.startswith("slide"):
      m = m.translate(off) if bolt_in else m.translate(wait)
    elif name != "receiver nut" and not receiver_in:
      continue
    out.append((m, STEEL))
  return out"""),
("""def assembly_parts(with_grip: bool = True, dz: float = 0.0, off=(0.0, 0.0, 0.0), bolt_in: bool = True) -> list:
  \"\"\"Everything, the carrier slid dz along the column and moved off (to show it going in).\"\"\"
  mg = RA.motor_and_gear(dz)
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=18)).rotate((0.0, 0.0, RA.THETA))      # the 20 set, the one on the car
  mov = [(RA.carrier(dz), CARRIER), (mg["motor"], DARK), (mg["board"], DARK), (mg["gear"], ORANGE)]
  parts = [(RA.plate_to_wheel(RA.frame_plate_v4()), PLATE), (RA.arm(), BLUE)] + \\
    [(m.translate(off), c) for m, c in mov] + hardware(dz, off, bolt_in)""",
 """def assembly_parts(with_grip: bool = True, dz: float = 0.0, off=(0.0, 0.0, 0.0), bolt_in: bool = True,
                   receiver_in: bool = True, arm_dx: float = 0.0) -> list:
  \"\"\"Everything, the carrier slid dz along the column and moved off (to show it going in), the arm slid arm_dx
  across in the receiver.\"\"\"
  mg = RA.motor_and_gear(dz)
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=18)).rotate((0.0, 0.0, RA.THETA))      # the 20 set, the one on the car
  mov = [(RA.carrier(dz), CARRIER), (mg["motor"], DARK), (mg["board"], DARK), (mg["gear"], ORANGE)]
  a = (arm_dx, 0.0, 0.0)
  parts = [(RA.plate_to_wheel(RA.frame_plate_v5()), PLATE), (RA.arm().translate(a), BLUE)] + \\
    [(m.translate(off).translate(a), c) for m, c in mov] + hardware(dz, off, bolt_in, receiver_in, arm_dx)"""),
("""         suptitle="The right arm mount v5, assembled, the motor slid up the groove: gear in the teeth, lane keeping on. \"""",
 """         suptitle="The right arm mount v6, assembled, the motor slid up the groove: gear in the teeth, lane keeping on. \""""),
("""  bench = [p for p in assembly_parts(with_grip=False, dz=RA.DZ_OUT, off=off, bolt_in=False) if p[1] is not PLATE]""",
 """  bench = [p for p in assembly_parts(with_grip=False, dz=RA.DZ_OUT, off=off, bolt_in=False, receiver_in=False)
           if p[1] is not PLATE]"""),
("""                 (f"OUT: loosened, slid down until the carrier sits on the tower ({-RA.DZ_OUT:.0f} mm; 6 is enough), "
                  "tightened"),""",
 """                 (f"OUT: loosened, slid down until the carrier sits on the tower ({-RA.DZ_OUT:.0f} mm below the drawn "
                  "depth; 6 is enough), tightened"),"""),
("""def part_sheet(path: str, m: Manifold, color, title: str, note: str, views=None, titles=None) -> None:""",
 """def receiver_picture(path: str) -> None:
  \"\"\"The arm's slide in the receiver: slid all the way in and out, from below and from your side; and going in.\"\"\"
  def parts(dx, receiver_in=True, away=0.0):
    ps = assembly_parts(with_grip=False, dz=RA.DZ_OUT, arm_dx=dx + away, receiver_in=receiver_in)
    return ps
  below, yours = R.look((0.0, -1.0, 0.0), (0, 0, 1)), R.look((0.25, -0.55, 1.0), (0, 1, 0))
  views = [(parts(-RA.ARM_SLIDE), below), (parts(RA.ARM_SLIDE), below), (parts(0.0), yours),
           (parts(0.0, receiver_in=False, away=70.0), yours)]
  R.save(path, views, cols=2, size=(1100, 800),
         titles=[f"slid all the way in ({RA.ARM_SLIDE:.1f} mm), from below, the wheel at the top",
                 f"slid all the way out ({RA.ARM_SLIDE:.1f} mm), from below",
                 "as drawn, from your seat, low: the wing bolt in the receiver's groove, on your side",
                 "PUTTING IT ON: the arm, with the motor on it and the nut in the slot in its top, slides into the "
                 "receiver from the key side; then the wing bolt and washer in through the groove"],
         suptitle="The arm's slide, the same as the motor's: one wing bolt through a 42 mm groove in the receiver's wall "
                  "on your side, screwed into a nut in the arm's bar. Loosen it, slide the arm across by it, tighten it: "
                  "it pulls the bar against the wall. The groove's ends keep the arm in.")


def part_sheet(path: str, m: Manifold, color, title: str, note: str, views=None, titles=None) -> None:"""),
("""  slide_picture(os.path.join(REPORT_DIR, "review-1b-slide.png"))
  part_sheet(os.path.join(REPORT_DIR, "review-2-frame-plate.png"), bed["column-frame-plate-v4"], PLATE,
             "Plate 11, frame plate v4", "6 mm thick. Hangs on the two cover screws (the cup slot and slot 1). The square tube is "
             "the receiver: the arm slides in from the key side, one wing bolt through the tube's far wall pinches it; the nut drops "
             "into the slot in that wall. Printed labels up; in the car the labels face down.")
  part_sheet(os.path.join(REPORT_DIR, "review-3-arm.png"), bed["right-arm"], BLUE,
             "Plate 12, the arm v5 (printed flat, the tower standing up)", "The 10 x 30 bar goes in the receiver (47 mm "
             "in, nominal; 5 mm further in, or out as far as you like). Just outside the receiver the arm is 50 mm deep "
             "along the column, so it doesn't twist. The tower at its end has a square tube up it, closed all round: "
             "the motor carrier's bar slides down into it from the top. The slide's wing bolt runs in the groove up "
             "its outer wall.",""",
 """  slide_picture(os.path.join(REPORT_DIR, "review-1b-slide.png"))
  receiver_picture(os.path.join(REPORT_DIR, "review-1c-receiver.png"))
  part_sheet(os.path.join(REPORT_DIR, "review-2-frame-plate.png"), bed["column-frame-plate-v5"], PLATE,
             "Plate 11, frame plate v5", "6 mm thick. Hangs on the two cover screws (the cup slot and slot 1). The square tube is "
             "the receiver, its bore 20 wide: the arm slides in from the key side; one wing bolt through the long groove in "
             "the tube's wall on your side, into a nut in the arm, holds it anywhere along the groove. Printed labels up; in "
             "the car the labels face down.")
  part_sheet(os.path.join(REPORT_DIR, "review-3-arm.png"), bed["right-arm"], BLUE,
             "Plate 12, the arm v6 (printed flat, the tower standing up)", "The 20 x 30 bar goes in the receiver (47 mm "
             "in as drawn, 17.5 further in or out by the groove); its M5 nut drops into the slot in its top, flats along "
             "the bar, and the receiver's wing bolt comes in from the face on your side. Just outside the receiver the arm "
             "is 50 mm deep along the column, so it doesn't twist. The tower at its end has a square tube up it, closed all "
             "round: the motor carrier's bar slides down into it from the top. The motor's wing bolt runs in the groove up "
             "its outer wall.","""),
("""             "Plate 12, the motor carrier v5 (printed on its side)", "The motor bolts to the standing plate with four M3 \"""",
 """             "Plate 12, the motor carrier v6 (printed on its side)", "The motor bolts to the standing plate with four M3 \""""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:70]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
grep -n "def parts\|ps = \|return ps" visuals.py
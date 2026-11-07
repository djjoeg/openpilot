python3 - <<'EOF'
p='allinone.py'; s=open(p).read()
rep=[('''One print for everything the right-arm build needs (2 Nov 2026): the frame plate v4, the steering wheel teeth v2 (the
20 set: 19 teeth, 19.5 degrees each way, the same teeth as the first print you held on the wheel), the arm and the
motor carrier, on one 256 x 256 mm bed,''','''One print for everything the right-arm build needs (2 Nov 2026; 3 Nov: the arm and carrier v4, the teeth v3): the
frame plate v4, the steering wheel teeth v3 (the 20 set: 19 teeth, 19.5 degrees each way, the channel 7 mm in, the
ends cut back to the teeth), the arm and the motor carrier, on one 256 x 256 mm bed,'''),
('''  "steering-wheel-teeth-v2-20-winding-roads": ("mid-teeth", "teeth v2, 20", P.STANDARD),''','''  "steering-wheel-teeth-v3-20-winding-roads": ("mid-teeth", "teeth v3, 20", P.STANDARD),'''),
('''TEETH = "steering-wheel-teeth-v2-20-winding-roads"''','''TEETH = "steering-wheel-teeth-v3-20-winding-roads"''')]
for a,b in rep:
  assert a in s, a[:60]; s=s.replace(a,b)
open(p,'w').write(s)

p='visuals.py'; s=open(p).read()
rep=[
('''Review pictures of everything to print for the right-arm build (2 Nov 2026, the arm v3: two printed pieces, the
motor slides in and out of the teeth): the apparatus close up with its wing bolts and nuts drawn in; slid in, slid
out and going on; then each printed piece on its own, big, two views, with its size and what it does.''',
'''Review pictures of everything to print for the right-arm build (3 Nov 2026, the arm v4: two printed pieces, the
motor slides in and out of the teeth in a closed tube, an M4 bolt in the carrier's end the stop): the apparatus close
up with its bolts and nuts drawn in; slid in, slid out and going together; then each printed piece on its own, big,
two views, with its size and what it does.'''),
('''  for name, m in RC.hardware(dz, RA.STOP_P).items():''', '''  for name, m in RC.hardware(dz, RA.STOP_GAP).items():'''),
('''  mov = [(RA.carrier(dz), CARRIER), (mg["motor"], DARK), (mg["board"], DARK), (mg["gear"], ORANGE)]
  parts = [(RA.plate_to_wheel(RA.frame_plate_v4()), PLATE), (RA.arm(), BLUE)] + \\
    [(m.translate(off), c) for m, c in mov] + [(teeth, ORANGE)] + hardware(dz, off)
  if with_grip:
    parts.append((grip_segment(), CAR))
  return parts''',
'''  mov = [(RA.carrier(dz), CARRIER), (mg["motor"], DARK), (mg["board"], DARK), (mg["gear"], ORANGE)]
  parts = [(RA.plate_to_wheel(RA.frame_plate_v4()), PLATE), (RA.arm(), BLUE)] + \\
    [(m.translate(off), c) for m, c in mov] + hardware(dz, off)
  if with_grip:
    parts += [(teeth, ORANGE), (grip_segment(), CAR)]
  return parts'''),
('''def slide_picture(path: str) -> None:
  """The slide close up: in, slid out, and the carrier going on."""
  t = 30.0
  off = (float(t * RA.V[0]), float(t * RA.V[1]), 0.0)
  near = [assembly_parts(dz=0.0), assembly_parts(dz=RA.DZ_OUT), assembly_parts(dz=RA.DZ_OUT, off=off)]
  side, below = R.look((1.0, -0.6, 0.0), (0, 0, 1)), R.look((0.6, -1.0, 0.5), (0, 0, 1))
  views = [(near[0], side), (near[1], side), (near[0], below), (near[1], below),
           (near[2], R.look((0.9, -0.9, 0.6), (0, 0, 1))),
           (near[2], R.look((float(RA.U[0]), float(RA.U[1]), 0.15), (0, 0, 1)))]
  R.save(path, views, cols=2, size=(1100, 800),
         titles=["IN: slid up against the stop, the push wing bolt tight (the wheel is up, the dash down)",
                 (f"OUT: push bolt loosened, motor slid down until the carrier sits on the tower ({-RA.DZ_OUT:.0f} mm; "
                  "6 is enough), tightened"),
                 "IN, from below on the right", "OUT, from below on the right",
                 "PUTTING IT ON: the carrier, motor on it, comes in from the motor's side into the channel",
                 "the same from the passenger's side"],
         suptitle="On and off: loosen the wing bolt on the tower's outer side, slide the motor along the column, tighten "
                  "it. The wing bolt up through the lug at the bottom of the motor carrier's bar is the stop: it sets "
                  "how deep the gear sits in the teeth (set it once; the jam nut above its wings holds it).")''',
'''def slide_picture(path: str) -> None:
  """The slide close up: in, slid out, and the carrier going down into the tower (off the car)."""
  off = (0.0, 0.0, 95.0)
  near = [assembly_parts(dz=0.0), assembly_parts(dz=RA.DZ_OUT)]
  bench = [p for p in assembly_parts(with_grip=False, dz=RA.DZ_OUT, off=off) if p[1] is not PLATE]
  side, below = R.look((1.0, -0.6, 0.0), (0, 0, 1)), R.look((0.6, -1.0, 0.5), (0, 0, 1))
  views = [(near[0], side), (near[1], side), (near[0], below), (near[1], below),
           (bench, R.look((0.9, -0.9, 0.6), (0, 0, 1))),
           (bench, R.look((float(RA.U[0]), float(RA.U[1]), 0.15), (0, 0, 1)))]
  R.save(path, views, cols=2, size=(1100, 800),
         titles=["IN: slid up against the stop, the tower's wing bolt tight (the wheel is up, the dash down)",
                 (f"OUT: wing bolt loosened, motor slid down until the carrier sits on the tower ({-RA.DZ_OUT:.0f} mm; "
                  "6 is enough), tightened"),
                 "IN, from below on the right", "OUT, from below on the right",
                 "PUTTING IT TOGETHER, off the car: the carrier's bar goes down the tower's tube from the top",
                 "the same from the passenger's side; then the M4 stop into the bar's end below"],
         suptitle="On and off: loosen the wing bolt on the tower's outer side, slide the motor along the column, tighten "
                  "it. The M4 bolt in the bottom end of the carrier's bar, a fender washer under its head, is the stop: "
                  "it sets how deep the gear sits in the teeth (set it once; the jam nut on it holds it), and it keeps "
                  "the carrier in the tube.")'''),
('''  part_sheet(os.path.join(REPORT_DIR, "review-3-arm.png"), bed["right-arm"], BLUE,
             "Plate 12, the arm (printed flat, the tower standing up)", "The 10 x 30 bar goes in the receiver (47 mm in, "
             "nominal; slide it 25 mm either way). The tower at its end has a channel up it, open on the side towards the "
             "motor: the motor carrier's bar slides in it. The wing bolt goes in through the tower's outer wall and pushes "
             "the bar tight; its nut drops into the slot from the top.",
             views=[R.view_matrix(-50, 35), R.view_matrix(60, 30)],
             titles=["from the front left, above", "from the front right, above: the channel"])
  part_sheet(os.path.join(REPORT_DIR, "review-4-carrier.png"), bed["right-carrier"], CARRIER,
             "Plate 12, the motor carrier (printed on its side)", "The motor bolts to the standing plate with four M3 x 10 "
             "from the side with the four round pads (the boss in the big hole, the shaft through it towards the wheel's "
             "middle). The long bar slides in the arm's tower; the lug at its far end takes the stop wing bolt, its nut "
             "in the hex pocket.",
             views=[R.view_matrix(-50, 35), R.view_matrix(130, 30)])''',
'''  part_sheet(os.path.join(REPORT_DIR, "review-3-arm.png"), bed["right-arm"], BLUE,
             "Plate 12, the arm v4 (printed flat, the tower standing up)", "The 10 x 30 bar goes in the receiver (47 mm "
             "in, nominal; slide it 25 mm either way). The tower at its end has a square tube up it, closed all round: "
             "the motor carrier's bar slides down into it from the top. The wing bolt goes in through the tower's outer "
             "wall and pushes the bar tight; its nut drops into the slot from the top.",
             views=[R.view_matrix(-50, 35), R.view_matrix(60, 30)],
             titles=["from the front left, above", "from the front right, above: the tube"])
  part_sheet(os.path.join(REPORT_DIR, "review-4-carrier.png"), bed["right-carrier"], CARRIER,
             "Plate 12, the motor carrier v4 (printed on its side)", "The motor bolts to the standing plate with four M3 "
             "x 10 from the side with the four round pads (the boss in the big hole, the shaft through it towards the "
             "wheel's middle). The long bar slides down the arm's tower; the M4 stop bolt screws into its plain far end "
             "(its nut dropped into the slot on top, 4 mm in).",
             views=[R.view_matrix(-50, 35), R.view_matrix(130, 30)])'''),
('''  R.save(path, panels, cols=2, size=(1000, 650),
         titles=["as printed: the teeth up, the wheel side down", "turned over: the channel that goes on the grip",
                 "as printed, from above", "turned over, from above"],
         suptitle=f"Teeth v2, 20 (winding roads: 19 teeth, 19.5 degrees each way), plate 9: {size_text(bed)}, about {round(2 * t.half / 360 * 2 * math.pi * t.w_out):.0f} mm "
                  "along the grip. The channel 8 mm narrower than the first print; the inner wall only in the middle "
                  "(23 mm each side of centre), one 12 mm zip tie slot through it; the ends are the bare back and the outer wall.")''',
'''  R.save(path, panels, cols=2, size=(1000, 650),
         titles=["as printed: the teeth up, the wheel side down", "turned over: the channel that goes on the grip",
                 "as printed, from above", "turned over, from above"],
         suptitle=f"Teeth v3, 20 (winding roads: 19 teeth, 19.5 degrees each way), plate 9: {size_text(bed)}, about {round(2 * t.half / 360 * 2 * math.pi * t.w_out):.0f} mm "
                  "along the grip. The channel 1 mm wider than v2 (the inner wall pulled 7 mm); the ends cut back to just "
                  "past the last teeth, clear of the spokes; the inner wall only in the middle (23 mm each side of "
                  "centre), one 12 mm zip tie slot through it.")'''),
('''  teeth_sheet(os.path.join(REPORT_DIR, "review-5-teeth-v2.png"))''', '''  teeth_sheet(os.path.join(REPORT_DIR, "review-5-teeth-v3.png"))'''),
('''STALE = ("review-4-bar.png", "review-5-bracket.png", "review-5b-carrier.png", "review-6-teeth-v2.png")   # v2's sheets''',
'''STALE = ("review-4-bar.png", "review-5-bracket.png", "review-5b-carrier.png", "review-6-teeth-v2.png",   # v2's sheets
         "review-5-teeth-v2.png")'''),
]
for a,b in rep:
  assert a in s, a[:70]; s=s.replace(a,b)
open(p,'w').write(s)

for p in ('incar.py','carphoto.py'):
  s=open(p).read()
  s=s.replace("RC.hardware(0.0, RA.STOP_P)", "RC.hardware(0.0, RA.STOP_GAP)")
  open(p,'w').write(s)
EOF
ruff check visuals.py allinone.py incar.py carphoto.py --output-format concise | head; grep -n "assembly_picture" -A 14 visuals.py | head -16
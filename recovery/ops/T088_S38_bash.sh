python3 - <<'EOF'
p='accord_lka_parts.py'; s=open(p).read()

old='''  fit tests             - a short piece of the steering wheel teeth to try on your steering wheel, and a few teeth to
                          try against the printed motor gear

Run it with no options'''
new='''  fit tests             - a short piece of the steering wheel teeth to try on your steering wheel, and a few teeth to
                          try against the printed motor gear

  column mount (hardware/stl/column-mount): the motor under the steering wheel, behind it, on a clamp round the
  steering column covers instead of the dash (columnparts.py):
  ring teeth            - zip-tied round the bottom of the steering wheel; a skirt behind the wheel carries a ring of
                          teeth facing the hub, the motor gear runs inside it (the short set only)
  column clamp          - two V saddles round the steering column covers on four M6 threaded rods; the lower one
                          carries the arm's joint
  hinge block (column)  - the hinge block with its arm slot centred on an arm closer to the column
  fit test              - a few ring teeth to try the printed motor gear in
  The motor gear, carrier, lever bracket, lift lever, arm and setup gauge are the same parts.

Run it with no options'''
assert old in s; s=s.replace(old,new)

old='''  python3 accord_lka_parts.py --arm 143

It checks'''
new='''  python3 accord_lka_parts.py --arm 143
  python3 accord_lka_parts.py --cover-width 118 --cover-height 92 --clamp-behind 180

It checks'''
assert old in s; s=s.replace(old,new)

old='''  ap.add_argument("--bed", type=float, nargs=3, default=list(P.BED), metavar=("X", "Y", "Z"), help="print bed size (mm)")'''
new='''  ap.add_argument("--cover-width", type=float, default=P.COVER_W, help="column mount: the steering column covers, side to side, where the clamp sits (mm)")
  ap.add_argument("--cover-height", type=float, default=P.COVER_H, help="column mount: the covers, top to bottom, there (mm)")
  ap.add_argument("--clamp-behind", type=float, default=-P.CLAMP_Z,
                  help="column mount: the middle of the clamp, mm behind the middle of the part of the steering wheel you hold")
  ap.add_argument("--bed", type=float, nargs=3, default=list(P.BED), metavar=("X", "Y", "Z"), help="print bed size (mm)")'''
assert old in s; s=s.replace(old,new)

old='''      sorted(f for f in os.listdir(args.report) if f.startswith("parts-") and f.endswith(".png"))

  report["problems"] = problems'''
new='''      sorted(f for f in os.listdir(args.report) if f.startswith("parts-") and f.endswith(".png"))

  # ----- the column mount -----
  report["column_mount"] = column_mount(args, base, arms, problems, on_bed, write_stl, part_rows, bed)

  report["problems"] = problems'''
assert old in s, "pictures block"; s=s.replace(old,new)
open(p,'w').write(s); print("ok part 1")
EOF
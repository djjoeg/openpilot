python3 - <<'EOF'
src = open('accord_lka_parts.py').read()

# 1. docstring additions
src = src.replace('''  fit test              - a few ring teeth to try the printed motor gear in
  The motor gear, lever bracket, lift lever, arm and setup gauge are the same parts.
''', '''  fit test              - a few ring teeth to try the printed motor gear in
  The motor gear, lever bracket, lift lever, arm and setup gauge are the same parts.

  right-side mount (hardware/stl/column-mount-right): the same motor parts turned a quarter turn round the column,
  the ring teeth at 3 o'clock on the back of the wheel and the motor behind it there; the arm back to a bracket on the
  right-hand side of the column covers, held to the dash's own screw at the driver's right (columnparts.py):
  ring teeth (right)    - the ring teeth with a shallow channel, so it can sit over the right spoke's junction with the
                          grip; zip tie slots all along it
  side bracket          - a flat plate zip-tied to the covers' right-hand side on two rubber strips, with the arm's
                          joint and a bar for the screw tab
  screw tab             - a bar from the side bracket to the dash's screw, three lengths, each adjustable
  The hinge block (column), motor carrier (column) and the fit test are the column mount's.
''')
src = src.replace('''  python3 accord_lka_parts.py --cover-width 118 --cover-height 92 --clamp-behind 180
''', '''  python3 accord_lka_parts.py --cover-width 118 --cover-height 92 --clamp-behind 180
  python3 accord_lka_parts.py --screw-right 50 --screw-down 70 --screw-behind 270 --cover-front-width 102
''')

# 2. arguments
src = src.replace('''  ap.add_argument("--bed", type=float, nargs=3,''', '''  ap.add_argument("--screw-right", type=float, default=P.SCREW_RIGHT,
                  help="right-side mount: the dash's screw, right of the steering wheel's outer edge at 3 o'clock (mm)")
  ap.add_argument("--screw-down", type=float, default=P.SCREW_DOWN, help="right-side mount: the screw below that point (mm)")
  ap.add_argument("--screw-behind", type=float, default=P.SCREW_BEHIND,
                  help="right-side mount: the screw's trim behind the front face of the steering wheel's rim (mm)")
  ap.add_argument("--cover-front-width", type=float, default=P.COVER_FRONT_W,
                  help="the column covers, side to side, at their front edge near the wheel (mm)")
  ap.add_argument("--ring-at", type=float, default=0.0,
                  help="right-side mount: turn the whole mount this many degrees above 3 o'clock (the screw tab's plate tilts with it)")
  ap.add_argument("--tab-length", type=float, default=None, help="right-side mount: also make a screw tab of exactly this length (mm)")
  ap.add_argument("--bed", type=float, nargs=3,''')

# 3. call the right-side section after the column mount
src = src.replace('''  report["column_mount"] = column_mount(args, base, arms, problems, on_bed, write_stl, part_rows, bed)
''', '''  report["column_mount"] = column_mount(args, base, arms, problems, on_bed, write_stl, part_rows, bed)
  report["side_mount"] = side_mount(args, base, arms, problems, on_bed, write_stl, part_rows, bed)
''')
open('accord_lka_parts.py', 'w').write(src)
print('ok')
EOF
grep -n "COVER_FRONT_W\|P.COVER_W\b" accord_lka_parts.py columnassembly.py | head; grep -n "import params as P\|^import\|^from" accord_lka_parts.py | head
python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()
# the clamp bar
old = '''CLAMP_Y = ((SPOOL_Y[0] + SPOOL_Y[1]) / 2 - CF["w"] / 2 - 2.2, (SPOOL_Y[0] + SPOOL_Y[1]) / 2 + CF["w"] / 2 + 2.2)'''
new = '''CLAMP_Y = ((SPOOL_Y[0] + SPOOL_Y[1]) / 2 - CF["w"] / 2 - 2.2, (SPOOL_Y[0] + SPOOL_Y[1]) / 2 + CF["w"] / 2 + 2.2)
# The strip's end is pinched between the tab and a small printed bar by two M3 x 10 screws beside its edges. The screws
# go in from the tab's 6 o'clock side (the latch's ear is in the way on the other) and cut their own thread in the bar.
CLAMP_BAR = ((STRIP_X - 0.2 - 4.0, STRIP_X - 0.2), (CLAMP_Y[0] - 3.5, CLAMP_Y[1] + 3.5), (CLAMP_Z - 4.0, CLAMP_Z + 4.0))'''
assert old in s
s = s.replace(old, new)
old = '''  # the strip's two clamp screws (M3 x 6, washers on the strip), cut their own thread into the tab
  for y in CLAMP_Y:
    part = part - cyl_x(M3_PILOT / 2, TAB[0][0] - 1.0, TAB[0][1] + 1.0, y=y, z=CLAMP_Z, segments=24)'''
new = '''  # the strip's two clamp screws, in from the tab's 6 o'clock side
  for y in CLAMP_Y:
    part = part - cyl_x(M3_CLEAR / 2, TAB[0][0] - 1.0, TAB[0][1] + 1.0, y=y, z=CLAMP_Z, segments=24)
  # slots through the finger guard's dash side, so a hex key reaches the power switch's screws from 6 o'clock with the
  # motor out on the teeth (to set the switch)
  for dy in (MP.SW_LEN / 2 - MP.SW_PITCH / 2, MP.SW_LEN / 2 + MP.SW_PITCH / 2):
    part = part - Manifold.batch_hull([cyl_x(2.6, -MP.GUARD_OUT - 15.0, MP.GUARD_OUT + 15.0, y=SW_Y0 + dy, z=SW_HOLES_Z + s,
                                             segments=24) for s in (-SW_SLOT, SW_SLOT)])'''
assert old in s
s = s.replace(old, new)
old = '''  clamp = union([cyl_x(3.5, STRIP_X - 0.7, STRIP_X - 0.2, y=y, z=CLAMP_Z - slide, segments=24) +
                 cyl_x(2.75, STRIP_X - 3.7, STRIP_X - 0.7, y=y, z=CLAMP_Z - slide, segments=24) for y in CLAMP_Y])'''
new = '''  heads = union([cyl_x(2.75, TAB[0][1], TAB[0][1] + 3.0, y=y, z=CLAMP_Z - slide, segments=24) for y in CLAMP_Y])
  clamp = slid(strip_clamp(), slide) + heads'''
assert old in s
s = s.replace(old, new)
# the bar itself
old = '''def block_screws() -> Manifold:'''
new = '''def strip_clamp() -> Manifold:
  """The bar that pinches the spring's strip against the bracket's tab (carrier frame, motor on)."""
  (x0, x1), (y0, y1), (z0, z1) = CLAMP_BAR
  bar = box(x0, x1, y0, y1, z0, z1)
  for y in CLAMP_Y:
    bar = bar - cyl_x(M3_PILOT / 2, x0 - 1.0, x1 + 1.0, y=y, z=CLAMP_Z, segments=24)
  return clean(bar)


def block_screws() -> Manifold:'''
s = s.replace(old, new, 1)
# the docstring
s = s.replace('''  motor bracket   - the motor bolts to its face (finger guard round the gear, as before); a flange along the motor's
                    4 o'clock side bolts to the rail's block; beside it the latch's ear, with the hole the plunger's
                    pin drops into, and the end that presses the switch; on the motor's dash side the tab the spring's
                    strip is clamped to''', '''  motor bracket   - the motor bolts to its face (finger guard round the gear, as before); a flange along the motor's
                    4 o'clock side bolts to the rail's block; beside it the latch's ear, with the hole the plunger's
                    pin drops into, and the end that presses the switch; on the motor's dash side the tab the spring's
                    strip is clamped to
  strip clamp     - a small bar that pinches the spring's strip against the tab (two M3 screws)''')
open(p, "w").write(s)

p = "sidebuild.py"
s = open(p).read()
s = s.replace('''  ("M3 x 6 socket head screw + M3 washer", 2, "the spring's strip to the bracket's tab (the washers clamp the strip's edges)"),''',
              '''  ("M3 x 10 socket head screw", 2, "the spring's strip: through the bracket's tab from the 6 o'clock side into the strip clamp"),''')
s = s.replace('''    "side-board-cover": (S.side_board_cap(), (0, 0, 0), "on its closed back", "none"),''',
              '''    "side-board-cover": (S.side_board_cap(), (0, 0, 0), "on its closed back", "none"),
    "side-strip-clamp": (S.strip_clamp(), (0, 90, 0), "flat", "none"),''')
open(p, "w").write(s)
EOF
grep -n "side-strip-clamp\|M3 x 10 socket head screw\"" sidebuild.py; PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import sideparts as S
b = S.side_bracket(); print('bracket', round(b.volume()), b.genus(), len(b.decompose()))
c = S.strip_clamp(); print('clamp', round(c.volume()), [round(v,1) for v in c.bounding_box()])
" && PYTHONPATH=/home/claude/pylib timeout 900 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/run_internal.py
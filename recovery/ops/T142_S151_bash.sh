python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)
rep('''PL_FRONT_Z = -92.0            # the right leg's front end (behind the key cylinder's bulge)''',
'''PL_FRONT_Z = -92.0            # the right leg's front end (behind the key cylinder's bulge) ...
PL_NOTCH = (44.0, -114.0)     # ... except outside x 44, where it starts at z -114: the springs' bolt on the hinge block
                              # and the springs' loops on it hang just above there''')
rep('''PL_SLOTS = ((52.0, -100.0, 52.0, -186.0), (28.0, -136.0, 28.0, -186.0), (-40.0, -198.0, 4.0, -198.0),
            (-57.0, -132.0, -57.0, -184.0), (20.0, -104.0, 44.0, -104.0))''',
'''PL_SLOTS = ((54.0, -122.0, 54.0, -186.0), (28.0, -136.0, 28.0, -186.0), (-40.0, -198.0, 4.0, -198.0),
            (-57.0, -132.0, -57.0, -184.0), (20.0, -104.0, 38.0, -104.0))''')
rep('''  part = union([right, left, bridge])
  # round the corners you might touch
  part = _round_corner(part, PL_RIGHT_X[0], PL_FRONT_Z, 1, -1, 8.0, y0, y1)''',
'''  part = union([right, left, bridge])
  part = part - box(PL_NOTCH[0], PL_RIGHT_X[1] + 1.0, y0 - 1.0, y1 + 1.0, PL_NOTCH[1], PL_FRONT_Z + 1.0)
  # round the corners you might touch
  part = _round_corner(part, PL_RIGHT_X[0], PL_FRONT_Z, 1, -1, 8.0, y0, y1)
  part = _round_corner(part, PL_NOTCH[0], PL_FRONT_Z, -1, -1, 6.0, y0, y1)''')
rep('''  x_lo = min(min(xs) - FLANGE_PAD, PL_RIGHT_X[1] - 8.0)
  return [(x_lo, y_lo), (max(xs) + FLANGE_PAD + 2.0, y_lo), (max(xs) + FLANGE_PAD + 2.0, max(ys) + SLOT_Y + FLANGE_PAD),
          (x_lo, max(ys) + SLOT_Y + FLANGE_PAD)]''',
'''  x_lo = min(min(xs) - FLANGE_PAD, PL_RIGHT_X[1] - 8.0)
  x_hi = max(xs) + FLANGE_PAD + 2.0
  # its lower outer corner cut away: the lower spring sweeps past there as the motor pops off
  cx = max(xs) - 4.0
  cy = max(min(ys), y_lo + 10.0)
  return [(x_lo, y_lo), (cx, y_lo), (x_hi, cy), (x_hi, max(ys) + SLOT_Y + FLANGE_PAD), (x_lo, max(ys) + SLOT_Y + FLANGE_PAD)]''')
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache python3 -c "
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2')
import run_u, popassembly as PA, popparts as PP, numpy as np
from cadlib import union
t, parts = run_u.build()
A = PA.PopAssembly(t, parts)
PL = A.plate()
print('outline', [tuple(round(v,1) for v in q) for q in PP.plate_flange_outline()])
keep = PP.MOUNT_DEG
for adj in (0.0, -3.0, 6.0):
  PP.MOUNT_DEG = keep + adj
  sw = union([A.springs(float(l)) + A.bolts(float(l)) for l in np.arange(-3, 76, 2.5)])
  x = sw ^ PL
  print('adj', adj, 'overlap', round(x.volume(),2), [round(v,1) for v in x.bounding_box()] if x.volume() > 1e-3 else '')
PP.MOUNT_DEG = keep
for r in PA.tab_placements(): print(r[0], tuple(round(float(v),1) for v in r[3]), r[4], r[5])
"
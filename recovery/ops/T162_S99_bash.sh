python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()
rep = [
('''PLATE_T = 6.0
X_PL = (X_RAIL_BOT - PLATE_T, X_RAIL_BOT)                      # the plate (-48.8, -42.8)''',
'''PLATE_T = 6.8
X_PL = (X_RAIL_BOT - PLATE_T, X_RAIL_BOT)                      # the plate (-49.6, -42.8)'''),
('''BOSS_OUT = 0.8                    # a boss on the plate's outer face under the plunger's collar
X_COLLAR = X_PL[0] - BOSS_OUT                                  # -49.6''',
'''X_COLLAR = X_PL[0]                                             # its collar on the plate's outer face, -49.6'''),
('''HOLDER_X = (SW_X[0] - 3.5, SW_X[0])        # the wall it hangs on''',
'''HOLDER_X = (X_RAIL_BOT, SW_X[0])           # the block it hangs on, out from the plate'''),
('''M2_CLEAR, M2_NUT_AF, M2_NUT_T = MP.M2_CLEAR, MP.M2_NUT_AF, MP.M2_NUT_T''',
'''M2_CLEAR, M2_NUT_AF, M2_NUT_T = MP.M2_CLEAR, MP.M2_NUT_AF, MP.M2_NUT_T
SW_SCREW_LEN = 12.0                        # M2 x 12: through the switch into a nut in a slot in the block
SW_NUT_X = (SW_X[1] - SW_SCREW_LEN + 0.2, SW_X[1] - SW_SCREW_LEN + 0.2 + M2_NUT_T)'''),
]
for a, b in rep:
    assert a in s, a[:60]
    s = s.replace(a, b)
old = s[s.index("  # the plunger's boss on the outside\n"):s.index("  # the spool's post\n")]
new = '''  # the switch's holder: a block out from the plate, with a stop beside the switch in the pin's band
  hx, hy, hz = HOLDER_X, HOLDER_Y, HOLDER_Z
  parts.append(box(hx[0] - 0.01, hx[1], hy[0], hy[1], hz[0], hz[1]))
  parts.append(box(hx[1] - 0.01, BEVEL_TOP + 4.6, hy[0], SW_Y0 - 0.3, hz[0], hz[0] + 7.0))
'''
s = s.replace(old, new)
old = s[s.index("  # the switch's two M2 screws: slots along z through the wall"):s.index("  # the spool's M4 screw: cuts its own thread into the post")]
new = '''  # the switch's two M2 x 12 screws: slots along z (it slides +- SW_SLOT to set it), each into a nut that slides in a
  # hex slot open at the block's top
  for dy in (MP.SW_LEN / 2 - MP.SW_PITCH / 2, MP.SW_LEN / 2 + MP.SW_PITCH / 2):
    y = SW_Y0 + dy
    part = part - Manifold.batch_hull([cyl_x(M2_CLEAR / 2, SW_NUT_X[0] - 1.0, hx[1] + 1.0, y=y, z=SW_HOLES_Z + s, segments=20)
                                       for s in (-SW_SLOT, SW_SLOT)])
    part = part - box(SW_NUT_X[0], SW_NUT_X[1], y - M2_NUT_AF / 2, y + M2_NUT_AF / 2, SW_HOLES_Z - SW_SLOT - 2.6, hz[1] + 1.0)
'''
s = s.replace(old, new)
open(p, "w").write(s)
EOF
grep -n "HOLDER_X\|SW_NUT_X\|X_COLLAR\|PLATE_T" sideparts.py | head; PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import sideparts as S
p = S.side_plate(); print('plate', round(p.volume()), p.genus(), [round(v,1) for v in p.bounding_box()], len(p.decompose()))
print(S.SW_NUT_X, S.HOLDER_X, S.X_COLLAR, S.X_THREAD_END, S.X_PIN_TIP)
" && PYTHONPATH=/home/claude/pylib timeout 900 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/run_internal.py
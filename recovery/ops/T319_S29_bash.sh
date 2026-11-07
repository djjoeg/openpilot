cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v5/cad && python3 - <<'EOF'
p = 'rightarm.py'
s = open(p).read()
reps = [
("""M4_SLOT = (M4_NUT_AF / math.cos(math.radians(30)) + 0.4, M4_NUT_T + 0.4)   # across (corners), along the bar""",
 """M4_SLOT = (M4_NUT_AF + 0.4, M4_NUT_T + 0.4)   # across (the nut's flats, so it can't turn), along the bar
M4_SLOT_DEEP = M4_NUT_AF / 2 / math.cos(math.radians(30)) + 0.25   # from the bar's middle line to the slot's bottom
DEEP = 50.0                      # v5: the arm this deep along the column, from DEEP_X0 to the tower (it twisted before)
DEEP_X0 = ARM_X[0] + 47.0 + 5.5  # 125.5: 5.5 outside the receiver's mouth at the nominal place (5 mm left to slide in)"""),
("""  m = m - uvz(bu - M4_SLOT[0] / 2, bu + M4_SLOT[0] / 2, bv - M4_NUT_AF / 2 - 0.25, BAR_V[1] + 1.0, z0, z0 + M4_SLOT[1])""",
 """  m = m - uvz(bu - M4_SLOT[0] / 2, bu + M4_SLOT[0] / 2, bv - M4_SLOT_DEEP, BAR_V[1] + 1.0, z0, z0 + M4_SLOT[1])"""),
("""  tower = uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], TOWER_Z[0], TOWER_Z[1])
  m = a + foot + tower""",
 """  tower = uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], TOWER_Z[0], TOWER_Z[1])
  z1 = ARM_Z[0] + DEEP
  deep = Manifold.batch_hull([box(DEEP_X0, ARM_X[1], ARM_Y[0], ARM_Y[1] - 1.0, ARM_Z[0], z1),
                              uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], ARM_Z[0], z1)])
  deep = deep ^ box(DEEP_X0, 400.0, -400.0, ARM_Y[1] - 1.0, ARM_Z[0] - 1.0, z1)   # 1 under the frame plate
  m = a + foot + tower + deep"""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
open(p, 'w').write(s)
p = 'rightcheck.py'
s = open(p).read()
reps = [
("""  \"\"\"An M4 nut along z from z0, its corners along U (as it sits in the carrier's slot).\"\"\"
  return hex_prism_z(RA.M4_NUT_AF, z0, z0 + RA.M4_NUT_T, x=x, y=y, rot=RA.THETA)""",
 """  \"\"\"An M4 nut along z from z0, its flats facing U (as it sits in the carrier's slot).\"\"\"
  return hex_prism_z(RA.M4_NUT_AF, z0, z0 + RA.M4_NUT_T, x=x, y=y, rot=RA.THETA + 30.0)"""),
("""  for dx in (-20.0, 20.0):""", """  for dx in (-5.0, 20.0):                  # v5: in by more than 5.5 the deep part meets the receiver's end"""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
open(p, 'w').write(s)
print('ok')
EOF
grep -n "def hex_prism_z" -A 8 cadlib.py | head -12
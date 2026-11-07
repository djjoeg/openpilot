python3 - << 'EOF'
p = "mountparts.py"
s = open(p).read()
rep = [
("""CARRIER_KNUCKLE = 15.0                # carrier's knuckle spans x +-this""",
 """CARRIER_KNUCKLE = 15.0                # carrier's knuckle spans x +-this
CARRIER_KNUCKLE_R = 6.5               # carrier's knuckle radius (it turns in a channel of radius HINGE_R + CHANNEL_GAP)"""),
("""  knuckle = cyl_x(HINGE_R, -CARRIER_KNUCKLE, CARRIER_KNUCKLE, y=hy, z=hz) + \\
    box(-CARRIER_KNUCKLE, CARRIER_KNUCKLE, TOP_Y[1] - 1.0, hy, hz - HINGE_R, hz + HINGE_R)
  # a pointed front (below the hinge block) and a slope down to the carrier's top: it prints guard down unsupported
  tip = (hy, hz + HINGE_R * math.sqrt(2.0))
  side = (hy + HINGE_R / math.sqrt(2.0), hz + HINGE_R / math.sqrt(2.0))
  knuckle = knuckle + prism_x([(hy - HINGE_R / math.sqrt(2.0), side[1]), side, tip], -CARRIER_KNUCKLE, CARRIER_KNUCKLE)""",
 """  kr = CARRIER_KNUCKLE_R
  knuckle = cyl_x(kr, -CARRIER_KNUCKLE, CARRIER_KNUCKLE, y=hy, z=hz) + \\
    box(-CARRIER_KNUCKLE, CARRIER_KNUCKLE, TOP_Y[1] - 1.0, hy, hz - kr, hz + kr)
  # a pointed front (it stays below the hinge block at any lift) and a slope down to the carrier's top, so the
  # carrier prints finger guard down without supports here
  tip = (hy, hz + kr * math.sqrt(2.0))
  side = (hy + kr / math.sqrt(2.0), hz + kr / math.sqrt(2.0))
  knuckle = knuckle + prism_x([(hy - kr / math.sqrt(2.0), side[1]), side, tip], -CARRIER_KNUCKLE, CARRIER_KNUCKLE)"""),
]
for a, b in rep:
  assert a in s, a[:80]
  s = s.replace(a, b)
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  "; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/overhang_where.py 2>&1 | sed -n '/carrier/,/clamp/p' | head -14
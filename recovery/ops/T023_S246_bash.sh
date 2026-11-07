python3 - << 'EOF'
p = "mountparts.py"
s = open(p).read()
rep = [
# carrier knuckle: teardrop point towards the front, so it prints guard down without supports
("""  rise = hy - TOP_Y[1] + 0.5
  knuckle = knuckle + prism_x([(TOP_Y[1] - 0.5, hz + HINGE_R - 0.01), (hy, hz + HINGE_R - 0.01),
                               (TOP_Y[1] - 0.5, hz + HINGE_R + rise)], -CARRIER_KNUCKLE, CARRIER_KNUCKLE)""",
"""  # a pointed front (below the hinge block) and a slope down to the carrier's top: it prints guard down unsupported
  tip = (hy, hz + HINGE_R * math.sqrt(2.0))
  side = (hy + HINGE_R / math.sqrt(2.0), hz + HINGE_R / math.sqrt(2.0))
  knuckle = knuckle + prism_x([(hy - HINGE_R / math.sqrt(2.0), side[1]), side, tip], -CARRIER_KNUCKLE, CARRIER_KNUCKLE)
  rise = tip[0] - TOP_Y[1] + 0.5
  knuckle = knuckle + prism_x([(TOP_Y[1] - 0.5, tip[1] - 0.01), (tip[0], tip[1] - 0.01),
                               (TOP_Y[1] - 0.5, tip[1] + 1.2 * rise)], -CARRIER_KNUCKLE, CARRIER_KNUCKLE)"""),
# fin ramp a bit steeper than 45 degrees
("""  fin = prism_x([(TOP_Y[0], vz - FIN_LEN / 2), (FIN_TOP, vz - FIN_LEN / 2), (FIN_TOP, zf),
                 (TOP_Y[1] - 0.5, zf + FIN_TOP - TOP_Y[1] + 0.5), (TOP_Y[0], zf + FIN_TOP - TOP_Y[1] + 0.5)], -FIN_HALF, FIN_HALF)""",
"""  run = 1.2 * (FIN_TOP - TOP_Y[1] + 0.5)
  fin = prism_x([(TOP_Y[0], vz - FIN_LEN / 2), (FIN_TOP, vz - FIN_LEN / 2), (FIN_TOP, zf),
                 (TOP_Y[1] - 0.5, zf + run), (TOP_Y[0], zf + run)], -FIN_HALF, FIN_HALF)"""),
# hinge block: lever walls' front edge steeper; rest and cage fronts cut back
("""  wall_cs = CrossSection.batch_hull([circle_yz(8.0, vy, vz), rect_yz(HB_BOTTOM, HB_TOP, vz - 4.0, HB_BODY_BACK + 2.0),""",
 """  wall_cs = CrossSection.batch_hull([circle_yz(8.0, vy, vz), rect_yz(HB_BOTTOM, HB_TOP + 3.5, vz - 4.0, HB_BODY_BACK + 2.0),"""),
("""  rest = place_yz(rest_and_cage(), LEVER_ON, vy, vz)
  part = union([body] + kn + ears + walls + [rest])""",
 """  rest = place_yz(rest_and_cage(), LEVER_ON, vy, vz) - rest_front_cut()
  part = union([body] + kn + ears + walls + [rest])"""),
("""def switch_body() -> Manifold:""",
 """def rest_front_cut() -> Manifold:
  \"\"\"Takes the front off the rest and the switch cage along a plane leaning back 40 degrees from upright, so they
  print front face down without supports (hinge block frame).\"\"\"
  c = _lever_frame_point(-HANDLE_T / 2, -REST_D[0])
  n = np.array([math.sin(math.radians(50.0)), math.cos(math.radians(50.0))])     # (y, z), points out of the cut
  big = box(-50, 50, -100, 100, 0.0, 200.0)                                       # z >= 0: removed side
  ang = math.degrees(math.atan2(n[0], n[1]))                                      # turn +z onto n
  return place_yz(big, -ang, float(c[0]), float(c[1]))


def switch_body() -> Manifold:"""),
]
for a, b in rep:
  assert a in s, a[:80]
  s = s.replace(a, b)
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  "; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/overhang_where.py 2>&1 | head -30
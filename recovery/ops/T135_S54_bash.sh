python3 - <<'EOF'
s = open('popparts.py').read()
# 1. lobe ramp placeholder -> a lobe whose radius tapers at each end
old = """  # the switch's lobe: a raised arc on the knuckle, where the switch's roller rests while the motor is on
  lobe_cs = _sector_yz(KNUCKLE_R - 0.5, LOBE_R, SW_BETA + LOBE_ON[0], SW_BETA + LOBE_ON[1], 0.5)
  # a ramp each end, so the roller climbs on smoothly
  ramp_a = _sector_yz(KNUCKLE_R - 0.5, LOBE_R, SW_BETA + LOBE_ON[1], SW_BETA + LOBE_ON[1] + 1.0, 0.25)
  lobe = extrude_x(lobe_cs, *LOBE)
  part = union([plate, guard, top, walls, bar, knuckle, webs, lobe])
  part = part - extrude_x(ramp_a, LOBE[0] - 1, LOBE[1] + 1) * 0  # placeholder for a later smoother ramp
"""
new = """  # the switch's lobe: a raised arc on the knuckle where the switch's roller rests while the motor is on, sloping down
  # to the knuckle over LOBE_RAMP degrees at each end so the roller rolls on and off
  lobe = extrude_x(_lobe_outline(), *LOBE)
  part = union([plate, guard, top, walls, bar, knuckle, webs, lobe])
"""
assert old in s
s = s.replace(old, new)
old2 = """def pop_carrier() -> Manifold:"""
new2 = """LOBE_RAMP = 12.0


def _lobe_outline() -> CrossSection:
  hy, hz = HINGE_P
  b0, b1 = SW_BETA + LOBE_ON[0], SW_BETA + LOBE_ON[1]

  def r_at(b):
    if b < b0:
      return KNUCKLE_R + (LOBE_R - KNUCKLE_R) * (b - (b0 - LOBE_RAMP)) / LOBE_RAMP
    if b > b1:
      return KNUCKLE_R + (LOBE_R - KNUCKLE_R) * ((b1 + LOBE_RAMP) - b) / LOBE_RAMP
    return LOBE_R

  bs = np.linspace(b0 - LOBE_RAMP, b1 + LOBE_RAMP, 81)
  pts = [(hy + r_at(b) * math.cos(math.radians(b)), hz + r_at(b) * math.sin(math.radians(b))) for b in bs]
  pts += [(hy + (KNUCKLE_R - 1.0) * math.cos(math.radians(b)), hz + (KNUCKLE_R - 1.0) * math.sin(math.radians(b)))
          for b in bs[::-1]]
  cs = CrossSection([pts])
  return cs if cs.area() > 0 else CrossSection([pts[::-1]])


def pop_carrier() -> Manifold:"""
s = s.replace(old2, new2, 1)
# 2. spring holes: a single back bolt
s = s.replace("""SPRING_HOLES = (0.0, -(2 * SPRING_WIRE_P))   # the back bolt's second hole sits closer by this much, along the spring:
                                             # for McMaster's length being measured over the loops
""", "")
s = s.replace('''def b_bolt(hole: int = 0) -> np.ndarray:
  """The hinge block's spring bolt: hole 0, or hole 1 a little closer to the carrier's bolt along the spring."""
  d = C_BOLT - B_BOLT
  return B_BOLT + SPRING_HOLES[hole] * -d / np.linalg.norm(d)
''', '''def b_bolt(hole: int = 0) -> np.ndarray:
  return B_BOLT
''')
s = s.replace("""# (113.0 N) at most, 3.53 in (89.7 mm) long at that (McMaster's table). McMaster's table doesn't say whether its length
# is inside the loops or overall; the hinge block has two holes for the back bolt, one for each (see SPRING_HOLES).""",
"""# (113.0 N) at most, 3.53 in (89.7 mm) long at that (McMaster's table). McMaster's table doesn't say whether its length
# is inside the loops or over them: the bolts are placed for inside; over them, each spring pulls 15 N more (the
# margins cover both).""")
# 3. spring solid: loops and coil
old3 = s[s.index("def spring_solid("):]
new3 = '''def spring_solid(lift: float, hole: int = 0) -> Manifold:
  """Both springs (coils and end loops), carrier frame, the carrier swung off by lift (the back bolt doesn't move). Each
  loop's inside rests on the far side of its bolt."""
  c = turn(C_BOLT, lift)
  b = b_bolt(hole)
  r_out = SPRING_OD_P / 2
  r_in = r_out - SPRING_WIRE_P
  out = []
  for s in (1, -1):
    a3 = np.array([s * SPRING_X, c[0], c[1]])
    b3 = np.array([s * SPRING_X, b[0], b[1]])
    d = b3 - a3
    L = float(np.linalg.norm(d))
    z = d / L
    x = np.array([1.0, 0.0, 0.0])
    y = np.cross(z, x)
    R = np.stack([x, y, z], axis=1)
    lc0 = -PIN_D / 2 + r_in + r_out             # the loop's middle, then where the coils start
    ring = (cyl_x(r_out, -SPRING_WIRE_P / 2, SPRING_WIRE_P / 2, segments=40) -
            cyl_x(r_in, -SPRING_WIRE_P, SPRING_WIRE_P, segments=40))
    loop_a = ring.translate((0, 0, -PIN_D / 2 + r_in))
    loop_b = ring.translate((0, 0, L + PIN_D / 2 - r_in))
    coil = cyl(r_out, lc0 - 0.5, L - lc0 + 0.5, segments=40)
    out.append(place(coil + loop_a + loop_b, R, a3))
  return union(out)
'''
s = s.replace(old3, new3)
open('popparts.py', 'w').write(s)
EOF
grep -n "class PopTeeth" -A 22 popparts.py | head -30
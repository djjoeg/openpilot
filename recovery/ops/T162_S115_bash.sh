cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()

# 1. gothic guard: printable lying on its driver side (the arch's top towards the dash comes to a 45 degree point)
old = s[s.index("def _guard() -> Manifold:"):s.index("def ear_bevel() -> Manifold:")]
new = '''def gothic(r: float, segments: int = 180) -> CrossSection:
  """A circle of radius r with a 45 degree point on its +y side (towards the dash): printed lying on its -y side, its
  top needs no support."""
  k = r / math.sqrt(2.0)
  return CrossSection.circle(r, segments) + CrossSection([[(-k, k), (k, k), (0.0, r * math.sqrt(2.0))]])


def teardrop_x(r: float, x0: float, x1: float, y: float, z: float) -> Manifold:
  """A hole along x with a 45 degree point on its +y side (printed with +y up)."""
  cs = gothic(r, 48).rotate(-90.0) if False else gothic(r, 48)
  # (u, v) = (z, y) in the outline: extrude along x
  m = cs.extrude(x1 - x0).transform([[0, 0, 1, x0], [0, 1, 0, 0], [1, 0, 0, 0]])
  m = m if m.volume() > 0 else m.mirror((1, 0, 0))
  return m.translate((0.0, y, z))


def _guard() -> Manifold:
  t = MOTOR_PLATE_T
  shell = gothic(MP.GUARD_OUT).extrude(GUARD_FRONT - t + 0.01).translate((0, 0, t - 0.01)) - \\
    gothic(MP.GUARD_IN).extrude(GUARD_FRONT - t + 2).translate((0, 0, t - 1))
  lip = gothic(MP.GUARD_OUT).extrude(1.6).translate((0, 0, GUARD_FRONT - 1.6)) - \\
    gothic(MP.GUARD_LIP_IN).extrude(4.0).translate((0, 0, GUARD_FRONT - 3))
  gw = FP.GUARD_WINDOW_F
  window = sector(MP.GUARD_OUT + 6, 270.0 - gw, 270.0 + gw).extrude(GUARD_FRONT + 4).translate((0, 0, t - 2))
  guard = (shell + lip) - window
  for sgn in (-1, 1):
    a = math.radians(270.0 + sgn * gw)
    rm = (MP.GUARD_IN + MP.GUARD_OUT) / 2
    guard = guard + cyl((MP.GUARD_OUT - MP.GUARD_IN) / 2 + 0.6, t - 0.01, GUARD_FRONT, rm * math.cos(a), rm * math.sin(a), 24)
  return guard


'''
s = s.replace(old, new)

# 2. the face plate's outline includes the guard's pointed top too
s = s.replace('''  outline = CrossSection.square((2 * MP.PLATE_HALF, 2 * MP.PLATE_HALF), center=True) + CrossSection.circle(MP.GUARD_OUT, 180)
  outline = outline ^ CrossSection.square((200, 200)).translate((-100, MP.PLATE_BOTTOM))
  # out to the flange''', '''  outline = CrossSection.square((2 * MP.PLATE_HALF, 2 * MP.PLATE_HALF), center=True) + gothic(MP.GUARD_OUT)
  outline = outline ^ CrossSection.square((200, 200)).translate((-100, MP.PLATE_BOTTOM))
  # out to the flange''')

# 3. teardrop holes for the motor's boss and the latch pin (printed lying on the bracket's driver side, +y up)
s = s.replace('''  part = part - cyl(NEMA_BOSS / 2 + 0.4, -3, MOTOR_PLATE_T + 1, segments=128)
  for sx in (-1, 1):''', '''  part = part - gothic(NEMA_BOSS / 2 + 0.4, 128).extrude(MOTOR_PLATE_T + 4).translate((0, 0, -3))
  for sx in (-1, 1):''')
s = s.replace('''  part = part - cyl_x(PIN_HOLE_D / 2, X_EAR[0] - 1.0, X_EAR[1] + 1.0, y=PIN_Y, z=PIN_Z, segments=48)''',
              '''  part = part - teardrop_x(PIN_HOLE_D / 2, X_EAR[0] - 1.0, X_EAR[1] + 1.0, PIN_Y, PIN_Z)''')

# 4. the spool: one flange (on the bed when printed); the post's face guides the coil's other side
s = s.replace('''SPOOL_Y = (31.0, 44.2)            # the drum between its flanges''',
              '''SPOOL_Y = (30.4, 43.6)            # the drum: the post's face on one side, the spool's flange on the other''')
s = s.replace('''POST = ((X_RAIL_BOT, -24.0), (24.0, SPOOL_Y[0] - SPOOL_FLANGE[1] - 0.4), (SPOOL_Z - 8.0, SPOOL_Z + 8.0))''',
              '''POST = ((X_RAIL_BOT, -24.0), (24.0, SPOOL_Y[0] - 0.4), (SPOOL_Z - 8.0, SPOOL_Z + 8.0))
POST_FACE = 13.5                  # the post's face round the axle (radius) that guides the coil's side''')
old = s[s.index("def side_spool() -> Manifold:"):s.index("# ***** the board cover, turned a quarter *****")]
new = '''def side_spool() -> Manifold:
  """Spool frame: its axle along y, y as fitted. One flange, on the screw head's side (on the print bed); the post's face
  guides the coil's other side."""
  d, (y0, y1) = DRUM_D, SPOOL_Y
  fd, ft = SPOOL_FLANGE
  hub = cyl_y(d / 2, y0, y1 + 0.01, segments=96)
  fl = cyl_y(fd / 2, y1, y1 + ft, segments=96)
  return clean((hub + fl) - cyl_y(2.2, y0 - 1.0, y1 + ft + 1.0, segments=32))


'''
s = s.replace(old, new)
# the post's round face
s = s.replace('''  # the spool's post
  (px0, px1), (py0, py1), (pz0, pz1) = POST
  parts.append(box(px0, px1, py0, py1, pz0, pz1))''', '''  # the spool's post, with a round face that guides the coil's side
  (px0, px1), (py0, py1), (pz0, pz1) = POST
  parts.append(box(px0, px1, py0, py1, pz0, pz1))
  parts.append(cyl_y(POST_FACE, py1 - 1.6, py1, x=SPOOL_X, z=SPOOL_Z, segments=96) ^ box(px0, 0.0, py0, py1 + 1.0, -200.0, 0.0))
  parts.append(Manifold.batch_hull([box(px0, px0 + 0.01, py1 - 1.6, py1, pz0, pz1),
                                    cyl_y(POST_FACE, py1 - 1.6, py1, x=SPOOL_X, z=SPOOL_Z, segments=96)]) ^
               box(px0, 0.0, py0, py1, -200.0, 0.0))''')
open(p, "w").write(s)
EOF
grep -n "def teardrop_x" -A8 sideparts.py | head -12
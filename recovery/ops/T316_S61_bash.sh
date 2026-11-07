python3 - <<'EOF'
p='rightarm.py'; s=open(p).read()
rep = [
('''def arm() -> Manifold:
  """The arm and the tower at its end, one piece (printed flat, the tower standing up): the arm runs into the
  tower's foot (the hull of the arm's end and the tower, as thick as the arm); the channel up the tower is open
  towards the motor; the push bolt goes in through the outer wall, its nut dropped into the slot from the top."""''',
'''def bore_mouths() -> Manifold:
  """The tube's two mouths cut back 45 degrees, BORE_CHAMFER deep: the bar's end finds its way in at the top, and the
  bottom's first layers (on the bed) can't pinch it."""
  c, e = BORE_CHAMFER, 0.5
  out = []
  for z_face, sgn in ((TOWER_Z[0], 1.0), (TOWER_Z[1], -1.0)):
    wide = uvz(CH_U[0] - c - e, CH_U[1] + c + e, CH_V0 - c - e, CH_V1 + c + e, z_face - sgn * e - 0.01, z_face - sgn * e + 0.01)
    bore = uvz(CH_U[0], CH_U[1], CH_V0, CH_V1, z_face + sgn * c - 0.01, z_face + sgn * c + 0.01)
    out.append(Manifold.batch_hull([wide, bore]))
  return union(out)


def arm() -> Manifold:
  """The arm and the tower at its end, one piece (printed flat, the tower standing up): the arm runs into the
  tower's foot (the hull of the arm's end and the tower, as thick as the arm); up the tower, a square tube the motor
  carrier's bar slides in (closed on all four sides, v4); the push bolt goes in through the outer wall, its nut
  dropped into the slot from the top."""'''),
('''  m = m - uvz(CH_U[0], CH_U[1], CH_V0, CH_V0 + 80.0, TOWER_Z[0] - 1.0, TOWER_Z[1] + 1.0)''',
'''  m = m - uvz(CH_U[0], CH_U[1], CH_V0, CH_V1, TOWER_Z[0] - 1.0, TOWER_Z[1] + 1.0) - bore_mouths()'''),
('''def carrier(dz: float = 0.0) -> Manifold:
  """The motor carrier, one piece (printed on its side towards 5 o'clock): the bar that slides in the tower's
  channel; the lug at its bottom end (the stop bolt up through it, its nut in the pocket on top); at its top the web
  and the plate the motor bolts to (perpendicular to U, the motor's face against its outside; pads round the four
  M3 holes inside; the big hole a teardrop so it prints). dz: slid along the column from the nominal depth
  (+ towards you, deeper into the teeth)."""
  lug_top = TOWER_Z[0] - STOP_P
  m = uvz(BAR_U[0], BAR_U[1], BAR_V[0], BAR_V[1], BAR_Z[0], BAR_Z[1])
  m = m + uvz(PLATE_U[0], BAR_U[0] + 0.01, BAR_V[0], BAR_V[1], WEB_Z0, PLATE_Z[1])               # the web
  m = m + uvz(PLATE_U[0], PLATE_U[1], PLATE_V[0], PLATE_V[1], PLATE_Z[0], PLATE_Z[1])            # the plate
  m = m + uvz(LUG_U[0], LUG_U[1] + 0.01, BAR_V[0], BAR_V[1], lug_top - LUG_T, lug_top)           # the lug''',
'''def teardrop_z(r: float, z0: float, z1: float, u: float, v: float, flat: float = 0.6) -> Manifold:
  """A hole along z at (u, v) of the motor's frame that prints without support lying on its side with +v up (the
  carrier): a circle with a 45 degree roof towards +v, cut flat `flat` above the circle."""
  c = cyl(r, z0, z1, x=u, y=v, segments=32)
  tip = cyl(0.01, z0, z1, x=u, y=v + r * math.sqrt(2.0), segments=8)
  m = Manifold.batch_hull([c, tip]) ^ box(u - r - 1.0, u + r + 1.0, v - r - 1.0, v + r + flat, z0 - 1.0, z1 + 1.0)
  return m.rotate((0.0, 0.0, THETA))


def carrier(dz: float = 0.0) -> Manifold:
  """The motor carrier, one piece (printed on its side towards 5 o'clock): the bar that slides in the tower's tube,
  plain to its bottom end (v4: no lug) so it goes in from the tower's top; up its middle from that end, the hole for
  the M4 stop bolt and the slot its nut drops into, 4 mm in; at its top the web and the plate the motor bolts to
  (perpendicular to U, the motor's face against its outside; pads round the four M3 holes inside; the big hole a
  teardrop so it prints). dz: slid along the column from the nominal depth (+ towards you, deeper into the teeth)."""
  m = uvz(BAR_U[0], BAR_U[1], BAR_V[0], BAR_V[1], BAR_Z[0], BAR_Z[1])
  m = m + uvz(PLATE_U[0], BAR_U[0] + 0.01, BAR_V[0], BAR_V[1], WEB_Z0, PLATE_Z[1])               # the web
  m = m + uvz(PLATE_U[0], PLATE_U[1], PLATE_V[0], PLATE_V[1], PLATE_Z[0], PLATE_Z[1])            # the plate'''),
('''  su, sv = STOP_UV
  sx, sy = rad(su, sv)
  m = m - uv_cyl_z(M5_HOLE / 2, su, sv, lug_top - LUG_T - 1.0, lug_top + 1.0)
  m = m - hex_prism_z(NUT_TRAP[0], lug_top - NUT_TRAP[1], lug_top + 1.0, x=sx, y=sy, rot=30.0 + THETA)
  return clean(m).translate((0.0, 0.0, dz))''',
'''  bu, bv = BAR_UV
  m = m - teardrop_z(M4_HOLE / 2, BAR_Z[0] - 1.0, BAR_Z[0] + M4_DEPTH, bu, bv)
  z0 = BAR_Z[0] + M4_SLOT_IN
  m = m - uvz(bu - M4_SLOT[0] / 2, bu + M4_SLOT[0] / 2, bv - M4_NUT_AF / 2 - 0.25, BAR_V[1] + 1.0, z0, z0 + M4_SLOT[1])
  return clean(m).translate((0.0, 0.0, dz))'''),
('''  """The plate labels up (the receiver standing on it); the arm flat, the tower standing up (the channel open on
  one side, its top flat); the carrier on its side towards 5 o'clock (the bar, the web, the lug and the plate's edge
  all start at v -39), the plate standing up from it."""''',
'''  """The plate labels up (the receiver standing on it); the arm flat, the tower standing up (the tube straight up,
  its top flat); the carrier on its side towards 5 o'clock (the bar, the web and the plate's edge all start at v -39),
  the plate standing up from it, the stop nut's slot open on top."""'''),
]
for a,b in rep:
  assert a in s, a[:70]
  s = s.replace(a,b)
open(p,'w').write(s)
EOF
ruff check rightarm.py --output-format concise | head; export PYTHONPATH=/home/claude/pylib && timeout 300 python3 -c "
import rightarm as RA
a = RA.arm(); c = RA.carrier()
print('arm', a.genus(), round(a.volume()/1000*1.28,1), 'g', [round(x,1) for x in a.bounding_box()])
print('carrier', c.genus(), round(c.volume()/1000*1.28,1), 'g', [round(x,1) for x in c.bounding_box()])
print('arm/carrier overlap', round((a ^ c).volume(), 3))
for dz in (-10, -6, 0, 4): print(dz, round((a ^ RA.carrier(dz)).volume(), 3))
"
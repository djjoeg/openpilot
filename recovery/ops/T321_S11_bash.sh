python3 - <<'EOF'
p = 'rightarm.py'
s = open(p, encoding='utf-8').read()
reps = [
("""def arm() -> Manifold:
  \"\"\"The arm and the tower at its end, one piece (printed flat, the tower standing up): the arm runs into the
  tower's foot (the hull of the arm's end and the tower, as thick as the arm); up the tower, a square tube the motor
  carrier's bar slides in (closed on all four sides, v4); the push bolt goes in through the outer wall, its nut
  dropped into the slot from the top.\"\"\"
  a = box(ARM_X[0], ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1])
  foot = Manifold.batch_hull([box(ARM_X[1] - 5.0, ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1]),
                              uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], ARM_Z[0], ARM_Z[1])])
  foot = foot ^ box(ARM_X[0], 400.0, -400.0, ARM_Y[1], ARM_Z[0] - 1.0, ARM_Z[1] + 1.0)   # no higher than the arm (v4: the
                                                 # tower's top corner now stands above it; slid in, it would meet the plate)
  tower = uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], TOWER_Z[0], TOWER_Z[1])
  m = a + foot + tower
  m = m - uvz(CH_U[0], CH_U[1], CH_V0, CH_V1, TOWER_Z[0] - 1.0, TOWER_Z[1] + 1.0) - bore_mouths()
  pv, pz = PUSH_VZ
  hole = cyl_x(M5_HOLE / 2, CH_U[1] - 1.0, TOWER_U[1] + 1.0, y=pv, z=pz, segments=32).rotate((0.0, 0.0, THETA))
  tw = NUT_TRAP[0]
  slot = uvz(PUSH_NUT_U[0], PUSH_NUT_U[1], pv - tw / 2, pv + tw / 2, pz - tw / 2 / math.cos(math.radians(30)),
             TOWER_Z[1] + 1.0)
  return clean(m - hole - slot)""",
 """def groove() -> Manifold:
  \"\"\"v5: the slide's groove, along the column through the tower's outer wall, round-ended, on the bar's middle line.\"\"\"
  v = BAR_UV[1]
  r = SLOT_W / 2
  ends = [cyl_x(r, CH_U[1] - 1.0, TOWER_U[1] + 1.0, y=v, z=z, segments=32) for z in (GROOVE_Z[0] + r, GROOVE_Z[1] - r)]
  return Manifold.batch_hull(ends).rotate((0.0, 0.0, THETA))


def arm() -> Manifold:
  \"\"\"The arm and the tower at its end, one piece (printed flat, the tower standing up): the arm runs into the
  tower's foot (the hull of the arm's end and the tower, as thick as the arm) and, v5, a 50 mm deep block from just
  outside the receiver to the tower, so the arm doesn't twist; up the tower, a square tube the motor carrier's bar
  slides in (closed on all four sides), with the slide's groove up its outer wall.\"\"\"
  a = box(ARM_X[0], ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1])
  foot = Manifold.batch_hull([box(ARM_X[1] - 5.0, ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1]),
                              uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], ARM_Z[0], ARM_Z[1])])
  foot = foot ^ box(ARM_X[0], 400.0, -400.0, ARM_Y[1], ARM_Z[0] - 1.0, ARM_Z[1] + 1.0)   # no higher than the arm (v4: the
                                                 # tower's top corner now stands above it; slid in, it would meet the plate)
  z1 = ARM_Z[0] + DEEP
  deep = Manifold.batch_hull([box(DEEP_X0, ARM_X[1], ARM_Y[0], ARM_Y[1] - 1.0, ARM_Z[0], z1),
                              uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], ARM_Z[0], z1)])
  deep = deep ^ box(DEEP_X0, 400.0, -400.0, ARM_Y[1] - 1.0, ARM_Z[0] - 1.0, z1)    # 1 mm under the frame plate
  tower = uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], TOWER_Z[0], TOWER_Z[1])
  m = a + foot + deep + tower
  m = m - uvz(CH_U[0], CH_U[1], CH_V0, CH_V1, TOWER_Z[0] - 1.0, TOWER_Z[1] + 1.0) - bore_mouths()
  return clean(m - groove())"""),
("""  \"\"\"The motor carrier, one piece (printed on its side towards 5 o'clock): the bar that slides in the tower's tube,
  plain to its bottom end (v4: no lug) so it goes in from the tower's top; up its middle from that end, the hole for
  the M4 stop bolt and the slot its nut drops into, 4 mm in; at its top the web and the plate the motor bolts to
  (perpendicular to U, the motor's face against its outside; pads round the four M3 holes inside; the big hole a
  teardrop so it prints). dz: slid along the column from the nominal depth (+ towards you, deeper into the teeth).\"\"\"""",
 """  \"\"\"The motor carrier, one piece (printed on its side towards 5 o'clock): the bar that slides in the tower's tube,
  plain to its bottom end (no lug) so it goes in from the tower's top; across it, v5, the slide's wing bolt hole and
  the slot its M5 nut drops into (from the motor's side, flats along the bar so it can't turn), and the depth ticks on
  its outer face; at its top the web and the plate the motor bolts to (perpendicular to U, the motor's face against its
  outside; pads round the four M3 holes inside; the big hole a teardrop so it prints). dz: slid along the column from
  the nominal depth (+ towards you, deeper into the teeth).\"\"\""""),
("""  bu, bv = BAR_UV
  m = m - teardrop_z(M4_HOLE / 2, BAR_Z[0] - 1.0, BAR_Z[0] + M4_DEPTH, bu, bv)
  z0 = BAR_Z[0] + M4_SLOT_IN
  m = m - uvz(bu - M4_SLOT[0] / 2, bu + M4_SLOT[0] / 2, bv - M4_NUT_AF / 2 - 0.25, BAR_V[1] + 1.0, z0, z0 + M4_SLOT[1])
  return clean(m).translate((0.0, 0.0, dz))""",
 """  bu, bv = BAR_UV
  m = m - teardrop_x(M5_HOLE / 2, SLIDE_NUT_U[0] - 2.0, BAR_U[1] + 1.0, y=bv, z=SLIDE_Z0, flat=0.6).rotate((0.0, 0.0, THETA))
  tw, tt = NUT_TRAP                                             # 8.4 along the bar (the flats), 4.4 thick
  m = m - uvz(SLIDE_NUT_U[0], SLIDE_NUT_U[1], bv - M5_NUT_AF / 2 / math.cos(math.radians(30)) - 0.25, BAR_V[1] + 1.0,
              SLIDE_Z0 - tw / 2, SLIDE_Z0 + tw / 2)
  for d in TICK_DZ:                                             # the bar's point at the tower's top when slid d
    zt = TOWER_Z[1] - d
    w = 7.0 if d in TICK_LONG else 4.0
    m = m - uvz(BAR_U[1] - 0.6, BAR_U[1] + 1.0, bv - w, bv + w, zt - 0.4, zt + 0.4)
  return clean(m).translate((0.0, 0.0, dz))"""),
("""the plate standing up from it, the stop nut's slot open on top.\"\"\"""",
 """the plate standing up from it, the slide nut's slot open on top.\"\"\""""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import rightarm as RA
a = RA.arm(); c = RA.carrier()
print('arm', round(a.volume()/1000*1.28), 'g', [round(v,1) for v in a.bounding_box()], 'genus', a.genus())
print('carrier', round(c.volume()/1000*1.28), 'g', 'genus', c.genus())
print('groove z', RA.GROOVE_Z)"
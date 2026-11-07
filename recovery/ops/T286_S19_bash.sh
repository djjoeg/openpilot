cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "rightcheck.py"
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)

rep("""turned. Then the gear in mesh over the teeth's whole arc.
""", """turned, with each of the three teeth sets (11, 15 and 20; the 20 is the one on the car). Then the gear in mesh over
each set's whole arc.
""")
rep("""MESH_PHASE = 10.5   # the gear's turn on its shaft that puts it in step with the teeth (found by a search, 2 Nov 2026)
""", """MESH_PHASE = 10.5   # the gear's turn on its shaft that puts it in step with the teeth (found by a search, 2 Nov 2026;
                    # every set has a tooth in its middle, so the same phase fits all three)
TEETH_SETS = ((18, "20"), (14, "15"), (10, "11"))   # MidTeeth's n_teeth and the set's name; the 20 is the one fitted
""")
rep("""def teeth_piece() -> Manifold:
  return MT.mid_teeth(MT.MidTeeth(n_teeth=10))""", """def teeth_piece(n_teeth: int = 18) -> Manifold:
  return MT.mid_teeth(MT.MidTeeth(n_teeth=n_teeth))""")
rep("""  g, teeth = grip(), teeth_piece()
""", """  g = grip()
  pieces = {name: teeth_piece(n) for n, name in TEETH_SETS}
""")
rep("""  # 5. the steering wheel turned, the teeth piece where the stop puts the gear in mesh (s = how far nearer you the
  # teeth piece sits than drawn): nothing but the gear may touch the grip or the teeth piece; slid out 6 mm, not even
  # the gear
  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_P - s
    mv = moving(s)
    near = {"carrier": mv["carrier"], "motor": mv["motor"], "board": mv["board"], **fixed}
    hw = {k: v for k, v in hardware(s, p, True).items() if "nut" not in k}
    out = RA.motor_and_gear(s - 6.0)["gear"]
    for a in range(-40, 41, 5):
      t = teeth.rotate((0.0, 0.0, RA.THETA + a)).translate((0.0, 0.0, s))
      gr = g.translate((0.0, 0.0, s))
      for n, m in {**near, **hw}.items():
        check(f"teeth {s:+.0f} mm, wheel {a:+d} deg: {n} / teeth piece", m, t)
        check(f"teeth {s:+.0f} mm, wheel {a:+d} deg: {n} / grip", m, gr)
      check(f"teeth {s:+.0f} mm, wheel {a:+d} deg: gear slid out 6 mm / teeth piece", out, t)

  # 6. the gear in mesh at the nominal depth, phased, over the teeth's whole arc (the 11 teeth)
  g0 = S.side_gear_teeth_only()
  t = MT.MidTeeth(n_teeth=10)
  c = RA.R_FACE_OUT * RA.U
  mat = [[0.0, RA.V[0], -RA.U[0], float(c[0])], [0.0, RA.V[1], -RA.U[1], float(c[1])], [1.0, 0.0, 0.0, RA.Z_AXIS]]
  w = -t.teeth_half
  while w <= t.teeth_half + 1e-9:
    gm = g0.rotate((0.0, 0.0, MESH_PHASE + S.FP.FACE_RATIO * w)).transform(mat)
    check(f"gear in mesh, wheel {w:+.1f} deg / teeth", gm, teeth.rotate((0.0, 0.0, RA.THETA + w)), tol=1e-3)
    w += 0.5
""", """  # 5. the steering wheel turned, the teeth piece where the stop puts the gear in mesh (s = how far nearer you the
  # teeth piece sits than drawn): nothing but the gear may touch the grip or the teeth piece; slid out 6 mm, not even
  # the gear. Every teeth set; the grip once
  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_P - s
    mv = moving(s)
    near = {"carrier": mv["carrier"], "motor": mv["motor"], "board": mv["board"], **fixed}
    hw = {k: v for k, v in hardware(s, p, True).items() if "nut" not in k}
    out = RA.motor_and_gear(s - 6.0)["gear"]
    for a in range(-40, 41, 5):
      gr = g.translate((0.0, 0.0, s))
      for n, m in {**near, **hw}.items():
        check(f"teeth {s:+.0f} mm, wheel {a:+d} deg: {n} / grip", m, gr)
      for name, piece in pieces.items():
        t = piece.rotate((0.0, 0.0, RA.THETA + a)).translate((0.0, 0.0, s))
        for n, m in {**near, **hw}.items():
          check(f"teeth {name} {s:+.0f} mm, wheel {a:+d} deg: {n} / teeth piece", m, t)
        check(f"teeth {name} {s:+.0f} mm, wheel {a:+d} deg: gear slid out 6 mm / teeth piece", out, t)

  # 6. the gear in mesh at the nominal depth, phased, over each set's whole arc
  g0 = S.side_gear_teeth_only()
  c = RA.R_FACE_OUT * RA.U
  mat = [[0.0, RA.V[0], -RA.U[0], float(c[0])], [0.0, RA.V[1], -RA.U[1], float(c[1])], [1.0, 0.0, 0.0, RA.Z_AXIS]]
  for n_teeth, name in TEETH_SETS:
    t = MT.MidTeeth(n_teeth=n_teeth)
    w = -t.teeth_half
    while w <= t.teeth_half + 1e-9:
      gm = g0.rotate((0.0, 0.0, MESH_PHASE + S.FP.FACE_RATIO * w)).transform(mat)
      check(f"gear in mesh with the {name}, wheel {w:+.1f} deg / teeth", gm, pieces[name].rotate((0.0, 0.0, RA.THETA + w)), tol=1e-3)
      w += 0.5
""")
open(p, "w").write(s)
print("ok")
EOF
(time PYTHONPATH=/home/claude/pylib python3 rightcheck.py) > /home/claude/build/logs/rightcheck_v3.log 2>&1; head -40 /home/claude/build/logs/rightcheck_v3.log; tail -4 /home/claude/build/logs/rightcheck_v3.log
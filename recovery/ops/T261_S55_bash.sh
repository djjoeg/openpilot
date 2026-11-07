python3 - <<'EOF'
p = "rightcheck.py"
s = open(p).read()
a = '''  bad = [r for r in results if not r[0]]'''
b = '''  # 5. the gear in mesh at the nominal depth, phased, over the teeth's whole arc (the 11 teeth)
  g0 = S.side_gear_teeth_only()
  t = MT.MidTeeth(n_teeth=10)
  c = RA.R_FACE_OUT * RA.U
  mat = [[0.0, RA.V[0], -RA.U[0], float(c[0])], [0.0, RA.V[1], -RA.U[1], float(c[1])], [1.0, 0.0, 0.0, RA.Z_AXIS]]
  w = -t.teeth_half
  while w <= t.teeth_half + 1e-9:
    g = g0.rotate((0.0, 0.0, MESH_PHASE + S.FP.FACE_RATIO * w)).transform(mat)
    check(f"gear in mesh, wheel {w:+.1f} deg / teeth", g, teeth.rotate((0.0, 0.0, RA.THETA + w)), tol=1e-3)
    w += 0.5

  bad = [r for r in results if not r[0]]'''
assert s.count(a) == 1
s = s.replace(a, b)
s = s.replace('''TOL = 0.5    # mm^3: overlaps below this are touching faces''',
              '''TOL = 0.5    # mm^3: overlaps below this are touching faces
MESH_PHASE = 10.5   # the gear's turn on its shaft that puts it in step with the teeth (found by a search, 2 Nov 2026)''')
open(p, "w").write(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib timeout 3600 python3 rightcheck.py 2>&1 | tail -3
PYTHONPATH=/home/claude/pylib timeout 1800 python3 -c "
import rightarm as RA
info = RA.build()
for k, v in info.items(): print(k, v)
for n, fname, plate_name, rows, size in RA.bambu_plates(): print(fname, round(size/1e3), 'kB')
"; ls -la ../stl/right-arm/ ../plates/plate-1[12]*
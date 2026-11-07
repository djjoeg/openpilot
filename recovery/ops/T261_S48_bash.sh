python3 - <<'EOF'
p = "rightarm.py"
s = open(p).read()
def rep(a, b):
  global s
  assert s.count(a) == 1, (a[:90], s.count(a))
  s = s.replace(a, b)
rep('''  parts = {"right-arm": ("arm", 1, P.SOLID), "right-bar": ("bar", 1, P.SOLID), "right-bracket": ("bracket", 1, P.SOLID)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-12-right-arm", "12 right arm", list(parts), "Plate 12: the right arm mount: arm, bar, bracket")])''',
'''  parts = {"right-arm": ("arm", 1, P.SOLID), "right-bar": ("bar", 1, P.SOLID), "right-bracket": ("bracket", 1, P.SOLID),
           "right-carrier": ("motor carrier", 1, P.SOLID)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-12-right-arm", "12 right arm v2", list(parts),
                              "Plate 12: the right arm mount v2: arm, bar, bracket, motor carrier")])''')
rep('''  return [(sc.column_cover(back=130.0), car), (grip, car), (teeth, orange), (mg["gear"], orange), (mg["motor"], dark),
          (mg["board"], dark), (plate_to_wheel(frame_plate_v4()), plate), (arm(), app), (bar(), app), (bracket(), app)]''',
'''  return [(sc.column_cover(back=130.0), car), (grip, car), (teeth, orange), (mg["gear"], orange), (mg["motor"], dark),
          (mg["board"], dark), (plate_to_wheel(frame_plate_v4()), plate), (arm(), app), (bar(), app), (bracket(), app),
          (carrier(), app)]''')
rep('''           ([(bed["right-bracket"], blue)], R.view_matrix(-50, 35))]''',
'''           ([(bed["right-bracket"], blue)], R.view_matrix(-50, 35)), ([(bed["right-carrier"], blue)], R.view_matrix(-50, 35))]''')
rep('''                 "arm, as printed", "bar, as printed", "bracket, as printed"],''',
'''                 "arm, as printed", "bar, as printed", "bracket, as printed", "motor carrier, as printed"],''')
open(p, "w").write(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
import rightarm as RA
for name, f in (("bar", RA.bar), ("bracket", RA.bracket), ("carrier", RA.carrier)):
  m = f()
  print(name, "volume", round(m.volume()), "genus", m.genus(), "bbox", [round(v,1) for v in m.bounding_box()])
for stem, m in RA.parts_on_bed().items():
  bb = m.bounding_box(); print(stem, [round(bb[i+3]-bb[i],1) for i in range(3)], "g", round(m.volume()/1000*1.27))
EOF
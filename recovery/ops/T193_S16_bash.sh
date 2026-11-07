python3 - <<'EOF'
p = 'plates.py'
s = open(p).read()
s = s.replace('''def build(out_dir=OUT_DIR, stl_dir=STL_DIR):
  os.makedirs(out_dir, exist_ok=True)
  meshes = {stem: read_stl(os.path.join(stl_dir, stem + ".stl")) for stem in PARTS}
  report = []
  for n, (fname, plate_name, stems) in enumerate(PLATES, start=1):
    placed = layout(stems, meshes)
    check_layout(placed)
    pieces, labels = [], []
    for stem, k, x0, y0, rot, w, h in placed:
      verts, tris = meshes[stem]
      label, count, settings = PARTS[stem]
      name = stem if count == 1 else f"{stem} {k + 1} of {count}"
      pieces.append((name, place(verts, x0, y0, rot), tris, settings))
      labels.append(label if count == 1 else f"{label} {k + 1}")
    title = f"Plate {n} of {len(PLATES)}: {plate_name.split(' ', 3)[3]}"''',
'''def build(out_dir=OUT_DIR, stl_dir=STL_DIR, parts=None, plate_list=None):
  """parts: stem -> (label, count, settings); plate_list: (file name, plate name, stems[, title]) per plate."""
  parts = parts or PARTS
  plate_list = plate_list or PLATES
  os.makedirs(out_dir, exist_ok=True)
  meshes = {stem: read_stl(os.path.join(stl_dir, stem + ".stl")) for stem in parts}
  report = []
  for n, entry in enumerate(plate_list, start=1):
    fname, plate_name, stems = entry[:3]
    placed = layout(stems, meshes, parts)
    check_layout(placed)
    pieces, labels = [], []
    for stem, k, x0, y0, rot, w, h in placed:
      verts, tris = meshes[stem]
      label, count, settings = parts[stem]
      name = stem if count == 1 else f"{stem} {k + 1} of {count}"
      pieces.append((name, place(verts, x0, y0, rot), tris, settings))
      labels.append(label if count == 1 else f"{label} {k + 1}")
    title = entry[3] if len(entry) > 3 else f"Plate {n} of {len(plate_list)}: {plate_name.split(' ', 3)[3]}"''')
s = s.replace('''    rows = [(PARTS[s][0] + ("" if PARTS[s][1] == 1 else f" {k + 1}"), x0, y0, rot, w, h) for s, k, x0, y0, rot, w, h in placed]''',
              '''    rows = [(parts[s][0] + ("" if parts[s][1] == 1 else f" {k + 1}"), x0, y0, rot, w, h) for s, k, x0, y0, rot, w, h in placed]''')
s = s.replace('''def layout(plate_parts, meshes):
  """Where each piece goes on the bed: list of (stem, copy index, x0, y0, rotated, w, h). The group is centred
  on the bed, which is where Bambu Studio puts it anyway, with the front-left corner kept clear."""
  items = []
  for stem in plate_parts:
    for k in range(PARTS[stem][1]):''',
'''def layout(plate_parts, meshes, parts=None):
  """Where each piece goes on the bed: list of (stem, copy index, x0, y0, rotated, w, h). The group is centred
  on the bed, which is where Bambu Studio puts it anyway, with the front-left corner kept clear."""
  parts = parts or PARTS
  items = []
  for stem in plate_parts:
    for k in range(parts[stem][1]):''')
open(p, 'w').write(s)
print('ok')
EOF
grep -n "SOLID_COLOR if s is SOLID" plates.py | head -3
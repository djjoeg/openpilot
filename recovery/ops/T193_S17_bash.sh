python3 - <<'EOF'
p = 'measureplate.py'
s = open(p).read()
s = s.replace('''def main():
  info = build()
  for name, v in info.items():
    print(f"{name}: {v['size_mm'][0]} x {v['size_mm'][1]} x {v['size_mm'][2]} mm, {v['grams_solid']:.0f} g solid")
  n = sum(1 for x in range(10, 100, 10) for y in range(10, 120, 10) if hole_ok(x, y))
  print(f"grid holes: {n}")''',
'''def bambu_plate() -> list:
  """The plate and three bars on one Bambu Studio plate (plates.py), as ../plates/plate-0-measuring-plate.3mf."""
  import plates as P
  parts = {"column-measuring-plate": ("measuring plate", 1, P.STANDARD), "column-measuring-bar": ("bar", BAR_COUNT, P.STANDARD)}
  plate_list = [("plate-0-measuring-plate", "0 measuring plate", list(parts), "Plate 0: the measuring plate, with its bars")]
  return P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts, plate_list=plate_list)


def main():
  info = build()
  for name, v in info.items():
    print(f"{name}: {v['size_mm'][0]} x {v['size_mm'][1]} x {v['size_mm'][2]} mm, {v['grams_solid']:.0f} g solid")
  n = sum(1 for x in range(10, 100, 10) for y in range(10, 120, 10) if hole_ok(x, y))
  print(f"grid holes: {n}")
  for n, fname, plate_name, rows, size in bambu_plate():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB): " + ", ".join(f"{label} at x {x0:.0f}..{x0 + w:.0f} y {y0:.0f}..{y0 + h:.0f}"
                                                            for label, x0, y0, rot, w, h in rows))''')
open(p, 'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 measureplate.py 2>&1 | tail -5; ls -la ../plates/ | grep measuring; /home/claude/bin/ruff check --output-format concise --line-length 140 measureplate.py plates.py; echo "ruff $?"
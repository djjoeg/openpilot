python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
for old, new in [
  ("PL_MAIN_X = (16.0, 66.0)      # the plate's main part across, right of the adjustment tab (and room for your fingers)",
   "PL_MAIN_X = (16.0, 70.0)      # the plate's main part across, right of the adjustment tab (and room for your fingers)"),
  ('''  return [(PL_MAIN_X[1] - 8.0, y_lo), (max(xs) + FLANGE_PAD + 2.0, y_lo), (max(xs) + FLANGE_PAD + 2.0, max(ys) + SLOT_Y + FLANGE_PAD),
          (PL_MAIN_X[1] - 8.0, max(ys) + SLOT_Y + FLANGE_PAD)]''',
   '''  x_lo = min(min(xs) - FLANGE_PAD, PL_MAIN_X[1] - 8.0)
  return [(x_lo, y_lo), (max(xs) + FLANGE_PAD + 2.0, y_lo), (max(xs) + FLANGE_PAD + 2.0, max(ys) + SLOT_Y + FLANGE_PAD),
          (x_lo, max(ys) + SLOT_Y + FLANGE_PAD)]'''),
]:
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
p.write_text(s)
print("ok")
EOF
sed -n 200,358p popassembly.py
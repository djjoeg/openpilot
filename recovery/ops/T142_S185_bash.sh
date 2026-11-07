python3 - <<'EOF'
import pathlib
p = pathlib.Path("popassembly.py")
s = p.read_text()
start = s.index("def tab_placements(screws=None, plate_dxz=(0.0, 0.0)) -> list:")
end = s.index("def tab_fit_study(")
new = '''def tab_placements(screws=None, plate_dxz=(0.0, 0.0)) -> list:
  """For each usable cover screw: (name, R, T, bolt (x, z), slot index, kind), the plate shifted by plate_dxz. Each
  tab's bolt goes as near its slot's middle as it can, the tabs kept clear of each other (tries the next best spots
  for the earlier tabs if a later one can't be placed)."""
  screws = screws if screws is not None else [(n, xz, kind) for n, xz, _, kind in COVER_SCREWS if kind]
  dx, dz = plate_dxz
  rels = [(xz[0] - dx, xz[1] - dz) for _, xz, _ in screws]       # in the plate's own frame

  def score(rel, o):
    i, b = o
    x0, z0, x1, z1 = PP.PL_SLOTS[i]
    mid = ((x0 + x1) / 2, (z0 + z1) / 2)
    return math.hypot(b[0] - mid[0], b[1] - mid[1]) + 0.2 * abs(math.hypot(b[0] - rel[0], b[1] - rel[1]) - 29.0)

  alone = [sorted(tab_options(rel, (), kind), key=lambda o, r=rel: score(r, o)) for rel, (_, _, kind) in zip(rels, screws)]

  def place(k, placed):
    if k == len(screws):
      return []
    for i, b in alone[k][::3] + alone[k][1::3] + alone[k][2::3]:
      if placed and not _tab_clear(rels[k], b, placed, PP.TAB_KINDS[screws[k][2]]["end_r"]):
        continue
      rest = place(k + 1, placed + [(rels[k], b)])
      if rest is not None:
        return [(i, b)] + rest
    return None

  chosen = place(0, [])
  if chosen is None:
    bad = next((screws[k][0] for k in range(len(screws)) if not alone[k]), screws[-1][0])
    raise ValueError(f"the tab for the {bad} can't reach a slot")
  out = []
  for (name, xz, kind), (i, b) in zip(screws, chosen):
    R, T, _ = PP.place_tab(xz, (b[0] + dx, b[1] + dz))
    out.append((name, R, T, (b[0] + dx, b[1] + dz), i, kind))
  return out


'''
s = s[:start] + new + s[end:]
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 -c "
import time; T0 = time.time()
import popassembly as PA
for r in PA.tab_placements(): print(r[0], tuple(round(float(v),1) for v in r[3]), r[4], r[5])
print(PA.tab_fit_study(n=5), round(time.time() - T0), 's')
"
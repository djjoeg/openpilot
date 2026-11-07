python3 - <<'EOF'
def edit(p, pairs):
    s = open(p).read()
    for old, new in pairs:
        assert s.count(old) == 1, (p, s.count(old), old[:70])
        s = s.replace(old, new)
    open(p, "w").write(s)

edit("allinone.py", [
    ("""One print for everything the right-arm build needs (2 Nov 2026): the frame plate v4, the steering wheel teeth v2 (the
11 set: the same 11 teeth, 10.8 degrees each way, as the first print you held on the wheel), the arm and the motor
carrier, on one 256 x 256 mm bed,""",
     """One print for everything the right-arm build needs (2 Nov 2026): the frame plate v4, the steering wheel teeth v2 (the
20 set: 19 teeth, 19.5 degrees each way, the same teeth as the first print you held on the wheel), the arm and the
motor carrier, on one 256 x 256 mm bed,"""),
    ("""  "steering-wheel-teeth-v2-11-straight-roads": ("mid-teeth", "teeth v2, 11", P.STANDARD),""",
     """  "steering-wheel-teeth-v2-20-winding-roads": ("mid-teeth", "teeth v2, 20", P.STANDARD),"""),
    ("""TOP = P.BED[1] - P.EDGE          # the back edge's limit; y runs from the front of the bed
""", """TOP = P.BED[1] - P.EDGE          # the back edge's limit; y runs from the front of the bed
TEETH = "steering-wheel-teeth-v2-20-winding-roads"
"""),
    ('''  """Columns standing against the back edge, left to right: the frame plate (turned 90 degrees), the carrier, the
  teeth; the arm lies across in front of them, clear of the front-left nozzle-wipe corner. Returns (stem, x0, y0,
  turned, w, h) per piece."""
  out, x = [], P.EDGE
  for stem in stems:
    if stem == "right-arm":
      continue''', '''  """Columns standing against the back edge: the frame plate (turned 90 degrees) and the carrier from the left, the
  teeth (the longest) at the right edge; the arm lies across in front of the left columns, clear of the front-left
  nozzle-wipe corner. Returns (stem, x0, y0, turned, w, h) per piece."""
  out, x = [], P.EDGE
  for stem in stems:
    if stem in ("right-arm", TEETH):
      continue'''),
    ('''  if "right-arm" in stems:
    w, h = P.footprint(meshes["right-arm"][0])
    lowest = min((y0 for _, _, y0, _, _, _ in out), default=TOP)
    assert P.EDGE + h + P.GAP <= lowest + 1e-6, "the arm does not fit in front of the columns"
    x_right = max((x0 + ww for _, x0, _, _, ww, _ in out), default=P.BED[0] - P.EDGE)
    x0 = max(P.NO_GO[0] + P.GAP, x_right - w)
    out.append(("right-arm", x0, P.EDGE, False, w, h))
  return out''', '''  if TEETH in stems:
    w, h = P.footprint(meshes[TEETH][0])
    turned = w > h
    if turned:
      w, h = h, w
    out.append((TEETH, P.BED[0] - P.EDGE - w, TOP - h, turned, w, h))
  if "right-arm" in stems:
    w, h = P.footprint(meshes["right-arm"][0])
    out.append(("right-arm", P.NO_GO[0] + P.GAP, P.EDGE, False, w, h))     # check_layout catches any overlap
  return out'''),
])
edit("visuals.py", [
    ("  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0.0, 0.0, RA.THETA))",
     "  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=18)).rotate((0.0, 0.0, RA.THETA))      # the 20 set, the one on the car"),
    ("  t = MT.MidTeeth(n_teeth=10)\n  m = MT.mid_teeth(t)", "  t = MT.MidTeeth(n_teeth=18)\n  m = MT.mid_teeth(t)"),
    ('suptitle=f"Teeth v2, 11 (straight roads), plate 7: {size_text(bed)},',
     'suptitle=f"Teeth v2, 20 (winding roads: 19 teeth, 19.5 degrees each way), plate 9: {size_text(bed)},'),
])
edit("rightarm.py", [
    ("  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0.0, 0.0, THETA))",
     "  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=18)).rotate((0.0, 0.0, THETA))    # the 20 set, the one on the car"),
])
print("ok")
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 allinone.py && /home/claude/bin/ruff check allinone.py visuals.py rightarm.py rightcheck.py
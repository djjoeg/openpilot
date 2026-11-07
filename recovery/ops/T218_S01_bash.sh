python3 - <<'EOF'
p='midteeth.py'; s=open(p).read()
s=s.replace('''def on_bed(m: Manifold) -> Manifold:''','''FIT_SPAN_DEG = 6.0        # the fit test piece: this far each side of the middle (35 mm along the grip)
FIT_PULLS = (0.0, 3.0, 6.0)   # three of them, the inner wall pulled out this much, the number cut into the outer wall


def mark_text(t: MidTeeth, text: str, deg0: float = 0.0) -> Manifold:
  """S.number_mark with any text, centred on deg0."""
  w = math.degrees(S.MARK_PX / t.w_out)
  cuts = []
  a = deg0 + (4 * len(text) - 1) * w / 2
  for ch in text:
    px = S.DIGITS[ch]
    for row in range(5):
      for col in range(3):
        if px[row * 3 + col] == "1":
          a1 = a - col * w
          z1 = S.MARK_Z0 + (5 - row) * S.MARK_PX
          cuts.append(FP.polar_box(t.w_out - S.MARK_DEPTH, t.w_out + 1.0, a1 - w, a1, z1 - S.MARK_PX, z1, step_deg=0.3))
    a -= 4 * w
  return union(cuts)


def fit_test(pull: float, span_deg: float = FIT_SPAN_DEG) -> Manifold:
  """A short piece of the middle section, the channel exactly as the real piece (no tooth spaces cut), with the tie
  slot: to try on the grip for width before printing the whole thing."""
  from cadlib import revolve
  t = MidTeeth(n_teeth=10, inner_pull=pull)
  body = revolve(t.profile(), -span_deg, span_deg, step_deg=0.25)
  body = body - FP.tip_chamfers(t, -span_deg - 1.0, span_deg + 1.0) - PP.inner_chamfer(t)
  return clean(body - wide_tie_path(t, TIE_SLOT_W) - mark_text(t, str(int(round(pull)))))


def build_fit_tests(out_dir: str = STL_DIR) -> dict:
  from cadlib import write_stl
  os.makedirs(out_dir, exist_ok=True)
  info = {}
  for pull in FIT_PULLS:
    m = on_bed(fit_test(pull))
    stem = f"teeth-fit-test-pull-{int(round(pull))}"
    write_stl(m, os.path.join(out_dir, stem + ".stl"), stem)
    bb = m.bounding_box()
    info[stem] = {"pull": pull, "size_mm": [round(bb[i + 3] - bb[i], 1) for i in range(3)], "grams_solid": round(m.volume() / 1000 * 1.28)}
  return info


def on_bed(m: Manifold) -> Manifold:''')
s=s.replace('''def main(argv):
  pull = float(argv[1]) if len(argv) > 1 else INNER_PULL''','''def fit_test_plate() -> list:
  import plates as P
  parts = {f"teeth-fit-test-pull-{int(round(p))}": (f"fit test, inner wall pulled {int(round(p))} mm", 1, P.STANDARD) for p in FIT_PULLS}
  plate_list = [("plate-10-teeth-fit-test", "10 teeth fit test", list(parts), "Plate 10: three short pieces of the teeth channel, the inner wall pulled 0, 3 and 6 mm")]
  return P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts, plate_list=plate_list)


def main(argv):
  pull = float(argv[1]) if len(argv) > 1 else INNER_PULL
  for stem, i in build_fit_tests().items():
    print(f"{stem}: {i['size_mm']} mm, about {i['grams_solid']} g solid")
  for n, fname, plate_name, rows, size in fit_test_plate():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")''')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 600 python3 -c "
import sys; sys.path.insert(0,'.')
import midteeth as MT
for stem,i in MT.build_fit_tests().items(): print(stem, i)
for r in MT.fit_test_plate(): print(r[1], r[4])
"
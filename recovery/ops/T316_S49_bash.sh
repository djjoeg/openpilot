python3 - <<'EOF'
p='midteeth.py'; s=open(p).read()
rep = [
('''Everything else (teeth, ramps, the pointed inner ends, the set number) is the side-slide piece's.

  python3 midteeth.py [INNER_PULL_MM]   # writes ../stl/mid-teeth/*.stl and ../plates/plate-7-teeth-v2-*.3mf
"""''',
'''Everything else (teeth, the pointed inner ends, the set number) is the side-slide piece's.

Third cut (3 Nov 2026, v3, from the second print held on the wheel):
  - the channel 1 mm wider: the inner wall pulled out 7 mm (8 was a little tight on the grip, 6 was 1 to 3 mm loose);
  - the ends cut back to END_PAST_DEG past the middle of the last tooth space: the old roller's flat band and the ramps
    beyond the teeth are gone. They ran over the spokes' joins, which come round the back of the grip, so the ends
    stood off it. Measured on photos of the same wheel (3 Nov): the gap between the joins runs from about 6 to 46
    degrees below 3 o'clock, so the 20 set (39 degrees of teeth) just fits, with the gear at its middle (rightarm.THETA).
  - fit_sample: a short, cheap piece of the channel alone, to try the width on the grip first.

  python3 midteeth.py [INNER_PULL_MM]   # writes ../stl/mid-teeth/*.stl, ../plates/plate-7/8/9-teeth-v3-*.3mf and
                                        # plate-14-teeth-fit-sample.3mf
"""'''),
('''MID_DEG = 8.0          # the inner wall runs this far each side of the middle (8 degrees is 23.5 mm along the grip)
TIE_SLOT_W = 12.0      # the one tie slot, across (two 4.8 mm ties or one 7.6 mm tie)
INNER_PULL = 8.0       # mm the inner wall moves out towards the grip (fit test 1 Nov 2026: 6 was still 1 to 3 mm loose)
SETS = ((10, "11-straight-roads"), (14, "15-highway"), (18, "20-winding-roads"))''',
'''MID_DEG = 8.0          # the inner wall runs this far each side of the middle (8 degrees is 23.5 mm along the grip)
TIE_SLOT_W = 12.0      # the one tie slot, across (two 4.8 mm ties or one 7.6 mm tie)
INNER_PULL = 7.0       # mm the inner wall moves out towards the grip (fit test 1 Nov 2026: 6 was still 1 to 3 mm loose;
                       # the v2 print at 8 was a little tight on the grip, 3 Nov)
END_PAST_DEG = 0.6     # v3: the piece ends this far past the middle of the last tooth space (1.75 mm at the teeth)
SETS = ((10, "11-straight-roads"), (14, "15-highway"), (18, "20-winding-roads"))
VERSION = "v3"'''),
('''class MidTeeth(S.SideTeeth):
  """The side-slide teeth piece, its length from its own teeth, its inner wall pulled out INNER_PULL."""

  def __init__(self, n_teeth: int = FP.N_TEETH_SHORT, inner_pull: float = INNER_PULL, **kw):
    super().__init__(n_teeth=n_teeth, **kw)
    self.roll_half = n_teeth / 2 * self.pitch_deg + FP.ROLL_PAST_TEETH
    self.lead_end = self.roll_half + FP.END_LEAD_IN
    self.half = self.lead_end + self.chamfer_deg
    self.inner_pull = inner_pull
    self.w_in = self.w_in + inner_pull''',
'''class MidTeeth(S.SideTeeth):
  """The side-slide teeth piece, its length from its own teeth, its inner wall pulled out INNER_PULL. short_ends (v3):
  it ends END_PAST_DEG past the middle of the last tooth space, with no band or ramps beyond the teeth."""

  def __init__(self, n_teeth: int = FP.N_TEETH_SHORT, inner_pull: float = INNER_PULL, short_ends: bool = True, **kw):
    super().__init__(n_teeth=n_teeth, **kw)
    self.short_ends = short_ends
    if short_ends:
      self.roll_half = self.lead_end = n_teeth / 2 * self.pitch_deg
      self.half = self.roll_half + END_PAST_DEG
    else:
      self.roll_half = n_teeth / 2 * self.pitch_deg + FP.ROLL_PAST_TEETH
      self.lead_end = self.roll_half + FP.END_LEAD_IN
      self.half = self.lead_end + self.chamfer_deg
    self.inner_pull = inner_pull
    self.w_in = self.w_in + inner_pull'''),
('''  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \\
    PP.inner_chamfer(t) - SP.slide_ramps(t) - ends_cut(t) - FP.centre_mark(t) - S.face_roofs(t) - band_cut(t)
  return clean(body)''',
'''  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \\
    PP.inner_chamfer(t) - ends_cut(t) - FP.centre_mark(t) - S.face_roofs(t) - band_cut(t)
  if not t.short_ends:
    body = body - SP.slide_ramps(t)
  return clean(body)'''),
('''def build_fit_tests(out_dir: str = STL_DIR) -> dict:''',
'''SAMPLE_PULL = 7.0
SAMPLE_SPAN_DEG = 3.5      # the fit sample: this far each side of the middle (about 20 mm along the grip)
SAMPLE_BACK = 3.0          # its back, behind the channel (the teeth's standoff left off)


def fit_sample(pull: float = SAMPLE_PULL, span_deg: float = SAMPLE_SPAN_DEG) -> Manifold:
  """The cheapest try of the channel's width: a short piece of the middle section, exactly as the real piece where
  it touches the grip (both walls, the inner wall's lip, the back's inside), but only SAMPLE_BACK behind the channel
  (no teeth) and no tie slot. The pull is cut into the outer wall."""
  from cadlib import box, revolve
  t = MidTeeth(n_teeth=10, inner_pull=pull)
  body = revolve(t.profile(), -span_deg, span_deg, step_deg=0.25)
  body = body - PP.inner_chamfer(t)
  body = body ^ box(0.0, 300.0, -300.0, 300.0, t.z_bridge - SAMPLE_BACK, 50.0)
  return clean(body - mark_text(t, str(round(pull))))


def build_fit_tests(out_dir: str = STL_DIR) -> dict:'''),
('''def build(inner_pull: float = INNER_PULL, out_dir: str = STL_DIR) -> dict:
  from cadlib import write_stl
  os.makedirs(out_dir, exist_ok=True)
  info = {}
  for n, label in SETS:
    t = MidTeeth(n_teeth=n, inner_pull=inner_pull)
    m = on_bed(mid_teeth(t))
    stem = f"steering-wheel-teeth-v2-{label}"''',
'''def build_sample(out_dir: str = STL_DIR) -> dict:
  from cadlib import write_stl
  os.makedirs(out_dir, exist_ok=True)
  m = on_bed(fit_sample())
  stem = f"teeth-fit-sample-pull-{round(SAMPLE_PULL)}"
  write_stl(m, os.path.join(out_dir, stem + ".stl"), stem)
  bb = m.bounding_box()
  return {stem: {"size_mm": [round(bb[i + 3] - bb[i], 1) for i in range(3)], "grams_solid": round(m.volume() / 1000 * 1.28, 1)}}


def build(inner_pull: float = INNER_PULL, out_dir: str = STL_DIR) -> dict:
  from cadlib import write_stl
  os.makedirs(out_dir, exist_ok=True)
  for stale in os.listdir(out_dir):                 # v2's pieces, superseded
    if stale.startswith("steering-wheel-teeth-v2-"):
      os.remove(os.path.join(out_dir, stale))
  info = {}
  for n, label in SETS:
    t = MidTeeth(n_teeth=n, inner_pull=inner_pull)
    m = on_bed(mid_teeth(t))
    stem = f"steering-wheel-teeth-{VERSION}-{label}"'''),
('''def bambu_plates() -> list:
  import plates as P
  out = []
  for k, (n, label) in enumerate(SETS, start=7):
    stem = f"steering-wheel-teeth-v2-{label}"
    parts = {stem: (f"teeth v2, {label.replace('-', ' ')}", 1, P.STANDARD)}
    plate_list = [(f"plate-{k}-teeth-v2-{label}", f"{k} teeth v2 {label.split('-')[0]}", [stem],
                   f"Plate {k}: steering wheel teeth v2, {label.replace('-', ' ')}")]
    out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts, plate_list=plate_list)
  return out''',
'''def bambu_plates() -> list:
  import plates as P
  plates_dir = os.path.join(HERE, "..", "plates")
  for stale in os.listdir(plates_dir):              # v2's plates, superseded
    if "-teeth-v2-" in stale:
      os.remove(os.path.join(plates_dir, stale))
  out = []
  for k, (n, label) in enumerate(SETS, start=7):
    stem = f"steering-wheel-teeth-{VERSION}-{label}"
    parts = {stem: (f"teeth {VERSION}, {label.replace('-', ' ')}", 1, P.STANDARD)}
    plate_list = [(f"plate-{k}-teeth-{VERSION}-{label}", f"{k} teeth {VERSION} {label.split('-')[0]}", [stem],
                   f"Plate {k}: steering wheel teeth {VERSION}, {label.replace('-', ' ')}")]
    out += P.build(out_dir=plates_dir, stl_dir=STL_DIR, parts=parts, plate_list=plate_list)
  return out


ECONOMY = None   # set in sample_plate: 2 walls, 3 top and bottom layers, 15% infill


def sample_plate() -> list:
  import plates as P
  economy = {**P.STANDARD, "wall_loops": "2", "top_shell_layers": "3", "bottom_shell_layers": "3",
             "sparse_infill_density": "15%"}
  stem = f"teeth-fit-sample-pull-{round(SAMPLE_PULL)}"
  parts = {stem: (f"fit sample, inner wall pulled {round(SAMPLE_PULL)} mm", 1, economy)}
  plate_list = [("plate-14-teeth-fit-sample", "14 teeth fit sample", [stem],
                 f"Plate 14: a short piece of the teeth channel, the inner wall pulled {round(SAMPLE_PULL)} mm, to try on the grip")]
  return P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts, plate_list=plate_list)'''),
('''def main(argv):
  pull = float(argv[1]) if len(argv) > 1 else INNER_PULL
  for stem, i in build_fit_tests().items():
    print(f"{stem}: {i['size_mm']} mm, about {i['grams_solid']} g solid")
  for n, fname, plate_name, rows, size in fit_test_plate():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")''',
'''def main(argv):
  pull = float(argv[1]) if len(argv) > 1 else INNER_PULL
  for stem, i in build_sample().items():
    print(f"{stem}: {i['size_mm']} mm, about {i['grams_solid']} g solid")
  for n, fname, plate_name, rows, size in sample_plate():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")'''),
]
for a,b in rep:
  assert a in s, a[:70]
  s = s.replace(a,b)
s = s.replace('''ECONOMY = None   # set in sample_plate: 2 walls, 3 top and bottom layers, 15% infill


''', '')
open(p,'w').write(s)
EOF
grep -n "def main" -A 16 midteeth.py; ruff check midteeth.py --output-format concise
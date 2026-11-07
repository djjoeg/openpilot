"""
The steering wheel teeth, second cut (31 Oct 2026, from the first print held on the wheel):
  - the piece sits in the gap between the right spoke and the bottom spoke, so its ends are at the spokes' junctions
    where no zip tie can go round the grip. The inner wall (the "extra plastic" inside the grip) is therefore only in
    the middle, MID_DEG each side, and the ends are the bare back with the teeth and the outer wall;
  - one wide zip tie slot in the middle (two ordinary 4.8 mm ties side by side, or one 7.6 mm tie);
  - the inner wall can be pulled out (INNER_PULL) once you say how much too wide it is: measure, with the outer wall
    against the outside of the grip, the gap between the inner wall and the grip;
  - each set is only as long as its own teeth need (the old pieces kept the 14-tooth length for their end ties);
  - the rolling band outside the teeth (for the old roller) cut down level: the gear now comes in from outside.
Everything else (teeth, the pointed inner ends, the set number) is the side-slide piece's.

Third cut (3 Nov 2026, v3, from the second print held on the wheel):
  - the channel 1 mm wider: the inner wall pulled out 7 mm (8 was a little tight on the grip, 6 was 1 to 3 mm loose);
  - the ends cut back to END_PAST_DEG past the middle of the last tooth space: the old roller's flat band and the ramps
    beyond the teeth are gone. They ran over the spokes' joins, which come round the back of the grip, so the ends
    stood off it. Measured on photos of the same wheel (3 Nov): the gap between the joins runs from about 6 to 46
    degrees below 3 o'clock, so the 20 set (39 degrees of teeth) just fits, with the gear at its middle (rightarm.THETA).
  - fit_sample: a short, cheap piece of the channel alone, to try the width on the grip first.

  python3 midteeth.py [INNER_PULL_MM]   # writes ../stl/mid-teeth/*.stl, ../plates/plate-7/8/9-teeth-v3-*.3mf and
                                        # plate-14-teeth-fit-sample.3mf
"""
import math
import os
import sys

from manifold3d import CrossSection, Manifold

import faceparts as FP
import popparts as PP
import sideparts as S
import slideparts as SP
from cadlib import clean, union

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "..", "stl", "mid-teeth")

MID_DEG = 8.0          # the inner wall runs this far each side of the middle (8 degrees is 23.5 mm along the grip)
TIE_SLOT_W = 12.0      # the one tie slot, across (two 4.8 mm ties or one 7.6 mm tie)
INNER_PULL = 7.0       # mm the inner wall moves out towards the grip (fit test 1 Nov 2026: 6 was still 1 to 3 mm loose;
                       # the v2 print at 8 was a little tight on the grip, 3 Nov)
END_PAST_DEG = 0.6     # v3: the piece ends this far past the middle of the last tooth space (1.75 mm at the teeth)
SETS = ((10, "11-straight-roads"), (14, "15-highway"), (18, "20-winding-roads"))
VERSION = "v3"


class MidTeeth(S.SideTeeth):
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
    self.w_in = self.w_in + inner_pull

  def profile(self):
    """The side-slide profile with the inner wall (its inside, its 45 degree corner and its outside) moved out by
    inner_pull towards the grip's middle; the back between the corners is that much shorter."""
    rr, rho, c1, p = self.rr, self.rho, self.c1, self.inner_pull
    w_in, k_i = self.w_in, self.k_i + p          # w_in already includes the pull; the corner's outside line is r + z = k_i
    r0 = FP.FACE_BAND[0]
    z_corner_at_teeth = k_i - r0                 # where the corner's outside line passes the teeth's inner end
    inner_outside = [(r0, z_corner_at_teeth)] if z_corner_at_teeth > self.z_root else [(k_i - self.z_root, self.z_root)]
    return [
      (rr - rho + p, FP.FRONT_Z), (rr - rho + p, -c1), (rr - c1 + p, self.z_bridge), (rr + c1, self.z_bridge), (rr + rho, -c1),
      (rr + rho, FP.FRONT_Z), (self.w_out, FP.FRONT_Z), (self.w_out, self.w_out - self.k_o),
      (self.k_o + self.z_flat, self.z_flat), (FP.ROLL_BAND[1], self.z_flat), (FP.ROLL_BAND[1], self.z_band),
      (FP.ROLL_BAND[0], self.z_band), (FP.ROLL_BAND[0], self.z_root), (FP.FACE_BAND[1], self.z_root), (FP.FACE_BAND[1], self.z_tip),
      (r0, self.z_tip), (r0, self.z_root), *inner_outside,
      (w_in, k_i - w_in), (w_in, FP.FRONT_Z),
    ]


def ends_cut(t: MidTeeth) -> Manifold:
  """Cuts the inner wall and its corner away outside the middle section: the same cut as the spoke notch, over both
  ends, so only the back and the outer wall run to the ends."""
  return FP.polar_box(0.0, FP.NOTCH_R, -t.half - 1.0, -MID_DEG, -80.0, 20.0) + \
    FP.polar_box(0.0, FP.NOTCH_R, MID_DEG, t.half + 1.0, -80.0, 20.0)


def wide_tie_path(t: MidTeeth, width: float) -> Manifold:
  """FP.tie_path, but width wide across (FP.tie_path is FP.TIE_W)."""
  saved = FP.TIE_W
  try:
    FP.TIE_W = width
    return FP.tie_path(t)
  finally:
    FP.TIE_W = saved


def band_cut(t: MidTeeth) -> Manifold:
  """The rolling band (the ridge the old roller rode on, just outside the teeth) cut down level with the flat beside
  it: nothing rolls on it now, and the gear's outer teeth just touched it."""
  return FP.polar_box(FP.ROLL_BAND[0] - 0.3, FP.ROLL_BAND[1] + 0.5, -t.half - 1.0, t.half + 1.0, -80.0, t.z_flat)


def mid_solid(t: MidTeeth) -> Manifold:
  from cadlib import revolve
  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2
  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \
    PP.inner_chamfer(t) - ends_cut(t) - FP.centre_mark(t) - S.face_roofs(t) - band_cut(t)
  if not t.short_ends:
    body = body - SP.slide_ramps(t)
  return clean(body)


def mid_teeth(t: MidTeeth) -> Manifold:
  return clean(mid_solid(t) - wide_tie_path(t, TIE_SLOT_W) - S.number_mark(t))


FIT_SPAN_DEG = 6.0        # the fit test piece: this far each side of the middle (35 mm along the grip)
FIT_PULLS = (0.0, 3.0, 6.0)   # three of them, the inner wall pulled out this much, the number cut into the outer wall


def mark_text(t: MidTeeth, text: str, deg0: float = 0.0, z0: float = S.MARK_Z0) -> Manifold:
  """S.number_mark with any text, centred on deg0, its bottom row at z0."""
  w = math.degrees(S.MARK_PX / t.w_out)
  cuts = []
  a = deg0 + (4 * len(text) - 1) * w / 2
  for ch in text:
    px = S.DIGITS[ch]
    for row in range(5):
      for col in range(3):
        if px[row * 3 + col] == "1":
          a1 = a - col * w
          z1 = z0 + (5 - row) * S.MARK_PX
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


SAMPLE_PULL = 7.0
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
  return clean(body - mark_text(t, str(round(pull)), z0=-10.5))     # on the outer wall's flat outside


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


def on_bed(m: Manifold) -> Manifold:
  """As the side-slide pieces print: the front (grip) side down, the teeth up. The piece lies flat on the walls' front
  edges, which are at z = FRONT_Z; so flip it over."""
  from cadlib import on_bed as ob
  return ob(m, rotate=(180.0, 0.0, 0.0))


def build_sample(out_dir: str = STL_DIR) -> dict:
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
    stem = f"steering-wheel-teeth-{VERSION}-{label}"
    write_stl(m, os.path.join(out_dir, stem + ".stl"), stem)
    bb = m.bounding_box()
    info[stem] = {"teeth": n, "reach_deg": t.reach_deg, "size_mm": [round(bb[i + 3] - bb[i], 1) for i in range(3)],
                  "length_mm": round(2 * t.half / 360 * 2 * math.pi * t.w_out, 0), "grams_solid": round(m.volume() / 1000 * 1.28)}
  return info


def bambu_plates() -> list:
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


def sample_plate() -> list:
  import plates as P
  economy = {**P.STANDARD, "wall_loops": "2", "top_shell_layers": "3", "bottom_shell_layers": "3",
             "sparse_infill_density": "15%"}
  stem = f"teeth-fit-sample-pull-{round(SAMPLE_PULL)}"
  parts = {stem: (f"fit sample, inner wall pulled {round(SAMPLE_PULL)} mm", 1, economy)}
  plate_list = [("plate-14-teeth-fit-sample", "14 teeth fit sample", [stem],
                 f"Plate 14: teeth fit sample, the inner wall pulled {round(SAMPLE_PULL)} mm")]
  return P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts, plate_list=plate_list)


def fit_test_plate() -> list:
  import plates as P
  parts = {f"teeth-fit-test-pull-{int(round(p))}": (f"fit test, inner wall pulled {int(round(p))} mm", 1, P.STANDARD) for p in FIT_PULLS}
  plate_list = [("plate-10-teeth-fit-test", "10 teeth fit test", list(parts), "Plate 10: three short pieces of the teeth channel, the inner wall pulled 0, 3 and 6 mm")]
  return P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts, plate_list=plate_list)


def main(argv):
  pull = float(argv[1]) if len(argv) > 1 else INNER_PULL
  for stem, i in build_sample().items():
    print(f"{stem}: {i['size_mm']} mm, about {i['grams_solid']} g solid")
  for n, fname, plate_name, rows, size in sample_plate():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")
  for stem, i in build(pull).items():
    print(f"{stem}: {i['teeth']} teeth, {i['reach_deg']} deg each way, {i['size_mm']} mm, about {i['length_mm']:.0f} mm along the grip, "
          f"{i['grams_solid']} g solid; inner wall pulled out {pull} mm")
  for n, fname, plate_name, rows, size in bambu_plates():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")


if __name__ == "__main__":
  sys.exit(main(sys.argv))

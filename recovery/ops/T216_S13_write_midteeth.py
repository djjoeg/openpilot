"""
The steering wheel teeth, second cut (31 Oct 2026, from the first print held on the wheel):
  - the piece sits in the gap between the right spoke and the bottom spoke, so its ends are at the spokes' junctions
    where no zip tie can go round the grip. The inner wall (the "extra plastic" inside the grip) is therefore only in
    the middle, MID_DEG each side, and the ends are the bare back with the teeth and the outer wall;
  - one wide zip tie slot in the middle (two ordinary 4.8 mm ties side by side, or one 7.6 mm tie);
  - the inner wall can be pulled out (INNER_PULL) once you say how much too wide it is: measure, with the outer wall
    against the outside of the grip, the gap between the inner wall and the grip;
  - each set is only as long as its own teeth need (the old pieces kept the 14-tooth length for their end ties).
Everything else (teeth, ramps, the pointed inner ends, the set number) is the side-slide piece's.

  python3 midteeth.py [INNER_PULL_MM]   # writes ../stl/mid-teeth/*.stl and ../plates/plate-7-teeth-v2-*.3mf
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
INNER_PULL = 0.0       # mm the inner wall moves out towards the grip (0 until measured)
SETS = ((10, "11-straight-roads"), (14, "15-highway"), (18, "20-winding-roads"))


class MidTeeth(S.SideTeeth):
  """The side-slide teeth piece, its length from its own teeth, its inner wall pulled out INNER_PULL."""

  def __init__(self, n_teeth: int = FP.N_TEETH_SHORT, inner_pull: float = INNER_PULL, **kw):
    super().__init__(n_teeth=n_teeth, **kw)
    self.roll_half = n_teeth / 2 * self.pitch_deg + FP.ROLL_PAST_TEETH
    self.lead_end = self.roll_half + FP.END_LEAD_IN
    self.half = self.lead_end + self.chamfer_deg
    self.inner_pull = inner_pull
    self.w_in = self.w_in + inner_pull

  def profile(self):
    """The side-slide profile with the inner wall moved out by inner_pull (its 45 degree corner moves with it)."""
    rr, rho, c1, p = self.rr, self.rho, self.c1, self.inner_pull
    pts = super().profile()
    out = []
    for r, z in pts:
      if r <= rr - c1 + 1e-6 and r < FP.FACE_BAND[0] - 1.0:      # the inner wall, its corner and the back inside the teeth
        r = r + p if r < rr - c1 - 1e-6 else r
      out.append((r, z))
    # the inner corner's outside (k_i) and the wall's outside moved with it
    out = [(r, z) if not (abs(r - (self.k_i - p - self.z_root)) < 1e-6) else (r, z) for r, z in out]
    return out


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


def mid_solid(t: MidTeeth) -> Manifold:
  from cadlib import revolve
  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2
  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \
    PP.inner_chamfer(t) - SP.slide_ramps(t) - ends_cut(t) - FP.centre_mark(t) - S.face_roofs(t)
  return clean(body)


def mid_teeth(t: MidTeeth) -> Manifold:
  return clean(mid_solid(t) - wide_tie_path(t, TIE_SLOT_W) - S.number_mark(t))


def on_bed(m: Manifold) -> Manifold:
  """As the side-slide pieces print: the front (grip) side down, the teeth up. The piece lies flat on the walls' front
  edges, which are at z = FRONT_Z; so flip it over."""
  from cadlib import on_bed as ob
  return ob(m, rotate=(180.0, 0.0, 0.0))


def build(inner_pull: float = INNER_PULL, out_dir: str = STL_DIR) -> dict:
  from cadlib import write_stl
  os.makedirs(out_dir, exist_ok=True)
  info = {}
  for n, label in SETS:
    t = MidTeeth(n_teeth=n, inner_pull=inner_pull)
    m = on_bed(mid_teeth(t))
    stem = f"steering-wheel-teeth-v2-{label}"
    write_stl(m, os.path.join(out_dir, stem + ".stl"), stem)
    bb = m.bounding_box()
    info[stem] = {"teeth": n, "reach_deg": t.reach_deg, "size_mm": [round(bb[i + 3] - bb[i], 1) for i in range(3)],
                  "length_mm": round(2 * t.half / 360 * 2 * math.pi * t.w_out, 0), "grams_solid": round(m.volume() / 1000 * 1.28)}
  return info


def bambu_plates() -> list:
  import plates as P
  out = []
  for k, (n, label) in enumerate(SETS, start=7):
    stem = f"steering-wheel-teeth-v2-{label}"
    parts = {stem: (f"teeth v2, {label.replace('-', ' ')}", 1, P.STANDARD)}
    plate_list = [(f"plate-{k}-teeth-v2-{label}", f"{k} teeth v2 {label.split('-')[0]}", [stem],
                   f"Plate {k}: steering wheel teeth v2, {label.replace('-', ' ')}")]
    out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts, plate_list=plate_list)
  return out


def main(argv):
  pull = float(argv[1]) if len(argv) > 1 else INNER_PULL
  for stem, i in build(pull).items():
    print(f"{stem}: {i['teeth']} teeth, {i['reach_deg']} deg each way, {i['size_mm']} mm, about {i['length_mm']:.0f} mm along the grip, "
          f"{i['grams_solid']} g solid; inner wall pulled out {pull} mm")
  for n, fname, plate_name, rows, size in bambu_plates():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")


if __name__ == "__main__":
  sys.exit(main(sys.argv))

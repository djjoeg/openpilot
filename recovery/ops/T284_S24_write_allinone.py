"""
One print for everything the right-arm build needs (2 Nov 2026): the frame plate v4, the steering wheel teeth v2 (the
11 set: the same 11 teeth, 10.8 degrees each way, as the first print you held on the wheel), the arm and the motor
carrier, on one 256 x 256 mm bed, each piece with its own settings (the frame plate and the teeth 40% gyroid, the arm
and the carrier solid). Plate 13b is the same without the frame plate, for when that is already printed.

  python3 allinone.py    # writes ../plates/plate-13-all-in-one.3mf, plate-13b-all-but-the-frame-plate.3mf (+ .png)
"""
import os
import sys

import numpy as np

import plates as P

HERE = os.path.dirname(os.path.abspath(__file__))
STL_ROOT = os.path.join(HERE, "..", "stl")
OUT_DIR = os.path.join(HERE, "..", "plates")

# stem -> (folder, label, settings)
PIECES = {
  "column-frame-plate-v4": ("right-arm", "frame plate v4", P.STANDARD),
  "right-carrier": ("right-arm", "motor carrier", P.SOLID),
  "steering-wheel-teeth-v2-11-straight-roads": ("mid-teeth", "teeth v2, 11", P.STANDARD),
  "right-arm": ("right-arm", "arm", P.SOLID),
}
TOP = P.BED[1] - P.EDGE          # the back edge's limit; y runs from the front of the bed


def layout(stems, meshes) -> list:
  """Columns standing against the back edge, left to right: the frame plate (turned 90 degrees), the carrier, the
  teeth; the arm lies across in front of them, clear of the front-left nozzle-wipe corner. Returns (stem, x0, y0,
  turned, w, h) per piece."""
  out, x = [], P.EDGE
  for stem in stems:
    if stem == "right-arm":
      continue
    w, h = P.footprint(meshes[stem][0])
    turned = w > h
    if turned:
      w, h = h, w
    out.append((stem, x, TOP - h, turned, w, h))
    x += w + P.GAP
  if "right-arm" in stems:
    w, h = P.footprint(meshes["right-arm"][0])
    lowest = min((y0 for _, _, y0, _, _, _ in out), default=TOP)
    assert P.EDGE + h + P.GAP <= lowest + 1e-6, "the arm does not fit in front of the columns"
    x_right = max((x0 + ww for _, x0, _, _, ww, _ in out), default=P.BED[0] - P.EDGE)
    x0 = max(P.NO_GO[0] + P.GAP, x_right - w)
    out.append(("right-arm", x0, P.EDGE, False, w, h))
  return out


def build_one(fname: str, plate_name: str, title: str, stems: list, meshes: dict) -> tuple:
  placed = layout(stems, meshes)
  P.check_layout([(s, 0, x0, y0, rot, w, h) for s, x0, y0, rot, w, h in placed])
  pieces, labels = [], []
  for stem, x0, y0, rot, w, h in placed:
    verts, tris = meshes[stem]
    pieces.append((stem, P.place(verts, x0, y0, rot), tris, PIECES[stem][2]))
    labels.append(PIECES[stem][1])
  P.picture(os.path.join(OUT_DIR, fname + ".png"), f"{title}  ({P.BED[0]:.0f} x {P.BED[1]:.0f} mm bed)", pieces, labels)
  path = os.path.join(OUT_DIR, fname + ".3mf")
  P.write_3mf(path, title, plate_name, pieces, P.thumbnail(pieces))
  objects, settings, plate = P.read_back(path)                   # read it back and compare with what was placed
  assert len(objects) == len(pieces) and plate["plater_name"] == plate_name
  for oid, (name, v, t) in objects.items():
    want = pieces[oid - 1]
    assert name == want[0] and len(v) == len(want[1]) and len(t) == len(want[2])
    assert np.allclose(v.min(axis=0), want[1].min(axis=0), atol=1e-4) and np.allclose(v.max(axis=0), want[1].max(axis=0), atol=1e-4)
    assert abs(v.min(axis=0)[2]) < 1e-6, "a part floats above the bed"
    for key, value in want[3].items():
      assert settings[oid][key] == value, (name, key)
    lo, hi = want[1].min(axis=0), want[1].max(axis=0)
    assert lo[0] >= P.EDGE - 1e-3 and lo[1] >= P.EDGE - 1e-3 and hi[0] <= P.BED[0] - P.EDGE + 1e-3 and hi[1] <= P.BED[1] - P.EDGE + 1e-3
  return path, placed


def main():
  os.makedirs(OUT_DIR, exist_ok=True)
  meshes = {stem: P.read_stl(os.path.join(STL_ROOT, folder, stem + ".stl")) for stem, (folder, _, _) in PIECES.items()}
  every = list(PIECES)
  for fname, plate_name, title, stems in (
      ("plate-13-all-in-one", "13 all in one", "Plate 13: everything for the right-arm build, one print", every),
      ("plate-13b-all-but-the-frame-plate", "13b all but the frame plate",
       "Plate 13b: the same without the frame plate (if it is already printed)", every[1:])):
    path, placed = build_one(fname, plate_name, title, stems, meshes)
    print(f"{fname}.3mf ({os.path.getsize(path) / 1e6:.1f} MB)")
    for stem, x0, y0, rot, w, h in placed:
      print(f"   {PIECES[stem][1]:16s} x {x0:6.1f}..{x0 + w:6.1f}  y {y0:6.1f}..{y0 + h:6.1f}{'  turned' if rot else ''}")


if __name__ == "__main__":
  sys.exit(main())

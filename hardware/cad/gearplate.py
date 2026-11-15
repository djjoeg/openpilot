"""Plate 16: the motor's gear on its own (15 Nov).

The right-arm build uses the side-slide mount's gear (sideparts.side_gear: 16 teeth, module 2, the outer tooth ends
pointed, a D-shaped hole for the motor's 5 mm shaft and an M3 set screw onto its flat), but none of plates 12 to 15
carry it: it was only ever on plate 1 of the side-slide mount. This puts it on a plate by itself, unchanged, printed
the way plate 1 had it: on its motor end, the pointed tooth ends up, solid, no supports.

  python3 gearplate.py     # writes ../print/plate-16-motor-gear.3mf and .png
"""
import os
import tempfile

import plates as P
import sideparts as S
from cadlib import write_stl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "print")


def main():
  gear = S.side_gear()
  z0 = gear.bounding_box()[2]
  gear = gear.translate((0.0, 0.0, -z0))      # its motor end on the bed
  with tempfile.TemporaryDirectory() as d:
    write_stl(gear, os.path.join(d, "motor-gear.stl"), "motor gear")
    report = P.build(out_dir=OUT, stl_dir=d, parts={"motor-gear": ("motor gear (solid)", 1, P.SOLID)},
                     plate_list=[("plate-16-motor-gear", "16 motor gear", ["motor-gear"],
                                  "Plate 16: the motor's gear, solid, on its motor end (no supports)")])
  bb = gear.bounding_box()
  print(f"gear: {bb[3] - bb[0]:.1f} x {bb[4] - bb[1]:.1f} x {bb[5] - bb[2]:.1f} mm, {gear.volume() / 1000.0 * 1.27:.1f} g solid PETG")
  for n, fname, plate_name, rows, size in report:
    print(f"{fname}.3mf ({size / 1e3:.0f} kB): " + ", ".join(f"{r[0]} at ({r[1]:.0f}, {r[2]:.0f})" for r in rows))


if __name__ == "__main__":
  main()

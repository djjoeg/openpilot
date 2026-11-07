"""
The frame plate's fit test (3 Nov 2026, from your fit of the printed frame plate v4): the plate alone, no receiver,
to get its mounting right on the car before anything goes on it. The same as v4 and v5 except, from what you found:

  - the long piece (on the driver's-door side) and its slot run 2 in (51 mm) further back, towards the dash: the
    slot is now 88 mm long (v4: 37), so it reaches the second cover screw;
  - the cross bar at the end of the long piece is 51 mm further back with it, so the tilt lever can come all the way
    down; the block round the cup screw reaches back to it.

Same 6 mm thickness as the real plate, so the screws and the fit are the real ones; printed sparse (2 walls, 15%
infill) so it is quick. It goes on with #8 x 2 in screws and a fender washer under each. What to look for: both
screws square in their slots, the plate flat against the cover at both, the lever all the way down and up again
without touching it.

Plate frame as rightarm.py's frame plate: x towards the driver's door, y towards the dash, 0 at the cup screw.

  python3 platefit.py   # writes ../stl/right-arm/frame-plate-fit-test.stl, ../plates/plate-15-frame-plate-fit-test.3mf
                        # and ../report/frame-plate-fit-test.png
"""
import os
import sys

import rightarm as RA
from cadlib import box, clean, on_bed, union, write_stl

HERE = os.path.dirname(os.path.abspath(__file__))
STEM = "frame-plate-fit-test"
BACK = 51.0                                   # 2 in further back (towards the dash), your fit
T = RA.PLATE_T
BLOCK = RA.BLOCK                              # (-60, 28, -14, 50): round the cup screw, as v4 and v5
BAR_V4, LEG_V4 = RA.BAR, RA.LEG               # (-18, 106, 36, 50), (88, 106, -46, 50)
XC, SLOT_Y0, SLOT_Y1_V4 = RA.LEG_SLOT         # the long piece's slot: x 97, y -40 to -3 on v4
BAR = (BAR_V4[0], BAR_V4[1], BAR_V4[2] + BACK, BAR_V4[3] + BACK)    # (-18, 106, 87, 101)
LEG = (LEG_V4[0], LEG_V4[1], LEG_V4[2], LEG_V4[3] + BACK)           # (88, 106, -46, 101)
LINK = (BAR[0], BLOCK[1], BLOCK[3] - 1.0, BAR[2] + 1.0)             # the block reaching back to the bar
SLOT = (XC, SLOT_Y0, SLOT_Y1_V4 + BACK)                             # (97, -40, 48)


def rect(r):
  return box(r[0], r[1], r[2], r[3], 0.0, T)


def plate():
  import frameplate as FR
  import slotplate as SL
  body = rect(BLOCK) + rect(LINK) + rect(BAR) + rect(LEG)
  body = body - RA.AM.through_slot(0.0, 0.0, FR.SLOT_L, FR.SLOT_W, "x")          # the cup slot, as v4
  xc, y0, y1 = SLOT
  body = body - RA.AM.through_slot(xc, (y0 + y1) / 2, y1 - y0, FR.SLOT_W, "y")
  SL.FONT.setdefault("<", ("010", "100", "111", "100", "010"))
  labels = [FR.text("< KEY", RA.TUBE_X[1] + 3.0, BLOCK[3] - 8.0, T), FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, T, pix=0.9),
            FR.text("1", xc - FR.text_width("1", 0.9) / 2, LEG[2] + 3.0, T, pix=0.9)]
  return clean(body - union(labels).translate((0.0, 0.0, -SL.LABEL_H + 0.01)))     # cut in, as v5


def drawing(path):
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  from matplotlib.patches import Circle, Rectangle
  import frameplate as FR
  fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=150)
  for r in (BLOCK, LINK, BAR, LEG):
    ax.add_patch(Rectangle((r[0], r[2]), r[1] - r[0], r[3] - r[2], fc="#cfd3d6", ec="none"))
  for r in (BLOCK, BAR_V4, LEG_V4):                                                 # v4's outline, dashed
    ax.add_patch(Rectangle((r[0], r[2]), r[1] - r[0], r[3] - r[2], fc="none", ec="#c0392b", ls="--", lw=1.0))
  ax.add_patch(Rectangle((-FR.SLOT_L / 2, -FR.SLOT_W / 2), FR.SLOT_L, FR.SLOT_W, fc="white", ec="#444"))
  xc, y0, y1 = SLOT
  ax.add_patch(Rectangle((xc - FR.SLOT_W / 2, y0), FR.SLOT_W, y1 - y0, fc="white", ec="#444"))
  ax.plot([xc - 6, xc + 6], [SLOT_Y1_V4, SLOT_Y1_V4], color="#c0392b", lw=1.0)
  ax.text(xc - 9, SLOT_Y1_V4, "v4's slot ended here", ha="right", va="center", fontsize=7, color="#c0392b")
  ax.add_patch(Rectangle((RA.TUBE_X[0], RA.TUBE_Y[0]), RA.TUBE_X[1] - RA.TUBE_X[0], RA.TUBE_Y[1] - RA.TUBE_Y[0],
                         fc="none", ec="#777", ls=":", lw=1.0))
  ax.text((RA.TUBE_X[0] + RA.TUBE_X[1]) / 2, (RA.TUBE_Y[0] + RA.TUBE_Y[1]) / 2, "the receiver\ngoes here later",
          ha="center", va="center", fontsize=7, color="#555")
  ax.add_patch(Circle((0, 0), 6.25, fc="none", ec="#1f5fa8", lw=1.2))
  ax.text(0, -18, "cup screw", ha="center", va="center", fontsize=8, color="#1f5fa8")
  ax.text(xc, -52, "second screw\n(anywhere in the slot)", ha="center", va="bottom", fontsize=8, color="#1f5fa8")
  ax.annotate("", xy=(60, BAR[3]), xytext=(60, BAR_V4[3]), arrowprops=dict(arrowstyle="->", color="#1f5fa8", lw=1.2))
  ax.text(57, (BAR[3] + BAR_V4[3]) / 2, "cross bar 51 mm\n(2 in) further back", ha="right", va="center", fontsize=8,
          color="#1f5fa8")
  ax.text(58, 10, "tilt lever's\nroom", ha="center", va="center", fontsize=8, color="#555")
  ax.set_aspect("equal")
  ax.set_xlim(125, -75)
  ax.set_ylim(118, -62)
  ax.set_xlabel("across the car, mm (0 = cup screw; the key side to the right)")
  ax.set_ylabel("along the column, mm (0 = cup screw; the wheel is up)")
  ax.set_title("Frame plate fit test, seen from below as in your photos: the wheel at the top, the key side on the right.\n"
               "Grey: the fit test. Red dashes: v4, the one you fitted. 6 mm thick, no receiver yet.", fontsize=9)
  ax.grid(True, lw=0.3, alpha=0.5)
  fig.tight_layout()
  fig.savefig(path)
  plt.close(fig)


def main():
  import plates as P
  m = on_bed(plate())
  os.makedirs(RA.STL_DIR, exist_ok=True)
  write_stl(m, os.path.join(RA.STL_DIR, STEM + ".stl"), STEM)
  bb = m.bounding_box()
  print(f"{STEM}: {[round(bb[i + 3] - bb[i], 1) for i in range(3)]} mm, about {round(m.volume() / 1000 * 1.28)} g solid")
  economy = {**P.STANDARD, "wall_loops": "2", "top_shell_layers": "3", "bottom_shell_layers": "3",
             "sparse_infill_density": "15%"}
  out = P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=RA.STL_DIR,
                parts={STEM: ("frame plate fit test", 1, economy)},
                plate_list=[("plate-15-frame-plate-fit-test", "15 frame plate fit test", [STEM],
                             "Plate 15: the frame plate's fit test (no receiver), the long piece 2 in further back")])
  for n, fname, plate_name, rows, size in out:
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")
  drawing(os.path.join(RA.REPORT_DIR, "frame-plate-fit-test.png"))


if __name__ == "__main__":
  sys.exit(main())

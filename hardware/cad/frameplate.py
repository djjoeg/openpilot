"""
The frame plate, v1 (test fit): a flat frame that sits against the underside of the steering column's lower
cover, around the tilt lever. It hangs on the key-side cup screw (a slot, so the plate can shift across the car)
and on whatever the second screw turns out to be on the driver's-door side (a slotted strip, like the slot plate,
so any point there can be used). The window in the middle clears the tilt lever's handle block and the arm
behind it, which stay open to the rear.

Frame: origin at the cup screw; x across the car, + towards the driver's door; y along the column, + towards the
dash (away from the wheel). Numbers are from the photos of 31 Oct 2026 and are rough (± 5 mm), which the slots
are there to absorb.

Printing: flat, labels up; 0.2 mm layers, 4 walls, no supports; about 35 g.

  python3 frameplate.py      # writes ../stl/column-frame-plate/column-frame-plate.stl, ../plates/plate-0b-frame-plate.3mf
                             # and ../report/column-frame-plate.png (the drawing with the car's features)
"""
import os
import sys

from manifold3d import Manifold

from cadlib import box, cyl, union, write_stl
from slotplate import text, text_width

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "..", "stl", "column-frame-plate")
REPORT_DIR = os.path.join(HERE, "..", "report")

T = 4.0
# the car's features, from the photos (rough)
CUP = (0.0, 0.0, 12.5)                   # key-side screw: x, y, diameter of the cup in the cover
CAP = (32.0, 70.0, -10.0, 34.0)          # tilt lever handle block: x0, x1, y0, y1
PIN = (78.0, -30.0)                      # the silver pin in the grey tab at the lever's base
BOOT = (55.0, 86.0, -100.0, -23.0)       # the lever's rubber boot and arm, running rearward from the block
WHEEL_Y = -127.0                         # back of the wheel, by the user's tape (5 in)

# the plate
RIGHT = (-18.0, 28.0, -14.0, 50.0)       # block around the cup
FRONT = (-18.0, 140.0, 36.0, 50.0)       # bar in front of the lever block, joining the two sides
STRIP = (90.0, 140.0, -46.0, 50.0)       # slotted strip on the driver's-door side
SLOT_W, SLOT_L = 6.0, 20.0               # the cup slot: 6 wide (a #8 screw), 20 long across the car
STRIP_COLS = [97.0, 105.0, 113.0, 121.0, 129.0]
STRIP_SLOTS = ((-40.0, -3.0), (3.0, 30.0))   # two slots per column (y ranges), web between


def rbox(r, z0=0.0, z1=T) -> Manifold:
  x0, x1, y0, y1 = r
  return box(x0, x1, y0, y1, z0, z1)


def slot(xc: float, yc: float, length: float, width: float, along: str) -> Manifold:
  """Oblong hole through the plate; along 'x' or 'y'."""
  r = width / 2
  d = (length - width) / 2
  if along == "x":
    a, b = cyl(r, -1.0, T + 1.0, x=xc - d, y=yc, segments=32), cyl(r, -1.0, T + 1.0, x=xc + d, y=yc, segments=32)
  else:
    a, b = cyl(r, -1.0, T + 1.0, x=xc, y=yc - d, segments=32), cyl(r, -1.0, T + 1.0, x=xc, y=yc + d, segments=32)
  return Manifold.batch_hull([a, b])


def plate() -> Manifold:
  """Built in the car frame, then mirrored so that, printed labels up and fitted labels down, the layout seen from
  below matches the photos (key side on the right). The labels are added after the mirror so they read correctly."""
  body = rbox(RIGHT) + rbox(FRONT) + rbox(STRIP)
  body = body - slot(CUP[0], CUP[1], SLOT_L, SLOT_W, "x")
  for xc in STRIP_COLS:
    for y0, y1 in STRIP_SLOTS:
      body = body - slot(xc, (y0 + y1) / 2, y1 - y0, SLOT_W, "y")
  body = body.mirror((1.0, 0.0, 0.0))              # x -> -x: the key side is now +x
  labels = []
  # slot numbers 1..5 on the strip's front bar, "KEY >" by the cup, "WHEEL" on the edge nearest the wheel
  for k, xc in enumerate(STRIP_COLS, start=1):
    s = str(k)
    labels.append(text(s, -xc - text_width(s, 0.9) / 2, STRIP[3] - 5.0, T, pix=0.9))
  labels.append(text("KEY >", -RIGHT[0] - text_width("KEY >") - 2.0, RIGHT[3] - 8.0, T))
  labels.append(text("WHEEL", -8.0, RIGHT[2] + 3.0, T, pix=0.9))
  return body + union(labels)


def build(out_dir: str = STL_DIR) -> dict:
  os.makedirs(out_dir, exist_ok=True)
  m = plate()
  bb = m.bounding_box()
  m = m.translate((-bb[0], -bb[1], 0.0))
  write_stl(m, os.path.join(out_dir, "column-frame-plate.stl"), "column-frame-plate")
  bb = m.bounding_box()
  return {"size_mm": [round(bb[i + 3] - bb[i], 1) for i in range(3)], "grams_solid": round(m.volume() / 1000 * 1.28, 0),
          "origin_offset": (-bb[0], -bb[1])}


def drawing(path: str) -> None:
  """Top view (as printed, labels up), with the car's features drawn in; the wheel is towards the bottom."""
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  from matplotlib.patches import Circle, Rectangle

  fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=150)
  for r in (RIGHT, FRONT, STRIP):
    ax.add_patch(Rectangle((r[0], r[2]), r[1] - r[0], r[3] - r[2], fc="#cfd3d6", ec="none"))
  for r in (RIGHT, FRONT, STRIP):
    ax.add_patch(Rectangle((r[0], r[2]), r[1] - r[0], r[3] - r[2], fc="none", ec="#444", lw=1.2))
  # cover the inner edges where the rectangles join
  ax.add_patch(Rectangle((RIGHT[0] + 0.6, FRONT[2] + 0.6), RIGHT[1] - RIGHT[0] - 1.2, FRONT[3] - FRONT[2] - 1.2, fc="#cfd3d6", ec="none"))
  ax.add_patch(Rectangle((STRIP[0] + 0.6, FRONT[2] + 0.6), STRIP[1] - STRIP[0] - 1.2, FRONT[3] - FRONT[2] - 1.2, fc="#cfd3d6", ec="none"))

  def oblong(xc, yc, length, width, along, **kw):
    if along == "x":
      ax.add_patch(Rectangle((xc - length / 2, yc - width / 2), length, width, **kw))
    else:
      ax.add_patch(Rectangle((xc - width / 2, yc - length / 2), width, length, **kw))

  oblong(CUP[0], CUP[1], SLOT_L, SLOT_W, "x", fc="white", ec="#444", lw=1)
  for xc in STRIP_COLS:
    for y0, y1 in STRIP_SLOTS:
      oblong(xc, (y0 + y1) / 2, y1 - y0, SLOT_W, "y", fc="white", ec="#444", lw=1)
  for k, xc in enumerate(STRIP_COLS, start=1):
    ax.text(xc, STRIP[3] - 3, str(k), ha="center", va="top", fontsize=7, color="#222")
  # the car
  ax.add_patch(Circle((CUP[0], CUP[1]), CUP[2] / 2, fc="none", ec="#c0392b", lw=1.5, ls="--"))
  ax.add_patch(Rectangle((CAP[0], CAP[2]), CAP[1] - CAP[0], CAP[3] - CAP[2], fc="#f7d9d4", ec="#c0392b", lw=1.5, ls="--", alpha=0.9))
  ax.add_patch(Rectangle((BOOT[0], BOOT[2]), BOOT[1] - BOOT[0], BOOT[3] - BOOT[2], fc="#f7d9d4", ec="#c0392b", lw=1.5, ls="--", alpha=0.9))
  ax.add_patch(Circle(PIN, 3.0, fc="none", ec="#c0392b", lw=1.5, ls="--"))
  ax.text(CUP[0], CUP[1] - 11, "cup screw\n(key side)", ha="center", va="top", fontsize=8, color="#c0392b")
  ax.text((CAP[0] + CAP[1]) / 2, (CAP[2] + CAP[3]) / 2, "tilt lever\nhandle block", ha="center", va="center", fontsize=8, color="#c0392b")
  ax.text((BOOT[0] + BOOT[1]) / 2, -60, "lever arm\nand boot", ha="center", va="center", fontsize=8, color="#c0392b")
  ax.text(PIN[0] - 5, PIN[1], "pin", ha="right", va="center", fontsize=8, color="#c0392b")
  ax.annotate("", xy=(-32, -45), xytext=(-32, -20), arrowprops={"arrowstyle": "->", "color": "#444"})
  ax.text(-32, -48, "to the wheel\n(127 mm from\nthe cup)", ha="center", va="top", fontsize=8, color="#444")
  ax.text(-40, 30, "KEY SIDE", ha="center", va="center", fontsize=8, color="#444", rotation=-90)
  ax.text(STRIP[1] + 14, 0, "DRIVER'S-DOOR SIDE", ha="center", va="center", fontsize=8, color="#444", rotation=90)
  # dimensions
  ax.annotate("", xy=(RIGHT[0], 56), xytext=(STRIP[1], 56), arrowprops={"arrowstyle": "<->", "color": "#444"})
  ax.text((RIGHT[0] + STRIP[1]) / 2, 58, f"{STRIP[1] - RIGHT[0]:.0f} mm", ha="center", va="bottom", fontsize=8)
  ax.annotate("", xy=(146, STRIP[2]), xytext=(146, STRIP[3]), arrowprops={"arrowstyle": "<->", "color": "#444"})
  ax.text(148, (STRIP[2] + STRIP[3]) / 2, f"{STRIP[3] - STRIP[2]:.0f} mm", ha="left", va="center", fontsize=8, rotation=90)
  ax.set_aspect("equal")
  ax.set_xlim(160, -50)          # seen from below: the key side is on the right, like the photos
  ax.set_ylim(-105, 66)
  ax.set_xlabel("across the car, mm (0 = cup screw)")
  ax.set_ylabel("along the column, mm (0 = cup screw, + towards the dash)")
  ax.set_title("Frame plate v1 seen from below, as in the photos (print labels up; in the car the labels face down).\n"
               "Red dashed: the car, from the photos (rough).", fontsize=9)
  ax.grid(True, lw=0.3, alpha=0.5)
  fig.tight_layout()
  os.makedirs(os.path.dirname(path), exist_ok=True)
  fig.savefig(path)
  plt.close(fig)


def bambu_plate() -> list:
  import plates as P
  parts = {"column-frame-plate": ("frame plate v1", 1, P.STANDARD)}
  plate_list = [("plate-0b-frame-plate", "0b frame plate", list(parts), "Plate 0b: the frame plate (test fit)")]
  return P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts, plate_list=plate_list)


def main():
  info = build()
  print(f"column-frame-plate: {info['size_mm'][0]} x {info['size_mm'][1]} x {info['size_mm'][2]} mm, about {info['grams_solid']:.0f} g")
  drawing(os.path.join(REPORT_DIR, "column-frame-plate.png"))
  for n, fname, plate_name, rows, size in bambu_plate():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")


if __name__ == "__main__":
  sys.exit(main())

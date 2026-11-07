"""
The measuring plate: a flat, light plate for the underside of the steering column's lower cover.

What it is for: the mount will hang from the cover's own screws (put in longer ones, with washers), and nothing in the
photo model pins those screws down to better than a centimetre. So before any real part is drawn, this plate goes up
flat against the cover's underside and tells us where everything is: the screws show through two big windows with a
millimetre scale along their edges, the plate's own edges carry a scale, and a grid of 4.5 mm holes every 10 mm gives
places to screw to, mark against, or hang the next part from.

Frame on the plate (what you read off it): X across, 0 at the plate's left edge, growing to the driver's right (the key
is on the right); Y along the column, 0 at the dash end, growing towards the steering wheel. The printed numbers are
these millimetres. In the car's CAD frame (x to the driver's right from the column's middle, z along the column towards
the driver from the middle of the part of the wheel you hold): x = X + X_CAR_OFFSET, z = Y + Z_CAR_OFFSET.

The plate sits with its labelled face down (you read it from the footwell looking up) and its wheel end at the cover's
front; its front-left corner is cut away for the tilt lever's paddle. Three bars with a slot go across a window so a
screw can hold the plate wherever it falls in the window (the bar spans the window on the window's rim).

Printing: the plate flat, labels up (that is the face you will see); 0.2 mm layers, 4 walls, no supports. About 30 g.

  python3 measureplate.py        # writes ../stl/column-measuring-plate/*.stl and ../plates/plate-5-measuring-plate.3mf
"""
import os
import sys

from manifold3d import Manifold

from cadlib import box, cyl, union, write_stl

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "..", "stl", "column-measuring-plate")

# ----- the plate (print frame: X across, Y along the column towards the wheel, Z up = the labelled face) -----
T = 2.4                      # the plate
RIM_W, RIM_H = 3.0, 1.6      # a rim round the outside and round each window, up from the labelled face
PLATE = (0.0, 100.0, 0.0, 120.0)          # X0, X1, Y0, Y1
X_CAR_OFFSET, Z_CAR_OFFSET = -8.0, -195.0   # plate (0, 0) in the car's CAD frame: x -8 (8 mm left of the column's
                                            # middle), z -195 (195 mm behind the middle of the part of the wheel you hold)
NOTCH = (0.0, 16.0, 60.0, 120.0)          # the front-left corner, cut away for the tilt lever's paddle (its estimate,
                                          # x -41 to 3, z -135 to -75, plus 5 mm)
# the windows, X0, X1, Y0, Y1: where the photo model puts the cover's screws, plus their uncertainty each way
WINDOWS = {
  "the screw in the round cup under the key": (52.0, 92.0, 50.0, 100.0),    # model: x 63 +-4 (+-18 along the column)
  "the M5 beside the tilt lever's slot, if it is in reach": (5.0, 27.0, 5.0, 45.0),   # model: x 1 +-12, z -188 +-15
}
HOLE_D, PITCH = 4.5, 10.0    # the grid: 4.5 mm holes (an M4 or a #8 screw) every 10 mm
HOLE_KEEP = 2.0              # no hole closer than this to a window, the notch or the edge
PIX = 1.2                    # the raised labels: a 3 x 5 pixel font, this big a pixel, LABEL_H high
LABEL_H = 0.6
TICK = (0.8, 3.0, 0.5)       # scale ticks: width, length, height; a long tick (x2) every 10 mm

# ----- the bar across a window -----
BAR = (56.0, 12.0, 3.0)      # length, width, thickness
BAR_SLOT = (4.6, 42.0)       # its slot: width (a #8 or M4 screw), length (the big window's width plus a little)
BAR_COUNT = 3

FONT = {  # 3 x 5 pixels, top row first
  "0": ("111", "101", "101", "101", "111"), "1": ("010", "110", "010", "010", "111"),
  "2": ("111", "001", "111", "100", "111"), "3": ("111", "001", "111", "001", "111"),
  "4": ("101", "101", "111", "001", "001"), "5": ("111", "100", "111", "001", "111"),
  "6": ("111", "100", "111", "101", "111"), "7": ("111", "001", "001", "010", "010"),
  "8": ("111", "101", "111", "101", "111"), "9": ("111", "101", "111", "001", "111"),
  "A": ("010", "101", "111", "101", "101"), "D": ("110", "101", "101", "101", "110"),
  "E": ("111", "100", "111", "100", "111"), "H": ("101", "101", "111", "101", "101"),
  "I": ("111", "010", "010", "010", "111"), "K": ("101", "101", "110", "101", "101"),
  "L": ("100", "100", "100", "100", "111"), "S": ("111", "100", "111", "001", "111"),
  "W": ("101", "101", "101", "111", "101"), "Y": ("101", "101", "010", "010", "010"),
  "X": ("101", "101", "010", "101", "101"), "^": ("010", "111", "010", "010", "010"),
  ">": ("010", "001", "111", "001", "010"), " ": ("000", "000", "000", "000", "000"),
}


def text(s: str, x: float, y: float, z0: float, h: float = LABEL_H, pix: float = PIX) -> Manifold:
  """Raised text with its lower-left corner at (x, y), reading in +X, upright in +Y, on a face at z0."""
  cells = []
  for i, ch in enumerate(s):
    rows = FONT[ch]
    for r, row in enumerate(rows):
      for c, bit in enumerate(row):
        if bit == "1":
          cx = x + (i * 4 + c) * pix
          cy = y + (4 - r) * pix
          cells.append(box(cx, cx + pix, cy, cy + pix, z0, z0 + h))
  return union(cells)


def text_width(s: str, pix: float = PIX) -> float:
  return (len(s) * 4 - 1) * pix


def ticks_along_x(x0: float, x1: float, y: float, z0: float, up: bool, numbers: bool) -> list:
  """Scale ticks at every 5 mm of X from x0 to x1 (a long one every 10), standing on a face at z0, pointing +Y if up."""
  w, ln, h = TICK
  parts = []
  x = x0
  while x <= x1 + 1e-6:
    L = ln * 2 if abs(x % 10) < 1e-6 or abs(x % 10 - 10) < 1e-6 else ln
    y0, y1 = (y, y + L) if up else (y - L, y)
    parts.append(box(x - w / 2, x + w / 2, y0, y1, z0, z0 + h))
    if numbers and abs(x % 20) < 1e-6:
      s = str(int(round(x)))
      ty = y1 + 1.0 if up else y0 - 1.0 - 5 * PIX
      parts.append(text(s, x - text_width(s) / 2, ty, z0))
    x += 5.0
  return parts


def ticks_along_y(y0: float, y1: float, x: float, z0: float, right: bool, numbers: bool) -> list:
  w, ln, h = TICK
  parts = []
  y = y0
  while y <= y1 + 1e-6:
    L = ln * 2 if abs(y % 10) < 1e-6 or abs(y % 10 - 10) < 1e-6 else ln
    x0, x1 = (x, x + L) if right else (x - L, x)
    parts.append(box(x0, x1, y - w / 2, y + w / 2, z0, z0 + h))
    if numbers and abs(y % 20) < 1e-6:
      s = str(int(round(y)))
      tx = x1 + 1.0 if right else x0 - 1.0 - text_width(s)
      parts.append(text(s, tx, y - 2.5 * PIX, z0))
    y += 5.0
  return parts


def hole_ok(cx: float, cy: float) -> bool:
  r = HOLE_D / 2 + HOLE_KEEP
  X0, X1, Y0, Y1 = PLATE
  if cx - r < X0 + RIM_W or cx + r > X1 - RIM_W or cy - r < Y0 + RIM_W or cy + r > Y1 - RIM_W:
    return False
  for (x0, x1, y0, y1) in [NOTCH] + list(WINDOWS.values()):
    if x0 - r < cx < x1 + r and y0 - r < cy < y1 + r:
      return False
  return True


def plate() -> Manifold:
  X0, X1, Y0, Y1 = PLATE
  body = box(X0, X1, Y0, Y1, 0.0, T)
  nx0, nx1, ny0, ny1 = NOTCH
  body = body - box(nx0 - 1, nx1, ny0, ny1 + 1, -1.0, T + RIM_H + 1)
  # the rim round the outside (and round the notch)
  outline = box(X0, X1, Y0, Y1, T, T + RIM_H) - box(X0 + RIM_W, X1 - RIM_W, Y0 + RIM_W, Y1 - RIM_W, T - 1, T + RIM_H + 1)
  outline = outline - box(nx0 - 1, nx1, ny0, ny1 + 1, T - 1, T + RIM_H + 1)
  notch_rim = box(nx1, nx1 + RIM_W, ny0, Y1, T, T + RIM_H) + box(nx0, nx1 + RIM_W, ny0 - RIM_W, ny0, T, T + RIM_H)
  body = body + outline + notch_rim
  # the windows, each with a rim and a scale along two edges (mm of the plate's own X and Y)
  labels = []
  for name, (x0, x1, y0, y1) in WINDOWS.items():
    body = body + (box(x0 - RIM_W, x1 + RIM_W, y0 - RIM_W, y1 + RIM_W, T, T + RIM_H))
    body = body - box(x0, x1, y0, y1, -1.0, T + RIM_H + 1)
    # ticks on the rim's top: along the window's wheel-end edge (X values) and its right edge (Y values)
    labels += ticks_along_x(x0, x1, y1 + RIM_W, T + RIM_H, up=True, numbers=True)
    labels += ticks_along_y(y0, y1, x1 + RIM_W, T + RIM_H, right=True, numbers=(x1 + RIM_W + 14 < X1))
  # the grid of holes
  x = PITCH
  while x < X1:
    y = PITCH
    while y < Y1:
      if hole_ok(x, y):
        body = body - cyl(HOLE_D / 2, -1.0, T + RIM_H + 1, x=x, y=y, segments=32)
      y += PITCH
    x += PITCH
  # the plate's own scales: X along the dash-end edge, Y along the right edge, on the rim's top
  labels += ticks_along_x(10.0, X1 - 10.0, Y0 + RIM_W, T + RIM_H, up=True, numbers=True)
  labels += ticks_along_y(10.0, Y1 - 10.0, X1 - RIM_W, T + RIM_H, right=False, numbers=True)
  # words: which way is the wheel, which side the key is on
  labels.append(text("WHEEL ^", 40.0, Y1 - RIM_W - 8.0, T))
  labels.append(text("KEY SIDE >", X1 - RIM_W - text_width("KEY SIDE >") - 1.0, Y1 - RIM_W - 16.0, T))
  labels.append(text("X", X1 - 22.0, Y0 + RIM_W + 8.0, T))
  labels.append(text("Y", X1 - RIM_W - 12.0, 52.0, T))
  return body + union(labels)


def bar() -> Manifold:
  L, W, H = BAR
  sw, sl = BAR_SLOT
  b = box(-L / 2, L / 2, -W / 2, W / 2, 0.0, H)
  slot = Manifold.batch_hull([cyl(sw / 2, -1.0, H + 1, x=-sl / 2 + sw / 2, y=0.0, segments=32),
                              cyl(sw / 2, -1.0, H + 1, x=sl / 2 - sw / 2, y=0.0, segments=32)])
  return b - slot


def build(out_dir: str = STL_DIR) -> dict:
  os.makedirs(out_dir, exist_ok=True)
  parts = {"column-measuring-plate": plate(), "column-measuring-bar": bar()}
  info = {}
  for name, m in parts.items():
    path = os.path.join(out_dir, name + ".stl")
    write_stl(m, path, name)
    bb = m.bounding_box()
    info[name] = {"size_mm": [round(bb[i + 3] - bb[i], 1) for i in range(3)], "volume_cm3": round(m.volume() / 1000, 1),
                  "grams_solid": round(m.volume() / 1000 * 1.28, 0)}
  return info


def main():
  info = build()
  for name, v in info.items():
    print(f"{name}: {v['size_mm'][0]} x {v['size_mm'][1]} x {v['size_mm'][2]} mm, {v['grams_solid']:.0f} g solid")
  n = sum(1 for x in range(10, 100, 10) for y in range(10, 120, 10) if hole_ok(x, y))
  print(f"grid holes: {n}")


if __name__ == "__main__":
  sys.exit(main())

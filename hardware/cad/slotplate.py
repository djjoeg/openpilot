"""
The slot plate: a thin rectangle that is mostly oblong holes, for the underside of the steering column's lower cover.

The cover's own screws (put in longer ones, with washers) go through the slots wherever they fall, and the plate is
then screwed to the car. Each screw's place is read off the plate: which slot it is in (numbered 1 to 11 across the
wheel end) and where along the slot (ticks every 5 mm up both sides, numbered every 20). From those screw points the
real mount is drawn.

Frame on the plate: slots numbered 1 to 11 from the left (the key is on the right); Y along the column, 0 at the dash
end, 120 at the wheel end. The plate reads from below, its labelled face down, "WHEEL" towards the steering wheel.

Printing: flat, labels up; 0.2 mm layers, no supports; about 20 g.

  python3 slotplate.py       # writes ../stl/column-slot-plate/column-slot-plate.stl and ../plates/plate-0-slot-plate.3mf
"""
import os
import sys

from manifold3d import Manifold

from cadlib import box, cyl, union, write_stl

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "..", "stl", "column-slot-plate")

T = 3.0                                  # the plate
PLATE = (100.0, 120.0)                   # X across, Y along the column
SIDE_RAIL, END_RAIL = 6.0, 10.0          # solid rails: along both sides (X), at both ends (Y)
SLOT_W, SLOT_PITCH = 6.0, 8.0            # oblong holes 6 mm wide (a #8 or M4 screw, with a washer over the slot), 2 mm webs
CROSS_WEB = (58.0, 62.0)                 # a web across the middle (Y) so the plate stays stiff: two slots per column
PIX, LABEL_H = 1.2, 0.5                  # raised labels: 3 x 5 pixel font, pixel size, height
TICK = (0.8, 2.0, 4.0, 0.4)              # ticks on the side rails: width, short, long (every 10 mm), height

FONT = {
  "0": ("111", "101", "101", "101", "111"), "1": ("010", "110", "010", "010", "111"),
  "2": ("111", "001", "111", "100", "111"), "3": ("111", "001", "111", "001", "111"),
  "4": ("101", "101", "111", "001", "001"), "5": ("111", "100", "111", "001", "111"),
  "6": ("111", "100", "111", "101", "111"), "7": ("111", "001", "001", "010", "010"),
  "8": ("111", "101", "111", "101", "111"), "9": ("111", "101", "111", "001", "111"),
  "W": ("101", "101", "101", "111", "101"), "H": ("101", "101", "111", "101", "101"),
  "E": ("111", "100", "111", "100", "111"), "L": ("100", "100", "100", "100", "111"),
  "K": ("101", "101", "110", "101", "101"), "Y": ("101", "101", "010", "010", "010"),
  "^": ("010", "111", "010", "010", "010"), ">": ("010", "001", "111", "001", "010"),
  " ": ("000", "000", "000", "000", "000"),
}


def text(s: str, x: float, y: float, z0: float, rot: float = 0.0, pix: float = PIX) -> Manifold:
  """Raised text, lower-left corner at (x, y) on a face at z0, reading in +X; rot 90 turns it to read in +Y."""
  cells = []
  for i, ch in enumerate(s):
    for r, row in enumerate(FONT[ch]):
      for c, bit in enumerate(row):
        if bit == "1":
          cx, cy = (i * 4 + c) * pix, (4 - r) * pix
          cells.append(box(cx, cx + pix, cy, cy + pix, z0, z0 + LABEL_H))
  return union(cells).rotate((0.0, 0.0, rot)).translate((x, y, 0.0))


def text_width(s: str, pix: float = PIX) -> float:
  return (len(s) * 4 - 1) * pix


def columns() -> list:
  """The X centre of each slot column, 1 to 11."""
  X, _ = PLATE
  n = int((X - 2 * SIDE_RAIL + (SLOT_PITCH - SLOT_W)) // SLOT_PITCH)
  x0 = (X - (n * SLOT_PITCH - (SLOT_PITCH - SLOT_W))) / 2 + SLOT_W / 2
  return [x0 + k * SLOT_PITCH for k in range(n)]


def slot(xc: float, y0: float, y1: float) -> Manifold:
  r = SLOT_W / 2
  return Manifold.batch_hull([cyl(r, -1.0, T + 1.0, x=xc, y=y0 + r, segments=32), cyl(r, -1.0, T + 1.0, x=xc, y=y1 - r, segments=32)])


def plate() -> Manifold:
  X, Y = PLATE
  body = box(0.0, X, 0.0, Y, 0.0, T)
  cols = columns()
  for xc in cols:
    body = body - slot(xc, END_RAIL, CROSS_WEB[0]) - slot(xc, CROSS_WEB[1], Y - END_RAIL)
  labels = []
  # the slot numbers on the wheel-end rail
  for k, xc in enumerate(cols, start=1):
    s = str(k)
    labels.append(text(s, xc - text_width(s, 0.9) / 2, Y - END_RAIL + 2.5, T, pix=0.9))
  # ticks every 5 mm of Y up both side rails, long at every 10, numbers every 20 on the right rail (reading up)
  w, short, long, h = TICK
  y = 10.0
  while y <= Y - 10.0 + 1e-6:
    L = long if abs(y % 10) < 1e-6 or abs(y % 10 - 10) < 1e-6 else short
    labels.append(box(0.0, L, y - w / 2, y + w / 2, T, T + h))
    labels.append(box(X - L, X, y - w / 2, y + w / 2, T, T + h))
    if abs(y % 20) < 1e-6 and 20.0 <= y <= Y - 20.0:
      s = str(round(y))
      labels.append(text(s, X - 0.6, y - text_width(s) / 2, T, rot=90.0))     # on the right rail, reading up
    y += 5.0
  # words: which way is the wheel (on the left rail, reading up), which side the key is (on the dash-end rail)
  labels.append(text("WHEEL ^", SIDE_RAIL, Y / 2 + 6.0, T, rot=90.0))
  labels.append(text("KEY >", X - SIDE_RAIL - text_width("KEY >") - 1.0, 2.0, T))
  return body + union(labels)


def build(out_dir: str = STL_DIR) -> dict:
  os.makedirs(out_dir, exist_ok=True)
  m = plate()
  write_stl(m, os.path.join(out_dir, "column-slot-plate.stl"), "column-slot-plate")
  bb = m.bounding_box()
  return {"size_mm": [round(bb[i + 3] - bb[i], 1) for i in range(3)], "grams_solid": round(m.volume() / 1000 * 1.28, 0),
          "slots": len(columns()) * 2, "slot_x": [round(x, 1) for x in columns()]}


def bambu_plate() -> list:
  import plates as P
  parts = {"column-slot-plate": ("slot plate", 1, P.STANDARD)}
  plate_list = [("plate-0-slot-plate", "0 slot plate", list(parts), "Plate 0: the slot plate for the column")]
  return P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts, plate_list=plate_list)


def main():
  info = build()
  print(f"column-slot-plate: {info['size_mm'][0]} x {info['size_mm'][1]} x {info['size_mm'][2]} mm, about {info['grams_solid']:.0f} g; "
        f"{info['slots']} slots, columns at x {info['slot_x']}")
  for n, fname, plate_name, rows, size in bambu_plate():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")


if __name__ == "__main__":
  sys.exit(main())

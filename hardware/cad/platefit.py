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
                        # and ../report/frame-plate-fit-test.png, frame-plate-fit-test-template.pdf (full size,
                        # to print on paper at 100% and cut out first)
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
  ax.text(LEG[0] - 2.0, SLOT_Y1_V4, "< v4's slot ended here", ha="left", va="center", fontsize=7, color="#c0392b")
  ax.add_patch(Rectangle((RA.TUBE_X[0], RA.TUBE_Y[0]), RA.TUBE_X[1] - RA.TUBE_X[0], RA.TUBE_Y[1] - RA.TUBE_Y[0],
                         fc="none", ec="#777", ls=":", lw=1.0))
  ax.text((RA.TUBE_X[0] + RA.TUBE_X[1]) / 2, (RA.TUBE_Y[0] + RA.TUBE_Y[1]) / 2, "the receiver\ngoes here later",
          ha="center", va="center", fontsize=7, color="#555")
  ax.add_patch(Circle((0, 0), 6.25, fc="none", ec="#1f5fa8", lw=1.2))
  ax.text(0, -18, "cup screw", ha="center", va="center", fontsize=8, color="#1f5fa8")
  ax.text(xc, -52, "second screw\n(anywhere in the slot)", ha="center", va="bottom", fontsize=8, color="#1f5fa8")
  ax.annotate("", xy=(60, BAR[3]), xytext=(60, BAR_V4[3]), arrowprops={"arrowstyle": "->", "color": "#1f5fa8", "lw": 1.2})
  ax.text(63, (BAR[3] + BAR_V4[3]) / 2, "cross bar 51 mm\n(2 in) further back", ha="right", va="center", fontsize=8,
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


MM = 72.0 / 25.4          # points in a millimetre
YOUR_PRINTER = 3.75 / 4.0 # your printer's page: the template's 4 in bar came out 3 3/4 in (4 Nov)
PAPER_SCALE = 4.03125 / 4.0   # the scaled template as you printed it: its 4 in bar came out 4 1/32 in (4 Nov), so
                              # it is 0.78% big; measurements read off it are divided by this. (So the printer
                              # really prints at about 94.5%: use 0.945 for YOUR_PRINTER next time.)


def paper_template(path, printer_scale=1.0):
  """The fit test full size on US Letter, to cut out: seen from below, as you hold it up under the column (printed
  side down, the top edge towards the steering wheel), with scale bars across and up and down to check the size.
  printer_scale: what the printer does to the page (your 4 in bar came out 3 3/4 in: 0.9375); the drawing is made
  that much bigger, so it comes out full size."""
  from reportlab.lib.pagesizes import letter
  from reportlab.pdfgen import canvas
  k = 1.0 / printer_scale
  mine = abs(k - 1.0) > 1e-9
  c = canvas.Canvas(path, pagesize=letter)
  c.setTitle("Frame plate fit test: full-size paper template" + (", scaled for your printer" if mine else ""))
  ou, ov = 130.95, 188.0                       # page mm of the cup screw; page u = ou - x, v = ov - y (seen from below)
  cx, cy = 107.95, 146.5                       # the middle of the drawing, which the scaling is about

  def pt(x, y):
    return (ou - x) * MM, (ov - y) * MM

  def text(u, v, s_, size=9.0, bold=False, angle=0.0, anchor="left"):
    c.saveState()
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.translate(u * MM, v * MM)
    c.rotate(angle)
    {"left": c.drawString, "centre": c.drawCentredString, "right": c.drawRightString}[anchor](0.0, 0.0, s_)
    c.restoreState()

  def ruler(u, v, length, step, minor, unit, upright=False):
    """A scale bar from (u, v), along the page or (upright) up it, long ticks every step, numbered."""
    def ln(a0, b0, a1, b1):
      if upright:
        c.line(u * MM - b0 * MM, (v + a0) * MM, u * MM - b1 * MM, (v + a1) * MM)
      else:
        c.line((u + a0) * MM, (v + b0) * MM, (u + a1) * MM, (v + b1) * MM)
    ln(0.0, 0.0, length, 0.0)
    n = 0
    while n * minor <= length + 1e-6:
      a = n * minor
      big = abs(a / step - round(a / step)) < 1e-6
      ln(a, 0.0, a, 3.0 if big else 1.6)
      if big:
        label = str(round(a / step) * (10 if unit == "mm" else 1))
        if upright:
          text(u - 4.5, v + a - 1.0, label, 7.0, anchor="right")
        else:
          text(u + a, v + 4.2, label, 7.0, anchor="centre")
      n += 1

  c.saveState()                                # the drawing, true size after the printer
  c.translate(cx * MM, cy * MM)
  c.scale(k, k)
  c.translate(-cx * MM, -cy * MM)
  c.setLineWidth(0.7)                          # the cut line: the plate's outline and its two slots, from the part
  for poly in plate().slice(T / 2).to_polygons():
    path_ = c.beginPath()
    path_.moveTo(*pt(*poly[0]))
    for q in poly[1:]:
      path_.lineTo(*pt(*q))
    path_.close()
    c.drawPath(path_, stroke=1, fill=0)
  c.setLineWidth(0.5)                          # marks that are not cut
  x0, y0 = pt(0.0, 0.0)
  c.line(x0 - 4 * MM, y0, x0 + 4 * MM, y0)
  c.line(x0, y0 - 4 * MM, x0, y0 + 4 * MM)
  c.setDash(1.5, 2.5)
  u0, v0 = pt(RA.TUBE_X[1], RA.TUBE_Y[1])
  u1, v1 = pt(RA.TUBE_X[0], RA.TUBE_Y[0])
  c.rect(u0, v0, u1 - u0, v1 - v0, stroke=1, fill=0)
  c.setDash()
  text(ou, ov + 8.0, "cup screw", 8.0, anchor="centre")
  text(ou + 22.0, ov - 32.0, "the receiver goes here (do not cut)", 7.5, anchor="centre")
  text(ou - SLOT[0] + 7.0, ov - 40.0, "second screw: anywhere in this slot", 8.0, angle=90.0)
  text(ou - 70.0, ov + 37.0, "tilt lever's room", 8.0, anchor="centre")
  text(ou - 23.0, ov + 53.0, "TOP EDGE: TOWARD THE STEERING WHEEL", 9.0, bold=True, anchor="centre")
  text(ou - 23.0, ov - 108.0, "BOTTOM EDGE: TOWARD THE DASH", 9.0, bold=True, anchor="centre")
  text(ou - 113.0, ov - 23.0, "DRIVER'S DOOR SIDE", 9.0, bold=True, angle=90.0, anchor="centre")
  text(ou + 67.0, ov - 23.0, "KEY SIDE", 9.0, bold=True, angle=-90.0, anchor="centre")
  c.setLineWidth(0.6)
  ruler(25.0, 66.0, 100.0, 10.0, 5.0, "mm")
  text(129.0, 65.4, "100 mm across: it must measure exactly 100 mm", 8.5)
  ruler(25.0, 52.0, 101.6, 25.4, 12.7, "in")
  text(130.6, 51.4, "4 in across: it must measure exactly 4 in", 8.5)
  ruler(97.0, ov - 80.0, 100.0, 10.0, 5.0, "mm", upright=True)
  text(87.0, ov - 30.0, "100 mm up and down: it must measure exactly 100 mm", 7.5, angle=90.0, anchor="centre")
  c.restoreState()

  if mine:                                      # the title and the notes, any size
    text(107.95, 268.0, "Frame plate fit test (plate 15): paper template, scaled for your printer", 12.5, bold=True,
         anchor="centre")
    text(107.95, 261.0, "Seen from below, as you hold it up under the steering column: printed side down.", 9.5,
         anchor="centre")
    lines = [(f"1.  For your printer, which prints a page at {100 * printer_scale:.2f}% (your 4 in bar came out "
              f"{4 * printer_scale:.2f} in): drawn {100 * (k - 1):.1f}%"),
             "     bigger, so it comes out full size. Print it exactly the way you did before.",
             "2.  Measure all three bars: each must now be exactly 100 mm or 4 in. If not, tell me what they measure.",
             "3.  Cut along the solid lines, the two slots too. Card stock holds its shape better than paper.",
             "4.  Hold it up under the column, printed side down, the top edge toward the steering wheel: the cup screw",
             "     in the short slot, the second screw in the long one. Work the tilt lever all the way down and back up."]
  else:
    text(107.95, 268.0, "Frame plate fit test (plate 15): full-size paper template", 13.0, bold=True, anchor="centre")
    text(107.95, 261.0, "Seen from below, as you hold it up under the steering column: printed side down.", 9.5,
         anchor="centre")
    lines = ["1.  Print at 100% (\"Actual size\"), not \"Fit to page\". Measure the three bars: if any is off, the",
             "     printer scaled it.",
             "2.  Cut along the solid lines, the two slots too. Card stock holds its shape better than paper.",
             "3.  Hold it up under the column, printed side down, the top edge toward the steering wheel: the cup screw",
             "     in the short slot, the second screw in the long one. Work the tilt lever all the way down and back up."]
  for i, ln_ in enumerate(lines):
    text(22.0, 36.0 - 4.8 * i, ln_, 9.0)
  c.showPage()
  c.save()


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
  paper_template(os.path.join(RA.REPORT_DIR, "frame-plate-fit-test-template.pdf"))
  paper_template(os.path.join(RA.REPORT_DIR, "frame-plate-fit-test-template-your-printer.pdf"), YOUR_PRINTER)


if __name__ == "__main__":
  sys.exit(main())

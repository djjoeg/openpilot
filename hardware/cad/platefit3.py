"""Frame plate, third shape (v3): paper template (11 Nov), from option 1 of crosspiece_options.py.

Your pick (11 Nov): the new crosspiece straight across, right behind the block, folding up about 45 degrees with the
cover into the space above the tilt lever's tab. The old crossbar is gone (your purple line), the long piece ends at
the fold, and the strip is notched where the tab passes under it. The block, the cup slot and the receiver's place
are unchanged; the long slot keeps its dash end.

Plate frame (mm): x toward the driver's door, y toward the dash, origin at the cup screw. The template is seen from
below, printed side down: page u = OU - x, v = OV - y (wheel at the top, key side on the right), as v2.

  python3 platefit3.py ../print     # writes frame-plate-v3-paper-template-your-printer.pdf and -100.pdf
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import crosspiece_options as CO
from platefit2 import MM, PAGE_W, YOUR_PRINTER, ruler_across, ruler_up, slot_path

FOLD_Y = CO.OPTIONS["1"]["fold"][0][1]          # -14: right behind the block, straight across
BACK_Y = FOLD_Y - CO.W                          # -39: the strip's far edge, laid flat (your purple line)
NOTCH_X = (CO.TAB[0] - CO.CLEAR, CO.TAB[1] + CO.CLEAR)    # (34, 70)
NOTCH_Y = FOLD_Y - round(CO.notch_t(), 1)       # -18.6: the strip's edge over the tab, cut back 4.6 mm
BX0, BX1, BY0, BY1 = CO.BLOCK                   # the block: x -60..28, y -14..50
LX0, LX1 = CO.LONG_X                            # the long piece: x 88..106
STEM_X = CO.STEM_X                              # 8: the strip's key-side end

OUTLINE = [(BX0, BY1), (BX0, FOLD_Y), (STEM_X, FOLD_Y), (STEM_X, BACK_Y), (LX1, BACK_Y), (LX1, CO.LONG_END),
           (LX0, CO.LONG_END), (LX0, FOLD_Y), (NOTCH_X[1], FOLD_Y), (NOTCH_X[1], NOTCH_Y), (NOTCH_X[0], NOTCH_Y),
           (NOTCH_X[0], FOLD_Y), (BX1, FOLD_Y), (BX1, BY1)]
STRIP = [(STEM_X, FOLD_Y), (STEM_X, BACK_Y), (LX1, BACK_Y), (LX1, FOLD_Y), (NOTCH_X[1], FOLD_Y),
         (NOTCH_X[1], NOTCH_Y), (NOTCH_X[0], NOTCH_Y), (NOTCH_X[0], FOLD_Y)]
FOLDS = [(STEM_X, BX1), (LX0, LX1)]             # where the strip joins the block and the long piece
LONG_SLOT = (97, FOLD_Y + 6, 62)                # centre x, y from, y to (outer ends); 6 mm wide; v2's dash end
CUP_SLOT = (0, 0, 20, 6)                        # centre x, y, length (across), width
RECEIVER = CO.RECEIVER                          # x from, x to, y from, y to (dotted, not cut)
SLOT_W = 6


def poly(c, P, pts, fill=0, stroke=1):
  p = c.beginPath()
  u, v = P(*pts[0])
  p.moveTo(u * MM, v * MM)
  for pt in pts[1:]:
    u, v = P(*pt)
    p.lineTo(u * MM, v * MM)
  p.close()
  c.drawPath(p, stroke=stroke, fill=fill)


def rotated(c, u, v, angle, text, font=("Helvetica", 7)):
  c.saveState()
  c.translate(u * MM, v * MM)
  c.rotate(angle)
  c.setFont(*font)
  c.drawCentredString(0, 0, text)
  c.restoreState()


def paper_template(path, printer_scale):
  k = 1 / printer_scale
  OU, OV = 130.95, 200.0
  cx, cy = PAGE_W / 2, 146.5

  def P(x, y):
    return OU - x, OV - y

  c = canvas.Canvas(path, pagesize=letter)
  c.setTitle("Frame plate fit test v3: paper template")
  c.saveState()
  c.translate(cx * MM, cy * MM)
  c.scale(k, k)
  c.translate(-cx * MM, -cy * MM)

  full = abs(printer_scale - 1) < 1e-9
  c.setFont("Helvetica-Bold", 12)
  c.drawCentredString(108 * MM, 262 * MM, "Frame plate fit test v3: paper template, " +
                      ("full size (print at 100%)" if full else "scaled for your printer"))
  c.setFont("Helvetica", 8.5)
  c.drawCentredString(108 * MM, 256.5 * MM, "Seen from below, as you hold it up under the steering column: printed side down.")
  c.setFont("Helvetica-Bold", 9)
  c.drawCentredString(73 * MM, 249 * MM, "TOP EDGE: TOWARD THE STEERING WHEEL")

  # the strip that folds up, lightly shaded, then the outline (cut line)
  c.setFillGray(0.9)
  poly(c, P, STRIP, fill=1, stroke=0)
  c.setFillGray(0)
  c.setLineWidth(1.0)
  poly(c, P, OUTLINE)

  # the two folds
  c.setLineWidth(0.9)
  c.setDash(3, 2)
  for x0, x1 in FOLDS:
    ua, v = P(x0, FOLD_Y)
    ub, _ = P(x1, FOLD_Y)
    c.line(ua * MM, v * MM, ub * MM, v * MM)
  c.setDash()

  # slots
  c.setLineWidth(0.8)
  sx, sy0, sy1 = LONG_SLOT
  slot_path(c, P, sx, sy0, sx, sy1, SLOT_W)
  cxp, cyp, L, Wd = CUP_SLOT
  slot_path(c, P, cxp - L / 2, cyp, cxp + L / 2, cyp, Wd)
  u, v = P(cxp, cyp)
  c.setLineWidth(0.4)
  c.line((u - 3) * MM, v * MM, (u + 3) * MM, v * MM)
  c.line(u * MM, (v - 3) * MM, u * MM, (v + 3) * MM)

  # receiver footprint, dotted
  c.setDash(1, 2)
  c.setLineWidth(0.5)
  x0, x1, y0, y1 = RECEIVER
  ua, va = P(x1, y1)
  ub, vb = P(x0, y0)
  c.rect(ua * MM, va * MM, (ub - ua) * MM, (vb - va) * MM, stroke=1, fill=0)
  c.setDash()

  # labels
  c.setFont("Helvetica-Bold", 8)
  u, v = P(57, -31.5)
  c.drawCentredString(u * MM, v * MM, "NEW CROSSPIECE: folds up against the cover")
  c.setFont("Helvetica", 7.5)
  c.drawCentredString(u * MM, (v - 4) * MM, "where it turns up, above the tilt lever's tab")
  c.setFont("Helvetica-Bold", 7)
  for x0, x1 in FOLDS:
    u, v = P((x0 + x1) / 2, FOLD_Y - 6.5)
    c.drawCentredString(u * MM, v * MM, "FOLD UP")
    c.drawCentredString(u * MM, (v - 3) * MM, "about 45°")
  c.setFont("Helvetica", 7)
  u, v = P(52, FOLD_Y + 4)
  c.drawCentredString(u * MM, v * MM, "notch: the tab passes under here")
  c.setFont("Helvetica", 7.5)
  u, v = P(0, -7)
  c.drawCentredString(u * MM, v * MM, "cup screw")
  u, v = P(-22, 31)
  c.drawCentredString(u * MM, v * MM, "the receiver goes here (do not cut)")
  u, v = P(58, 30)
  c.setFont("Helvetica-Bold", 8)
  c.drawCentredString(u * MM, v * MM, "cut this out:")
  c.drawCentredString(u * MM, (v - 4) * MM, "the tilt lever's room")
  u, v = P(91.3, 27)
  rotated(c, u, v, 90, "second screw: anywhere in this slot")

  c.setFont("Helvetica-Bold", 9)
  c.drawCentredString(150 * MM, 122 * MM, "BOTTOM EDGE: TOWARD THE DASH")
  rotated(c, 14, 185, 90, "DRIVER'S DOOR SIDE", ("Helvetica-Bold", 9))
  rotated(c, 201, 238, -90, "KEY SIDE", ("Helvetica-Bold", 9))

  # scale bars
  ruler_across(c, 20, 108, 100, 10, 1, lambda d: str(int(round(d))), "100 mm across: it must measure exactly 100 mm")
  ruler_across(c, 20, 93, 101.6, 25.4, 25.4 / 8, lambda d: str(int(round(d / 25.4))),
               "4 in across: it must measure exactly 4 in")
  ruler_up(c, 203, 118, 100)
  rotated(c, 206.5, 168, 90, "100 mm up and down: it must measure exactly 100 mm", ("Helvetica", 7.5))

  first = ([
    "1. Print at 100% (actual size, not fit to page).",
  ] if full else [
    "1. Print it exactly the way you printed the last one. It is drawn %.1f%% big, because your printer shrinks a page"
    % ((1 / printer_scale - 1) * 100),
    "    to %.1f%%, so it should come out full size." % (printer_scale * 100),
  ])
  notes = first + [
    "2. Before cutting, measure the three bars. Each must be exactly 100 mm or 4 in. If not, tell me what they measure.",
    "3. Cut on the solid line, notch included, and cut out both slots.",
    "4. Fold the grey strip up along the two short dashed lines, about 45°, away from the printed side.",
    "5. Hold it up under the column, printed side down, top edge toward the wheel: the cup screw in the short slot,",
    "    the second screw in the long one. Press the strip up against the cover where it turns up, over the tab.",
    "6. Check: the folds sit where the cover turns up; the tab passes under the notch; the tilt lever goes all the",
    "    way down and back up; the wheel turns lock to lock. Nothing should touch the paper.",
    "7. Where something doesn't fit, cut the paper until it does and tell me how much you took off. If the folds",
    "    aren't where the cover turns up, measure how far off they are, toward the wheel or toward the dash.",
  ]
  c.setFont("Helvetica", 8.3)
  v = 78
  for line in notes:
    c.drawString(20 * MM, v * MM, line)
    v -= 4.3
  c.restoreState()
  c.showPage()
  c.save()


if __name__ == "__main__":
  import sys
  out = sys.argv[1] if len(sys.argv) > 1 else "."
  paper_template(f"{out}/frame-plate-v3-paper-template-your-printer.pdf", YOUR_PRINTER)
  paper_template(f"{out}/frame-plate-v3-paper-template-100.pdf", 1.0)
  print("printer scale", round(YOUR_PRINTER, 4), "drawn", round(1 / YOUR_PRINTER, 4), "notch to y", NOTCH_Y)

cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "platefit.py"
s = open(p, encoding="utf-8").read()
start = s.index("def paper_template(path):")
end = s.index("def main():")
new = '''def paper_template(path, printer_scale=1.0):
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
    lines = [f"1.  For your printer, which prints a page at {100 * printer_scale:.2f}% (your 4 in bar came out "
             f"{4 * printer_scale:.2f} in): drawn {100 * (k - 1):.1f}%",
             "     bigger, so it comes out full size. Print it exactly the way you did before.",
             "2.  Measure all three bars: each must now be exactly 100 mm or 4 in. If not, tell me what they measure.",
             "3.  Cut along the solid lines, the two slots too. Card stock holds its shape better than paper.",
             "4.  Hold it up under the column, printed side down, the top edge toward the steering wheel: the cup screw",
             "     in the short slot, the second screw in the long one. Work the tilt lever all the way down and back up."]
  else:
    text(107.95, 268.0, "Frame plate fit test (plate 15): full-size paper template", 13.0, bold=True, anchor="centre")
    text(107.95, 261.0, "Seen from below, as you hold it up under the steering column: printed side down.", 9.5,
         anchor="centre")
    lines = ["1.  Print at 100% (\\"Actual size\\"), not \\"Fit to page\\". Measure the three bars: if any is off, the",
             "     printer scaled it.",
             "2.  Cut along the solid lines, the two slots too. Card stock holds its shape better than paper.",
             "3.  Hold it up under the column, printed side down, the top edge toward the steering wheel: the cup screw",
             "     in the short slot, the second screw in the long one. Work the tilt lever all the way down and back up."]
  for i, ln_ in enumerate(lines):
    text(22.0, 36.0 - 4.8 * i, ln_, 9.0)
  c.showPage()
  c.save()


'''
s = s[:start] + new + s[end:]
a = '''  paper_template(os.path.join(RA.REPORT_DIR, "frame-plate-fit-test-template.pdf"))
'''
b = '''  paper_template(os.path.join(RA.REPORT_DIR, "frame-plate-fit-test-template.pdf"))
  paper_template(os.path.join(RA.REPORT_DIR, "frame-plate-fit-test-template-your-printer.pdf"), YOUR_PRINTER)
'''
assert s.count(a) == 1
s = s.replace(a, b)
a = '''MM = 72.0 / 25.4          # points in a millimetre
'''
b = '''MM = 72.0 / 25.4          # points in a millimetre
YOUR_PRINTER = 3.75 / 4.0 # your printer's page: the template's 4 in bar came out 3 3/4 in (4 Nov)
'''
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
ruff check platefit.py | tail -2; PYTHONPATH=/home/claude/pylib timeout 600 python3 -c "
import os, platefit as F, rightarm as RA
F.paper_template(os.path.join(RA.REPORT_DIR, 'frame-plate-fit-test-template.pdf'))
F.paper_template(os.path.join(RA.REPORT_DIR, 'frame-plate-fit-test-template-your-printer.pdf'), F.YOUR_PRINTER)
print('ok')
"
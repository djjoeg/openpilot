python3 - <<'EOF'
p = "platefit.py"
s = open(p, encoding="utf-8").read()
a = '''def main():
  import plates as P'''
b = '''MM = 72.0 / 25.4          # points in a millimetre


def paper_template(path):
  """The fit test full size on US Letter, to print at 100% and cut out: seen from below, as you hold it up under the
  column (printed side down, the top edge towards the steering wheel). Two scale bars to check the printer's size."""
  from reportlab.lib.pagesizes import letter
  from reportlab.pdfgen import canvas
  pw, ph = letter
  c = canvas.Canvas(path, pagesize=letter)
  c.setTitle("Frame plate fit test: full-size paper template")
  ou, ov = 130.95, 192.0                       # page mm of the cup screw; page u = ou - x, v = ov - y (seen from below)

  def pt(x, y):
    return (ou - x) * MM, (ov - y) * MM

  def text(u, v, s, size=9.0, bold=False, angle=0.0, anchor="left"):
    c.saveState()
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.translate(u * MM, v * MM)
    c.rotate(angle)
    {"left": c.drawString, "centre": c.drawCentredString, "right": c.drawRightString}[anchor](0.0, 0.0, s)
    c.restoreState()

  # the cut line: the plate's outline and its two slots, from the part itself
  c.setLineWidth(0.7)
  for poly in plate().slice(T / 2).to_polygons():
    path_ = c.beginPath()
    path_.moveTo(*pt(*poly[0]))
    for q in poly[1:]:
      path_.lineTo(*pt(*q))
    path_.close()
    c.drawPath(path_, stroke=1, fill=0)
  # marks that are not cut
  c.setLineWidth(0.5)
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
  text(ou - 58.0, ov + 12.0, "tilt lever's room", 8.0, anchor="centre")
  # which way it goes
  text(ou - 23.0, ov + 54.0, "TOP EDGE: TOWARD THE STEERING WHEEL", 9.0, bold=True, anchor="centre")
  text(ou - 23.0, ov - 108.0, "BOTTOM EDGE: TOWARD THE DASH", 9.0, bold=True, anchor="centre")
  text(ou - 113.0, ov - 23.0, "DRIVER'S DOOR SIDE", 9.0, bold=True, angle=90.0, anchor="centre")
  text(ou + 67.0, ov - 23.0, "KEY SIDE", 9.0, bold=True, angle=-90.0, anchor="centre")
  # title
  text(107.95, 266.0, "Frame plate fit test (plate 15): full-size paper template", 13.0, bold=True, anchor="centre")
  text(107.95, 259.0, "Seen from below, as you hold it up under the steering column: printed side down.", 9.5,
       anchor="centre")
  # scale bars
  c.setLineWidth(0.6)
  for v, length, step, minor, label, unit in ((62.0, 100.0, 10.0, 5.0, "100 mm", "mm"), (48.0, 101.6, 25.4, 12.7, "4 in", "in")):
    u = 25.0
    c.line(u * MM, v * MM, (u + length) * MM, v * MM)
    k = 0
    while k * minor <= length + 1e-6:
      big = abs((k * minor) / step - round((k * minor) / step)) < 1e-6
      c.line((u + k * minor) * MM, v * MM, (u + k * minor) * MM, (v + (3.0 if big else 1.6)) * MM)
      if big:
        n = round(k * minor / step) * (10 if unit == "mm" else 1)
        text(u + k * minor, v + 4.2, str(n), 7.0, anchor="centre")
      k += 1
    text(u + length + 4.0, v - 0.6, f"{label}: measure it; it must be exactly {label}", 9.0)
  # how to
  lines = ["1.  Print at 100% (\\"Actual size\\"), not \\"Fit to page\\". Measure both bars above: if either is off, the",
           "     printer scaled it; print again.",
           "2.  Cut along the solid lines, the two slots too. Card stock holds its shape better than paper.",
           "3.  Hold it up under the column, printed side down, the top edge toward the steering wheel: the cup screw in",
           "     the short slot, the second screw in the long one. Then work the tilt lever all the way down and back up."]
  for i, ln in enumerate(lines):
    text(25.0, 34.0 - 5.0 * i, ln, 9.0)
  c.showPage()
  c.save()


def main():
  import plates as P'''
assert s.count(a) == 1
s = s.replace(a, b)
a = '''  drawing(os.path.join(RA.REPORT_DIR, "frame-plate-fit-test.png"))
'''
b = '''  drawing(os.path.join(RA.REPORT_DIR, "frame-plate-fit-test.png"))
  paper_template(os.path.join(RA.REPORT_DIR, "frame-plate-fit-test-template.pdf"))
'''
assert s.count(a) == 1
s = s.replace(a, b)
s = s.replace('''                        # and ../report/frame-plate-fit-test.png
"""''', '''                        # and ../report/frame-plate-fit-test.png, frame-plate-fit-test-template.pdf (full size,
                        # to print on paper at 100% and cut out first)
"""''')
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
ruff check platefit.py | tail -3; PYTHONPATH=/home/claude/pylib timeout 600 python3 -c "
import os, platefit as F, rightarm as RA
F.paper_template(os.path.join(RA.REPORT_DIR, 'frame-plate-fit-test-template.pdf'))
print('ok')
"
python3 - <<'EOF'
p = "platefit.py"
s = open(p, encoding="utf-8").read()
a = '''    lines = [f"1.  For your printer, which prints a page at {100 * printer_scale:.2f}% (your 4 in bar came out "
             f"{4 * printer_scale:.2f} in): drawn {100 * (k - 1):.1f}%",'''
b = '''    lines = [(f"1.  For your printer, which prints a page at {100 * printer_scale:.2f}% (your 4 in bar came out "
              f"{4 * printer_scale:.2f} in): drawn {100 * (k - 1):.1f}%"),'''
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
ruff check platefit.py | tail -1; PYTHONPATH=/home/claude/pylib timeout 600 python3 -c "
import os, platefit as F, rightarm as RA
F.paper_template(os.path.join(RA.REPORT_DIR, 'frame-plate-fit-test-template.pdf'))
F.paper_template(os.path.join(RA.REPORT_DIR, 'frame-plate-fit-test-template-your-printer.pdf'), F.YOUR_PRINTER)
" && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/photos && pdftoppm -r 100 -png /home/claude/deliver/hardware/report/frame-plate-fit-test-template-your-printer.pdf mine && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import pdfplumber
for f in ("frame-plate-fit-test-template.pdf", "frame-plate-fit-test-template-your-printer.pdf"):
    with pdfplumber.open("/home/claude/deliver/hardware/report/" + f) as pdf:
        pg = pdf.pages[0]
        mm = lambda v: round(v / 72 * 25.4, 2)
        big = [c for c in pg.curves if (c["x1"] - c["x0"]) > 100]
        out = [(mm(c["x1"] - c["x0"]), mm(c["bottom"] - c["top"])) for c in big]
        hbars = sorted(mm(l["x1"] - l["x0"]) for l in pg.lines if abs(l["top"] - l["bottom"]) < 0.01 and (l["x1"] - l["x0"]) > 250)
        vbars = sorted(mm(l["bottom"] - l["top"]) for l in pg.lines if abs(l["x0"] - l["x1"]) < 0.01 and (l["bottom"] - l["top"]) > 250)
        objs = pg.chars
        xs = [ch["x0"] for ch in objs] + [ch["x1"] for ch in objs]; ys = [ch["top"] for ch in objs] + [ch["bottom"] for ch in objs]
        print(f, "page", mm(pg.width), "x", mm(pg.height), "outline", out, "bars across", hbars, "up", vbars,
              "text from", mm(min(xs)), mm(min(ys)), "to", mm(max(xs)), mm(max(ys)))
EOF
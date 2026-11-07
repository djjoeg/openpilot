mkdir -p /home/claude/deliver/hardware/cad /home/claude/deliver/hardware/print && cat > /home/claude/deliver/hardware/cad/platefit2.py <<'EOF'
"""Frame plate, second shape (v2): paper template and a before/after picture.

Plate frame (mm): x toward the driver's door, y toward the dash, origin at the cup screw.
The template is seen from below, printed side down: page u = OU - x, v = OV - y
(wheel at the top, key side on the right).
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

MM = 72 / 25.4
PAGE_W, PAGE_H = 215.9, 279.4

# The first paper template, drawn 1/0.9375 big, came out 4 1/32 in on its 4 in bar.
YOUR_PRINTER = (4.03125 / 4) * (3.75 / 4)  # = 0.9448: how much your printer shrinks a page

# Old outline (v1 paper template), for the before/after picture.
OLD = [(106, -46), (106, 101), (-18, 101), (-18, 87), (-18, 50), (-60, 50), (-60, -14), (28, -14), (28, 87),
       (88, 87), (88, -46)]

# New outline (v2): dash-end crossbar and link removed, long piece ends 8 mm past its slot,
# new crossbar at the wheel end (in the nook), stem down to the block's corner, 6 mm chamfers inside.
BAR_TOP = -76            # wheel-side edge of the new crossbar (trim lines below it)
BAR_BOT = -46            # dash-side edge of the crossbar (the old long piece's top end)
TRIM = [("A", -70), ("B", -64), ("C", -58)]  # C: narrowest (12 mm)
STEM_X = 8               # stem's key-side edge
LEG_END = 70             # dash end of the long piece
CH = 6                   # inside chamfer
NEW = [(-60, -14), (STEM_X - CH, -14), (STEM_X, -14 - CH), (STEM_X, BAR_TOP), (106, BAR_TOP), (106, LEG_END),
       (88, LEG_END), (88, BAR_BOT + CH), (88 - CH, BAR_BOT), (28 + CH, BAR_BOT), (28, BAR_BOT + CH), (28, 50),
       (-60, 50)]
LONG_SLOT = (97, -40, 62)        # centre x, y from, y to (outer ends); 6 mm wide
LONG_SLOT_OLD_END = 48
CUP_SLOT = (0, 0, 20, 6)         # centre x, y, length (across), width
RECEIVER = (-47, 3, 15, 45.4)    # x from, x to, y from, y to (dotted, not cut)
SLOT_W = 6


def slot_path(c, P, x0, y0, x1, y1, w):
    """Rounded slot from (x0,y0) to (x1,y1) (outer ends), width w, drawn with page mapper P."""
    r = w / 2
    p = c.beginPath()
    if x0 == x1:  # along y
        ya, yb = min(y0, y1) + r, max(y0, y1) - r
        u, va = P(x0 + r, ya)
        p.moveTo(u * MM, va * MM)
        u2, vb = P(x0 + r, yb)
        p.lineTo(u2 * MM, vb * MM)
        cu, cv = P(x0, yb)
        p.arcTo((cu - r) * MM, (cv - r) * MM, (cu + r) * MM, (cv + r) * MM, startAng=180, extent=180)
        u3, va3 = P(x0 - r, ya)
        p.lineTo(u3 * MM, va3 * MM)
        cu, cv = P(x0, ya)
        p.arcTo((cu - r) * MM, (cv - r) * MM, (cu + r) * MM, (cv + r) * MM, startAng=0, extent=180)
    else:  # along x
        xa, xb = min(x0, x1) + r, max(x0, x1) - r
        ua, v = P(xa, y0 - r)
        p.moveTo(ua * MM, v * MM)
        ub, v2 = P(xb, y0 - r)
        p.lineTo(ub * MM, v2 * MM)
        cu, cv = P(xb, y0)
        p.arcTo((cu - r) * MM, (cv - r) * MM, (cu + r) * MM, (cv + r) * MM, startAng=90, extent=180)
        ua3, v3 = P(xa, y0 + r)
        p.lineTo(ua3 * MM, v3 * MM)
        cu, cv = P(xa, y0)
        p.arcTo((cu - r) * MM, (cv - r) * MM, (cu + r) * MM, (cv + r) * MM, startAng=270, extent=180)
    p.close()
    c.drawPath(p, stroke=1, fill=0)


def ruler_across(c, u0, v, length_mm, step, minor, labels, unit_label):
    c.setLineWidth(0.6)
    c.line(u0 * MM, v * MM, (u0 + length_mm) * MM, v * MM)
    n = round(length_mm / minor)
    for i in range(n + 1):
        d = i * minor
        major = abs(d / step - round(d / step)) < 1e-6
        half = abs((d / step) * 2 - round((d / step) * 2)) < 1e-6
        h = 4 if major else (2.6 if half else 1.5)
        c.line((u0 + d) * MM, v * MM, (u0 + d) * MM, (v + h) * MM)
        if major:
            c.setFont("Helvetica", 7)
            c.drawCentredString((u0 + d) * MM, (v + 5.3) * MM, labels(d))
    c.setFont("Helvetica", 8)
    c.drawString((u0 + length_mm + 4) * MM, (v - 1) * MM, unit_label)


def ruler_up(c, u, v0, length_mm):
    c.setLineWidth(0.6)
    c.line(u * MM, v0 * MM, u * MM, (v0 + length_mm) * MM)
    for d in range(0, int(length_mm) + 1):
        h = 4 if d % 10 == 0 else (2.6 if d % 5 == 0 else 1.5)
        c.line((u - h) * MM, (v0 + d) * MM, u * MM, (v0 + d) * MM)
        if d % 10 == 0:
            c.setFont("Helvetica", 7)
            c.drawRightString((u - 5) * MM, (v0 + d - 1) * MM, str(d))


def paper_template(path, printer_scale):
    k = 1 / printer_scale
    OU, OV = 130.95, 170.0
    cx, cy = PAGE_W / 2, 146.5

    def P(x, y):
        return OU - x, OV - y

    c = canvas.Canvas(path, pagesize=letter)
    c.setTitle("Frame plate fit test v2: paper template")
    c.saveState()
    c.translate(cx * MM, cy * MM)
    c.scale(k, k)
    c.translate(-cx * MM, -cy * MM)

    # Title
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(108 * MM, 262 * MM, "Frame plate fit test v2: paper template, scaled for your printer")
    c.setFont("Helvetica", 8.5)
    c.drawCentredString(108 * MM, 256.5 * MM, "Seen from below, as you hold it up under the steering column: printed side down.")
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(73 * MM, 250 * MM, "TOP EDGE: TOWARD THE STEERING WHEEL")

    # Outline (cut line)
    c.setLineWidth(1.0)
    p = c.beginPath()
    u, v = P(*NEW[0])
    p.moveTo(u * MM, v * MM)
    for pt in NEW[1:]:
        u, v = P(*pt)
        p.lineTo(u * MM, v * MM)
    p.close()
    c.drawPath(p, stroke=1, fill=0)

    # Slots
    c.setLineWidth(0.8)
    sx, sy0, sy1 = LONG_SLOT
    slot_path(c, P, sx, sy0, sx, sy1, SLOT_W)
    cxp, cyp, L, W = CUP_SLOT
    slot_path(c, P, cxp - L / 2, cyp, cxp + L / 2, cyp, W)
    u, v = P(cxp, cyp)
    c.setLineWidth(0.4)
    c.line((u - 3) * MM, v * MM, (u + 3) * MM, v * MM)
    c.line(u * MM, (v - 3) * MM, u * MM, (v + 3) * MM)

    # Old end of the long slot, thin dashed, for reference
    c.setDash(1.5, 1.5)
    c.setLineWidth(0.3)
    u0, v0 = P(sx - 3, LONG_SLOT_OLD_END - 3)
    u1, _ = P(sx + 3, LONG_SLOT_OLD_END - 3)
    c.line(u0 * MM, v0 * MM, u1 * MM, v0 * MM)
    c.setDash()

    # Receiver footprint, dotted
    c.setDash(1, 2)
    c.setLineWidth(0.5)
    x0, x1, y0, y1 = RECEIVER
    ua, va = P(x1, y1)
    ub, vb = P(x0, y0)
    c.rect(ua * MM, va * MM, (ub - ua) * MM, (vb - va) * MM, stroke=1, fill=0)
    c.setDash()

    # Trim lines on the crossbar
    c.setDash(3, 2)
    c.setLineWidth(0.5)
    for name, y in TRIM:
        ua, v = P(106, y)
        ub, _ = P(STEM_X, y)
        c.line(ua * MM, v * MM, ub * MM, v * MM)
        c.setFont("Helvetica-Bold", 8)
        c.drawString((ub + 1.2) * MM, (v - 1.2) * MM, name)
    c.setDash()

    # Labels
    c.setFont("Helvetica", 7.5)
    u, v = P(0, -7)
    c.drawCentredString(u * MM, v * MM, "cup screw")
    u, v = P(-22, 31)
    c.drawCentredString(u * MM, v * MM, "the receiver goes here (do not cut)")
    u, v = P(57, -66.5)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(u * MM, v * MM, "new crossbar: it sits in the nook where the cover meets the wheel")
    u, v = P(58, 12)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(u * MM, v * MM, "cut this out:")
    c.drawCentredString(u * MM, (v - 4) * MM, "the tilt lever's room")

    c.saveState()
    u, v = P(91.3, 10)
    c.translate(u * MM, v * MM)
    c.rotate(90)
    c.setFont("Helvetica", 7)
    c.drawCentredString(0, 0, "second screw: anywhere in this slot (now 14 mm longer toward the dash)")
    c.restoreState()

    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(150 * MM, 108 * MM, "BOTTOM EDGE: TOWARD THE DASH")
    c.saveState()
    c.translate(16 * MM, 165 * MM)
    c.rotate(90)
    c.drawCentredString(0, 0, "DRIVER'S DOOR SIDE")
    c.restoreState()
    c.saveState()
    c.translate(200 * MM, 228 * MM)
    c.rotate(-90)
    c.drawCentredString(0, 0, "KEY SIDE")
    c.restoreState()

    # Scale bars
    ruler_across(c, 20, 88, 100, 10, 1, lambda d: str(int(round(d))), "100 mm across: it must measure exactly 100 mm")
    ruler_across(c, 20, 73, 101.6, 25.4, 25.4 / 8, lambda d: str(int(round(d / 25.4))),
                 "4 in across: it must measure exactly 4 in")
    ruler_up(c, 203, 100, 100)
    c.saveState()
    c.translate(206.5 * MM, 150 * MM)
    c.rotate(90)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(0, 0, "100 mm up and down: it must measure exactly 100 mm")
    c.restoreState()

    # Notes
    notes = [
        "1. Print it exactly the way you printed the first one. It is drawn 5.8% big, because your printer shrinks a",
        "    page to 94.5% (the first one's 4 in bar came out 4 1/32 in), so it should come out full size.",
        "2. Before cutting, measure the three bars. Each must be exactly 100 mm or 4 in. If not, tell me what they measure.",
        "3. Cut on the solid line, and cut out both slots. The middle is open: that is the tilt lever's room.",
        "4. Hold it up under the column, printed side down, top edge toward the wheel: the cup screw in the short",
        "    slot, the second screw in the long one.",
        "5. Check three things: the tilt lever goes all the way down and back up without touching the paper; the",
        "    wheel turns lock to lock without touching it; the crossbar sits in the nook.",
        "6. If the crossbar's top edge touches anything, cut it back to line A, B or C, and tell me which line.",
        "    C is as narrow as the crossbar can be.",
    ]
    c.setFont("Helvetica", 8.3)
    v = 60
    for line in notes:
        c.drawString(20 * MM, v * MM, line)
        v -= 4.3
    c.restoreState()
    c.showPage()
    c.save()


def before_after(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(7, 7.6), dpi=150)

    def uv(pts):
        return [(-x, -y) for x, y in pts]

    ax.add_patch(Polygon(uv(OLD), closed=True, fill=False, ls="--", lw=1.3, ec="#9a9a9a"))
    ax.add_patch(Polygon(uv(NEW), closed=True, fc="#dfe9f7", ec="#1f4e9a", lw=2))
    for x0, y0, x1, y1, w in [(97, -40, 97, 62, 6), (-10, 0, 10, 0, 6)]:
        if x0 == x1:
            ax.add_patch(FancyBboxPatch((-(x0 + w / 2), -max(y0, y1)), w, abs(y1 - y0), boxstyle="round,pad=0,rounding_size=3",
                                        fc="white", ec="#1f4e9a", lw=1.2))
        else:
            ax.add_patch(FancyBboxPatch((-max(x0, x1), -(y0 + w / 2)), abs(x1 - x0), w, boxstyle="round,pad=0,rounding_size=3",
                                        fc="white", ec="#1f4e9a", lw=1.2))
    x0, x1, y0, y1 = RECEIVER
    ax.add_patch(plt.Rectangle((-x1, -y1), x1 - x0, y1 - y0, fill=False, ls=":", ec="#1f4e9a"))
    for name, y in TRIM:
        ax.plot([-106, -STEM_X], [-y, -y], ls="--", lw=0.8, c="#1f4e9a")
        ax.text(-STEM_X + 1.5, -y, name, va="center", fontsize=8, color="#1f4e9a", fontweight="bold")
    ax.text(-57, 61, "new crossbar\n(in the nook)", ha="center", va="center", fontsize=9, color="#1f4e9a")
    ax.text(-58, -15, "tilt lever's room\n(open)", ha="center", va="center", fontsize=9)
    ax.text(-40, -94, "old crossbar and link: gone", ha="center", va="center", fontsize=9, color="#777")
    ax.text(-115, -55, "slot\n14 mm\nlonger", ha="right", va="center", fontsize=8.5, color="#1f4e9a")
    ax.annotate("", xy=(-100, -60), xytext=(-113, -55), arrowprops=dict(arrowstyle="->", color="#1f4e9a", lw=0.8))
    ax.text(0, 7.5, "cup screw", ha="center", fontsize=8)
    ax.text(-22, -31, "receiver", ha="center", va="center", fontsize=8)
    ax.text(-23, 86, "TOWARD THE WHEEL", ha="center", fontsize=9, fontweight="bold")
    ax.text(-23, -110, "TOWARD THE DASH", ha="center", fontsize=9, fontweight="bold")
    ax.text(-130, -15, "driver's door side", rotation=90, ha="center", va="center", fontsize=8.5)
    ax.text(70, -15, "key side", rotation=-90, ha="center", va="center", fontsize=8.5)
    ax.plot([], [], ls="--", c="#9a9a9a", label="first paper shape")
    ax.plot([], [], c="#1f4e9a", lw=2, label="new shape (v2)")
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    ax.set_xlim(-140, 78)
    ax.set_ylim(-118, 96)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Frame plate v2, seen from below (as on the paper)", fontsize=11)
    fig.tight_layout()
    fig.savefig(path)


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    paper_template(f"{out}/frame-plate-v2-paper-template-your-printer.pdf", YOUR_PRINTER)
    paper_template(f"{out}/frame-plate-v2-paper-template-100.pdf", 1.0)
    before_after(f"{out}/frame-plate-v2-before-after.png")
    print("printer scale", round(YOUR_PRINTER, 4), "drawn", round(1 / YOUR_PRINTER, 4))
EOF
cd /home/claude/deliver/hardware/cad && python3 platefit2.py /home/claude/deliver/hardware/print
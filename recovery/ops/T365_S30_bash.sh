cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
import re
s=open('platefit2.py').read()
s=s.replace('''    # Old end of the long slot, thin dashed, for reference
    c.setDash(1.5, 1.5)
    c.setLineWidth(0.3)
    u0, v0 = P(sx - 3, LONG_SLOT_OLD_END - 3)
    u1, _ = P(sx + 3, LONG_SLOT_OLD_END - 3)
    c.line(u0 * MM, v0 * MM, u1 * MM, v0 * MM)
    c.setDash()

''','')
s=s.replace('''    c.drawCentredString(108 * MM, 262 * MM, "Frame plate fit test v2: paper template, scaled for your printer")''',
'''    full = abs(printer_scale - 1) < 1e-9
    c.drawCentredString(108 * MM, 262 * MM, "Frame plate fit test v2: paper template, " +
                        ("full size (print at 100%)" if full else "scaled for your printer"))''')
s=s.replace('''    notes = [
        "1. Print it exactly the way you printed the first one. It is drawn 5.8% big, because your printer shrinks a",
        "    page to 94.5% (the first one's 4 in bar came out 4 1/32 in), so it should come out full size.",''',
'''    first = ([
        "1. Print at 100% (actual size, not fit to page).",
    ] if full else [
        "1. Print it exactly the way you printed the first one. It is drawn %.1f%% big, because your printer shrinks a"
        % ((1 / printer_scale - 1) * 100),
        "    page to %.1f%% (the first one's 4 in bar came out 4 1/32 in), so it should come out full size."
        % (printer_scale * 100),
    ])
    notes = first + [''')
s=s.replace('''    ax.text(-57, 61, "new crossbar\\n(in the nook)", ha="center", va="center", fontsize=9, color="#1f4e9a")''',
'''    ax.text(-57, 51.5, "new crossbar (in the nook)", ha="center", va="center", fontsize=9, color="#1f4e9a")''')
s=s.replace('''    ax.text(-22, -31, "receiver", ha="center", va="center", fontsize=8)''','''    ax.text(22, -30, "receiver", ha="center", va="center", fontsize=8)''')
open('platefit2.py','w').write(s)
EOF
grep -n "LONG_SLOT_OLD_END\|full\b\|receiver\", ha" platefit2.py | head; python3 platefit2.py /home/claude/deliver/hardware/print && cd ../print && python3 -c "
import pdfplumber
for n in ['your-printer','100']:
  with pdfplumber.open(f'frame-plate-v2-paper-template-{n}.pdf') as pdf:
    pg=pdf.pages[0]; print(n, pg.extract_text().splitlines()[0]); print([l for l in pg.extract_text().splitlines() if l.startswith('1.') or 'page to' in l])
"
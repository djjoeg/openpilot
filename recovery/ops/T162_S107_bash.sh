cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && python3 - <<'EOF'
p = "drawing.py"
s = open(p).read()
s = s.replace('''ax.set_ylabel("towards 4 o'clock  (mm)  towards 6 o'clock", fontsize=9)''',
              '''ax.set_ylabel("towards 6 o'clock   (mm)   towards 4 o'clock", fontsize=9)''')
old = s[s.index('lab = dict(fontsize=9, color="#222", zorder=9)'):s.index('ax.set_xlim(225, 30)')]
new = '''lab = dict(fontsize=9, color="#222", zorder=9)
def note(text, xy, xytext, color="#222", ha="center"):
  ax.annotate(text, xy=xy, xytext=xytext, ha=ha, va="center", fontsize=9, color=color, zorder=9,
              arrowprops=dict(arrowstyle="-", lw=0.7, color="#555", shrinkA=0, shrinkB=2))
note("steering wheel\\n(the round part you hold)", (R_IN + 6, 70), (200, 84))
note("teeth piece", (t.w_out - 2, -30), (205, -50))
note("gear (no roller now)", (F + 13, -10), (196, -30))
note("finger guard", (F + 22, 20), (205, 30))
note("motor", (F - 25, -5), (120, -50))
note("board cover", (F - 46, -10), (95, -50))
note("motor bracket: its flange\\nbolts to the rail's block", (F - 40, 29), (88, 66))
note("mounting plate (fixed),\\nthe rail on it", (F - 75, 47), (62, 82))
note("latch knob:\\npull it to let go", (F - 12, 64), (170, 52), color=C["plunger"])
note("power switch", (F + 11, 27), (196, 8))
note("spring", (F - 74, 30), (52, 22))
'''
s = s.replace(old, new)
s = s.replace('''ax.text(52, ZA, "?\\nis this\\nclear, all the\\nway round as the\\nsteering wheel\\nturns?", ha="center", va="center", fontsize=10, color="#8a5a00")''',
              '''ax.text(48, ZA - 4, "?", ha="center", va="center", fontsize=22, color="#8a5a00")
ax.text(100, -96, "is this band clear 88 mm in from the inside edge,\\nall the way round as the steering wheel turns?",
        ha="center", va="center", fontsize=9.5, color="#8a5a00")''')
s = s.replace('''for x0, txt, y in ((cap_in, f"motor in: its back end {R_IN - cap_in:.0f} mm in from the inside edge", -106),
                   (cap_in - S.STROKE, f"slid in: {R_IN - cap_in + S.STROKE:.0f} mm in", -121)):''',
'''for x0, txt, y in ((cap_in, f"motor in: its back end {R_IN - cap_in:.0f} mm in from the inside edge", -108),
                   (cap_in - S.STROKE, f"slid in: {R_IN - cap_in + S.STROKE:.0f} mm in", -121)):''')
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 900 python3 drawing.py . 2>&1 | tail -2
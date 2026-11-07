cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && python3 - <<'EOF'
p = "drawing.py"
s = open(p).read()
s = s.replace('note("teeth piece", (t.w_out - 2, -30), (205, -50))', 'note("teeth piece", (178, -30), (205, -50))')
s = s.replace('note("latch knob:\\npull it to let go", (F - 12, 64), (170, 52), color=C["plunger"])',
              'note("latch knob:\\npull it to let go", (F - 6, 70), (122, 86), color=C["plunger"])')
s = s.replace('note("motor bracket: its flange\\nbolts to the rail\'s block", (F - 40, 29), (88, 66))',
              'note("motor bracket: its flange\\nbolts to the rail\'s block", (F - 40, 29), (80, 64))')
s = s.replace('note("mounting plate (fixed),\\nthe rail on it", (F - 75, 47), (62, 82))',
              'note("mounting plate (fixed),\\nthe rail on it", (F - 75, 47), (62, 84))')
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 900 python3 drawing.py . 2>&1 | tail -1
python3 - <<'EOF'
p='visuals.py'; s=open(p).read()
a='''         titles=["from your seat: the motor outside the rim at 4 o'clock, shaft pointing at the wheel's middle",
                 "from below, the wheel at the top (as in your photos)",
                 "from your right and below", "from the passenger's side (the right)"],
         suptitle="The right arm mount v3, assembled, the motor slid up against its stop: gear in the teeth, lane keeping "
                  "on. Plate light grey (on the column cover, not drawn), the arm blue, the motor carrier green, motor "
                  "dark, gear and teeth orange, the wing bolts and nuts steel, a piece of the wheel grip grey.")'''
assert a in s
s=s.replace(a,'''         titles=["from your seat: the motor outside the rim just above 4 o'clock, shaft pointing at the wheel's middle",
                 "from below, the wheel at the top (as in your photos)",
                 "from your right and below", "from the passenger's side (the right)"],
         suptitle="The right arm mount v4, assembled, the motor slid up against its stop: gear in the teeth, lane keeping "
                  "on. Plate light grey (on the column cover, not drawn), the arm blue, the motor carrier green, motor "
                  "dark, gear and teeth orange, the bolts, nuts and washer steel, a piece of the wheel grip grey.")''')
open(p,'w').write(s)
EOF
cat /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v3d/rightcheck.log 2>/dev/null | tail -5
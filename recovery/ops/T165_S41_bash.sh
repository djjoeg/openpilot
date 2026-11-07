cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sidemock && python3 - <<'EOF'
p = "side_export.py"
s = open(p).read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:80], s.count(old))
    s = s.replace(old, new)
sub('''along -z by s (0 latched out, 40 slid in); the gear turns about z; the plunger's pin and knob move along -x; the
spring's strip and the switch's lever stretch along z.''', '''along -z by s (0 latched out, 40 slid in); the gear turns about z; the lever swings about its pin (along z) towards
the dash by up to SLOT_DEG (0 in a notch, SLOT_DEG in its slot); the spring's strip and the switch's lever stretch
along z.''')
sub('''pl = S.plunger(0.0)
sw = S.switch(0.0)''', '''sw = S.switch(0.0)''')
sub('''  ("plunger", "fixed", "steel", pl["fixed"]),
''', '')
sub('''  ("pin", "pin", "steel", pl["pin"]),
  ("knob", "pin", "knob", pl["knob"]),
''', '')
sub('''  ("clamp", "moving", "clamp", sp["clamp"]),''', '''  ("clamp", "moving", "clamp", sp["clamp"]),
  ("lever_pin", "moving", "steel", parts["lever's pin"]),
  ("lever", "lever", "knob", parts["lever"]),''')
sub('''ss = [round(float(s), 2) for s in np.arange(-0.2, S.STROKE + 1e-6, 0.25)]
pin_back = [round(S.pin_back_at(s), 3) for s in ss]
''', '')
sub('''  "slide": {"s": ss, "pin_back": pin_back},''', '''  "pivot": [S.PIVOT[0], S.PIVOT[1]], "slot_deg": S.SLOT_DEG,''')
sub('''"plate": mid("plate", (0.0, 0.5, 0.25)), "rail": mid("rail", (1.0, 0.5, 0.2)), "knob": mid("knob", (0.0, 0.5, 0.5)),''',
    '''"plate": mid("plate", (0.0, 0.5, 0.25)), "rail": mid("rail", (1.0, 0.5, 0.2)),
    "knob": [S.PIVOT[0] - S.KNOB_D, S.PIVOT[1], sum(S.LEVER_Z) / 2],''')
open(p, "w").write(s)
EOF
grep -n "pin_back\|plunger\|\"pin\"\|knob" side_export.py
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fitaudit && python3 - <<'EOF'
p = "fit_audit.py"
s = open(p).read()
s = s.replace('''import json
import math
import sys
''', '''import dataclasses
import json
import sys
''')
s = s.replace('''fits = {}
for tilt in P.COLUMN_TILT_RANGE[:1] + (P.COLUMN_TILT,) + P.COLUMN_TILT_RANGE[1:]:
  fits[tilt] = AS.solve(t, P.ARM_PIVOT_UP, P.ARM_PIVOT_FORWARD, tilt)''', '''parts["arm"] = MP.arm(130.0)
fits = {}
for tilt in P.COLUMN_TILT_RANGE[:1] + (P.COLUMN_TILT,) + P.COLUMN_TILT_RANGE[1:]:
  sol = AS.solve(t, P.ARM_PIVOT_UP, P.ARM_PIVOT_FORWARD, tilt)
  fits[tilt] = dataclasses.replace(sol, ok=True, arm_len=130.0, slide=sol.reach - 130.0, notes=[])''')
s = s.replace('''  for sx in (-1, 1):
    x = MP.SW_X + sx * P_SW_PITCH / 2 if False else MP.SW_X + sx * MP.SW_PITCH / 2
    shank = AS.cyl(1.0, MP.CAGE_FRONT[1] - 16.0, MP.CAGE_FRONT[1], x, MP.SW_HOLES, 24) if False else None
    # along z: from the front face (CAGE_FRONT[1]) back 16 mm; head 3.8 x 2 in front
    s = cyl(1.0''', '''  for sx in (-1, 1):
    x = MP.SW_X + sx * MP.SW_PITCH / 2
    # along z: from the front wall's face (CAGE_FRONT[1]) back 16 mm; head 3.8 across, 2 tall, in front
    s = cyl(1.0''')
s = s.replace('''  lb = A._carried(MP.lever_in_carrier(LB, 0.0) if False else LB, 0.0)''', '''  lb = A._carried(LB, 0.0)''')
open(p, "w").write(s)
EOF
grep -n "cyl(1.0, MP.CAGE_FRONT" fit_audit.py; grep -n "def cyl\b\|def cyl(" /home/claude/deliver/hardware/cad/cadlib.py; sed -n "$(grep -n 'def cyl(' /home/claude/deliver/hardware/cad/cadlib.py | cut -d: -f1),+8p" /home/claude/deliver/hardware/cad/cadlib.py; grep -n "def cyl_x\|def cyl_y" -A6 /home/claude/deliver/hardware/cad/cadlib.py | head -20
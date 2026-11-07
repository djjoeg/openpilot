python3 - <<'EOF'
p = "sideassembly.py"
s = open(p).read()
s = s.replace('''"spring's coil and spool": sp["coil"] + self.p["spool"],''', '''"spring's coil and spool": sp["coil"] + self.p["spool"].translate((S.SPOOL_X, 0.0, S.SPOOL_Z)),''')
open(p, "w").write(s)
EOF
grep -n "spring's coil and spool\": sp" sideassembly.py
cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/run_internal.py <<'EOF'
import time, sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import sideparts as S
import sideassembly as SA
from cadlib import union
t0 = time.time()
mb = S.motor_board()
p = {"t": S.SideTeeth(), "teeth": None, "gear": S.side_gear(), "gear_teeth_only": S.side_gear_teeth_only(),
     "bracket": S.side_bracket(), "plate": S.side_plate(), "spool": S.side_spool(),
     "motor": union([mb["motor"], mb["board+cap"], mb["car plug"], mb["motor plug"], mb["motor's own plug"]]),
     "rail": S.rail(), "block": S.block(), "block screws": S.block_screws()}
A = SA.SideAssembly(p)
res = SA.internal(A)
bad = sorted([(k, v) for k, v in res.items() if v[0] > 1e-3 and "touching" not in k], key=lambda kv: -kv[1][0])
print("internal: over 0.001 mm3:", bad)
# closest approaches between moving and fixed over the slide
import numpy as np
worst = {}
for s in [0.0, 0.2, 1, 2, 5, 10, 15, 20, 25, 30, 35, 40]:
    mv, fx = A.movers(s), A.fixed(s)
    for mn, m in mv.items():
        for fn, f in fx.items():
            if (mn, fn) in SA.EXPECTED:
                continue
            g = m.min_gap(f, 3.0)
            if g < worst.get((mn, fn), (99, None))[0]:
                worst[(mn, fn)] = (round(g, 2), s)
for k, v in sorted(worst.items(), key=lambda kv: kv[1][0]):
    if v[0] < 3.0:
        print("  closest", k, v)
print("time", round(time.time() - t0, 1))
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/run_internal.py
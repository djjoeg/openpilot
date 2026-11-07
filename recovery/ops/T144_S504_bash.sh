cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > springx.py <<'EOF'
"""If the springs sat closer together (a narrower hinge), would they clear the tab and the key below 4:45?"""
import os, sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import numpy as np
import carref as CR
import popassembly as PA, popparts as PP
from run_u import build
from mindist import min_dist
t, parts = build()
A = PA.PopAssembly(t, parts)
a = (CR.KEY_CLOCK_DEG, CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG)
b = CR.bezel(*a)
KEY = CR.key_bulge(*a) + b["ring"] + CR.key_in(*a)
ROOM = CR.key_turn_room(*a)
lo = (CR.KEY_RANGE["clock_deg"][0], CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG)
b2 = CR.bezel(*lo)
KEY_LO = CR.key_bulge(*lo) + b2["ring"] + CR.key_in(*lo)
ROOM_LO = CR.key_turn_room(*lo)
TAB = A.tilt_lever()
def g(x, y):
    v = (x ^ y).volume()
    return f"OVER {v:.0f}" if v > 0.5 else f"{min_dist(x, y, 1.5)[0]:.1f}"
for sx in [float(v) for v in sys.argv[1].split(",")]:
    PP.SPRING_X = sx
    for target in [float(v) for v in sys.argv[2].split(",")]:
        d = target - PP.MOUNT_DEG
        out = []
        for lift in (0.0, PP.LIFT_OFF):
            m = (A.springs(lift) + A.bolts(lift)).rotate((0, 0, d))
            out.append(f"lift {lift:.0f}: tab {g(m, TAB):>9s} key {g(m, KEY):>9s} hand {g(m, ROOM):>9s} | key at 3:52: key {g(m, KEY_LO):>9s} hand {g(m, ROOM_LO):>9s}")
        print(f"springs at +-{sx:.0f}, mount at {target:+.0f}:  " + "  ||  ".join(out), flush=True)
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 springx.py 25,22 -60,-63,-66 2>&1 | tail -8
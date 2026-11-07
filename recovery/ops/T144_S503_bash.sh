cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > anglescan3.py <<'EOF'
import os, sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import numpy as np
import carref as CR
import popassembly as PA, popparts as PP
from cadlib import union
from run_u import build
from mindist import min_dist
t, parts = build()
A = PA.PopAssembly(t, parts)
PARTS = {"motor": lambda l: A.motor(l) + A.gear(l), "carrier": A.carrier, "springs": A.springs, "bolts": A.bolts}
a = (CR.KEY_CLOCK_DEG, CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG)
b = CR.bezel(*a)
KEY = CR.key_bulge(*a) + b["ring"] + CR.key_in(*a)
ROOM = CR.key_turn_room(*a)
TAB = A.tilt_lever()
def g(x, y):
    v = (x ^ y).volume()
    return f"OVER {v:.0f}" if v > 0.5 else f"{min_dist(x, y, 2.0)[0]:.1f}"
for target in [float(v) for v in sys.argv[1].split(",")]:
    d = target - PP.MOUNT_DEG
    print(f"motor at {target:+.0f}:")
    for pn, f in PARTS.items():
        on, off = f(0.0).rotate((0, 0, d)), f(PP.LIFT_OFF).rotate((0, 0, d))
        print(f"   {pn:8s} on: key {g(on, KEY):>10s} hand {g(on, ROOM):>10s} tab {g(on, TAB):>10s} | off: key {g(off, KEY):>10s} hand {g(off, ROOM):>10s} tab {g(off, TAB):>10s}", flush=True)
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 anglescan3.py -58,-62,-66 2>&1 | tail -16
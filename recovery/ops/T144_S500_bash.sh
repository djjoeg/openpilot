cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > anglescan2.py <<'EOF'
import os, sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import numpy as np
import carref as CR
import popassembly as PA, popparts as PP
from cadlib import union, box
from run_u import build
from mindist import min_dist
t, parts = build()
A = PA.PopAssembly(t, parts)
def mob(l):
    return A.motor(l) + A.carrier(l) + A.springs(l) + A.bolts(l) + A.gear(l)
ON, OFF = mob(0.0), mob(PP.LIFT_OFF)
SWING = union([mob(l) for l in (10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0)])
BLOCK = A.block() + A.switch()
KEYS = {"best": (CR.KEY_CLOCK_DEG, CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG),
        "low": (CR.KEY_RANGE["clock_deg"][0], CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG),
        "low+out+fwd": (CR.KEY_RANGE["clock_deg"][0], CR.KEY_RANGE["r"][1], CR.KEY_RANGE["z"][1], CR.KEY_RANGE["tilt_deg"][1]),
        "low+back": (CR.KEY_RANGE["clock_deg"][0], CR.KEY_R, CR.KEY_RANGE["z"][0], CR.KEY_RANGE["tilt_deg"][0])}
def key_solid(a):
    b = CR.bezel(*a)
    return CR.key_bulge(*a) + b["ring"] + CR.key_in(*a)
K = {n: (key_solid(a), CR.key_turn_room(*a)) for n, a in KEYS.items()}
TAB_REST = PA.tab_lever(0.0)
TAB_ALL = A.tilt_lever()
def g(a, b):
    v = (a ^ b).volume()
    return f"OVER {v:.0f}" if v > 0.5 else f"{min_dist(a, b, 2.0)[0]:.1f}"
for target in [float(v) for v in sys.argv[1].split(",")]:
    d = target - PP.MOUNT_DEG
    on, off, sw, bl = (m.rotate((0, 0, d)) for m in (ON, OFF, SWING, BLOCK))
    print(f"motor at {target:+.0f} deg:")
    for kn, (ks, room) in K.items():
        print(f"   key {kn:12s} on/key {g(on, ks):>10s}  on/hand {g(on, room):>10s}  off/key {g(off, ks):>10s}  off/hand {g(off, room):>10s}  swing/key {g(sw, ks):>10s}  block/key {g(bl, ks):>10s}", flush=True)
    print(f"   tab: on/tab+fingers {g(on, TAB_ALL)}  off/tab+fingers {g(off, TAB_ALL)}  swing/tab at rest {g(sw, TAB_REST)}  block/tab+fingers {g(bl, TAB_ALL)}", flush=True)
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 anglescan2.py -48,-52,-56 2>&1 | tail -30
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > anglescan.py <<'EOF'
"""Where round the column can the mount sit? The current mount's parts turned to each angle, against the key (best
place and the ends of its range), the adjustment tab and your fingers on it, and the covers: overlap volume and gap."""
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
movers = {"motor+carrier on": A.motor() + A.carrier() + A.springs() + A.bolts(),
          "swinging": union([A.motor(l) + A.carrier(l) + A.springs(l) + A.bolts(l) for l in (10.0, 25.0, 40.0, 55.0, 65.0, PP.LIFT_OFF)])}
def key_set(clock, r, z, tilt):
    b = CR.bezel(clock, r, z, tilt)
    return CR.key_bulge(clock, r, z, tilt) + b["ring"] + CR.key_in(clock, r, z, tilt) + CR.key_turn_room(clock, r, z, tilt)
keys = {"best": key_set(CR.KEY_CLOCK_DEG, CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG),
        "low": key_set(CR.KEY_RANGE["clock_deg"][0], CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG),
        "low+out": key_set(CR.KEY_RANGE["clock_deg"][0], CR.KEY_RANGE["r"][1], CR.KEY_Z, CR.KEY_TILT_DEG),
        "low+fwd": key_set(CR.KEY_RANGE["clock_deg"][0], CR.KEY_R, CR.KEY_RANGE["z"][1], CR.KEY_RANGE["tilt_deg"][1])}
tab = A.tilt_lever()
for target in [float(v) for v in sys.argv[1].split(",")]:
    d = target - PP.MOUNT_DEG
    row = []
    for mn, m in movers.items():
        mm = m.rotate((0, 0, d))
        for kn, k in keys.items():
            v = (mm ^ k).volume()
            g = 0.0 if v > 0.5 else min_dist(mm, k, 3.0)[0]
            row.append(f"{mn}/key {kn}: " + (f"OVERLAP {v:.0f}" if v > 0.5 else f"gap {g:.1f}"))
        v = (mm ^ tab).volume()
        g = 0.0 if v > 0.5 else min_dist(mm, tab, 3.0)[0]
        row.append(f"{mn}/tab+fingers: " + (f"OVERLAP {v:.0f}" if v > 0.5 else f"gap {g:.1f}"))
    print(f"motor at {target:+.0f} deg:\n   " + "\n   ".join(row), flush=True)
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 anglescan.py -50,-54,-58,-62 2>&1 | tail -45
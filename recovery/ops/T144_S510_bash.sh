cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > tabsplit.py <<'EOF'
import os, sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import numpy as np
import popassembly as PA, popparts as PP
from cadlib import box, union
from run_u import build
from mindist import min_dist
t, parts = build()
A = PA.PopAssembly(t, parts)
sweep = union([PA.tab_lever(float(a)) for a in np.arange(0.0, PA.TAB_SWING + 1e-9, 4.0)])
fingers = box(*PA.TAB_FINGERS)
def g(x, y):
    v = (x ^ y).volume()
    return f"OVER {v:.0f}" if v > 0.5 else f"{min_dist(x, y, 1.5)[0]:.1f}"
for target in (-60.0, -63.0, -66.0):
    d = target - PP.MOUNT_DEG
    for lift in (0.0, PP.LIFT_OFF):
        m = (A.springs(lift) + A.bolts(lift)).rotate((0, 0, d))
        bb = (m ^ fingers).bounding_box() if (m ^ fingers).volume() > 0.5 else None
        print(f"{target:+.0f} lift {lift:.0f}: springs+bolts vs paddle sweep {g(m, sweep):>10s}, vs fingers box {g(m, fingers):>10s}", ("overlap box " + str([round(v) for v in bb])) if bb else "")
EOF
PYTHONPATH=/home/claude/pylib timeout 1500 python3 tabsplit.py 2>&1 | tail -8
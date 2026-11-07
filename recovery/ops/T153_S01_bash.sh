cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > fitD2.py <<'EOF'
import os, sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
import numpy as np
import popparts as PP
import carscene as CS
from cadlib import box
from params import NEMA, NEMA_LEN
h = NEMA / 2
pieces = {
  "board only": box(-h, h, -h, h, -NEMA_LEN - 14.0, -NEMA_LEN),
  "board's car plug (to dash)": box(-6, 6, h, h + 14, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0),
  "motor's own plug (to dash)": box(-8, 8, h, h + 12, -NEMA_LEN + 2.0, -NEMA_LEN + 18.0),
  "board's motor plug (side)": box(-h - 14, -h, -6, 6, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0),
  "debug plug (side)": box(h, h + 5, -6, 6, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0),
}
def placed(m, deg):
    keep = PP.MOUNT_DEG; PP.MOUNT_DEG = deg
    try: return PP.to_wheel(m)
    finally: PP.MOUNT_DEG = keep
def gap(a, b, far=25.0):
    v = (a ^ b).volume()
    return -round(v) if v > 0.5 else round(a.min_gap(b, far), 1)
for D in (97.0, 103.0, 106.0, 110.0, 115.0):
    sc = CS.CarScene(D)
    cov, bc = sc.column_cover(), sc.back_cover()
    print(f"D {D:.0f}:")
    for deg in (-56.0, -63.0, -70.0):
        print(f"   mount {deg:+.0f}: " + "; ".join(f"{n}: cover {gap(placed(p, deg), cov)} back {gap(placed(p, deg), bc)}" for n, p in pieces.items()), flush=True)
EOF
PYTHONPATH=/home/claude/pylib timeout 1200 python3 fitD2.py
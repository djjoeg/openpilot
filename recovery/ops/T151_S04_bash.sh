cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > fitD.py <<'EOF'
"""The motor (engaged, core carrier without the old hinge parts) against the rebuilt car, for key depths D and mount angles."""
import os, sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
import numpy as np
import popparts as PP
import popassembly as PA
import carscene as CS
from core import core_carrier
from cadlib import union

mb = PP.motor_and_board()
board = mb["board"] + mb["plugs"]
motor = mb["body"]
carrier = core_carrier(with_knuckle=False)
gear = PP.pop_motor_gear()
parts = {"board+plugs": board, "motor": motor, "carrier": carrier, "gear": gear}

def placed(m, deg, slide=(0.0, 0.0)):
    keep = PP.MOUNT_DEG
    PP.MOUNT_DEG = deg
    try:
        return PP.to_wheel(m.translate((0.0, slide[0], slide[1])))
    finally:
        PP.MOUNT_DEG = keep

def gap(a, b, far=25.0):
    if (a ^ b).volume() > 0.5:
        return -round((a ^ b).volume())
    return round(a.min_gap(b, far), 1)

Ds = [float(v) for v in sys.argv[1].split(",")] if len(sys.argv) > 1 else [90.0, 97.0, 105.0, 112.0, 120.0]
angles = [float(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else [-50.0, -56.0, -63.0, -70.0]
for D in Ds:
    sc = CS.CarScene(D)
    car = {"column cover": sc.column_cover(), "back cover (swept)": sc.back_cover()}
    car.update(sc.key_parts())
    print(f"D {D:.0f}: cover underside {sc.cover_bottom:.1f}, front {sc.cover_front_z:.1f}; back cover rim r {sc.back_cover_rim[0]:.1f} z {sc.back_cover_rim[1]:.1f}")
    for deg in angles:
        row = []
        for pn, pm in parts.items():
            m = placed(pm, deg)
            for cn, cm in car.items():
                g = gap(m, cm)
                if g < 10:
                    row.append(f"{pn}/{cn}: {g}")
        print(f"   mount {deg:+.0f}: " + ("; ".join(row) if row else "all >= 10 mm"), flush=True)
EOF
PYTHONPATH=/home/claude/pylib timeout 1200 python3 fitD.py
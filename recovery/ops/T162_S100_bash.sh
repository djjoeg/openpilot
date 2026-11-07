mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/shots.py <<'EOF'
"""Quick look at the side-slide mount: motor in and slid in, seen from behind the steering wheel."""
import math, sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import render as R
import sideparts as S
import sideassembly as SA
import faceparts as FP
import popparts as PP
from cadlib import revolve, union, box, cyl
t0 = time.time()
parts = SA.build_parts()
A = SA.SideAssembly(parts)
t = A.t
# a piece of the steering wheel and the teeth piece round the motor
grip_pts = [(t.rr + (PP.GRIP_P / 2) * math.cos(a), (PP.GRIP_P / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 36, endpoint=False)]
grip = revolve(grip_pts, S.MOUNT_DEG - 45, S.MOUNT_DEG + 45, step_deg=1.5)
teeth = A.teeth(0.0)
C = {"grip": (0.25, 0.25, 0.27), "teeth": (0.80, 0.80, 0.78), "motor": (0.35, 0.40, 0.48), "bracket": (0.30, 0.55, 0.85),
     "gear": (0.90, 0.60, 0.20), "plate": (0.55, 0.75, 0.45), "rail": (0.70, 0.70, 0.75), "block": (0.55, 0.55, 0.60),
     "plunger": (0.85, 0.30, 0.30), "switch": (0.20, 0.20, 0.20), "spring": (0.75, 0.70, 0.30)}

def scene(s):
    mv, fx = A.movers(s), A.fixed(s)
    W = A.W
    sp = S.spring_parts(s)
    out = [(grip, C["grip"]), (teeth, C["teeth"]),
           (W(mv["motor, board and plugs"]), C["motor"]), (W(mv["motor bracket"]), C["bracket"]), (W(mv["gear"]), C["gear"]),
           (W(mv["block"]), C["block"]), (W(parts["plate"]), C["plate"]), (W(parts["rail"]), C["rail"]),
           (W(fx["plunger and nut"] + fx["plunger's knob"] + fx["plunger's pin"]), C["plunger"]),
           (W(fx["switch"]), C["switch"]), (W(fx["spring's coil and spool"] + sp["strip"]), C["spring"])]
    return out

a = math.radians(S.MOUNT_DEG)
radial = np.array([math.cos(a), math.sin(a), 0.0])
tang = np.array([-math.sin(a), math.cos(a), 0.0])     # towards 4 o'clock
views = {
  "behind": R.look(-np.array([0, 0, 1.0]) * 1.0 + 0.35 * tang - 0.25 * radial, [0, 1, 0]),
  "side": R.look(0.9 * tang - 0.5 * np.array([0, 0, 1.0]) + 0.2 * radial, [0, 0, 1]),
}
for name, rot in views.items():
    R.save(f"/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/q-{name}.png",
           [(scene(0.0), rot), (scene(S.STROKE), rot)], titles=["motor in (on the teeth)", "slid in 40 mm"], size=(900, 760))
    print(name, round(time.time() - t0), flush=True)
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 1800 python3 shots.py 2>&1 | tail -5
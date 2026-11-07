mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/run_wheel.py <<'EOF'
import time, sys, json
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import sideparts as S
import sideassembly as SA
t0 = time.time()
def log(*a):
    print(*a, f"[{time.time() - t0:.0f}s]", flush=True)
parts = SA.build_parts()
log("parts built; teeth vol", round(parts["teeth"].volume(), 1))
A = SA.SideAssembly(parts)
out = {}
out["mesh"] = SA.mesh_sweep(A); log("mesh", out["mesh"])
out["slide_out"] = SA.slide_out_of_teeth(A); log("slide out of teeth", out["slide_out"])
r = SA.wheel_turned(A)
out["wheel_turned"] = {k: (round(v[0], 3), v[1]) for k, v in r.items()}
log("wheel turned:", {k: v for k, v in out["wheel_turned"].items() if v[0] > 1e-3})
out["end_teeth"] = SA.end_teeth_meeting(A); log("end teeth", out["end_teeth"])
r = SA.slid_in(A)
out["slid_in"] = {k: round(v, 3) for k, v in r.items()}
log("slid in over 0.001:", {k: v for k, v in out["slid_in"].items() if v > 1e-3})
out["clearances"] = SA.clearances(A); log("clearances")
for row in out["clearances"]:
    print("   ", row)
out["car_estimates"] = SA.car_estimates(A); log("car estimates")
for row in out["car_estimates"]:
    print("   ", row)
json.dump(out, open("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/wheel_checks.json", "w"), indent=1, default=str)
log("done")
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && echo started
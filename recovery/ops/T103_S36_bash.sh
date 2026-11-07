sed -n 286,294p accord_lka_parts.py && cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side_test.py <<'EOF'
import time, sys, os
import numpy as np
sys.path.insert(0, '/home/claude/deliver/hardware/cad')
import columnassembly as CA, columnparts as CP, mountparts as MP, wheelparts as WP, params as P
t0 = time.time()
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP, shallow=True)
fit = CA.solve_side()
base = {"gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(), "bracket": MP.lever_bracket(),
        "lever": MP.lift_lever(), "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab()}
parts = dict(base, teeth=CP.ring_teeth(t), hinge_block=MP.hinge_block(CP.ARM_NOMINAL_C), carrier=MP.motor_carrier(CP.GUARD_WINDOW_C),
             side_bracket=CP.side_bracket(), arm=MP.arm(fit.arm_len))
A = CA.SideAssembly(t, fit, parts)
print('parts built', round(time.time()-t0,1))
res = CA.check_all(A)
bad = {k: v for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)}
print(len(res), 'checks;', len(bad), 'bad', round(time.time()-t0,1))
for k, v in sorted(bad.items(), key=lambda kv: -kv[1])[:40]:
    print(f'  {v:10.2f}  {k}')
print('margins', CA.margins(A))
print('reach back', CA.reach_back(A))
import render as R
from cadlib import box
lift = MP.cam_lift(MP.A_OFF)
out = '/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sb'
R.save(out + '/side-assembly.png',
       [(CA.parts_scene(A), R.look((0, 0, 1), (0, 1, 0))), (CA.parts_scene(A, lift, MP.A_OFF), R.look((0, 0, 1), (0, 1, 0))),
        (CA.parts_scene(A), R.look((0, 1, 0), (0, 0, 1))), (CA.parts_scene(A), R.look((1.0, 0.8, 0.9), (0, 1, 0)))],
       ["from the driver's seat, lever down", "lever up", "from above", "3d"], size=(800, 800))
print('done', round(time.time()-t0,1))
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib timeout 1500 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side_test.py 2>&1 | tail -60
cd /home/claude/deliver/hardware/cad && cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side_render.py <<'EOF'
import sys
sys.path.insert(0, '/home/claude/deliver/hardware/cad')
import columnassembly as CA, columnparts as CP, mountparts as MP, wheelparts as WP, params as P
import render as R
from cadlib import box
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP, shallow=True)
fit = CA.solve_side()
parts = {"gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(), "bracket": MP.lever_bracket(),
         "lever": MP.lift_lever(), "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(),
         "teeth": CP.ring_teeth(t), "hinge_block": MP.hinge_block(CP.ARM_NOMINAL_C), "carrier": MP.motor_carrier(CP.GUARD_WINDOW_C),
         "side_bracket": CP.side_bracket(), "arm": MP.arm(fit.arm_len)}
A = CA.SideAssembly(t, fit, parts)
lift = MP.cam_lift(MP.A_OFF)
out = '/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sb/'
crop = box(-200, 330, -200, 200, -290, 40)
def sc(*a):
    return [(m ^ crop, c) for m, c in CA.parts_scene(A, *a) if not (m ^ crop).is_empty()]
behind = R.look((0.9, 0.35, -0.75), (0, 1, 0))     # from the passenger side, behind the wheel
above = R.look((0.5, 1.0, 0.45), (0, 0, -1))
R.save(out + 'side-render-behind.png', [(sc(), behind), (sc(lift, MP.A_OFF), behind)],
       ["lift lever on (handle pushed out)", "lift lever off (handle pulled in): gear lifted out of the ring"],
       suptitle="3 o'clock mount seen from the passenger side, behind the wheel: ring teeth on the back of the rim, motor, side bracket on the column covers, screw tab to the dash",
       size=(1000, 900))
R.save(out + 'side-render-above.png', [(sc(), above)], ["from above and to the right"], size=(1300, 1000))
print('ok')
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side_render.py
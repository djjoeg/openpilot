cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side_dbg.py <<'EOF'
import sys
sys.path.insert(0, '/home/claude/deliver/hardware/cad')
import columnassembly as CA, columnparts as CP, mountparts as MP, wheelparts as WP, params as P
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP, shallow=True)
fit = CA.solve_side()
parts = {"gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(), "bracket": MP.lever_bracket(),
         "lever": MP.lift_lever(), "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(),
         "teeth": CP.ring_teeth(t), "hinge_block": MP.hinge_block(CP.ARM_NOMINAL_C), "carrier": MP.motor_carrier(CP.GUARD_WINDOW_C),
         "side_bracket": CP.side_bracket(), "arm": MP.arm(fit.arm_len)}
A = CA.SideAssembly(t, fit, parts)
lift = MP.cam_lift(MP.A_OFF)
bb = lambda m: [round(v, 1) for v in m.bounding_box()]
print('lever down', bb(A.lever(0, 0)))
print('lever up  ', bb(A.lever(MP.A_OFF, lift + 0.05)))
ov = A.lever(MP.A_OFF, lift + 0.05) ^ A.covers()
print('lever up ^ covers', bb(ov), round(ov.volume(), 1))
ov = A.clamp() ^ A.rods(); print('bracket ^ bolts', bb(ov), round(ov.volume(), 1))
ov = A.arm() ^ A.rods(); print('arm ^ bolts', bb(ov), round(ov.volume(), 1))
ov = A.arm() ^ A.dash_at_screw(); print('arm ^ dash', bb(ov), round(ov.volume(), 1))
print('arm', bb(A.arm()), 'bracket', bb(A.clamp()), 'tab', bb(A.clamp_upper()))
print('hinge block', bb(A.hinge_block()), 'motor', bb(A.motor()), 'carrier', bb(A.carrier()))
EOF
PYTHONPATH=/home/claude/pylib timeout 600 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side_dbg.py
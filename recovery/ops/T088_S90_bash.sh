sed -i 's/Z_TEETH_SPLIT = Z_GEAR_TEETH_C\[0\] - 3.1/Z_TEETH_SPLIT = Z_GEAR_TEETH_C[0] - 3.4/' columnparts.py && sed -i 's/# move about 3 mm back along the column into the rolling band.s zone; from here forward the ring.s inside follows/# move about 3.2 mm back along the column into the rolling band'"'"'s zone; from here forward the ring'"'"'s inside follows/' columnparts.py && grep -n "Z_TEETH_SPLIT =" columnparts.py && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import params as P, columnparts as CP, columnassembly as CA, mountparts as MP, wheelparts as WP
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP)
fit = CA.solve()
parts = {"teeth": CP.ring_teeth(t), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(CP.GUARD_WINDOW_C), "hinge_block": MP.hinge_block(CP.ARM_NOMINAL_C), "bracket": MP.lever_bracket(), "lever": MP.lift_lever(),
         "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "clamp_lower": CP.column_clamp_lower(),
         "clamp_upper": CP.column_clamp_upper()}
A = CA.ColumnAssembly(t, fit, parts)
res = CA.check_all(A, lever_step=4.0)
bad = {k: round(v,3) for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)}
print(len(res), "checks;", len(bad), "bad:", bad)
EOF
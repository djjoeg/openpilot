sed -i 's/RING_BACK_Z = Z_GEAR_ROLLER_C\[0\] + 2.0     # the skirt.s back face: the roller.s back 2 mm hang off the rolling band, so/RING_BACK_Z = Z_GEAR_ROLLER_C[0] + 3.0     # the skirt'"'"'s back face: the roller'"'"'s back 3 mm hang off the rolling band, so/' columnparts.py && grep -n "RING_BACK_Z =" columnparts.py && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import time, json
t0=time.time()
import params as P, columnparts as CP, columnassembly as CA, mountparts as MP, wheelparts as WP
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP)
fit = CA.solve()
parts = {"teeth": CP.ring_teeth(t), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(CP.ARM_NOMINAL_C), "bracket": MP.lever_bracket(), "lever": MP.lift_lever(),
         "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "clamp_lower": CP.column_clamp_lower(),
         "clamp_upper": CP.column_clamp_upper()}
A = CA.ColumnAssembly(t, fit, parts)
res = CA.check_all(A, lever_step=2.0)
bad = {k: round(v,3) for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)}
print(len(res), "checks;", len(bad), "bad:", bad)
print("margins:", CA.margins(A))
print("ring back", CP.RING_BACK_Z, "flat from", CP.Z_ROLL_C[1] - (t.r_skirt_in - t.r_roll), "to", CP.RING_BACK_Z)
print(round(time.time()-t0,1), "s")
EOF
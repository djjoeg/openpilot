python3 - <<'EOF'
p='columnparts.py'; s=open(p).read()
old='''  step = t.r_root - t.r_roll
  zlo, zhi = Z_TEETH_SPLIT, -t.base.wz_out + 0.01
  cut = polar_mask(lambda a: min(t.inner_radius_at(a - 270.0) + step, t.r_out - 1.5), a0 - 0.5, a1 + 0.5, zlo, zhi)
  cut = cut - cyl(t.r_root - 0.01, zlo - 1, zhi + 1, segments=1440)
  body = body - cut'''
new='''  step = t.r_root - t.r_roll

  def teeth_zone_inside(a_deg: float) -> float:
    a = abs(a_deg - 270.0)
    return min(t.inner_radius_at(a) + step, t.r_out - 1.5) if a > t.roll_half else t.r_roll - 0.5

  zlo, zhi = Z_TEETH_SPLIT, -t.base.wz_out + 0.01
  cut = polar_mask(teeth_zone_inside, a0 - 0.5, a1 + 0.5, zlo, zhi)
  cut = cut - cyl(t.r_roll - 0.3, zlo - 1, zhi + 1, segments=1440)
  body = body - cut'''
assert old in s; s=s.replace(old,new)
s=s.replace("Z_TEETH_SPLIT = Z_GEAR_TEETH_C[0] - 3.2\n","Z_TEETH_SPLIT = Z_GEAR_TEETH_C[0] - 3.1\n")
open(p,'w').write(s); print("ok")
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import time, json
t0=time.time()
import params as P, columnparts as CP, columnassembly as CA, mountparts as MP, wheelparts as WP
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP)
fit = CA.solve()
parts = {"teeth": CP.ring_teeth(t), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(CP.GUARD_WINDOW_C), "hinge_block": MP.hinge_block(CP.ARM_NOMINAL_C), "bracket": MP.lever_bracket(), "lever": MP.lift_lever(),
         "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "clamp_lower": CP.column_clamp_lower(),
         "clamp_upper": CP.column_clamp_upper()}
print("ring", len(parts["teeth"].decompose()), parts["teeth"].status(), round(parts["teeth"].volume()/1000,1))
A = CA.ColumnAssembly(t, fit, parts)
res = CA.check_all(A, lever_step=4.0)
bad = {k: round(v,3) for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)}
print(len(res), "checks;", len(bad), "bad:", bad)
for w in (21.1, 22, 23, 24, 25, 26, 27, 28, 29):
  print("w", w, "drop", round(CA.roller_drop_deg(A, w),2))
print(round(time.time()-t0,1), "s")
EOF
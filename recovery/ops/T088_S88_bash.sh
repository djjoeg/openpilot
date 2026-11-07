python3 - <<'EOF'
p='columnassembly.py'; s=open(p).read()
old='''  worst = 0.0
  for w in np.arange(A.t.roll_half, A.t.half + 1.0, 0.5):
    drop = roller_drop_deg(A, float(w))
    for part in (A.gear(-drop), A.carrier(-drop)):
      for sign in (1, -1):
        worst = max(worst, overlap(A.teeth(sign * float(w)), part))
  res["ring's lead-in with the carrier dropping: teeth/gear and teeth/carrier (worst)"] = worst
  return res'''
new='''  worst = 0.0
  for w in np.arange(A.t.roll_half, A.t.half + 1.0, 0.5):
    drop = roller_drop_deg(A, float(w))     # the roller itself rests on the ring there, so it is left out
    for part in (A._carried(A.p["gear_teeth_only"], -drop), A.carrier(-drop)):
      for sign in (1, -1):
        worst = max(worst, overlap(A.teeth(sign * float(w)), part))
  res["ring's lead-in with the carrier dropping: teeth/gear teeth and teeth/carrier (worst)"] = worst
  return res'''
assert old in s; s=s.replace(old,new); open(p,'w').write(s); print("ok")
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
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
# the dash carrier (window 60) in the column mount: how much it would touch
parts2 = dict(parts, carrier=MP.motor_carrier())
A2 = CA.ColumnAssembly(t, fit, parts2)
res2 = CA.check_all(A2, lever_step=8.0)
print("with the dash carrier:", {k: round(v,3) for k, v in res2.items() if ("should touch" not in k and v > 1e-3)})
EOF
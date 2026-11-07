python3 - <<'EOF'
p='columnparts.py'; s=open(p).read()
old="Z_ROLL_C = (Z_GEAR_ROLLER_C[0] + 0.5, Z_TEETH_C[0])                 # the rolling band, behind them; its back end is\nRING_BACK_Z = Z_ROLL_C[0]                                           # the skirt's back face, 1 mm clear of the carrier's plate\n"
new="RING_BACK_Z = Z_GEAR_ROLLER_C[0] + 2.0     # the skirt's back face: the roller's back 2 mm hang off the rolling band, so\n                                           # the carrier's plate (1 mm behind the roller) clears the back face as it lifts\nZ_ROLL_C = (RING_BACK_Z, Z_TEETH_C[0])     # the rolling band, behind the teeth\n"
assert old in s; s=s.replace(old,new)
old="""      (self.r_roll, zr0),
      (self.r_roll, RING_BACK_Z), (self.r_out, RING_BACK_Z), (self.r_out, zf),"""
new="""      (self.r_roll, RING_BACK_Z), (self.r_out, RING_BACK_Z), (self.r_out, zf),"""
assert old in s; s=s.replace(old,new)
open(p,'w').write(s)
p='columnassembly.py'; s=open(p).read()
old="""  # the ring sweeping past the motor gear everywhere the gear is on it: every 2 degrees over the tracked arc
  worst = 0.0
  for w in np.arange(-A.t.roll_half, A.t.roll_half + 1e-9, 2.0):
    worst = max(worst, overlap(A.teeth(float(w)), G), overlap(A.teeth(float(w)), C))
  res["ring turned through its arc: teeth/gear and teeth/carrier (worst)"] = worst
  return res"""
new="""  # the ring turned through its arc with the motor gear turning with it (the same way, RING_TEETH / MOTOR_TEETH times
  # faster): the gear's teeth and roller and the carrier clear the ring at every 1 degree of steering wheel
  ratio = WP.RING_TEETH / WP.MOTOR_TEETH
  worst_gear = worst_carrier = 0.0
  for w in np.arange(-A.t.roll_half, A.t.roll_half + 1e-9, 1.0):
    Gw = A._carried(A.p["gear"].rotate((0, 0, float(w) * ratio)), 0.0)
    worst_gear = max(worst_gear, overlap(A.teeth(float(w)), Gw))
    worst_carrier = max(worst_carrier, overlap(A.teeth(float(w)), C))
  res["ring turned through its arc: teeth/gear (worst)"] = worst_gear
  res["ring turned through its arc: teeth/carrier (worst)"] = worst_carrier
  return res"""
assert old in s; s=s.replace(old,new)
open(p,'w').write(s); print("ok")
EOF
grep -n "RING_TEETH\|MOTOR_TEETH" /home/claude/deliver/hardware/cad/wheelparts.py | head -3
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
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
res = CA.check_all(A, lever_step=4.0)
bad = {k: round(v,2) for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)}
print(len(res), "checks;", len(bad), "bad:"); print(json.dumps(bad, indent=1))
print("margins:", CA.margins(A))
print("ring back", CP.RING_BACK_Z, "roll", CP.Z_ROLL_C, "teeth", CP.Z_TEETH_C, "gear roller", CP.Z_GEAR_ROLLER_C)
print(round(time.time()-t0,1), "s")
EOF
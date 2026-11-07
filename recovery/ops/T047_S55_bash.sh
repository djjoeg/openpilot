cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety && python3 - <<'EOF'
p = "safety_calc.py"
s = open(p).read()

# understeer variants: openpilot's generic tire model, and a car that understeers 3x as much
s = s.replace('''def vm_for(sr: float) -> VehicleModel:
  vm = VehicleModel(CP)
  vm.update_params(1.0, sr)
  return vm''', '''STIFF = {"openpilot's tire model": 1.0, "3x the understeer": 1.0 / 3.0}


def vm_for(sr: float, stiff: float = 1.0) -> VehicleModel:
  vm = VehicleModel(CP)
  vm.update_params(stiff, sr)
  return vm


def combos():
  for rn, sr in RATIOS.items():
    for un, k in STIFF.items():
      yield f"{rn} / {un}", vm_for(sr, k)''')

s = s.replace('''acc = {}
for name, sw in TEETH.items():
  acc[name] = {rn: round(U70 ** 2 * vm_for(sr).calc_curvature(sw * DEG, U70, 0.0), 2) for rn, sr in RATIOS.items()}
out["lateral_accel_70mph_at_teeth_end_m_s2"] = acc''', '''acc = {}
for name, sw in TEETH.items():
  vals = {cn: round(U70 ** 2 * vm.calc_curvature(sw * DEG, U70, 0.0), 2) for cn, vm in combos()}
  acc[name] = {"min": min(vals.values()), "max": max(vals.values()), "port_model": vals["the port's 15.3 / openpilot's tire model"], "all": vals}
out["lateral_accel_70mph_at_teeth_end_m_s2"] = acc
out["understeer_deg_per_g"] = {un: round(-calc_slip_factor(vm_for(15.3, k)) * VM.l * G / DEG, 2) for un, k in STIFF.items()}''')

# curves: min/max over all combos
s = s.replace('''  row = {"speed_mph": v, "radius_ft": rft, "radius_m": round(r), "bank": "6%",
         "steer_deg": {rn: round(steer_needed(vm_for(sr), r, u, math.atan(0.06)), 1) for rn, sr in RATIOS.items()},
         "steer_deg_flat_road": {rn: round(steer_needed(vm_for(sr), r, u, 0.0), 1) for rn, sr in RATIOS.items()},
         "sideways_accel_m_s2": round(u ** 2 / r, 2)}
  curves.append(row)''', '''  vals = {cn: round(steer_needed(vm, r, u, math.atan(0.06)), 1) for cn, vm in combos()}
  curves.append({"speed_mph": v, "radius_ft": rft, "radius_m": round(r), "bank": "6%",
                 "steer_min": min(vals.values()), "steer_max": max(vals.values()),
                 "steer_port_model": vals["the port's 15.3 / openpilot's tire model"],
                 "sideways_accel_m_s2": round(u ** 2 / r, 2)})''')
s = s.replace('''  curves.append({"speed_mph": v, "radius_ft": rft, "radius_m": round(r), "bank": "8%",
                 "steer_deg": {rn: round(steer_needed(vm_for(sr), r, u, math.atan(0.08)), 1) for rn, sr in RATIOS.items()},
                 "steer_deg_flat_road": {rn: round(steer_needed(vm_for(sr), r, u, 0.0), 1) for rn, sr in RATIOS.items()},
                 "sideways_accel_m_s2": round(u ** 2 / r, 2)})''', '''  vals = {cn: round(steer_needed(vm, r, u, math.atan(0.08)), 1) for cn, vm in combos()}
  curves.append({"speed_mph": v, "radius_ft": rft, "radius_m": round(r), "bank": "8%",
                 "steer_min": min(vals.values()), "steer_max": max(vals.values()),
                 "steer_port_model": vals["the port's 15.3 / openpilot's tire model"],
                 "sideways_accel_m_s2": round(u ** 2 / r, 2)})''')
s = s.replace('''  curves.append({"speed_mph": v, "radius_ft": round(r / 0.3048), "radius_m": r, "bank": "flat (worst case)",
                 "steer_deg": {rn: round(steer_needed(vm_for(sr), r, u, 0.0), 1) for rn, sr in RATIOS.items()},
                 "sideways_accel_m_s2": round(u ** 2 / r, 2)})''', '''  vals = {cn: round(steer_needed(vm, r, u, 0.0), 1) for cn, vm in combos()}
  curves.append({"speed_mph": v, "radius_ft": round(r / 0.3048), "radius_m": r, "bank": "flat (worst case)",
                 "steer_min": min(vals.values()), "steer_max": max(vals.values()),
                 "steer_port_model": vals["the port's 15.3 / openpilot's tire model"],
                 "sideways_accel_m_s2": round(u ** 2 / r, 2)})''')

# scenarios: heavy steering variant for B, and C for the lightest and heaviest combos
s = s.replace('''scen["B: safety chip limits, port's estimate of push vs turn"] = point_mass(lambda x: min(6.25 * x, 4.5) / 4.0 * 1.5)''',
'''scen["B: safety chip limits, port's estimate of push vs turn"] = point_mass(lambda x: min(6.25 * x, 4.5) / 4.0 * 1.5)
# B2. heavier steering, like the BMW stepper port's torque values (2.3 m/s2 at its 12 Nm): 0.86 m/s2 at 4.5 Nm
scen["B2: safety chip limits, steering as heavy as the BMW port's numbers"] = point_mass(lambda x: min(6.25 * x, 4.5) / 12.0 * 2.3)''')
s = s.replace('''for label, sw_end in (("short teeth", 14.6), ("long teeth", 29.2)):
  for ramp in (0.72, 0.3):
    scen[f"C: wheel to the end of the {label} ({sw_end} deg) in {ramp} s"] = bicycle(
      lambda x, s=sw_end, r=ramp: s * min(1.0, x / r), U70)''', '''for label, sw_end in (("short teeth", 14.6), ("long teeth", 29.2)):
  for ramp in (0.72, 0.3):
    for vn, vm in (("most turning: 13.08 ratio, openpilot's tire model", vm_for(13.08, 1.0)),
                   ("least turning: 18 ratio, 3x the understeer", vm_for(18.0, 1.0 / 3.0))):
      scen[f"C: wheel to the end of the {label} ({sw_end} deg) in {ramp} s, {vn}"] = bicycle(
        lambda x, s=sw_end, r=ramp: s * min(1.0, x / r), U70, vm=vm)''')
open(p, "w").write(s)
EOF
grep -n "import copy" safety_calc.py; sed -i '/^import copy$/d' safety_calc.py; PYTHONPATH=/home/claude/pylib:/home/claude/work/opendbc timeout 900 python3 safety_calc.py 2>&1 | grep -v "setup checks not done" > safety_out.json; python3 - <<'EOF'
import json
o = json.load(open('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety/safety_out.json'))
print(o["car"], o["understeer_deg_per_g"])
print("\nSideways accel at 70 mph, wheel held at:")
for k, v in o["lateral_accel_70mph_at_teeth_end_m_s2"].items():
  print(f"  {k:40s} min {v['min']}  max {v['max']}  port model {v['port_model']}")
print("\nCurves:")
for c in o["curves"]:
  print(f"  {c['speed_mph']:3d} mph R={c['radius_ft']:5d} ft ({c['radius_m']:4d} m) bank {c['bank']:18s} a={c['sideways_accel_m_s2']:4.2f}  steer {c['steer_min']}-{c['steer_max']} (port model {c['steer_port_model']})")
print("\nWrong-way push at 70 mph:")
for k, v in o["wrong_way_push_70mph"].items():
  print(" ", k, "| max a", v["most_sideways_accel_m_s2"], "| 1 m in", v["time_to_1m_s"], "s | lane line in", v["time_to_lane_line_s"], "s")
  print("      ", " | ".join(f"{tr}: at {v[tr]['offset_at_reaction_m']} most {v[tr]['most_offset_m']}" for tr in ("react_0.5s", "react_1.0s", "react_1.5s")))
EOF
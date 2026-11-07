cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='margins.py'
s=open(p).read()
old='''def row(group, what, load, capacity, factor, basis, check="", kind="design", note=""):
  status = "OK" if factor >= AIM else ("meets the floor" if factor >= FLOOR else "UNDER")
  return {"group": group, "what": what, "load": load, "capacity": capacity, "factor": round(factor, 2), "status": status,
          "basis": basis, "check": check, "kind": kind, "note": note}
'''
new='''def row(group, what, load, capacity, factor, basis, check="", kind="design", note=""):
  """kind: "design" counts towards the floor; "condition" is the same failure without one of the build's measures (it
  says which); "test" can only be proven by a test on the car."""
  if math.isnan(factor):
    status, factor = "proof test", None
  else:
    status = "OK" if factor >= AIM else ("meets the floor" if factor >= FLOOR else "UNDER")
    factor = round(factor, 2)
  return {"group": group, "what": what, "load": load, "capacity": capacity, "factor": factor, "status": status,
          "basis": basis, "check": check, "kind": kind, "note": note}
'''
assert old in s; s=s.replace(old,new)
old='''    f = "proof test" if math.isnan(r["factor"]) else f"{r['factor']:.2f} {r['status']}"'''
new='''    f = r["status"] if r["factor"] is None else f"{r['factor']:.2f} {r['status']}"
    if r["kind"] == "condition":
      f += " (without one of this build's measures, below)"'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s)

p='accord_lka_parts.py'
s=open(p).read()
old='''  report["spring"] = {"part": "Lee Spring LCM100E03S (9 mm outside, 1 mm wire, 28.5 mm long, 1.98 N/mm)",'''
new='''  report["spring"] = {"part": f"{MP.SPRING_PART} ({MP.SPRING_OD} mm outside, 1.09 mm wire, {MP.SPRING_FREE:g} mm long, "
                              f"{MP.SPRING_RATE} N/mm)",'''
assert old in s; s=s.replace(old,new)
old='''  if MP.spring_force(most) > MP.SPRING_MAX_N:
    problems.append("the spring is pushed past its most load when the lever is up")
  if hold_n <= apart_n:
    problems.append(f"the spring holds the teeth in mesh against {hold_n:.1f} N, less than the {apart_n:.1f} N the most "
                    "torque pushes them apart with")
'''
new='''  if MP.spring_force(most) > MP.SPRING_MAX_N:
    problems.append("the spring is pushed past its most load when the lever is up")
  if hold_n <= apart_n:
    problems.append(f"the spring holds the teeth in mesh against {hold_n:.1f} N, less than the {apart_n:.1f} N the most "
                    "torque pushes them apart with")

  # ----- margins: every failure mode's factor (margins.py) -----
  mesh_mm = from_hinge(mesh_z)
  weight_n = MG.weight_hold(mesh_mm, (P.COLUMN_TILT_RANGE[0], P.COLUMN_TILT, P.COLUMN_TILT_RANGE[1]))
  report["margins"] = MG.table(report["spring"], mesh_mm, weight_n)
  for r in report["margins"]:
    if r["kind"] == "design" and r["status"] == "UNDER":
      problems.append(f"under the {MG.FLOOR} floor: {r['what']} ({r['factor']})")
'''
assert old in s; s=s.replace(old,new)
old='''           f"onto the rolling band with {sp['presses_roller_on_rolling_band_N']} N and holds the teeth in mesh against up to "
           f"{sp['holds_teeth_in_mesh_up_to_N']} N pushing them apart (by calculation, leaving out the motor's own weight, "
           f"which adds to both). The most torque lane keeping may use ({sp['most_torque_at_steering_wheel_Nm']} Nm at the "
           f"steering wheel) pushes them apart with {sp['most_torque_pushes_teeth_apart_N']} N: the spring has "
           f"{sp['times_what_it_needs']} times what it needs.")'''
new='''           f"onto the rolling band with {sp['presses_roller_on_rolling_band_N']} N and holds the teeth in mesh against up to "
           f"{sp['holds_teeth_in_mesh_up_to_N']} N pushing them apart (by calculation, leaving out the motor's own weight, "
           f"which adds to both). MARGINS below compares that with the push of the most torque, rubbing between the teeth "
           f"included.")'''
assert old in s; s=s.replace(old,new)
old='''  L.append("")
  L.append("BOLTS AND SCREWS")'''
new='''  L.append("")
  L.append(f"MARGINS: for each way it can fail, the worst load, what it takes, and the factor between them. Aim {MG.AIM}, "
           f"nothing under {MG.FLOOR} (NASA-STD-5001B uses 1.4 for tested hardware, the FAA 1.5). For heat, the factor is on "
           "how far the sun heats a part above the outside air (38 C).")
  L += MG.text_lines(r["margins"])
  L.append("")
  L.append("BOLTS AND SCREWS")'''
assert old in s; s=s.replace(old,new)
old='''import params as P  # noqa: E402
'''
new='''import params as P  # noqa: E402
import margins as MG  # noqa: E402
'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s)
EOF
grep -n "^import\|^  import\|import mountparts\|import gears" accord_lka_parts.py | head
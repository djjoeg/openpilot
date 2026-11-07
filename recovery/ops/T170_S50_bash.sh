python3 - <<'EOF'
import pathlib
p = pathlib.Path("sidebuild.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)
rep("""    "side-foot-bar": (S.from_wheel(S.foot_bar()).rotate((0, 0, 0)), (0, 0, 0), "flat (see below)", "none"),
    "side-foot-shim": (S.foot_shim(), (0, 0, 0), "flat", "none"),""",
    """    "side-foot-bar": (parts["foot bar"], (90, 0, 0), "flat, on its wide face", "none"),
    "side-foot-shim": (parts["foot shim"], (90, 0, 0), "flat (print four)", "none"),""")
rep("""  for name, (m, rot, how, supports) in printed_parts(parts).items():
    placed = on_bed(m, rot)""",
    """  for name, (m, rot, how, supports) in {**printed_parts(parts), **printed_teeth(parts)}.items():
    placed = on_bed(m, rot)""")
# run_checks per teeth set
rep("""def run_checks(A: SA.SideAssembly) -> dict:
  res = {}
  internal = SA.internal(A)
  res["internal"] = {k: [round(float(v[0]), 3), v[1]] for k, v in internal.items()}
  res["stops"] = SA.touching_at_stops(A)
  res["lever"] = SA.lever_notches(A)
  res["mesh"] = SA.mesh_sweep(A)
  res["slide_out_of_teeth"] = SA.slide_out_of_teeth(A)
  res["wheel_turned"] = {k: [round(float(v[0]), 3), v[1]] for k, v in SA.wheel_turned(A, step=0.5).items()}
  res["end_teeth"] = SA.end_teeth_meeting(A)
  res["slid_in"] = {k: round(float(v), 3) for k, v in SA.slid_in(A).items()}
  res["clearances"] = SA.clearances(A)
  res["forces"] = SA.forces()
  res["switch"] = SA.switch_states()
  res["slid_in_hold_g"] = round(SA.slid_in_hold_g(), 2)
  res["margins"] = SA.side_margins()
  res["car_estimates"] = SA.car_estimates(A)
  return res""",
    """def run_checks(A: SA.SideAssembly) -> dict:
  \"\"\"The mount's own checks once, and the checks that involve the steering wheel teeth for every set (the report's
  "mesh", "wheel_turned" and so on are the 14-tooth set's; "sets" has every set's).\"\"\"
  res = {}
  internal = SA.internal(A)
  res["internal"] = {k: [round(float(v[0]), 3), v[1]] for k, v in internal.items()}
  res["stops"] = SA.touching_at_stops(A)
  res["lever"] = SA.lever_notches(A)
  res["sets"] = {}
  for n in A.p["sets"]:
    An = SA.SideAssembly(A.p, A.mount, n_teeth=n)
    r = {"teeth": n, "reach_deg": An.t.reach_deg, "mesh": SA.mesh_sweep(An), "slide_out_of_teeth": SA.slide_out_of_teeth(An),
         "wheel_turned": {k: [round(float(v[0]), 3), v[1]] for k, v in SA.wheel_turned(An, step=0.5).items()},
         "end_teeth": SA.end_teeth_meeting(An), "slid_in": {k: round(float(v), 3) for k, v in SA.slid_in(An).items()},
         "clearances": SA.clearances(An)}
    res["sets"][n] = r
    if n == A.t.n_teeth:
      res.update({k: r[k] for k in ("mesh", "slide_out_of_teeth", "wheel_turned", "end_teeth", "slid_in", "clearances")})
  res["forces"] = SA.forces()
  res["switch"] = SA.switch_states()
  res["slid_in_hold_g"] = round(SA.slid_in_hold_g(), 2)
  res["margins"] = SA.side_margins()
  res["car_estimates"] = {D: SA.car_estimates(A, D) for D in (S.D_FOOT[0], S.D_FOOT[1])}
  res["foot_fit"] = [SA.foot_fit(D) for D in (S.D_FOOT[0], (S.D_FOOT[0] + S.D_FOOT[1]) / 2, S.D_FOOT[1])]
  return res""")
rep("""  if res["mesh"]["worst_overlap_mm3"] > 1e-3:
    out.append(f"the gear and the teeth overlap {res['mesh']['worst_overlap_mm3']} mm3")
  if res["slide_out_of_teeth"]["worst_overlap_mm3"] > 1e-3:
    out.append("the gear touches the teeth sliding out")
  for k, v in res["wheel_turned"].items():
    if v[0] > 1e-3:
      out.append(f"steering wheel turned: {k} overlap {v[0]} mm3")
  for k, v in res["slid_in"].items():
    if v > 1e-3:
      out.append(f"{k} overlap {v} mm3")""",
    """  for n, r in res["sets"].items():
    tag = f"{n} teeth: "
    if r["mesh"]["worst_overlap_mm3"] > 1e-3:
      out.append(f"{tag}the gear and the teeth overlap {r['mesh']['worst_overlap_mm3']} mm3")
    if r["slide_out_of_teeth"]["worst_overlap_mm3"] > 1e-3:
      out.append(f"{tag}the gear touches the teeth sliding out")
    for k, v in r["wheel_turned"].items():
      if v[0] > 1e-3:
        out.append(f"{tag}steering wheel turned: {k} overlap {v[0]} mm3")
    for k, v in r["slid_in"].items():
      if v > 1e-3:
        out.append(f"{tag}{k} overlap {v} mm3")
  for ff in res["foot_fit"]:
    if min(ff["room left in the window across (mm, either way)"]) < 0 or min(ff["room left along (mm, either way)"]) < 0:
      out.append(f"the cover's screw misses the foot's window at D {ff['D']}")""")
p.write_text(s)
print("ok")
EOF
sed -n 215,300p sidebuild.py
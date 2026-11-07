python3 - <<'EOF'
p = "faceassembly.py"
s = open(p).read()
old = """  for name, part in mount:
    pairs[f"arm/{name}"] = (AR, part) if name != "joint bolts" else (AR, Manifold())
    pairs[f"hinge block/{name}"] = (HB, part) if name != "joint bolts" else (HB, Manifold())
  pairs["column plate/joint bolts"] = (Manifold(), Manifold())
"""
new = """  for name, part in mount:
    pairs[f"arm/{name}"] = (AR, part)
    pairs[f"hinge block/{name}"] = (HB, part)
  pairs["column plate/joint bolts"] = (mount[0][1], mount[1][1])
"""
assert old in s
s = s.replace(old, new)
old2 = """  for fixed_name, fx in fixed:
    for mover_name, mover in movers:
      if mover_name == "hinge block" and fixed_name == "joint bolts":
        continue
      pairs[f"{mover_name}/{fixed_name}"] = (mover, fx)"""
new2 = """  for fixed_name, fx in fixed:
    for mover_name, mover in movers:
      pairs[f"{mover_name}/{fixed_name}"] = (mover, fx)"""
assert old2 in s
s = s.replace(old2, new2)
s = s.replace("""  for k, (a, b) in pairs.items():
    if a.is_empty() or b.is_empty():
      continue
    res["down: " + k] = overlap(a, b)""", """  for k, (a, b) in pairs.items():
    res["down: " + k] = overlap(a, b)""")
open(p, "w").write(s)
EOF
cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face/assy_test.py <<'EOF'
import sys, time, math, json
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import faceparts as FP
import faceassembly as FA
import mountparts as MP

T0 = time.time()
t = FP.FaceTeeth()
whole = FP.face_solid(t)
pieces = FP.face_pieces(t, whole)
fit = FA.solve_face(t)
print("fit", fit.ok, "reach", round(fit.reach, 1), "arm", fit.arm_len, "slide", round(fit.slide, 1), "j1", fit.j1.round(1), "j2", fit.j2.round(1),
      "j1 deg", round(fit.j1_deg, 1), "off", round(fit.j1_off, 2), fit.notes)
parts = {"teeth": pieces["one-piece"], "gear": FP.face_motor_gear(), "gear_teeth_only": FP.face_motor_gear_teeth_only(),
         "carrier": FP.face_carrier(), "bracket": MP.lever_bracket(), "lever": MP.lift_lever(),
         "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "hinge_block": FP.face_hinge_block(t),
         "plate": FP.column_plate(t)}
A = FA.FaceAssembly(t, fit, parts)
print("parts built", round(time.time() - T0, 1))
T0 = time.time()
ms = FA.mesh_sweep(A, step=2.0)
print("mesh", ms, round(time.time() - T0, 1))
T0 = time.time()
res = FA.check_all(A)
bad = {k: round(v, 3) for k, v in res.items() if (v > 1e-3 and "should touch" not in k) or ("should touch" in k and v >= 0)}
print("checks", len(res), "bad", len(bad), round(time.time() - T0, 1))
for k, v in sorted(bad.items(), key=lambda kv: -kv[1])[:60]:
  print("  ", v, k)
print("clearances", FA.clearances(A))
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && PYTHONPATH=/home/claude/pylib timeout 3000 python3 assy_test.py 2>&1 | tail -80
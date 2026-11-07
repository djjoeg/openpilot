python3 - <<'EOF'
p = "accord_lka_parts.py"
s = open(p).read()
old = """  def arm_for(up: float, forward: float) -> tuple[float, str]:
    \"\"\"The arm that fits a dash clamp bolt this far up and forward of the motor gear's centre at every tilt setting of
    the steering wheel: it reaches, both joints are within their range and nothing touches. Of several, the one
    nearest the middle of its slide with the tilt in the middle. Returns (length, "") or (0, why not).\"\"\"
    sols = [AS.solve(t, up, forward, tl) for tl in tilts]
"""
new = """  def arm_for(up: float, forward: float, at_tilts=tilts) -> tuple[float, str]:
    \"\"\"The arm that fits a dash clamp bolt this far up and forward of the motor gear's centre at each of these tilt
    settings of the steering wheel: it reaches, both joints are within their range and nothing touches. Of several,
    the one nearest the middle of its slide with the tilt in the middle. Returns (length, "") or (0, why not).\"\"\"
    sols = [AS.solve(t, up, forward, tl) for tl in at_tilts]
"""
assert old in s; s = s.replace(old, new)
old = """    if not cands:
      return 0.0, (f"the dash clamp's bolt is {sols[0].reach:.0f} to {sols[2].reach:.0f} mm from the hinge block's "
                   "across the tilt range; no arm covers all of it")
    for L in sorted(cands, key=lambda L: abs(sols[1].reach - L)):
      assy = dict(base)
      assy["arm"] = arms.get(L) or MP.arm(L)
      for tl, sol in zip(tilts, sols):
"""
new = """    if not cands:
      reaches = sorted(sol.reach for sol in sols)
      return 0.0, (f"the dash clamp's bolt is {reaches[0]:.0f} to {reaches[-1]:.0f} mm from the hinge block's; "
                   "no arm covers all of it")
    middle = sols[len(sols) // 2]
    for L in sorted(cands, key=lambda L: abs(middle.reach - L)):
      assy = dict(base)
      assy["arm"] = arms.get(L) or MP.arm(L)
      for tl, sol in zip(at_tilts, sols):
"""
assert old in s; s = s.replace(old, new)
old = """      L, why_not = arm_for(u, f)
      row.append(f"arm-{int(L):03d}" if L else "no: " + why_not)
"""
new = """      L, why_not = arm_for(u, f)
      if L:
        row.append(f"arm-{int(L):03d}")
        continue
      L_middle, _ = arm_for(u, f, (P.COLUMN_TILT,))
      # * fits with the tilt in the middle, but not at both ends of its range
      row.append(f"arm-{int(L_middle):03d}*" if L_middle else "no: " + why_not)
"""
assert old in s; s = s.replace(old, new)
old = """  if f["ok"]:
    L.append("  Your position across the tilt range: " + "; ".join("""
new = """  if any(c.endswith("*") for row in gr["cells"] for c in row):
    L.append("  * fits with the tilt in the middle of its range, but not at both ends: check yours with this script.")
  if f["ok"]:
    L.append("  Your position across the tilt range: " + "; ".join("""
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
print("ok")
EOF
OUT=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cad5 && rm -rf $OUT && mkdir -p $OUT && rm -rf __pycache__ && PYTHONPATH=/home/claude/pylib timeout 2400 python3 accord_lka_parts.py --out $OUT/stl --report $OUT/report > $OUT/run.log 2>&1; echo "exit $?"; sed -n '/WHICH DASH/,$p' $OUT/run.log
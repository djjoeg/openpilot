python3 - <<'EOF'
p = "params.py"
s = open(p).read()
old = "ARM_SLIDE = 11.0              # each arm slides +- this much at the dash clamp, so the lengths overlap\n"
new = ("ARM_SLIDE = 15.0              # each arm slides +- this much at the dash clamp: neighbouring lengths overlap by about\n"
       "                              # 10 mm, which covers the steering wheel's tilt range and some measuring error\n")
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)

p = "accord_lka_parts.py"
s = open(p).read()
old = "  arm                   - dash clamp to hinge block; printed in several lengths, each slides +-11 mm at the dash clamp\n"
new = "  arm                   - dash clamp to hinge block; printed in several lengths, each slides +-15 mm at the dash clamp\n"
assert old in s; s = s.replace(old, new)

old = """import argparse
import json
import math
import os
import sys
import time
"""
new = """import argparse
import dataclasses
import json
import math
import os
import sys
import time
"""
assert old in s; s = s.replace(old, new)

# the user's position: the arm that fits at every tilt setting
old = """  # ----- fit in the car -----
  fit = AS.solve(t, args.clamp_up, args.clamp_forward)
"""
new = """  # ----- fit in the car -----
  base = {"teeth": parts["steering-wheel-teeth-one-piece"][0], "gear": parts["motor-gear"][0],
          "gear_teeth_only": WP.motor_gear_teeth_only(), "carrier": parts["motor-carrier"][0],
          "hinge_block": parts["hinge-block"][0], "lever": parts["lift-lever"][0], "clamp": parts["dash-clamp"][0]}
  tilts = (P.COLUMN_TILT_RANGE[0], P.COLUMN_TILT, P.COLUMN_TILT_RANGE[1])

  def arm_for(up: float, forward: float) -> tuple[float, str]:
    \"\"\"The arm that fits a dash clamp bolt this far up and forward of the motor gear's centre at every tilt setting of
    the steering wheel: it reaches, both joints are within their range and nothing touches. Of several, the one
    nearest the middle of its slide with the tilt in the middle. Returns (length, "") or (0, why not).\"\"\"
    sols = [AS.solve(t, up, forward, tl) for tl in tilts]
    angle_notes = [n for sol in sols for n in sol.notes if "arms cover" not in n]
    if angle_notes:
      return 0.0, angle_notes[0]
    cands = [L for L in arm_lengths if all(abs(sol.reach - L) <= P.ARM_SLIDE - 0.5 for sol in sols)]
    if not cands:
      return 0.0, (f"the dash clamp's bolt is {sols[0].reach:.0f} to {sols[2].reach:.0f} mm from the hinge block's "
                   "across the tilt range; no arm covers all of it")
    for L in sorted(cands, key=lambda L: abs(sols[1].reach - L)):
      assy = dict(base)
      assy["arm"] = arms.get(L) or MP.arm(L)
      for tl, sol in zip(tilts, sols):
        g = dataclasses.replace(sol, ok=True, arm_len=float(L), slide=sol.reach - L, notes=[])
        res = AS.check_all(AS.Assembly(t, g, dict(assy), tl), lever_step=8.0)
        bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
        if bad:
          break
      else:
        return float(L), ""
    return 0.0, f"parts touch ({bad[0]})"

  arm_len, why_not = arm_for(args.clamp_up, args.clamp_forward)
  fit = AS.solve(t, args.clamp_up, args.clamp_forward)
  if arm_len:
    fit = dataclasses.replace(fit, ok=True, arm_len=arm_len, slide=fit.reach - arm_len, notes=[])
  else:
    fit = dataclasses.replace(fit, ok=False, arm_len=0.0, slide=0.0, notes=fit.notes or [why_not])
"""
assert old in s; s = s.replace(old, new)

old = """  base = {"teeth": parts["steering-wheel-teeth-one-piece"][0], "gear": parts["motor-gear"][0],
          "gear_teeth_only": WP.motor_gear_teeth_only(), "carrier": parts["motor-carrier"][0],
          "hinge_block": parts["hinge-block"][0], "lever": parts["lift-lever"][0], "clamp": parts["dash-clamp"][0]}
  checks = {}
"""
new = """  checks = {}
"""
assert old in s; s = s.replace(old, new)

old = """  # which dash clamp positions work, with the steering wheel's tilt in the middle of its range
  def clamp_grid(tilt: float) -> dict:
    grid = {"up_mm": [40, 60, 80, 105, 130, 160], "forward_mm": [80, 110, 140, 175, 210, 250], "tilt_deg": tilt, "cells": []}
    for u in grid["up_mm"]:
      row = []
      for f in grid["forward_mm"]:
        g = AS.solve(t, u, f, tilt)
        if not g.ok:
          row.append("no: " + g.notes[0])
          continue
        assy = dict(base)
        assy["arm"] = arms.get(g.arm_len) or MP.arm(g.arm_len)
        res = AS.check_all(AS.Assembly(t, g, assy, tilt), lever_step=8.0)
        bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
        row.append(f"arm-{int(g.arm_len):03d}" if not bad else "no: parts touch (" + bad[0] + ")")
      grid["cells"].append(row)
    return grid
  report["dash_clamp_positions"] = clamp_grid(P.COLUMN_TILT)

  # the same at the lowest and highest tilt settings: where the arm to print would differ
  tilt_rows = []
  for tilt in P.COLUMN_TILT_RANGE:
    g = AS.solve(t, args.clamp_up, args.clamp_forward, tilt)
    other = clamp_grid(tilt)
    changes = []
    for i, u in enumerate(other["up_mm"]):
      for j, f in enumerate(other["forward_mm"]):
        a, b = report["dash_clamp_positions"]["cells"][i][j], other["cells"][i][j]
        if a.split(":")[0] != b.split(":")[0]:
          changes.append({"up_mm": u, "forward_mm": f, "middle": a.split(":")[0], "here": b.split(":")[0]})
    tilt_rows.append({"tilt_deg": tilt, "arm_for_your_position": f"arm-{int(g.arm_len):03d}" if g.ok else None,
                      "notes": g.notes, "table_changes": changes})
  report["tilt_range"] = tilt_rows
"""
new = """  # which dash clamp positions work, each with the arm that fits at every tilt setting
  grid = {"up_mm": [40, 60, 80, 105, 130, 160], "forward_mm": [80, 110, 140, 175, 210, 250], "tilt_deg": list(tilts),
          "cells": []}
  for u in grid["up_mm"]:
    row = []
    for f in grid["forward_mm"]:
      L, why_not = arm_for(u, f)
      row.append(f"arm-{int(L):03d}" if L else "no: " + why_not)
    grid["cells"].append(row)
  report["dash_clamp_positions"] = grid
  # the arm's slide at each tilt setting, for your position
  report["tilt_range"] = [{"tilt_deg": tl, "bolt_to_bolt_mm": round(AS.solve(t, args.clamp_up, args.clamp_forward, tl).reach, 1),
                           "slide_from_middle_mm": round(AS.solve(t, args.clamp_up, args.clamp_forward, tl).reach - fit.arm_len, 1)
                           if fit.arm_len else None} for tl in tilts]
"""
assert old in s; s = s.replace(old, new)

old = """  L.append("WHICH DASH CLAMP POSITIONS WORK (rows: mm up from the motor gear's centre; columns: mm forward; steering "
           f"column at {gr['tilt_deg']} degrees)")
  L.append("        " + "".join(f"{x:>12}" for x in gr["forward_mm"]))
  for u, row in zip(gr["up_mm"], gr["cells"]):
    L.append(f"  {u:5}  " + "".join(f"{(c if not c.startswith('no') else 'no'):>12}" for c in row))
  L.append("")
  L.append(f"STEERING WHEEL TILT: the steering column is at {inp['column_tilt_deg']} degrees with the tilt in the middle "
           "(NHTSA tests 6229 and 7078); it tilts about 3.5 degrees either way.")
  for tr in r["tilt_range"]:
    arm = tr["arm_for_your_position"] or "nothing fits (" + "; ".join(tr["notes"]) + ")"
    changes = ", ".join(f"{c['up_mm']} up / {c['forward_mm']} forward: {c['here']} instead of {c['middle']}" for c in tr["table_changes"])
    L.append(f"  at {tr['tilt_deg']} degrees: your position needs {arm}. "
             + (f"In the table above: {changes}." if changes else "The table above is the same."))
  L.append("")
"""
new = """  tl = gr["tilt_deg"]
  L.append("WHICH DASH CLAMP POSITIONS WORK (rows: mm up from the motor gear's centre; columns: mm forward). Each arm "
           f"named fits at every tilt setting of the steering wheel: the steering column at {tl[0]} to {tl[2]} degrees "
           f"from level, {tl[1]} in the middle (measured by NHTSA, tests 6229 and 7078).")
  L.append("        " + "".join(f"{x:>12}" for x in gr["forward_mm"]))
  for u, row in zip(gr["up_mm"], gr["cells"]):
    L.append(f"  {u:5}  " + "".join(f"{(c if not c.startswith('no') else 'no'):>12}" for c in row))
  if f["ok"]:
    L.append("  Your position across the tilt range: " + "; ".join(
      f"at {t_['tilt_deg']} degrees bolt to bolt {t_['bolt_to_bolt_mm']} mm, slid {t_['slide_from_middle_mm']:+.1f} mm"
      for t_ in r["tilt_range"]) + ".")
  L.append("")
"""
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
print("ok")
EOF
grep -n "arm_lengths\b" accord_lka_parts.py | head -5
python3 - <<'EOF'
p = "params.py"
s = open(p).read()
old = """# Steering wheel. Published cover sizing lists the 2008-12 Accord at 14 3/8 - 14 1/2 in across (365-368 mm) and
# 4 1/8 in (105 mm) around the part you hold, which is 33 mm thick if it is round. Measure yours.
WHEEL_OD = 367.0      # across the steering wheel, outside edge to outside edge, through the centre
GRIP = 33.0           # thickness of the part you hold at the top (the distance around it divided by 3.14)

# Where the dash clamp's bolt (the one the arm turns on) ends up relative to the motor gear's centre, in the car (not
# the steering wheel frame): up (towards the roof) and forward (towards the windshield). These are estimates, not
# measurements of a 2010 Accord. They only pick which arm length to print and check that the parts reach; the build
# script also checks a range of positions around them (see the report).
ARM_PIVOT_UP = 105.0
ARM_PIVOT_FORWARD = 175.0
COLUMN_TILT = 22.0    # steering column angle from level, degrees: the column rises towards the driver, so the top of
                      # the steering wheel is further forward than the bottom. Estimate.
"""
new = """# Steering wheel. Steering wheel cover makers list the 2008-12 Accord's: Wheelskins 14 1/2 x 4 1/8 in (368 mm across,
# 105 mm around the part you hold), AutoPadre 14 3/8 x 4 1/8 in (365 mm). 105 mm around is 33 mm thick if it is round.
# The fit test checks it on your car; to make the parts for yours, measure it (see the guide).
WHEEL_OD = 367.0      # across the steering wheel, outside edge to outside edge, through the centre
GRIP = 33.0           # thickness of the part you hold at the top (the distance around it divided by 3.14)

# Steering column angle from level, degrees: the column rises towards the driver, so the top of the steering wheel is
# further forward than the bottom. Measured by NHTSA in its frontal crash tests, with the steering wheel in the middle
# of its tilt range: 22.1 on a 2008 Accord LX sedan (test 6229), 22.4 on a 2011 Accord LX sedan (test 7078). The same
# reports measure the tilt's whole range (about 3.5 degrees either way) and the reach range (34-35 mm).
COLUMN_TILT = 22.1
COLUMN_TILT_RANGE = (18.5, 25.9)   # lowest and highest tilt settings, from both reports; the build checks both

# Where the dash clamp's bolt (the one the arm turns on) ends up relative to the motor gear's centre, in the car (not
# the steering wheel frame): up (towards the roof) and forward (towards the windshield). Estimates: nothing published
# gives where the cover over the gauges sits relative to the steering wheel, and the answer changes with how you set
# the steering wheel's tilt and reach (the ranges above). They only pick which arm length to print and check that the
# parts reach; the build script also checks a range of positions around them (see the report).
ARM_PIVOT_UP = 105.0
ARM_PIVOT_FORWARD = 175.0
"""
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)

p = "accord_lka_parts.py"
s = open(p).read()
old = """  # which dash clamp positions work
  grid = {"up_mm": [40, 60, 80, 105, 130, 160], "forward_mm": [80, 110, 140, 175, 210, 250], "cells": []}
  for u in grid["up_mm"]:
    row = []
    for f in grid["forward_mm"]:
      g = AS.solve(t, u, f)
      if not g.ok:
        row.append("no: " + g.notes[0])
        continue
      assy = dict(base)
      assy["arm"] = arms.get(g.arm_len) or MP.arm(g.arm_len)
      res = AS.check_all(AS.Assembly(t, g, assy), lever_step=8.0)
      bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
      row.append(f"arm-{int(g.arm_len):03d}" if not bad else "no: parts touch (" + bad[0] + ")")
    grid["cells"].append(row)
  report["dash_clamp_positions"] = grid
"""
new = """  # which dash clamp positions work, with the steering wheel's tilt in the middle of its range
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
assert old in s; s = s.replace(old, new)

old = """  L.append("WHICH DASH CLAMP POSITIONS WORK (rows: mm up from the motor gear's centre; columns: mm forward)")
  L.append("        " + "".join(f"{x:>12}" for x in gr["forward_mm"]))
  for u, row in zip(gr["up_mm"], gr["cells"]):
    L.append(f"  {u:5}  " + "".join(f"{(c if not c.startswith('no') else 'no'):>12}" for c in row))
  L.append("")
"""
new = """  L.append("WHICH DASH CLAMP POSITIONS WORK (rows: mm up from the motor gear's centre; columns: mm forward; steering "
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
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
print("ok")
EOF
grep -n "column_tilt_deg" accord_lka_parts.py
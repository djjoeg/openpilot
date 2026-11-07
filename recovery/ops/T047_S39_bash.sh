cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety && sed -i 's/^import copy\n//' safety_calc.py && PYTHONPATH=/home/claude/pylib:/home/claude/work/opendbc timeout 600 python3 safety_calc.py 2>&1 | grep -v "setup checks not done" > safety_out.json; python3 - <<'EOF'
import json
o = json.load(open('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety/safety_out.json'))
print(o["car"])
print("\nSideways accel at 70 mph, wheel held at:")
for k, v in o["lateral_accel_70mph_at_teeth_end_m_s2"].items():
  print(f"  {k:40s}", v)
print("\nCurves:")
for c in o["curves"]:
  print(f"  {c['speed_mph']:3d} mph R={c['radius_ft']:5d} ft ({c['radius_m']:4d} m) bank {c['bank']:18s} a={c['sideways_accel_m_s2']:4.2f}  steer {list(c['steer_deg'].values())}  flat {list(c.get('steer_deg_flat_road',{}).values())}")
print("\nWrong-way push at 70 mph:")
for k, v in o["wrong_way_push_70mph"].items():
  print(" ", k, "| max a", v["most_sideways_accel_m_s2"], "| 1 m in", v["time_to_1m_s"], "s | lane line in", v["time_to_lane_line_s"], "s")
  for tr in ("react_0.5s", "react_1.0s", "react_1.5s"):
    print("     ", tr, v[tr])
print(o["lane"])
EOF
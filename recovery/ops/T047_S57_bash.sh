cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety && sed -i 's/for tr in (0.5, 1.0, 1.5):/for tr in (0.5, 0.7, 1.0, 1.5):/' safety_calc.py && PYTHONPATH=/home/claude/pylib:/home/claude/work/opendbc timeout 900 python3 safety_calc.py 2>&1 | grep -v "setup checks not done" > safety_out.json; python3 - <<'EOF'
import json
o = json.load(open('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety/safety_out.json'))
for k, v in o["wrong_way_push_70mph"].items():
  print(f"{k[:95]:95s} a {v['most_sideways_accel_m_s2']:5.2f} line {v['time_to_lane_line_s']} | " + " | ".join(f"{tr[6:]}: {v[tr]['most_offset_m']}" for tr in ("react_0.5s", "react_0.7s", "react_1.0s")))
EOF
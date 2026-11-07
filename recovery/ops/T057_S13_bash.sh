cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety && python3 - <<'EOF'
p='safety_calc.py'
s=open(p).read()
old='''# B. what the safety chip allows this port: 4.5 Nm, rising at 6.25 Nm/s, with the port's estimate that 4 Nm gives
#    1.5 m/s^2 (not measured)
scen["B: safety chip limits, port's estimate of push vs turn"] = point_mass(lambda x: min(6.25 * x, 4.5) / 4.0 * 1.5)
# B2. heavier steering, like the BMW stepper port's torque values (2.3 m/s2 at its 12 Nm): 0.86 m/s2 at 4.5 Nm
scen["B2: safety chip limits, steering as heavy as the BMW port's numbers"] = point_mass(lambda x: min(6.25 * x, 4.5) / 12.0 * 2.3)
# C. the steering wheel driven to the end of the teeth (the physical stop), rising over the safety chip's 0.72 s
#    torque ramp, or faster (0.3 s) if the steering is light
for label, sw_end in (("short teeth", 14.6), ("long teeth", 29.2)):
  for ramp in (0.72, 0.3):'''
new='''# B. what the safety chip allows this port, at the steering wheel: 4.41 Nm (47 firmware units with the 45 Ncm
#    motor), rising at most 5.63 Nm/s (15 units per 250 ms), with the port's estimate that its own most (4.03 Nm) gives
#    1.5 m/s^2 (not measured)
CHIP_NM, CHIP_RATE, LK_NM = 4.41, 5.63, 4.03
scen["B: safety chip limits, port's estimate of push vs turn"] = point_mass(lambda x: min(CHIP_RATE * x, CHIP_NM) / LK_NM * 1.5)
# B2. heavier steering, like the BMW stepper port's torque values (2.3 m/s2 at its 12 Nm)
scen["B2: safety chip limits, steering as heavy as the BMW port's numbers"] = point_mass(lambda x: min(CHIP_RATE * x, CHIP_NM) / 12.0 * 2.3)
# C. the steering wheel driven to the end of the teeth (the physical stop), rising over the safety chip's torque ramp
#    (0.78 s to its most), or faster (0.3 s) if the steering is light
for label, sw_end in (("short teeth", 14.6), ("long teeth", 29.2)):
  for ramp in (round(CHIP_NM / CHIP_RATE, 2), 0.3):'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib:/home/claude/work/opendbc timeout 600 python3 safety_calc.py > safety_out_100.json 2>/dev/null; echo exit $?; python3 - <<'EOF'
import json
d=json.load(open('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety/safety_out_100.json'))
for k,v in d['wrong_way_push_70mph'].items():
    print(k[:95].ljust(95), 'acc', v['most_sideways_accel_m_s2'], 'line', v['time_to_lane_line_s'], '1m', v['time_to_1m_s'], 'tot', [v[f'react_{t}s']['most_offset_m'] for t in (0.5,0.7,1.0)])
EOF
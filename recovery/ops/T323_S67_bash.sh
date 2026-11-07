cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "rightcheck.py"
s = open(p, encoding="utf-8").read()
a = """GEAR_IN, GEAR_OUT = 3.0, 3.0   # lining the gear up along the teeth: the arm this far further in or out across than
                               # drawn, relative to the steering wheel (in by 5 the carrier meets the teeth piece;
                               # out by 4, the motor slid off, the wiper stalk pushed all the way down meets the gear)"""
b = """GEAR_IN, GEAR_OUT = 4.0, 3.0   # lining the gear up along the teeth: the arm this far further in or out across than
                               # drawn, relative to the steering wheel (in by 5 the carrier meets the teeth piece;
                               # out by 4, the motor slid off, the wiper stalk pushed all the way down meets the gear)"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
(time PYTHONPATH=/home/claude/pylib python3 rightcheck.py) > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/rc4.txt 2>&1; tail -6 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/rc4.txt
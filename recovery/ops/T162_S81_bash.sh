python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()
s = s.replace('EAR_Z = (-25.0, 0.0)              # its outer end (+z) presses the switch and meets the stop',
              'EAR_Z = (-22.0, 0.0)              # its outer end (+z) presses the switch and meets the stop')
s = s.replace('SW_X = (-29.7, -29.7 + MP.SW_THICK)        # its thickness (x): the roller over the ear\'s end everywhere',
              'SW_X = (-30.0, -30.0 + MP.SW_THICK)        # its thickness (x): the roller over the ear\'s end everywhere')
open(p, "w").write(s)
EOF
grep -n "^EAR_Z\|^SW_X" sideparts.py && PYTHONPATH=/home/claude/pylib timeout 900 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/run_internal.py
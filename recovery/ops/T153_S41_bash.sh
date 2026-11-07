cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && python3 - <<'EOF'
import re
p='study90.py'
s=open(p).read()
s=s.replace('''          "motor's own plug": own_plug, "carrier": core_carrier(with_knuckle=False), "gear": PP.pop_motor_gear()}''','''          "motor's own plug": own_plug, "plate+guard": core_carrier(with_knuckle=False) ^ box(-60, 60, -60, 6.0, -1.0, 60),
          "gear": PP.pop_motor_gear()}''')
open(p,'w').write(s)
EOF
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache
for m in -70 -76 -82 -88; do (timeout 1200 python3 study90.py radial $m 97,103,106,110,115 0 6 > ra_$m.txt 2>&1 &) ; done; sleep 1; while pgrep -f "study90.py radial" >/dev/null; do sleep 10; done; cat ra_-70.txt ra_-76.txt ra_-82.txt ra_-88.txt
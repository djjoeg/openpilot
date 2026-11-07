cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/mockup && python3 - <<'EOF'
p='export.py'
s=open(p).read()
old='lift = [round(max(0.0, MP.cam_lift(a)), 3) for a in alphas]'
assert s.count(old)==1
s=s.replace(old,'lift = [round(MP.cam_lift(a), 3) for a in alphas]   # can be below 0: the rounded end lets the carrier drop')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 1500 python3 export.py . 2>&1 | tail -2; python3 -c "
import json; d=json.load(open('data.json')); print(d['lever']['lift'][:12]); print(d['lever']['lift'][-6:])"
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sidemock && python3 - <<'EOF'
import re
p = "side_export.py"
s = open(p).read()
s = s.replace('("teeth", "wheel", "teeth", A.teeth(0.0)),', '("teeth", "teeth", "teeth", A.teeth(0.0)),')
s = s.replace('("ties", "wheel", "tie", ties()),', '("ties", "teeth", "tie", ties()),')
open(p, "w").write(s)
EOF
grep -n '"teeth", "teeth"\|"ties", "teeth"' side_export.py; PYTHONPATH=/home/claude/pylib python3 side_export.py . > export.log 2>&1; tail -1 export.log; python3 -c "
import json; d = json.load(open('data.json')); print(d['labels']); print(d['strip'], d['swlever'], d['reach'], d['half'], d['pitch']); print(d['forces'])"
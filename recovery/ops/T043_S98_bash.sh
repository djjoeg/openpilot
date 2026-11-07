cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2 && python3 - <<'EOF'
import re
s = open('proto2.py').read()
s = s.replace('''  start = next(a for a, th, F in rows if th > 0.02)
  peak = max(rows, key=lambda r: r[1])
  rest = min((r for r in rows if r[0] >= peak[0]), key=lambda r: r[1])
  fmax = max(r[2] for r in rows)
  back = [r for r in rows if peak[0] < r[0] <= rest[0]]
  fback = -min(r[2] for r in back) if back else 0
  after = [r for r in rows if r[0] > rest[0]]
  fstop = max(r[2] for r in after) if after else 0''', '''  start = next(a for a, th, F in rows if th > 0.02)
  before = [r for r in rows if r[0] <= a_off + 1e-9]
  peak = max(before, key=lambda r: r[1])
  rest = before[-1]
  fmax = max(r[2] for r in before)
  fback = -rest[2]
  after = [r for r in rows if r[0] > a_off + 1e-9]
  fstop = after[0][2] if after else 0''')
open('proto2.py','w').write(s)
EOF
for args in "59.8 62 9.0 74 2.5 4" "59.8 64 9.0 76 4 4" "59.8 64 9.0 76 5 4" "59.8 62 9.0 76 5 4" "59.8 62 9.5 76 5 5" "59.8 60 9.5 74 5 5" "59.8 64 9.5 78 5 5" "59.8 62 10 78 5 5"; do echo "== $args"; PYTHONPATH=/home/claude/pylib python3 proto2.py $args; done
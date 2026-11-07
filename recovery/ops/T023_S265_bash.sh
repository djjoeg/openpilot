python3 - << 'EOF'
p = "mountparts.py"
s = open(p).read()
rep = [("A_DEAD, A_HARD_STOP, A_END = 55.0, 63.0, 70.0", "A_DEAD, A_HARD_STOP, A_END = 62.0, 70.0, 77.0"),
       ("HANDLE_LEN = 38.0                     # pivot to the end of the handle", "HANDLE_LEN = 36.0                     # pivot to the end of the handle"),
       ("LEVER_ON = -20.0                      # the handle hangs this far below the carrier's top plane when down",
        "LEVER_ON = -22.0                      # the handle hangs this far below the carrier's top plane when down")]
for a, b in rep:
  assert a in s, a
  s = s.replace(a, b)
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import mountparts as MP
print('raw drop limit (lift at lever down): %.2f deg' % MP.cam_lift(0))
rows = MP.lever_lift_table(2.0)
print(' '.join('%d:%.2f/%.1f' % (a, th, f) for a, th, f in rows))
print('max force %.1f N at %.0f mm' % (max(r[2] for r in rows), MP.HANDLE_LEN))
" ; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  " | tail -5; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/grid.py
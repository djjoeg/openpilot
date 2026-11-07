python3 - << 'EOF'
p = "mountparts.py"
s = open(p).read()
a = '''def cam_psi_range():
  """Lever-frame directions the fin can touch, with margin."""
  return (-90.0 - LEVER_ON - 12.0, -90.0 - LEVER_ON + A_END + 12.0)'''
b = '''def cam_psi_range():
  """Lever-frame directions that face the fin (straight down in the hinge block) between down and A_END, with margin.
  A lever-frame direction psi points at psi - (LEVER_ON + alpha) in the hinge block."""
  return (-90.0 + LEVER_ON - 12.0, -90.0 + LEVER_ON + A_END + 12.0)'''
assert a in s
s = s.replace(a, b)
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import mountparts as MP, math, numpy as np
print('cam psi range', MP.cam_psi_range())
rows = MP.lever_lift_table(2.0)
for a, th, f in rows: print('%5.0f  sched %6.2f  lift %6.2f  force %5.2f N' % (a, MP.lift_schedule(a), th, f))
pts = np.array(MP.cam_points(1.0)); r = np.hypot(pts[:,0], pts[:,1])
print('cam radius min %.2f max %.2f' % (r.min(), r.max()))
"; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  "
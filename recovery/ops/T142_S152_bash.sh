sed -i 's/^SHELF_X1 = 88.0               # the shelf under the flange, out to here (the springs. front bolt swings past beyond)/SHELF_X1 = 74.0               # the shelf under the flange, out to here (the lower spring sweeps past beyond)/' popparts.py && grep -n "^SHELF_X1" popparts.py && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache python3 -c "
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2')
import run_u, popassembly as PA, popparts as PP, numpy as np
from cadlib import union
t, parts = run_u.build()
A = PA.PopAssembly(t, parts)
PL = A.plate()
keep = PP.MOUNT_DEG
for adj in (-3.0,):
  PP.MOUNT_DEG = keep + adj
  for l in np.arange(-3, 76, 2.5):
    for n, m in (('springs', A.springs(float(l))), ('bolts', A.bolts(float(l)))):
      x = m ^ PL
      if x.volume() > 1e-3: print(adj, n, l, round(x.volume(),2), [round(v,1) for v in x.bounding_box()])
PP.MOUNT_DEG = keep
"
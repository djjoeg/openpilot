python3 - <<'EOF'
import pathlib, re
p = pathlib.Path("popparts.py")
s = p.read_text()
s2 = re.sub(r"^SHELF_X1 = 88\.0 +# the shelf under the flange, out to here \(the springs' front bolt swings past beyond\)",
            "SHELF_X1 = 74.0                # the shelf under the flange, out to here (the springs' front bolt swings past beyond)", s, flags=re.M)
assert s2 != s
s2 = s2.replace("MOUNT_ADJ = (3.0, 6.0)    # the whole mount", "MOUNT_ADJ = (2.0, 6.0)    # the whole mount")
s2 = s2.replace("# (towards the key) and up (towards the stalk) when fitting it: about 3:26 to 3:08.", "# (towards the key) and up (towards the stalk) when fitting it: about 3:24 to 3:08.")
p.write_text(s2)
print("ok")
EOF
grep -n "^SHELF_X1\|^MOUNT_ADJ\|3:24 to 3:08" popparts.py && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache python3 -c "
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2')
import run_u, popassembly as PA, popparts as PP, numpy as np
from mindist import min_dist
from cadlib import union
t, parts = run_u.build()
A = PA.PopAssembly(t, parts)
PL = A.plate()
keep = PP.MOUNT_DEG
for adj in (-2.0, 0.0, 6.0):
  PP.MOUNT_DEG = keep + adj
  sw = union([A.springs(float(l)) + A.bolts(float(l)) for l in np.arange(-3, 76, 2.5)] + [A.springs(75.0) + A.bolts(75.0)])
  x = sw ^ PL
  d = min_dist(sw, PL, spacing=1.0)[0] if x.volume() < 1e-3 else 0
  print('adj', adj, 'overlap', round(x.volume(),2), 'gap', round(d, 2))
PP.MOUNT_DEG = keep
"
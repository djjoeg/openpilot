cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > s2tri.py <<'EOF'
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
from s2load import *
pairs = {
  "CUP (check)": {33: (1080, 1680), 37: (970, 1584)},
  "33 lever left end / 37 paddle bottom-left": {33: (755, 1625), 37: (945, 1995)},
  "33 lever left end / 37 paddle top-left": {33: (755, 1625), 37: (985, 1810)},
  "33 lever right end / 37 arm exit": {33: (1010, 1685), 37: (1190, 1665)},
  "33 lever left end / 37 arm exit": {33: (755, 1625), 37: (1190, 1665)},
}
for si in (0, 2):
    s, cost, pb = SOL[si]
    print("s %.3f" % s)
    for name, pk in pairs.items():
        X, res = triangulate(pb, pk)
        # ray-ray closest distance
        (o1, d1), (o2, d2) = ray(pb, 33, pk[33]), ray(pb, 37, pk[37])
        n = np.cross(d1, d2); gap = abs((o2 - o1) @ n) / np.linalg.norm(n)
        print("   %-45s X %s  r %.0f  rays miss by %.1f mm  px res %s" % (name, np.round(X, 1), np.hypot(X[0], X[1]), gap, {k: round(v, 1) for k, v in res.items()}))
EOF
PYTHONPATH=/home/claude/pylib python3 s2tri.py
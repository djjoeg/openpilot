cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > s2bez.py <<'EOF'
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
from s2load import *
for s, cost, pb in SOL:
    print("s %.3f cost %.0f" % (s, cost))
    for name, c in pb.circles.items():
        print("   circle", name, "r %.2f r0 %s sigma %s" % (c["r"], c.get("r0"), c.get("r_sigma")), "centre key", c["centre"], np.round(to_car(pb.pts[c["centre"]]), 1) if c["centre"] in pb.pts else "")
    # distances between landmarks
    P = {k[1]: to_car(v) for k, v in pb.pts.items() if k[0] == "L"}
    for a, b in (("SH", "ST"), ("KS1", "KS2"), ("CUP", "KS1"), ("RH", "KS1"), ("PU", "KS1")):
        if a in P and b in P:
            print("   |%s-%s| = %.1f" % (a, b, np.linalg.norm(P[a] - P[b])))
EOF
PYTHONPATH=/home/claude/pylib python3 s2bez.py 2>&1 | head -40
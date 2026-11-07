cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > s2table.py <<'EOF'
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
from s2load import *
from jba import unit_from_angles
HOOK = {}
for si in (0, 2):
    s, cost, pb = SOL[si]
    P = {k[1]: to_car(v) for k, v in pb.pts.items() if k[0] == "L"}
    P["KEY"] = to_car(pb.pts[("B", "outer")])
    n = RZ @ unit_from_angles(*pb.circles["outer"]["ang"])
    if n @ np.array([P["KEY"][0], P["KEY"][1], 0]) < 0:
        n = -n
    # tape hook on photo 24's ray, 41 mm from the key centre (the far root)
    o, d = ray(pb, 24, (1170.0, 780.0))
    w = o - P["KEY"]; b = d @ w; c = w @ w - 41.0 ** 2
    t = -b - np.sqrt(b * b - c)
    P["HOOK"] = o + t * d
    print("solution", si, "s %.3f" % s)
    for k in ("KEY", "KS1", "KS2", "PU", "CUP", "SH", "ST", "RH", "HOOK"):
        if k in P:
            X = P[k]
            print("   %-5s (%7.1f, %7.1f, %7.1f)  r %6.1f  clock %6.1f" % (k, X[0], X[1], X[2], np.hypot(X[0], X[1]), np.degrees(np.arctan2(X[1], X[0]))))
    rad = np.array([P["KEY"][0], P["KEY"][1], 0]); rad /= np.linalg.norm(rad)
    tilt = np.degrees(np.arctan2(n[2], n @ rad))
    print("   bezel normal", np.round(n, 3), "tilt towards the driver %.1f" % tilt, " D = %.1f" % (-17.7 - P["KEY"][2]))
EOF
PYTHONPATH=/home/claude/pylib python3 s2table.py
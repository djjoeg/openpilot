cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > s2tape.py <<'EOF'
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
from s2load import *
hook = (1170.0, 780.0)
for si in (0, 2):
    s, cost, pb = SOL[si]
    K = to_car(pb.pts[("B", "outer")])
    o, d = ray(pb, 24, hook)
    # points on the ray at 41 mm from K (solve |o + t d - K| = 41)
    w = o - K
    b = d @ w
    c = w @ w - 41.0 ** 2
    disc = b * b - c
    print("s %.3f key %s  ray closest to key %.1f mm" % (s, np.round(K, 1), np.sqrt(max(w @ w - b * b, 0))))
    if disc >= 0:
        for t in (-b - np.sqrt(disc), -b + np.sqrt(disc)):
            P = o + t * d
            print("    hook at %s  r %.1f  (key z %.1f, dz %.1f)" % (np.round(P, 1), np.hypot(P[0], P[1]), K[2], P[2] - K[2]))
    # also where the ray meets r = 85, 90, 95, 100 cylinders
    for R in (85.0, 90.0, 95.0, 100.0):
        # |(o + t d)_xy| = R
        a2 = d[0] ** 2 + d[1] ** 2
        b2 = 2 * (o[0] * d[0] + o[1] * d[1])
        c2 = o[0] ** 2 + o[1] ** 2 - R * R
        dd = b2 * b2 - 4 * a2 * c2
        if dd >= 0:
            t = (-b2 - np.sqrt(dd)) / (2 * a2)
            P = o + t * d
            print("    ray meets r=%.0f at %s, %.1f from the key" % (R, np.round(P, 1), np.linalg.norm(P - K)))
EOF
PYTHONPATH=/home/claude/pylib python3 s2tape.py
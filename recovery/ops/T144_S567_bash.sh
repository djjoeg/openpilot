cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap/s2load.py <<'EOF'
import sys, pickle
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm")
import numpy as np
import __main__
import stage2
__main__.Stage2 = stage2.Stage2
from jba import rot
from lm import ID, centre
SOL = pickle.load(open("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm/stage2_1.164_1.280_1.407.pkl", "rb"))
ROLL = np.radians(-10.35)
RZ = np.array([[np.cos(ROLL), -np.sin(ROLL), 0], [np.sin(ROLL), np.cos(ROLL), 0], [0, 0, 1]])

def to_car(X):
    return RZ @ np.asarray(X, float)

def cam(pb, n):
    c = pb.cams[n]
    return rot(c["rv"]), np.asarray(c["t"], float), c["f"], np.asarray(c["c"], float)

def project(pb, n, Xcar):
    R, t, f, cc = cam(pb, n)
    Xw = RZ.T @ np.asarray(Xcar, float)
    p = R @ Xw + t
    return p[:2] / p[2] * f + cc, p[2]

def ray(pb, n, uv):
    R, t, f, cc = cam(pb, n)
    d = np.r_[(np.asarray(uv, float) - cc) / f, 1.0]
    o = -R.T @ t
    dw = R.T @ d
    dw /= np.linalg.norm(dw)
    return RZ @ o, RZ @ dw

def triangulate(pb, picks):
    """picks: {cam: (u, v)} -> least squares point (car frame) and per-view residual px."""
    A = []; b = []
    for n, uv in picks.items():
        o, d = ray(pb, n, uv)
        P = np.eye(3) - np.outer(d, d)
        A.append(P); b.append(P @ o)
    X = np.linalg.solve(sum(A), sum(b))
    res = {n: float(np.linalg.norm(project(pb, n, X)[0] - np.asarray(uv))) for n, uv in picks.items()}
    return X, res
EOF
cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap/s2check.py <<'EOF'
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
from s2load import *
for s, cost, pb in SOL:
    print("s", s, "cost", round(cost), "cams", sorted(pb.cams))
    for k in ("CUP", "KS1", "PU", "SH", "RH"):
        if ("L", k) in pb.pts:
            X = to_car(pb.pts[("L", k)])
            print("   %-4s car %s  r %.1f" % (k, np.round(X, 1), np.hypot(X[0], X[1])), {n: np.round(project(pb, n, X)[0]).astype(int).tolist() for n in pb.cams})
    for n in pb.cams:
        R, t, f, cc = cam(pb, n)
        print("   cam", n, "centre(car)", np.round(to_car(-R.T @ t)), "f", round(f), "c", cc)
EOF
PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap/s2check.py
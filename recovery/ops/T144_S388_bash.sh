cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > s35.py <<'EOF'
import numpy as np, cv2
from scipy.optimize import least_squares
import picks
from keyfit import SOLS36, wheel_from_cam36, fr, F, cluster_in_wheel, torus_res, look_at
from jba import rot
from lm import ID, centre
P = picks.P
G35 = np.array([(1537, 300), (1579, 650), (1578, 905), (1558, 1650), (1110, 250), (1200, 560), (1215, 660), (1213, 800),
                (1203, 900), (957, 1670), (882, 1830), (796, 1920), (711, 2075)], float)
Rw, C = wheel_from_cam36(SOLS36[1])
def fit(s, n=35, pts=G35, w=1.0 / 5.0):
    LW = cluster_in_wheel(s, Rw, C)
    ks = [k for k in P[n] if k in LW]
    X = np.array([LW[k] for k in ks]); uv = np.array([P[n][k][:2] for k in ks], float) - centre(ID[n])
    sig = np.array([P[n][k][2] for k in ks], float)
    def res(p):
        R = rot(p[:3]); Pc = X @ R.T + p[3:]
        q = Pc[:, :2] / Pc[:, 2:3] * F
        return np.r_[((q - uv) / sig[:, None]).ravel(), torus_res(p[:3], p[3:], pts, n) * w]
    K = np.array([[F, 0, 0], [0, F, 0], [0, 0, 1]])
    ok, rv, tv = cv2.solvePnP(X, uv, K, None, flags=cv2.SOLVEPNP_SQPNP)
    best = None
    for p0 in [np.r_[rv.ravel(), tv.ravel()]]:
        s_ = least_squares(res, p0, loss='soft_l1', f_scale=1.5)
        if best is None or s_.cost < best.cost: best = s_
    r = res(best.x)
    nc = 2 * len(ks)
    return best.cost, np.median(np.abs(r[:nc] * np.repeat(sig, 2))), np.median(np.abs(r[nc:] / w)), -rot(best.x[:3]).T @ best.x[3:]
for s in np.arange(0.9, 1.61, 0.05):
    c, ec, eg, cam = fit(s)
    print('s %.2f cost %.1f cluster px %.1f grip px %.1f camera %s' % (s, c, ec, eg, np.round(cam, 0)))
EOF
python3 s35.py
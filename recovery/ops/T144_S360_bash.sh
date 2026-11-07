cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > keyfit2.py <<'EOF'
import pickle, sys
import numpy as np, cv2
from scipy.optimize import least_squares
from keyfit import *

def fit_cam(n, LW, rng, n_starts=60, w_grip=1.0 / 8.0):
    ks = [k for k in P[n] if k in LW]
    X = np.array([LW[k] for k in ks]); uv = np.array([P[n][k][:2] for k in ks], float)
    sig = np.array([P[n][k][2] for k in ks], float)
    c = centre(ID[n])
    K = np.array([[F, 0, c[0]], [0, F, c[1]], [0, 0, 1]])
    starts = []
    for flag in (cv2.SOLVEPNP_SQPNP, cv2.SOLVEPNP_EPNP):
        try:
            ok, rv, tv = cv2.solvePnP(X, uv, K, None, flags=flag)
            if ok: starts.append(np.r_[rv.ravel(), tv.ravel()])
        except cv2.error:
            pass
    for _ in range(n_starts):
        cam = np.array([rng.uniform(150, 350), rng.uniform(-200, 120), rng.uniform(-160, 60)])
        tgt = np.array([75.0, -10.0, -100.0]) + rng.normal(size=3) * 25
        up = rng.normal(size=3)
        rv, t = look_at(cam, tgt, up)
        starts.append(np.r_[rv, t])
    def res(p):
        rv, t = p[:3], p[3:]
        pp, z = project(rv, t, X)
        r = (pp - (uv - c)) / sig[:, None]
        r[z <= 0] = 100.0
        out = [r.ravel()]
        if n in GB:
            out.append(torus_res(rv, t, GB[n], n) * w_grip)
        return np.concatenate(out)
    best = None
    for p0 in starts:
        try:
            s = least_squares(res, p0, loss='soft_l1', f_scale=1.5, max_nfev=300)
        except Exception:
            continue
        if best is None or s.cost < best[0]:
            best = (s.cost, s.x)
    return best

if __name__ == '__main__':
    cams = [24, 26, 33, 37]
    sel = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    Rw, C = wheel_from_cam36(SOLS36[sel])
    rng = np.random.default_rng(1)
    rows = []
    for s in np.exp(np.linspace(np.log(0.6), np.log(1.7), 12)):
        LW = cluster_in_wheel(s, Rw, C)
        tot = 0; per = {}
        for n in cams:
            cost, p = fit_cam(n, LW, rng)
            tot += cost; per[n] = (cost, p)
        rows.append((s, tot, per))
        line = ' '.join('%d:%.0f' % (n, per[n][0]) for n in cams)
        print('s %.3f total %.0f | %s' % (s, tot, line), flush=True)
    pickle.dump(rows, open('keyfit2_%d.pkl' % sel, 'wb'))
EOF
(timeout 3500 python3 keyfit2.py 1 > kf2_1.log 2>&1; timeout 3500 python3 keyfit2.py 0 > kf2_0.log 2>&1) &
echo started
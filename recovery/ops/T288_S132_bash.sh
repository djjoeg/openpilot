cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/comp && cat > pnp29.py <<'EOF'
import os, sys, pickle
import numpy as np, cv2
from scipy.optimize import least_squares
import camload as CL
SFM = CL.SFM
here = os.getcwd(); os.chdir(SFM)
import keyfit as KF
os.chdir(here)
s, cost, pb = CL.SOL[2]
LM = {k[1] if k[0] == 'L' else 'B' + k[1][0]: CL.RZ @ np.asarray(pb.pts[k]) for k in pb.pts if k[0] != 'T'}
Rw, C = KF.wheel_from_cam36(KF.SOLS36[1])
LW = KF.cluster_in_wheel(s, Rw, C)
CLU = {k: CL.RZ @ v for k, v in LW.items()}
picks = {'RH': (814, 500), 'CUP': (866, 1236), 'Bo': (1300, 812), 'KS1': (1270, 785), 'KS2': (1310, 858), 'PU': (1530, 795)}
clus = {'S60': (1717, 570), 'S80': (1825, 530)}
def solve(use_cluster, f0=1950.0, free_f=True):
    names = list(picks)
    X = [LM[k] for k in names]; U = [picks[k] for k in names]
    if use_cluster:
        for k, uv in clus.items():
            X.append(CLU[k]); U.append(uv); names.append(k)
    X = np.array(X, float); U = np.array(U, float)
    c = np.array([966.0, 1288.0])
    K = np.array([[f0, 0, c[0]], [0, f0, c[1]], [0, 0, 1]])
    best = None
    for flag in (cv2.SOLVEPNP_SQPNP, cv2.SOLVEPNP_EPNP, cv2.SOLVEPNP_ITERATIVE):
        try:
            ok, rv, tv = cv2.solvePnP(X, U, K, None, flags=flag)
        except cv2.error:
            continue
        if not ok: continue
        def res(p):
            R, _ = cv2.Rodrigues(p[:3]); t = p[3:6]; f = p[6] if free_f else f0
            q = X @ R.T + t
            return ((q[:, :2] / q[:, 2:3]) * f + c - U).ravel()
        p0 = np.r_[rv.ravel(), tv.ravel(), f0] if free_f else np.r_[rv.ravel(), tv.ravel()]
        sol = least_squares(res, p0, loss='soft_l1', f_scale=3.0)
        e = np.linalg.norm(sol.fun.reshape(-1, 2), axis=1)
        if best is None or np.median(e) < best[0]:
            best = (np.median(e), sol.x, e)
    med, p, e = best
    R, _ = cv2.Rodrigues(p[:3]); t = p[3:6]; f = p[6] if free_f else f0
    eye = -R.T @ t
    print('cluster' if use_cluster else 'column only', 'free f' if free_f else 'f %.0f' % f0, '-> f %.0f' % f, 'eye', np.round(eye, 1),
          'errors', dict(zip(names, np.round(e, 1))))
    return R, t, f
out = {}
for uc in (False, True):
    for ff in (True, False):
        out[(uc, ff)] = solve(uc, free_f=ff)
pickle.dump(out, open('pnp29.pkl', 'wb'))
EOF
PYTHONPATH=/home/claude/pylib python3 pnp29.py
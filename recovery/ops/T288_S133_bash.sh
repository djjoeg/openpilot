cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/comp && cat > pnp29b.py <<'EOF'
import numpy as np, cv2, itertools
from scipy.optimize import least_squares
import camload as CL
s, cost, pb = CL.SOL[2]
LM = {k[1] if k[0] == 'L' else 'B' + k[1][0]: CL.RZ @ np.asarray(pb.pts[k]) for k in pb.pts if k[0] != 'T'}
picks = {'RH': (814, 500), 'CUP': (866, 1236), 'Bo': (1300, 812), 'KS1': (1270, 785), 'KS2': (1310, 858), 'PU': (1530, 795)}
c = np.array([966.0, 1288.0])
def fit(names, f0=1950.0, loss='linear'):
    X = np.array([LM[k] for k in names]); U = np.array([picks[k] for k in names], float)
    K = np.array([[f0, 0, c[0]], [0, f0, c[1]], [0, 0, 1]])
    best = None
    for flag in (cv2.SOLVEPNP_SQPNP, cv2.SOLVEPNP_EPNP):
        try: ok, rv, tv = cv2.solvePnP(X, U, K, None, flags=flag)
        except cv2.error: continue
        def res(p):
            R, _ = cv2.Rodrigues(p[:3]); q = X @ R.T + p[3:6]
            return ((q[:, :2] / q[:, 2:3]) * p[6] + c - U).ravel()
        sol = least_squares(res, np.r_[rv.ravel(), tv.ravel(), f0], loss=loss)
        e = np.linalg.norm(sol.fun.reshape(-1, 2), axis=1)
        if best is None or e.max() < best[0]: best = (e.max(), sol.x, e)
    return best
mx, p, e = fit(list(picks))
R, _ = cv2.Rodrigues(p[:3]); print('all six, linear: f %.0f eye %s' % (p[6], np.round(-R.T @ p[3:6], 1)), dict(zip(picks, np.round(e, 1))))
for drop in picks:
    names = [k for k in picks if k != drop]
    mx, p, e = fit(names)
    R, _ = cv2.Rodrigues(p[:3])
    print('without', drop, 'f %.0f' % p[6], 'eye', np.round(-R.T @ p[3:6], 1), dict(zip(names, np.round(e, 1))))
# how far apart are the 3D points, and in the image
for a, b in itertools.combinations(picks, 2):
    print(a, b, '3D %.1f mm' % np.linalg.norm(LM[a] - LM[b]), 'image %.0f px' % np.linalg.norm(np.subtract(picks[a], picks[b])))
EOF
PYTHONPATH=/home/claude/pylib python3 pnp29b.py
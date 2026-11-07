cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > rig.py <<'EOF'
"""The key-photo rig (b3, mm, rigid) placed against the night cluster model (front.pkl, its own units): rotation,
translation and the scale between the two, from all the cluster numerals the key photos see."""
import pickle, sys
import numpy as np, cv2
from scipy.optimize import least_squares
import picks
from lm import ID, centre
from jba import rot
B = pickle.load(open(sys.argv[1] if len(sys.argv) > 1 else 'b3_1917.pkl', 'rb'))
fr = pickle.load(open('front.pkl', 'rb'))
L = {k[1]: v for k, v in fr.pts.items() if k[0] == 'L'}
P = picks.P
use = [n for n in (24, 26, 33, 37) if n in B.cams]
obs = [(n, L[k], np.array(P[n][k][:2], float), P[n][k][2]) for n in use for k in P[n] if k in L]
print(len(obs), 'observations')
def cam_in_front(x, n):
    # front -> rig: X_rig = s R X_front + t
    s, R, t = np.exp(x[0]), rot(x[1:4]), x[4:7]
    c = B.cams[n]; Rk = rot(c['rv'])
    return Rk, c['t'], s, R, t, c['f'], c['c']
def res(x):
    s, R, t = np.exp(x[0]), rot(x[1:4]), x[4:7]
    out = []
    for n, X, uv, sig in obs:
        c = B.cams[n]; Rk = rot(c['rv'])
        Xr = s * R @ X + t
        Pc = Rk @ Xr + c['t']
        if Pc[2] <= 0:
            out.append(np.array([100.0, 100.0])); continue
        p = Pc[:2] / Pc[2] * c['f'] + c['c']
        out.append((p - uv) / sig)
    return np.concatenate(out)
# start: PnP of each camera alone (with both planar solutions) to get candidate rig poses
starts = []
for n in use:
    ks = [k for k in P[n] if k in L]
    obj = np.array([L[k] for k in ks]); img = np.array([P[n][k][:2] for k in ks], float)
    c = B.cams[n]
    K = np.array([[c['f'], 0, c['c'][0]], [0, c['f'], c['c'][1]], [0, 0, 1]])
    for flag in (cv2.SOLVEPNP_SQPNP, cv2.SOLVEPNP_EPNP, cv2.SOLVEPNP_ITERATIVE):
        try:
            ok, rv, tv = cv2.solvePnP(obj, img, K, None, flags=flag)
        except cv2.error:
            continue
        if not ok: continue
        Rf = rot(rv.ravel())        # front -> camera n
        Rk = rot(c['rv'])           # rig -> camera n
        # X_cam = Rf X_front + tf = Rk (s R X_front + t) + tk  -> s R = Rk^T Rf, t = Rk^T (tf - tk) with s = 1 (units ~ mm)
        R0 = Rk.T @ Rf
        for s0 in (0.5, 0.8, 1.0, 1.3, 2.0):
            t0 = Rk.T @ (tv.ravel() * s0 - c['t'])
            starts.append(np.r_[np.log(s0), cv2.Rodrigues(R0)[0].ravel(), t0])
best = None
for x0 in starts:
    sol = least_squares(res, x0, loss='soft_l1', f_scale=1.0, max_nfev=3000)
    r = res(sol.x).reshape(-1, 2) * np.array([o[3] for o in obs])[:, None]
    e = np.linalg.norm(r, axis=1)
    if best is None or np.median(e) < best[0]:
        best = (np.median(e), sol.x, e)
med, x, e = best
print('median %.1f px, max %.1f, scale front-units -> mm %.3f' % (med, e.max(), np.exp(x[0])))
for (n, X, uv, sig), ee in zip(obs, e):
    pass
import collections
per = collections.defaultdict(list)
for (n, X, uv, sig), ee in zip(obs, e):
    per[n].append(round(float(ee), 1))
for n in per: print('  photo', n, per[n])
pickle.dump(x, open('rig_front.pkl', 'wb'))
EOF
python3 rig.py b3_1917.pkl
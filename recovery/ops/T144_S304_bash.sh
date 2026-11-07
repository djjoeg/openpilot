cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > rimfit.py <<'EOF'
"""The steering wheel's back-cover rim (a circle round the wheel's axis) fitted in the key-photo frame (b3_*.pkl)."""
import pickle, sys
import numpy as np
from scipy.optimize import least_squares
from jba import rot, unit_from_angles, angles_from_unit, basis
pb = pickle.load(open(sys.argv[1] if len(sys.argv) > 1 else 'b3_1917.pkl', 'rb'))
RIM = np.load('rim_pts.npy', allow_pickle=True).item()
use = [n for n in (24, 26, 33, 37) if n in RIM and n in pb.cams]

def rays(n, uv):
    c = pb.cams[n]; R = rot(c['rv'])
    x = np.c_[(np.asarray(uv, float) - c['c']) / c['f'], np.ones(len(uv))]
    d = x @ R; d /= np.linalg.norm(d, axis=1, keepdims=True)
    return -R.T @ c['t'], d, c['f']
SETS = [rays(n, RIM[n]) for n in use]

def res(p, sets=SETS):
    C, nrm, r = p[:3], unit_from_angles(p[3], p[4]), p[5]
    out = []
    for o, d, f in sets:
        s = (nrm @ (C - o)) / (d @ nrm)
        Q = o + s[:, None] * d
        depth = s
        out.append((np.linalg.norm(Q - C, axis=1) - r) * f / np.maximum(np.abs(depth), 1e-6))
    return np.concatenate(out)

if __name__ == '__main__':
    bz = pb.pts[('B', 'outer')]
    bn = unit_from_angles(*pb.circles['outer']['ang'])
    rng = np.random.default_rng(0)
    best = []
    for k in range(400):
        a = rng.normal(size=3); a /= np.linalg.norm(a)
        C0 = bz + rng.normal(size=3) * 80
        p0 = np.r_[C0, angles_from_unit(a), rng.uniform(40, 120)]
        try:
            s = least_squares(res, p0, loss='soft_l1', f_scale=2.0, max_nfev=300,
                              bounds=([-np.inf] * 5 + [20], [np.inf] * 5 + [200]))
        except Exception:
            continue
        r = res(s.x)
        per = []; i = 0
        for o, d, f in SETS:
            per.append(np.median(np.abs(r[i:i + len(d)]))); i += len(d)
        best.append((max(per), per, s.x))
    best.sort(key=lambda b: b[0])
    seen = []
    for w, per, x in best:
        C, a, r = x[:3], unit_from_angles(x[3], x[4]), x[5]
        if any(np.linalg.norm(C - q[0]) < 3 and abs(a @ q[1]) > 0.995 for q in seen):
            continue
        seen.append((C, a))
        v = bz - C
        print('worst %.1f %s | radius %.1f | key: along axis %.1f, off axis %.1f | key normal . axis %.2f' %
              (w, [round(float(q), 1) for q in per], r, v @ a, np.linalg.norm(v - (v @ a) * a), bn @ a))
        if len(seen) >= 8:
            break
    pickle.dump(best[0][2], open('rim_fit.pkl', 'wb'))
EOF
timeout 1500 python3 rimfit.py b3_1917.pkl
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > wheelB.py <<'EOF'
"""Wheel (grip ring + back-cover rim on one axis) fitted to a set of key photos with their cameras from b3_*.pkl."""
import pickle, sys
import numpy as np
from scipy.optimize import least_squares
from jba import rot, unit_from_angles, angles_from_unit, basis
pb = pickle.load(open(sys.argv[1], 'rb'))
use = [int(x) for x in sys.argv[2].split(',')]
R_CORE, R_TUBE = 186.0 - 17.7, 17.7
GB = np.load('gripB_clean.npy', allow_pickle=True).item()
RIM = np.load('rim_pts.npy', allow_pickle=True).item()
GB[33] = GB[33][(GB[33][:, 1] < 560) | (GB[33][:, 1] > 1240)]
def rays(n, uv):
    c = pb.cams[n]; R = rot(c['rv'])
    x = np.c_[(np.asarray(uv, float) - c['c']) / c['f'], np.ones(len(uv))]
    d = x @ R; d /= np.linalg.norm(d, axis=1, keepdims=True)
    return -R.T @ c['t'], d, c['f']
G = [rays(n, GB[n]) for n in use if n in GB]
Rm = [rays(n, RIM[n]) for n in use if n in RIM]
PHI = np.linspace(0, 2 * np.pi, 1440, endpoint=False)
def res(p):
    C, a, zs, rs = p[:3], unit_from_angles(p[3], p[4]), p[5], p[6]
    u1, u2 = basis(a)
    ring = C + R_CORE * (np.cos(PHI)[:, None] * u1 + np.sin(PHI)[:, None] * u2)
    out = []
    for o, d, f in G:
        w = ring - o
        al = d @ w.T
        perp = np.sqrt(np.maximum((w ** 2).sum(1)[None] - al ** 2, 0))
        k = np.argmin(perp, axis=1); idx = np.arange(len(k))
        out.append((perp[idx, k] - R_TUBE) * f / np.maximum(al[idx, k], 1e-6) / 2.0)
    Cr = C + zs * a
    for o, d, f in Rm:
        s = (a @ (Cr - o)) / (d @ a)
        Q = o + s[:, None] * d
        out.append((np.linalg.norm(Q - Cr - ((Q - Cr) @ a)[:, None] * a, axis=1) - rs) * f / np.maximum(np.abs(s), 1e-6))
    return np.concatenate(out)
bz = pb.pts[('B', 'outer')]
rng = np.random.default_rng(5)
sols = []
for k in range(500):
    a = rng.normal(size=3); a /= np.linalg.norm(a)
    u = np.cross(a, rng.normal(size=3)); u /= np.linalg.norm(u)
    C0 = bz + rng.uniform(40, 160) * u + rng.uniform(20, 160) * a
    p0 = np.r_[C0, angles_from_unit(a), rng.uniform(-140, -20), rng.uniform(45, 100)]
    try:
        s = least_squares(res, p0, loss='soft_l1', f_scale=3.0, max_nfev=300,
                          bounds=([-np.inf] * 5 + [-250, 30], [np.inf] * 5 + [0, 120]))
    except Exception:
        continue
    r = res(s.x)
    parts = []; i = 0
    for o, d, f in G + Rm:
        parts.append(np.median(np.abs(r[i:i + len(d)]))); i += len(d)
    sols.append((max(parts), parts, s.x))
sols.sort(key=lambda s: s[0])
seen = []
for w, parts, x in sols:
    C, a, zs, rs = x[:3], unit_from_angles(x[3], x[4]), x[5], x[6]
    v = bz - C
    if v @ a > 0:      # orient: axis towards the driver means the key is at negative z
        pass
    zk = v @ a
    rk = np.linalg.norm(v - zk * a)
    sig = (round(zs), round(rs), round(zk), round(rk))
    if any(abs(sig[0] - q[0]) < 4 and abs(sig[2] - q[2]) < 4 and abs(sig[3] - q[3]) < 4 for q in seen):
        continue
    seen.append(sig)
    print('photos %s worst %.1f %s | rim z %.0f r %.0f | bezel z %.0f, %.0f from axis' % (use, w, [round(float(q), 1) for q in parts], zs, rs, zk, rk))
    if len(seen) >= 6:
        break
EOF
for u in 24,26 33,37 24,26,33,37; do timeout 1200 python3 wheelB.py b3_1917.pkl $u; done
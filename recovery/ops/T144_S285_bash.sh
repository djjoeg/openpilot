cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > torus36.py <<'EOF'
"""The wheel's grip (a ring 372 mm across, 35.4 mm thick) fitted to its outline in photo 36, in camera 36's frame (mm):
every distinct solution."""
import numpy as np, pickle
from scipy.optimize import least_squares
from jba import unit_from_angles, angles_from_unit, basis
from lm import ID, centre
R_CORE, R_TUBE = 186.0 - 17.7, 17.7
SIL = np.load('silh_A.npy', allow_pickle=True).item()

def res(p, o, d, f):
    C, nrm = p[:3], unit_from_angles(p[3], p[4])
    u1, u2 = basis(nrm)
    phi = np.linspace(0, 2 * np.pi, 1440, endpoint=False)
    ring = C + R_CORE * (np.cos(phi)[:, None] * u1 + np.sin(phi)[:, None] * u2)
    w = ring - o
    al = d @ w.T
    perp = np.sqrt(np.maximum((w ** 2).sum(1)[None] - al ** 2, 0))
    k = np.argmin(perp, axis=1)
    idx = np.arange(len(k))
    return (perp[idx, k] - R_TUBE) * f / np.maximum(al[idx, k], 1e-9)

def solve(n, f, pts, seeds=60, rng=np.random.default_rng(0)):
    uv = np.asarray(pts, float)
    x = np.c_[(uv - centre(ID[n])) / f, np.ones(len(uv))]
    d = x / np.linalg.norm(x, axis=1, keepdims=True)
    o = np.zeros(3)
    E = SIL[n]['ell'] if n in SIL else None
    c = np.array(E[0]) if E is not None else uv.mean(0)
    cd = np.r_[(c - centre(ID[n])) / f, 1.0]; cd /= np.linalg.norm(cd)
    size = np.sqrt(E[1][0] * E[1][1]) / 2 if E is not None else 800
    dist = f * 186.0 / size
    sols = []
    for k in range(seeds):
        a = -cd + 0.6 * rng.normal(size=3); a /= np.linalg.norm(a)
        p0 = np.r_[cd * dist, angles_from_unit(a)]
        s = least_squares(res, p0, args=(o, d, f), loss='soft_l1', f_scale=2.0, max_nfev=300)
        r = res(s.x, o, d, f)
        C, a = s.x[:3], unit_from_angles(s.x[3], s.x[4])
        if a @ C < 0:
            a = -a          # axis pointing away from the camera (towards the dash)
        m = np.median(np.abs(r))
        if not any(np.linalg.norm(C - q[0]) < 3 and q[1] @ a > 0.999 for q in sols):
            sols.append((C, a, m))
    sols.sort(key=lambda s: s[2])
    return sols

if __name__ == '__main__':
    for f in (1917.0,):
        sols = solve(36, f, SIL[36]['pts'])
        for C, a, m in sols[:6]:
            print('f', f, 'centre', np.round(C, 1), '|%.0f|' % np.linalg.norm(C), 'axis', np.round(a, 3), 'median px %.2f' % m)
        pickle.dump(sols[:6], open('torus36_sols.pkl', 'wb'))
EOF
timeout 900 python3 torus36.py
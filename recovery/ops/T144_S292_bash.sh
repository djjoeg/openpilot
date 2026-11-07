cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > torusF.py <<'EOF'
"""The wheel in the night driver-side frame (front.pkl): the grip ring fitted to photo 36's outline and photo 21's
grip edges, with the frame's scale (mm per unit) free."""
import pickle, numpy as np
from scipy.optimize import least_squares
from jba import rot, unit_from_angles, angles_from_unit, basis
from lm import ID, centre
R_CORE, R_TUBE = 186.0 - 17.7, 17.7
pb = pickle.load(open('front.pkl', 'rb'))
SIL = np.load('silh_A.npy', allow_pickle=True).item()
G21 = np.load('grip21.npy', allow_pickle=True).item()

def clean(P, deg=3, tol=12.0):
    P = P[P[:, 1] < 2000]
    for _ in range(3):
        c = np.polyfit(P[:, 1], P[:, 0], deg)
        r = P[:, 0] - np.polyval(c, P[:, 1])
        keep = np.abs(r) < max(tol, 2.5 * np.median(np.abs(r)))
        P = P[keep]
    return P

def rays(n, uv):
    c = pb.cams[n]; R = rot(c['rv'])
    x = np.c_[(np.asarray(uv, float) - c['c']) / c['f'], np.ones(len(uv))]
    d = x @ R; d /= np.linalg.norm(d, axis=1, keepdims=True)
    return -R.T @ c['t'], d, c['f']

def res(p, sets):
    C, nrm, s = p[:3], unit_from_angles(p[3], p[4]), np.exp(p[5])
    R, r = R_CORE / s, R_TUBE / s
    u1, u2 = basis(nrm)
    phi = np.linspace(0, 2 * np.pi, 1440, endpoint=False)
    ring = C + R * (np.cos(phi)[:, None] * u1 + np.sin(phi)[:, None] * u2)
    out = []
    for o, d, f in sets:
        w = ring - o
        al = d @ w.T
        perp = np.sqrt(np.maximum((w ** 2).sum(1)[None] - al ** 2, 0))
        k = np.argmin(perp, axis=1); idx = np.arange(len(k))
        out.append((perp[idx, k] - r) * f / np.maximum(al[idx, k], 1e-9))
    return np.concatenate(out)

if __name__ == '__main__':
    L21, R21 = clean(G21['L']), clean(G21['R'])
    print('21 edges kept', len(L21), len(R21))
    sets = [rays(36, SIL[36]['pts']), rays(21, L21), rays(21, R21)]
    sols36 = pickle.load(open('torus36_sols.pkl', 'rb'))
    R36 = rot(pb.cams[36]['rv']); t36 = pb.cams[36]['t']; o36 = -R36.T @ t36
    best = []
    for C_cam, a_cam, m in sols36[:2]:
        # camera-36 frame (mm) -> front frame: X = R36^T (x_cam / s - ... ) ; try scales
        for s in np.exp(np.linspace(np.log(20), np.log(400), 25)):
            C = R36.T @ (C_cam / s - t36)
            a = R36.T @ a_cam
            p0 = np.r_[C, angles_from_unit(a), np.log(s)]
            sol = least_squares(res, p0, args=(sets,), loss='soft_l1', f_scale=2.0, max_nfev=300)
            r = res(sol.x, sets)
            n0 = len(sets[0][1]); n1 = len(sets[1][1])
            m36, mL, mR = np.median(np.abs(r[:n0])), np.median(np.abs(r[n0:n0 + n1])), np.median(np.abs(r[n0 + n1:]))
            best.append((max(m36, mL, mR), m36, mL, mR, sol.x))
    best.sort(key=lambda b: b[0])
    for b in best[:8]:
        x = b[4]
        print('worst %.1f  36 %.1f  21L %.1f  21R %.1f  scale %.1f mm/unit  axis %s' % (b[0], b[1], b[2], b[3], np.exp(x[5]),
              np.round(unit_from_angles(x[3], x[4]), 3)))
    pickle.dump(best[0][4], open('torusF.pkl', 'wb'))
EOF
timeout 1500 python3 torusF.py
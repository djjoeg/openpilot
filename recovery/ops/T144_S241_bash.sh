cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > torusA.py <<'EOF'
import pickle, numpy as np, cv2
from scipy.optimize import least_squares
from jba import rot, unit_from_angles, angles_from_unit, basis
from lm import ID, NUM, centre, load
R_MM, r_MM = 186.0 - 17.7, 17.7
S = load('sfm_A.pkl')['clusters'][0]
CAMS = {NUM[i]: v for i, v in S['cams'].items()}
K1 = S['k1']
SIL = np.load('silh_A.npy', allow_pickle=True).item()

def rays(n, uv):
    rv, t, f = CAMS[n]
    R = rot(rv)
    xd = (uv - centre(ID[n])) / f
    xu = xd.copy()
    for _ in range(5):
        xu = xd / (1 + K1 * (xu ** 2).sum(1, keepdims=True))
    d = np.c_[xu, np.ones(len(xu))] @ R
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    return -R.T @ np.asarray(t, float), d, f

def res(p, sets):
    C, nrm, s = p[:3], unit_from_angles(p[3], p[4]), np.exp(p[5])
    R, r = R_MM / s, r_MM / s
    u1, u2 = basis(nrm)
    phi = np.linspace(0, 2 * np.pi, 1440, endpoint=False)
    ring = C + R * (np.cos(phi)[:, None] * u1 + np.sin(phi)[:, None] * u2)
    out = []
    for o, d, f in sets:
        w = ring - o
        al = d @ w.T
        perp = np.sqrt(np.maximum((w ** 2).sum(1)[None] - al ** 2, 0))
        k = np.argmin(perp, axis=1)
        idx = np.arange(len(k))
        out.append((perp[idx, k] - r) * f / np.maximum(al[idx, k], 1e-9))
    return np.concatenate(out)

if __name__ == '__main__':
    use = [0, 6, 7, 9, 36]
    sets = [rays(n, SIL[n]['pts'][::2]) for n in use]
    # start: the centre of each photo's ellipse triangulated
    from lm import triangulate
    cv = {'cams': {ID[n]: CAMS[n] for n in CAMS}, 'k1': K1}
    X0, e = triangulate(cv, [(ID[n], np.array(SIL[n]['ell'][0])) for n in use])
    print('ellipse centres triangulate to', np.round(X0, 3), 'errors px', np.round(e, 1))
    # scale guess from photo 36: distance
    o, d, f = rays(36, np.array([SIL[36]['ell'][0]]))
    dist = np.linalg.norm(X0 - o)
    s0 = 1.0
    best = None
    for ax in ([0, 0, 1], [0, 0.3, 1], [0, -0.3, 1], [0.3, 0, 1], [-0.3, 0, 1]):
        a = np.array(ax, float); a /= np.linalg.norm(a)
        for s in (40, 80, 160, 320, 640):
            p0 = np.r_[X0, angles_from_unit(a), np.log(s)]
            sol = least_squares(res, p0, args=(sets,), loss='soft_l1', f_scale=2.0, max_nfev=400)
            m = np.median(np.abs(res(sol.x, sets)))
            if best is None or m < best[0]:
                best = (m, sol.x)
    p = best[1]
    r = res(p, sets)
    print('torus: centre', np.round(p[:3], 3), 'axis', np.round(unit_from_angles(p[3], p[4]), 4), 'mm per A unit', round(np.exp(p[5]), 2))
    k = 0
    for n, (o, d, f) in zip(use, sets):
        rr = r[k:k + len(d)]; k += len(d)
        print('   photo', n, 'median |px|', round(np.median(np.abs(rr)), 2), 'bias', round(np.median(rr), 2))
    pickle.dump(dict(p=p, use=use), open('torusA.pkl', 'wb'))
EOF
timeout 1200 python3 torusA.py
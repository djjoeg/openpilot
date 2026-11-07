cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > perphoto.py <<'EOF'
"""One key photo at a time: the camera's pose relative to the steering wheel found from the grip's outline (a ring 372
across, 35.4 thick) and the wheel's back-cover rim (a circle round the same axis: radius and depth free), then the key
bezel placed from its own outline (37 mm across). Wheel frame: z towards the driver, grip centre plane z = 0."""
import pickle, sys
import numpy as np
import cv2
from scipy.optimize import least_squares
from lm import ID, centre
R_CORE, R_TUBE = 186.0 - 17.7, 17.7
F = float(sys.argv[2]) if len(sys.argv) > 2 else 1917.0
GB = np.load('gripB_clean.npy', allow_pickle=True).item()
RIM = np.load('rim_pts.npy', allow_pickle=True).item()
ELL = pickle.load(open('bezel_ellipses.pkl', 'rb'))
GB[33] = GB[33][(GB[33][:, 1] < 560) | (GB[33][:, 1] > 1240)]

def cam_rays(rv, t, uv, n):
    R = cv2.Rodrigues(np.asarray(rv, float))[0]
    x = np.c_[(np.asarray(uv, float) - centre(ID[n])) / F, np.ones(len(uv))]
    d = x @ R
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    return -R.T @ np.asarray(t, float), d

PHI = np.linspace(0, 2 * np.pi, 1440, endpoint=False)
RING = np.c_[np.cos(PHI), np.sin(PHI), np.zeros_like(PHI)]

def torus_res(o, d):
    w = R_CORE * RING - o
    al = d @ w.T
    perp = np.sqrt(np.maximum((w ** 2).sum(1)[None] - al ** 2, 0))
    k = np.argmin(perp, axis=1); idx = np.arange(len(k))
    return (perp[idx, k] - R_TUBE) * F / np.maximum(al[idx, k], 1e-6)

def circle_res(o, d, zs, rs):
    # plane z = zs, centre on the axis
    s = (zs - o[2]) / d[:, 2]
    Q = o + s[:, None] * d
    return (np.hypot(Q[:, 0], Q[:, 1]) - rs) * F / np.maximum(np.abs(s), 1e-6)

def res(p, n):
    rv, t, zs, rs = p[:3], p[3:6], p[6], p[7]
    o, dg = cam_rays(rv, t, GB[n], n)
    _, dr = cam_rays(rv, t, RIM[n], n)
    return np.r_[torus_res(o, dg) / 2.0, circle_res(o, dr, zs, rs)]

def solve(n, seeds=300, rng=np.random.default_rng(0)):
    sols = []
    for k in range(seeds):
        # camera somewhere right of and behind the wheel, looking roughly at the column's right side
        zs0 = rng.uniform(-110, -25); rs0 = rng.uniform(45, 85)
        target = np.array([rng.uniform(30, 80), rng.uniform(-60, 20), zs0 - rng.uniform(10, 70)])
        dirn = rng.normal(size=3); dirn[0] = abs(dirn[0]) + 0.5; dirn /= np.linalg.norm(dirn)
        cpos = target + rng.uniform(150, 320) * dirn
        fwd = target - cpos; fwd /= np.linalg.norm(fwd)
        up = rng.normal(size=3); up -= (up @ fwd) * fwd; up /= np.linalg.norm(up)
        right = np.cross(fwd, up)          # image x
        down = np.cross(fwd, right)        # image y
        Rm = np.vstack([right, down, fwd])
        if np.linalg.det(Rm) < 0:
            Rm[0] = -Rm[0]
        rv = cv2.Rodrigues(Rm)[0].ravel(); t = -Rm @ cpos
        p0 = np.r_[rv, t, zs0, rs0]
        try:
            s = least_squares(res, p0, args=(n,), loss='soft_l1', f_scale=3.0, max_nfev=400,
                              bounds=([-np.inf] * 6 + [-200, 30], [np.inf] * 6 + [0, 110]))
        except Exception:
            continue
        r = res(s.x, n)
        ng = len(GB[n])
        mg, mr = np.median(np.abs(r[:ng])) * 2.0, np.median(np.abs(r[ng:]))
        sols.append((max(mg, mr), mg, mr, s.x))
    sols.sort(key=lambda s: s[0])
    return sols

def bezel_in_wheel(n, p):
    """The bezel's centre from its outline: on the ray through the outline's centre, at the distance its size gives."""
    E = ELL[n]['outer']
    rad = np.sqrt(E[1][0] * E[1][1]) / 2
    dist = F * 18.5 / rad
    o, d = cam_rays(p[:3], p[3:6], np.array([E[0]]), n)
    return o + dist * d[0], o

if __name__ == '__main__':
    n = int(sys.argv[1])
    sols = solve(n)
    seen = []
    for w, mg, mr, p in sols:
        b, o = bezel_in_wheel(n, p)
        key = tuple(np.round(b / 8))
        if any(np.linalg.norm(b - q) < 8 for q in seen):
            continue
        seen.append(b)
        ang = np.degrees(np.arctan2(b[1], b[0]))
        print('photo %d worst %.1f (grip %.1f rim %.1f) | rim z %.0f r %.0f | bezel x %.0f y %.0f z %.0f (%.0f deg, %.0f from axis) | camera %s'
              % (n, w, mg, mr, p[6], p[7], b[0], b[1], b[2], ang, np.hypot(b[0], b[1]), np.round(o, 0)))
        if len(seen) >= 6:
            break
    pickle.dump(sols[:20], open('perphoto_%d.pkl' % n, 'wb'))
EOF
for n in 26 33 24; do timeout 1700 python3 perphoto.py $n; done
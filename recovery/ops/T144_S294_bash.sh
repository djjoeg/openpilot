cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > rim21.py <<'EOF'
import pickle, numpy as np
from scipy.optimize import least_squares
from jba import basis
from lm import ID, centre
F = 1917.0
RIM = np.array([(1092, 1097), (1035, 1242), (1011, 1403), (1003, 1532), (1011, 1677), (1044, 1806), (1092, 1903)], float)
LH = np.array([1137.0, 1548.0])
def ray(uv):
    x = np.r_[(uv - centre(ID[21])) / F, 1.0]
    return x / np.linalg.norm(x)
def circle_res(p, C, a):
    zs, rs = p
    u1, u2 = basis(a)
    phi = np.linspace(0, 2 * np.pi, 2880, endpoint=False)
    ring = C + zs * a + rs * (np.cos(phi)[:, None] * u1 + np.sin(phi)[:, None] * u2)
    q = ring[:, :2] / ring[:, 2:3] * F + centre(ID[21])
    front = ring[:, 2] > 0
    out = []
    for uv in RIM:
        dd = np.linalg.norm(q[front] - uv, axis=1)
        out.append(dd.min())
    return np.array(out)
def hole_z(C, a, rs):
    """Where the hole's ray meets the cylinder of radius rs about the axis (the nearer hit): z along the axis."""
    d = ray(LH)
    # points X = t d; distance from the axis line (C, a) equals rs
    def f(t):
        X = t * d - C
        return np.linalg.norm(X - (X @ a) * a) - rs
    ts = np.linspace(50, 800, 3000)
    v = np.array([f(t) for t in ts])
    k = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]
    if not len(k):
        return np.nan, np.nan
    t = ts[k[0]]
    X = t * d - C
    return X @ a, t
sols = pickle.load(open('torus21_sols.pkl', 'rb'))
for s in sols[:12]:
    C, a = s[3], s[4]
    best = None
    for zs0 in (30, 60, 90, 120):
        for rs0 in (40, 60, 80):
            r = least_squares(circle_res, [zs0, rs0], args=(C, a), bounds=([0, 20], [250, 150]))
            if best is None or r.cost < best.cost:
                best = r
    zs, rs = best.x
    e = circle_res(best.x, C, a)
    zh, t = hole_z(C, a, rs)
    print('torus worst %.1f | rim: %.0f mm behind the grip centre, radius %.0f (fit px %.1f) | hole %.0f behind, %.0f from camera'
          % (s[0], zs, rs, np.sqrt(np.mean(e ** 2)), zh, t))
EOF
timeout 900 python3 rim21.py
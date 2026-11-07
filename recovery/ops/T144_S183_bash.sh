cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > circpose.py <<'EOF'
"""Pose of a circle of known radius from its edge pixels in one photo (camera at the origin looking along +z)."""
import numpy as np
from scipy.optimize import least_squares
from jba import unit_from_angles, angles_from_unit


def rays(uv, f, c):
    x = np.c_[(uv - c) / f, np.ones(len(uv))]
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def fit_circle(uv, f, c, r, starts=24, seed=0):
    d = rays(np.asarray(uv, float), f, c)
    m = d.mean(0)
    m /= np.linalg.norm(m)
    sols = []
    rng = np.random.default_rng(seed)
    for k in range(starts):
        # start: centre along the mean ray at a distance matching the apparent size, random normal facing the camera
        ang = np.median(np.arccos(np.clip(d @ m, -1, 1)))
        dist = r / np.tan(ang)
        n0 = -m + 0.9 * rng.normal(size=3)
        n0 /= np.linalg.norm(n0)
        if n0 @ m > 0:
            n0 = -n0
        x0 = np.r_[m * dist, angles_from_unit(n0)]

        def res(x):
            C, n = x[:3], unit_from_angles(x[3], x[4])
            s = (n @ C) / (d @ n)
            Q = s[:, None] * d
            return (np.linalg.norm(Q - C, axis=1) - r) * f / np.maximum(Q[:, 2], 1e-6)

        sol = least_squares(res, x0, loss='soft_l1', f_scale=2.0)
        C, n = sol.x[:3], unit_from_angles(sol.x[3], sol.x[4])
        if n @ C > 0:
            n = -n
        rms = np.sqrt(np.mean(res(sol.x) ** 2))
        if not any(np.linalg.norm(C - s[0]) < 1.0 and abs(n @ s[1]) > 0.999 for s in sols):
            sols.append((C, n, rms))
    sols.sort(key=lambda s: s[2])
    return sols
EOF
python3 - <<'EOF'
import pickle, numpy as np
from circpose import fit_circle
from lm import ID, centre
E = pickle.load(open('bezel_ellipses.pkl', 'rb'))
for n in (24, 26, 29, 33, 37):
    for ring, r in (('outer', 18.5), ('chrome', 12.5)):
        sols = fit_circle(E[n][ring + '_pts'], 1880.0, centre(ID[n]), r)
        print(n, ring, [(np.round(C, 1), np.round(nn, 3), round(rms, 2)) for C, nn, rms in sols[:3]])
EOF
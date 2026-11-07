cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > torus21.py <<'EOF'
"""Photo 21 alone: the grip ring (known size) fitted to the grip's two edges, in camera 21's frame (mm)."""
import pickle, numpy as np
from scipy.optimize import least_squares
from jba import unit_from_angles, angles_from_unit, basis
from torus36 import res
from torusF import clean
from lm import ID, centre
G21 = np.load('grip21.npy', allow_pickle=True).item()
F = 1917.0
L, R = clean(G21['L']), clean(G21['R'])
uv = np.r_[L, R]
x = np.c_[(uv - centre(ID[21])) / F, np.ones(len(uv))]
d = x / np.linalg.norm(x, axis=1, keepdims=True)
o = np.zeros(3)
rng = np.random.default_rng(1)
sols = []
for k in range(600):
    # a point on the grip near the band's middle, 60-400 mm away; ring centre 168 mm off in a random direction
    j = rng.integers(len(d)); dist = rng.uniform(60, 450)
    q = d[j] * dist
    a = rng.normal(size=3); a /= np.linalg.norm(a)
    u = np.cross(a, rng.normal(size=3)); u /= np.linalg.norm(u)
    p0 = np.r_[q + 168.3 * u, angles_from_unit(a)]
    s = least_squares(res, p0, args=(o, d, F), loss='soft_l1', f_scale=3.0, max_nfev=200)
    r = res(s.x, o, d, F)
    nL = len(L)
    mL, mR = np.median(np.abs(r[:nL])), np.median(np.abs(r[nL:]))
    C, a = s.x[:3], unit_from_angles(s.x[3], s.x[4])
    if a[2] < 0: a = -a
    sols.append((max(mL, mR), mL, mR, C, a))
sols.sort(key=lambda s: s[0])
for s in sols[:20]:
    print('worst %.1f L %.1f R %.1f centre %s |%.0f| axis %s' % (s[0], s[1], s[2], np.round(s[3], 0), np.linalg.norm(s[3]), np.round(s[4], 3)))
pickle.dump(sols[:20], open('torus21_sols.pkl', 'wb'))
EOF
timeout 1500 python3 torus21.py
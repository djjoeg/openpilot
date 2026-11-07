cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > brun2.py <<'EOF'
"""Key photos on their own (bezel for scale) plus the grip outline as a torus of known size: gives where the key sits
relative to the steering wheel's ring without going through the dash."""
import pickle, sys
import numpy as np
import brun, picks
from jba import lm_solve, unit_from_angles, angles_from_unit, basis, rot
from torus_fit import tor_res, rays_cam, R_CORE, R_TUBE

P = picks.P
P[24].pop('P', None)
P[37].pop('CUP', None)
for n in (24, 26):
    P[n]['ST'] = P[n]['ST'][:2] + (15,)
GB = np.load('gripB_clean.npy', allow_pickle=True).item()

pb = pickle.load(open('bjba.pkl', 'rb'))
pb.cams[29]['fprior'] = (1030.0, 60.0)
for n in (24, 26, 33, 37):
    pb.cams[n]['fprior'] = (2150.0, 250.0)
brun.add_all(pb)
lm_solve(pb, iters=30, verbose=False)
brun.prune(pb)
lm_solve(pb, iters=30, verbose=False)
brun.report(pb, worst=8)
# torus: start from many poses near the grip seen in photo 26, fit to all B outlines with the cameras fixed
sets = [(*rays_cam(pb, n, uv), pb.cams[n]['f']) for n, uv in GB.items()]
from scipy.optimize import least_squares
best = None
rng = np.random.default_rng(3)
o26, d26 = rays_cam(pb, 26, GB[26])
for trial in range(300):
    # a point on the grip: along a ray of photo 26's outline at 60-200 mm, the ring's centre 168 mm away in a random
    # direction perpendicular to a random axis
    k = rng.integers(len(d26)); dist = rng.uniform(60, 220)
    q = o26 + dist * d26[k]
    ax = rng.normal(size=3); ax /= np.linalg.norm(ax)
    u = np.cross(ax, rng.normal(size=3)); u /= np.linalg.norm(u)
    C0 = q + R_CORE * u
    p0 = np.r_[C0, angles_from_unit(ax)]
    try:
        s = least_squares(tor_res, p0, args=(sets,), loss='soft_l1', f_scale=4.0, max_nfev=300)
    except Exception:
        continue
    r = tor_res(s.x, sets)
    sc = np.median(np.abs(r))
    if best is None or sc < best[0]:
        best = (sc, s.x)
        print('  trial', trial, 'median px', round(sc, 2), flush=True)
p = best[1]
print('torus (B frame): centre', np.round(p[:3], 1), 'axis', np.round(unit_from_angles(p[3], p[4]), 3))
for n, uv in GB.items():
    r = tor_res(p, [(*rays_cam(pb, n, uv), pb.cams[n]['f'])])
    print('   photo', n, 'median', round(np.median(r), 1), 'mad', round(np.median(np.abs(r - np.median(r))), 1))
pickle.dump(dict(pb=pb, torus=p), open('bjba2.pkl', 'wb'))
EOF
timeout 3000 python3 brun2.py 2>&1 | tail -40
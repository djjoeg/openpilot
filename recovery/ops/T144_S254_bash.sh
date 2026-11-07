cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > torusB_family.py <<'EOF'
import pickle, numpy as np, sys
from scipy.optimize import least_squares
from jba import rot, unit_from_angles, angles_from_unit, basis
from torus_fit import tor_res, rays_cam, R_CORE, R_TUBE
pb = pickle.load(open(sys.argv[1] if len(sys.argv) > 1 else 'bjba_f1935.pkl', 'rb'))
GB = np.load('gripB_clean.npy', allow_pickle=True).item()
use = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [24, 26, 37, 29, 33]
GB[33] = GB[33][(GB[33][:, 1] < 560) | (GB[33][:, 1] > 1240)]
sets = [(*rays_cam(pb, n, GB[n]), pb.cams[n]['f']) for n in use]
key = pb.pts[('B', 'outer')]
keyn = unit_from_angles(*pb.circles['outer']['ang'])
rh = pb.pts.get(('L', 'RH'))
rng = np.random.default_rng(7)
sols = []
o26, d26 = rays_cam(pb, 26, GB[26])
for trial in range(400):
    k = rng.integers(len(d26)); dist = rng.uniform(50, 250)
    q = o26 + dist * d26[k]
    ax = rng.normal(size=3); ax /= np.linalg.norm(ax)
    u = np.cross(ax, rng.normal(size=3)); u /= np.linalg.norm(u)
    p0 = np.r_[q + R_CORE * u, angles_from_unit(ax)]
    try:
        s = least_squares(tor_res, p0, args=(sets,), loss='soft_l1', f_scale=4.0, max_nfev=200)
    except Exception:
        continue
    r = tor_res(s.x, sets)
    per = []
    kk = 0
    for (o, d, f) in sets:
        per.append(np.median(np.abs(r[kk:kk + len(d)]))); kk += len(d)
    C, a = s.x[:3], unit_from_angles(s.x[3], s.x[4])
    # orient the axis towards the driver: the key is behind the wheel (towards the dash), so make key.along < 0
    v = key - C
    if v @ a > 0:
        a = -a
    along = v @ a
    off = np.linalg.norm(v - along * a)
    vr = rh - C if rh is not None else None
    sols.append((max(per), np.median(np.abs(r)), along, off, C, a, (vr @ a if vr is not None else 0), (np.linalg.norm(vr - (vr @ a) * a) if vr is not None else 0)))
sols.sort(key=lambda s: s[0])
print('best worst-photo medians:', [round(s[0], 1) for s in sols[:15]])
good = [s for s in sols if s[0] < max(6.0, 1.5 * sols[0][0])]
print(len(good), 'good solutions')
for s in good[:25]:
    print('  worst %.1f  key: along %.0f off %.0f | RH: along %.0f off %.0f | axis.keynormal %.2f' % (s[0], s[2], s[3], s[6], s[7], s[5] @ keyn))
EOF
timeout 1500 python3 torusB_family.py bjba_f1935.pkl 2>&1 | grep -v "torus from photo\|grip outline residual"
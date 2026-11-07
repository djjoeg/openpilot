cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > torus_j2.py <<'EOF'
import pickle, numpy as np
from scipy.optimize import least_squares
from jba import rot, unit_from_angles, angles_from_unit, basis
from torus_fit import tor_res, rays_cam
SIL = np.load('silh_A.npy', allow_pickle=True).item()
GB = np.load('gripB_clean.npy', allow_pickle=True).item()
pb = pickle.load(open('jba2.pkl', 'rb'))
p36 = pickle.load(open('torus36.pkl', 'rb'))
def sets_for(pb, which):
    out = []
    for n in which:
        uv = SIL[n]['pts'][::3] if n in SIL else GB[n]
        out.append((*rays_cam(pb, n, uv), pb.cams[n]['f']))
    return out
for which in ([36], [36, 24, 26], [36, 24, 26, 33], [36, 24, 26, 33, 37, 29]):
    sets = sets_for(pb, which)
    best = None
    for dz in (0, 30, -30):
        for tilt in ([0, 0], [0.15, 0], [-0.15, 0], [0, 0.15], [0, -0.15]):
            a = unit_from_angles(p36[3], p36[4]) + np.array([tilt[0], tilt[1], 0])
            a /= np.linalg.norm(a)
            p0 = np.r_[p36[:3] + dz * a, angles_from_unit(a)]
            s = least_squares(tor_res, p0, args=(sets,), loss='soft_l1', f_scale=3.0, max_nfev=300)
            m = np.median(np.abs(tor_res(s.x, sets)))
            if best is None or m < best[0]:
                best = (m, s.x)
    p = best[1]
    r = tor_res(p, sets); k = 0; out = []
    for n, (o, d, f) in zip(which, sets):
        rr = r[k:k + len(d)]; k += len(d); out.append((n, round(float(np.median(rr)), 1), round(float(np.median(np.abs(rr))), 1)))
    C, ax = p[:3], unit_from_angles(p[3], p[4])
    key = pb.pts[('B', 'outer')]
    v = key - C
    along = v @ ax
    off = np.linalg.norm(v - along * ax)
    print(which, 'centre', np.round(C, 1), 'axis', np.round(ax, 3), '| key: along axis %.0f, off axis %.0f' % (along, off), out)
EOF
timeout 1200 python3 torus_j2.py 2>&1 | grep -v "torus from photo\|grip outline residual"
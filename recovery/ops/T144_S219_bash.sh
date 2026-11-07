cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > torus_fit.py <<'EOF'
import pickle, numpy as np, cv2
from scipy.optimize import least_squares
from jba import rot, unit_from_angles, angles_from_unit, basis, lm_solve
from grip_pts import G36
import brun

pb = pickle.load(open('jba2.pkl', 'rb'))
GB = np.load('gripB_clean.npy', allow_pickle=True).item()
R_TUBE = 17.7
R_CORE = 186.0 - R_TUBE

def rays_cam(pb, n, uv):
    c = pb.cams[n]; R = rot(c['rv']); f = c['f']
    x = np.c_[(uv - c['c']) / f, np.ones(len(uv))]
    d = x @ R; d /= np.linalg.norm(d, axis=1, keepdims=True)
    return -R.T @ c['t'], d

def tor_res(p, sets, R=R_CORE):
    Ct, nrm = p[:3], unit_from_angles(p[3], p[4])
    u1, u2 = basis(nrm)
    phi = np.linspace(0, 2 * np.pi, 1440, endpoint=False)
    ring = Ct + R * (np.cos(phi)[:, None] * u1 + np.sin(phi)[:, None] * u2)
    out = []
    for o, d, f in sets:
        w = ring - o
        al = d @ w.T
        perp = np.sqrt(np.maximum((w ** 2).sum(1)[None] - al ** 2, 0))
        k = np.argmin(perp, axis=1)
        dist = perp[np.arange(len(k)), k]
        depth = al[np.arange(len(k)), k]
        out.append((dist - R_TUBE) * f / np.maximum(depth, 1) )
    return np.concatenate(out)

o, d = rays_cam(pb, 36, G36)
f36 = pb.cams[36]['f']
ctr = np.array([931.0, 1238.0])
o_c, d_c = rays_cam(pb, 36, ctr[None])
dist = f36 * 372 / 1590
best = None
for tilt in np.linspace(-0.6, 0.6, 7):
    for tilt2 in np.linspace(-0.6, 0.6, 7):
        n0 = -d_c[0] + tilt * np.cross(d_c[0], [0, 1, 0]) + tilt2 * np.cross(d_c[0], [1, 0, 0])
        n0 /= np.linalg.norm(n0)
        p0 = np.r_[o_c + dist * d_c[0], angles_from_unit(n0)]
        s = least_squares(tor_res, p0, args=([(o, d, f36)],), loss='soft_l1', f_scale=3.0)
        cost = np.median(np.abs(tor_res(s.x, [(o, d, f36)])))
        if best is None or cost < best[0]:
            best = (cost, s.x)
p = best[1]
print('torus from photo 36 alone: centre', np.round(p[:3], 1), 'axis', np.round(unit_from_angles(p[3], p[4]), 3), 'median px', round(best[0], 2))
# check against the key photos' grip outlines with the cameras as solved
for n, uv in GB.items():
    o2, d2 = rays_cam(pb, n, uv)
    r = tor_res(p, [(o2, d2, pb.cams[n]['f'])])
    print('  photo', n, 'grip outline residual px: median', round(np.median(r), 1), 'spread', round(np.std(r), 1))
pickle.dump(p, open('torus36.pkl', 'wb'))
EOF
timeout 900 python3 torus_fit.py
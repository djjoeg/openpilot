cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > checkproj.py <<'EOF'
"""Project the solved key-region points into the driver-side photos (36, 22, 35) through the night cluster model."""
import pickle, sys
import numpy as np, cv2
from keyfit import SOLS36, wheel_from_cam36, fr, F
from jba import rot, unit_from_angles
from lm import UP, ID, centre, OUT

out = pickle.load(open(sys.argv[1], 'rb'))
pick = float(sys.argv[2])
s, cost, pb = min(out, key=lambda r: abs(r[0] - pick))
Rw, C = wheel_from_cam36(SOLS36[1])
def cam_in_wheel(n):
    # front-frame camera n -> wheel frame: X_c = Rn X_f + tn ; X_f -> camera 36: X_36 = R36 X_f + t36 ; wheel = Rw (s X_36 - C)
    R36, t36 = rot(fr.cams[36]['rv']), fr.cams[36]['t']
    Rn, tn = rot(fr.cams[n]['rv']), fr.cams[n]['t']
    # X_w = Rw (s (R36 X_f + t36) - C)  =>  X_f = R36^T ((Rw^T X_w + C)/s - t36)
    # X_cn (front units) = Rn X_f + tn ; in mm: s * X_cn
    def proj(Xw):
        Xw = np.atleast_2d(Xw)
        Xf = (((Xw @ Rw) + C) / s - t36) @ R36          # rows: R36^T(...)
        Xc = Xf @ Rn.T + tn
        p = Xc[:, :2] / Xc[:, 2:3] * fr.cams[n]['f'] + centre(ID[n])
        return p, Xc[:, 2]
    return proj
pts = {k[1]: v for k, v in pb.pts.items() if k[0] == 'L'}
pts['bezel'] = pb.pts[('B', 'outer')]
nb = unit_from_angles(*pb.circles['outer']['ang'])
pts['keyhead'] = pts['bezel'] + 50 * nb
tiles = []
for n in (36, 22, 21):
    if n not in fr.cams: continue
    proj = cam_in_wheel(n)
    im = cv2.imread(UP + ID[n] + '-image.jpg')
    for k, X in pts.items():
        p, z = proj(X)
        if z[0] <= 0: continue
        q = tuple(int(v) for v in p[0])
        cv2.circle(im, q, 14, (255, 0, 255), 4)
        cv2.putText(im, k, (q[0] + 16, q[1]), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 0, 255), 4)
    # the grip ring and the stalk line
    phi = np.linspace(0, 2 * np.pi, 400)
    ring = np.c_[186 * np.cos(phi), 186 * np.sin(phi), np.zeros_like(phi)]
    p, z = proj(ring)
    for a, b in zip(p[:-1], p[1:]):
        cv2.line(im, tuple(int(v) for v in a), tuple(int(v) for v in b), (0, 255, 0), 3)
    if 'SH' in pts and 'ST' in pts:
        p, z = proj(np.array([pts['SH'], pts['ST']]))
        cv2.line(im, tuple(int(v) for v in p[0]), tuple(int(v) for v in p[1]), (0, 200, 255), 5)
    print(n, {k: tuple(int(v) for v in proj(X)[0][0]) for k, X in pts.items()})
    sc = 600 / im.shape[0]
    tiles.append(cv2.resize(im, None, fx=sc, fy=sc))
cv2.imwrite(OUT + 'checkproj.jpg', np.hstack(tiles))
EOF
python3 checkproj.py stage2_1.164_1.280_1.407.pkl 1.164
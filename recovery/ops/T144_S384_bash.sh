cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > check35.py <<'EOF'
import pickle, numpy as np, cv2
import picks
from keyfit import SOLS36, wheel_from_cam36, fr, F
from jba import rot
from lm import ID, centre, UP, OUT
P = picks.P
Rw, C = wheel_from_cam36(SOLS36[1])
R36, t36 = rot(fr.cams[36]['rv']), fr.cams[36]['t']
L = {k[1]: v for k, v in fr.pts.items() if k[0] == 'L'}
def resect(n):
    ks = [k for k in P[n] if k in L]
    obj = np.array([L[k] for k in ks]); img = np.array([P[n][k][:2] for k in ks], float)
    K = np.array([[F, 0, centre(ID[n])[0]], [0, F, centre(ID[n])[1]], [0, 0, 1]])
    best = None
    for flag in (cv2.SOLVEPNP_SQPNP, cv2.SOLVEPNP_EPNP, cv2.SOLVEPNP_ITERATIVE):
        ok, rv, tv = cv2.solvePnP(obj, img, K, None, flags=flag)
        rv, tv = cv2.solvePnPRefineLM(obj, img, K, None, rv, tv)
        p, _ = cv2.projectPoints(obj, rv, tv, K, None)
        e = np.linalg.norm(p.reshape(-1, 2) - img, axis=1)
        if best is None or e.mean() < best[0]:
            best = (e.mean(), rv.ravel(), tv.ravel())
    return best
e35, rv35, tv35 = resect(35)
print('photo 35 resection mean err %.1f' % e35)
R35 = rot(rv35)
def proj(n_R, n_t, Xw, s):
    Xw = np.atleast_2d(Xw)
    Xc36 = (Xw @ Rw + C) / s
    Xf = (Xc36 - t36) @ R36
    Xc = Xf @ n_R.T + n_t
    return Xc[:, :2] / Xc[:, 2:3] * F + centre(ID[35]), Xc[:, 2]
im0 = cv2.imread(UP + ID[35] + '-image.jpg')
tiles = []
phi = np.linspace(0, 2 * np.pi, 720)
for s in (0.9, 1.05, 1.164, 1.3, 1.45):
    im = im0.copy()
    for rr, col in ((186.0, (0, 255, 0)), (150.6, (0, 160, 255))):
        ring = np.c_[rr * np.cos(phi), rr * np.sin(phi), np.zeros_like(phi)]
        p, z = proj(R35, tv35, ring, s)
        for a, b, za, zb in zip(p[:-1], p[1:], z[:-1], z[1:]):
            if za > 0 and zb > 0 and np.abs(a).max() < 1e5 and np.abs(b).max() < 1e5:
                cv2.line(im, tuple(int(v) for v in a), tuple(int(v) for v in b), col, 6)
    p, z = proj(R35, tv35, np.array([[0.3, 4.2, 3.0]]), s)
    cv2.circle(im, tuple(int(v) for v in p[0]), 25, (255, 0, 255), 6)
    cv2.putText(im, 's=%.2f' % s, (40, 200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 10)
    tiles.append(cv2.resize(im, None, fx=0.2, fy=0.2))
cv2.imwrite(OUT + 'check35.jpg', np.hstack(tiles))
EOF
python3 check35.py
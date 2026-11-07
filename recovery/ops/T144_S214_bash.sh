cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > grip_guided.py <<'EOF'
import cv2, numpy as np
from lm import UP, ID, OUT
def guided(n, poly, step=40, reach=70, smooth=5, tmin=1.0):
    """Search along normals of a hand-drawn polyline for the steepest brightness step (either sign)."""
    im = cv2.imread(UP + ID[n] + '-image.jpg', cv2.IMREAD_GRAYSCALE).astype(np.float32)
    im = cv2.GaussianBlur(im, (0, 0), smooth)
    poly = np.array(poly, float)
    out = []
    for a, b in zip(poly[:-1], poly[1:]):
        L = np.linalg.norm(b - a); d = (b - a) / L; nv = np.array([-d[1], d[0]])
        for u in np.arange(0, L, step):
            p = a + u * d
            s = np.arange(-reach, reach + 1)
            q = p[None] + s[:, None] * nv[None]
            ok = (q[:, 0] > 1) & (q[:, 1] > 1) & (q[:, 0] < im.shape[1] - 2) & (q[:, 1] < im.shape[0] - 2)
            if ok.sum() < len(s) * 0.8: continue
            q = q[ok]
            v = cv2.remap(im, q[:, 0].astype(np.float32).reshape(1, -1), q[:, 1].astype(np.float32).reshape(1, -1), cv2.INTER_LINEAR).ravel()
            g = np.abs(np.gradient(v))
            k = np.argmax(g)
            if g[k] < tmin: continue
            out.append(q[k])
    return np.array(out)
def show(n, pts, poly, name, scale=0.35):
    im = cv2.imread(UP + ID[n] + '-image.jpg')
    poly = np.array(poly, int)
    cv2.polylines(im, [poly.reshape(-1, 1, 2)], False, (255, 0, 0), 4)
    for p in pts: cv2.circle(im, (int(p[0]), int(p[1])), 8, (0, 255, 255), -1)
    cv2.imwrite(OUT + name, cv2.resize(im, None, fx=scale, fy=scale))
EOF
python3 - <<'EOF'
import numpy as np
from grip_guided import guided, show
polys = {33: [(570, 30), (520, 600), (440, 1000), (380, 1400), (320, 1800), (260, 2100)],
         37: [(790, 30), (720, 500), (620, 1000), (480, 1500), (300, 1950)],
         29: [(1190, 20), (900, 300), (500, 600), (100, 850)],
         26: [(550, 30), (430, 500), (300, 1000), (180, 1400), (120, 1700)],
         24: [(450, 330), (1000, 300), (1500, 280), (2000, 200), (2500, 110)]}
G = {}
for n, poly in polys.items():
    pts = guided(n, poly)
    G[n] = pts
    print(n, len(pts))
    show(n, pts, poly, 'gg%d.jpg' % n)
np.save('gripB_guided.npy', G, allow_pickle=True)
EOF
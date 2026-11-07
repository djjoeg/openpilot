cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > silh.py <<'EOF'
"""Outer outline of the steering wheel's grip in the driver-view photos: strongest edge along normals of a rough
ellipse, then a RANSAC ellipse to keep the consistent ones."""
import cv2, numpy as np, sys
from lm import UP, ID, OUT

def normals_search(n, ell, reach=70, smooth=3.0):
    cx, cy, a, b, ang = ell
    im = cv2.imread(UP + ID[n] + '-image.jpg')
    g = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), smooth)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    t = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    ca, sa = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    out = []
    for ti in t:
        x, y = a * np.cos(ti), b * np.sin(ti)
        p = np.array([cx + x * ca - y * sa, cy + x * sa + y * ca])
        nx, ny = np.cos(ti) / a, np.sin(ti) / b
        nv = np.array([nx * ca - ny * sa, nx * sa + ny * ca]); nv /= np.linalg.norm(nv)
        s = np.arange(-reach, reach + 1, 0.5)
        q = p[None] + s[:, None] * nv[None]
        ok = (q[:, 0] > 2) & (q[:, 1] > 2) & (q[:, 0] < im.shape[1] - 3) & (q[:, 1] < im.shape[0] - 3)
        if ok.sum() < 0.9 * len(s):
            continue
        q = q[ok]
        mx = cv2.remap(gx, q[:, 0].astype(np.float32)[None], q[:, 1].astype(np.float32)[None], cv2.INTER_LINEAR).ravel()
        my = cv2.remap(gy, q[:, 0].astype(np.float32)[None], q[:, 1].astype(np.float32)[None], cv2.INTER_LINEAR).ravel()
        proj = mx * nv[0] + my * nv[1]          # brightness rising outward: dark grip inside, brighter outside
        mag = np.hypot(mx, my)
        score = np.abs(proj)
        k = np.argmax(score)
        out.append((q[k][0], q[k][1], proj[k], mag[k]))
    return np.array(out), im

def edist(E, p):
    (cx, cy), (w, h), ang = E
    a, b = w / 2, h / 2; t = np.radians(ang)
    q = p - [cx, cy]
    u = q[:, 0] * np.cos(t) + q[:, 1] * np.sin(t); v = -q[:, 0] * np.sin(t) + q[:, 1] * np.cos(t)
    return np.abs(np.sqrt((u / a) ** 2 + (v / b) ** 2) - 1) * np.sqrt(a * b)

def ransac(P, tol=5.0, iters=4000, seed=0):
    rng = np.random.default_rng(seed)
    best = (0, None)
    for _ in range(iters):
        s = P[rng.choice(len(P), 6, replace=False)].astype(np.float32)
        try:
            E = cv2.fitEllipse(s)
        except cv2.error:
            continue
        if min(E[1]) < 200: continue
        k = (edist(E, P) < tol).sum()
        if k > best[0]: best = (k, E)
    E = best[1]
    for _ in range(3):
        inl = edist(E, P) < tol
        E = cv2.fitEllipse(P[inl].astype(np.float32))
    inl = edist(E, P) < tol
    return E, inl

ELL = {0: (937, 1312, 837, 712, 0), 6: (582, 1437, 572, 662, 0), 7: (790, 1300, 725, 775, 0),
       9: (850, 1275, 650, 725, 0), 36: (931.7, 1238.1, 788, 819, 151.0)}
if __name__ == '__main__':
    res = {}
    for n, ell in ELL.items():
        P, im = normals_search(n, ell, reach=90)
        E, inl = ransac(P[:, :2], tol=5.0)
        # second pass from the fitted ellipse with a short reach
        ell2 = (E[0][0], E[0][1], E[1][0] / 2, E[1][1] / 2, E[2])
        P2, _ = normals_search(n, ell2, reach=25)
        E2, inl2 = ransac(P2[:, :2], tol=3.0)
        res[n] = dict(pts=P2[inl2, :2], ell=E2)
        print(n, 'first', inl.sum(), '/', len(P), 'second', inl2.sum(), '/', len(P2), 'ellipse', [round(v, 1) for v in (*E2[0], *E2[1], E2[2])])
        vis = im.copy()
        cv2.ellipse(vis, E2, (255, 0, 0), 4)
        for p in P2[inl2]: cv2.circle(vis, (int(p[0]), int(p[1])), 7, (0, 255, 255), -1)
        for p in P2[~inl2]: cv2.circle(vis, (int(p[0]), int(p[1])), 7, (0, 0, 255), -1)
        cv2.putText(vis, str(n), (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 10)
        res[n]['vis'] = cv2.resize(vis, None, fx=0.2, fy=0.2)
    tiles = [res[n].pop('vis') for n in ELL]
    h = max(t.shape[0] for t in tiles)
    tiles = [np.pad(t, ((0, h - t.shape[0]), (0, 0), (0, 0))) for t in tiles]
    cv2.imwrite(OUT + 'silh.jpg', np.hstack(tiles))
    np.save('silh_A.npy', res, allow_pickle=True)
EOF
python3 silh.py
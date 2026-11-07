cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > ell.py <<'EOF'
import cv2, numpy as np, sys
from lm import UP, ID, OUT
rng = np.random.default_rng(1)
def edges(n, c, r):
    im = cv2.imread(UP + ID[n] + '-image.jpg', cv2.IMREAD_GRAYSCALE)
    x0, y0 = int(c[0] - 1.6 * r), int(c[1] - 1.6 * r)
    x1, y1 = int(c[0] + 1.6 * r), int(c[1] + 1.6 * r)
    g = im[y0:y1, x0:x1]
    g = cv2.GaussianBlur(g, (5, 5), 1.5)
    e = cv2.Canny(g, 20, 60)
    ys, xs = np.nonzero(e)
    return np.column_stack([xs + x0, ys + y0]).astype(np.float64), im
def ell_dist(E, p):
    (cx, cy), (w, h), ang = E
    a, b = w / 2, h / 2
    t = np.radians(ang)
    q = p - [cx, cy]
    u = q[:, 0] * np.cos(t) + q[:, 1] * np.sin(t)
    v = -q[:, 0] * np.sin(t) + q[:, 1] * np.cos(t)
    rr = np.sqrt((u / a) ** 2 + (v / b) ** 2)
    return np.abs(rr - 1) * np.sqrt(a * b)
def fit(n, c, r, lo=0.8, hi=1.2, tol=2.0, iters=4000, aspect=(0.45, 1.0)):
    P, im = edges(n, c, r)
    d = np.linalg.norm(P - c, axis=1)
    P = P[(d > lo * r) & (d < hi * r)]
    best = (0, None)
    for _ in range(iters):
        s = P[rng.choice(len(P), 6, replace=False)]
        try:
            E = cv2.fitEllipse(s.astype(np.float32))
        except cv2.error:
            continue
        (cx, cy), (w, h), ang = E
        if not (aspect[0] < min(w, h) / max(w, h) <= aspect[1]) or not (lo * r < max(w, h) / 2 < hi * r * 1.3):
            continue
        k = (ell_dist(E, P) < tol).sum()
        if k > best[0]:
            best = (k, E)
    k, E = best
    inl = P[ell_dist(E, P) < tol]
    E = cv2.fitEllipse(inl.astype(np.float32))
    inl = P[ell_dist(E, P) < tol]
    E = cv2.fitEllipse(inl.astype(np.float32))
    return E, inl, P
if __name__ == '__main__':
    pass
EOF
cat > ell_run.py <<'EOF'
import cv2, numpy as np, pickle
from ell import fit, UP, ID, OUT
guess = {26: ((1103, 1452), 150), 33: ((1277, 1245), 150), 37: ((1256, 1127), 150), 29: ((1277, 805), 100), 24: ((1234, 1073), 130)}
res = {}
tiles = []
for n, (c, r) in guess.items():
    c = np.array(c, float)
    Eo, io, P = fit(n, c, r, 0.8, 1.25)
    Ec, ic, _ = fit(n, np.array(Eo[0]), max(Eo[1]) / 2 * 0.68, 0.8, 1.2)
    res[n] = dict(outer=Eo, outer_pts=io, chrome=Ec, chrome_pts=ic)
    im = cv2.imread(UP + ID[n] + '-image.jpg')
    x0, y0 = int(c[0] - 1.5 * r), int(c[1] - 1.5 * r)
    cv2.ellipse(im, Eo, (0, 255, 255), 2); cv2.ellipse(im, Ec, (255, 0, 255), 2)
    for p in io[::4]: cv2.circle(im, tuple(int(v) for v in p), 1, (0, 255, 0), -1)
    t = im[y0:y0 + int(3 * r), x0:x0 + int(3 * r)]
    t = cv2.resize(t, (360, 360))
    cv2.putText(t, str(n), (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    tiles.append(t)
    print(n, 'outer', [round(v, 1) for v in Eo[0]], [round(v, 1) for v in Eo[1]], round(Eo[2], 1), len(io),
          '| chrome', [round(v, 1) for v in Ec[0]], [round(v, 1) for v in Ec[1]], round(Ec[2], 1), len(ic),
          '| ratio', round(np.sqrt(Eo[1][0]*Eo[1][1]) / np.sqrt(Ec[1][0]*Ec[1][1]), 3))
cv2.imwrite(OUT + 'ellipses.jpg', np.hstack(tiles))
pickle.dump(res, open('bezel_ellipses.pkl', 'wb'))
EOF
python3 ell_run.py
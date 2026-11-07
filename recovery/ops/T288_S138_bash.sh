cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/comp && cat > match29b.py <<'EOF'
import numpy as np, cv2, pickle
import camload as CL
sift = cv2.SIFT_create(nfeatures=30000, contrastThreshold=0.02)
def feats(fid):
    im = cv2.imread(CL.UP + fid + '-image.jpg', cv2.IMREAD_GRAYSCALE)
    k, d = sift.detectAndCompute(im, None)
    return np.array([p.pt for p in k]), d
F = {n: feats(CL.FID[n]) for n in (33, 37, 26)}
F[29] = feats('e58caae5')
bf = cv2.BFMatcher(cv2.NORM_L2)
def match(a, b, ratio=0.75):
    m = bf.knnMatch(F[a][1], F[b][1], k=2)
    return {x.queryIdx: x.trainIdx for x, y in m if x.distance < ratio * y.distance}
def P(n):
    c = CL.key_camera(n)
    K = np.array([[c['f'], 0, c['c'][0]], [0, c['f'], c['c'][1]], [0, 0, 1]])
    return K @ np.c_[c['R'], c['t']], c
pts3 = {}   # (photo, kp index) -> X
for a, b in ((33, 37), (33, 26), (37, 26)):
    mab = match(a, b)
    Pa, ca = P(a); Pb, cb = P(b)
    ia = np.array(list(mab.keys())); ib = np.array([mab[i] for i in ia])
    ua, ub = F[a][0][ia], F[b][0][ib]
    Xh = cv2.triangulatePoints(Pa, Pb, ua.T, ub.T); X = (Xh[:3] / Xh[3]).T
    ea = np.linalg.norm(CL.project(ca, X)[0] - ua, axis=1); eb = np.linalg.norm(CL.project(cb, X)[0] - ub, axis=1)
    za, zb = CL.project(ca, X)[1], CL.project(cb, X)[1]
    ok = (ea < 2.5) & (eb < 2.5) & (za > 50) & (zb > 50) & (za < 1500)
    for i, j, x in zip(ia[ok], ib[ok], X[ok]):
        pts3[(a, int(i))] = x; pts3[(b, int(j))] = x
    print(a, b, 'matches', len(ia), 'good triangulations', int(ok.sum()))
corr = []
for n in (33, 37, 26):
    m = match(29, n)
    for i, j in m.items():
        if (n, j) in pts3:
            corr.append((F[29][0][i], pts3[(n, j)]))
print('2D-3D for photo 29:', len(corr))
pickle.dump(corr, open('corr29b.pkl', 'wb'))
U = np.array([c[0] for c in corr]); X = np.array([c[1] for c in corr])
c0 = np.array([966.0, 1288.0])
for f in (1700, 1800, 1900, 1950, 2000, 2100, 2200):
    K = np.array([[f, 0, c0[0]], [0, f, c0[1]], [0, 0, 1]], float)
    ok, rv, tv, inl = cv2.solvePnPRansac(X, U, K, None, reprojectionError=4.0, iterationsCount=5000, flags=cv2.SOLVEPNP_SQPNP)
    if not ok: print(f, 'fail'); continue
    inl = inl.ravel()
    p, _ = cv2.projectPoints(X[inl], rv, tv, K, None); e = np.linalg.norm(p.reshape(-1, 2) - U[inl], axis=1)
    R, _ = cv2.Rodrigues(rv)
    print('f', f, 'inliers', len(inl), '/', len(U), 'median err %.2f' % np.median(e), 'eye', np.round(-R.T @ tv.ravel(), 1))
EOF
PYTHONPATH=/home/claude/pylib timeout 1500 python3 match29b.py
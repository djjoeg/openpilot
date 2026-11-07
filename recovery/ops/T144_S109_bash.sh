cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > asift_test.py <<'EOF'
import cv2, numpy as np, time
from lm import UP, ID
def feats(n, scale=0.5, roi=None):
    im = cv2.imread(UP + ID[n] + '-image.jpg', cv2.IMREAD_GRAYSCALE)
    off = np.array([0, 0])
    if roi is not None:
        x0, y0, x1, y1 = roi
        im = im[y0:y1, x0:x1]; off = np.array([x0, y0])
    g = cv2.resize(im, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    g = cv2.createCLAHE(2.0, (8, 8)).apply(g)
    af = cv2.AffineFeature_create(cv2.SIFT_create(nfeatures=4000, contrastThreshold=0.02), maxTilt=5, minTilt=0, tiltStep=1.4142135, rotateStepBase=72)
    t = time.time()
    kp, des = af.detectAndCompute(g, None)
    pts = np.array([k.pt for k in kp], np.float32) / scale + off
    print(n, len(kp), round(time.time() - t, 1), flush=True)
    return pts, des
def match(A, B):
    pa, da = A; pb, db = B
    fl = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=64))
    m1 = fl.knnMatch(da, db, k=2)
    good = [(m.queryIdx, m.trainIdx) for m, n in m1 if m.distance < 0.8 * n.distance]
    if len(good) < 10:
        return 0, None
    g = np.array(good)
    Fm, inl = cv2.findFundamentalMat(pa[g[:, 0]], pb[g[:, 1]], cv2.USAC_MAGSAC, 3.0, 0.9999, 20000)
    return int(inl.sum()) if inl is not None else 0, (g, inl)
F = {n: feats(n) for n in (26, 33, 7, 9, 21)}
for a, b in ((26, 7), (26, 9), (33, 7), (26, 21), (21, 7), (33, 21)):
    print(a, b, match(F[a], F[b])[0], flush=True)
EOF
timeout 1200 python3 asift_test.py
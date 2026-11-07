cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/comp && cat > match29.py <<'EOF'
import numpy as np, cv2, pickle
import camload as CL
s, cost, pb = CL.SOL[2]
# track observations per photo
obs = {}
for c, k, uv, sg in pb.obs:
    if k[0] == 'T':
        obs.setdefault(c, []).append((np.asarray(uv, float), k))
P3 = {k: CL.RZ @ np.asarray(v) for k, v in pb.pts.items()}
sift = cv2.SIFT_create(nfeatures=20000)
def feats(fid):
    im = cv2.imread(CL.UP + fid + '-image.jpg', cv2.IMREAD_GRAYSCALE)
    return sift.detectAndCompute(im, None)
k29, d29 = feats('e58caae5')
corr = []
for n in (33, 26, 37, 24):
    kn, dn = feats(CL.FID[n])
    bf = cv2.BFMatcher(cv2.NORM_L2)
    m = bf.knnMatch(d29, dn, k=2)
    good = [a for a, b in m if a.distance < 0.75 * b.distance]
    T = np.array([o[0] for o in obs.get(n, [])]); TK = [o[1] for o in obs.get(n, [])]
    hits = 0
    for g in good:
        p = np.array(kn[g.trainIdx].pt)
        if len(T) == 0: break
        dd = np.linalg.norm(T - p, axis=1); j = int(np.argmin(dd))
        if dd[j] < 3.0:
            corr.append((np.array(k29[g.queryIdx].pt), P3[TK[j]], n, TK[j])); hits += 1
    print('photo', n, 'tracks', len(T), 'matches', len(good), 'linked to tracks', hits)
pickle.dump(corr, open('corr29.pkl', 'wb'))
print('total', len(corr))
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 match29.py
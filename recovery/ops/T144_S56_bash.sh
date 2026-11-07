cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > match.py <<'EOF'
import cv2, numpy as np, pickle, time, itertools, sys
from multiprocessing import Pool
D = pickle.load(open('feats.pkl', 'rb'))
ids = [i for i in D['ids'] if i not in ('fc1c6691', '779484df', '31acc20e')]
F = D['f']
def match(pair):
    a, b = pair
    fa, fb = F[a], F[b]
    flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=64))
    m1 = flann.knnMatch(fa['des'], fb['des'], k=2)
    m2 = flann.knnMatch(fb['des'], fa['des'], k=2)
    fwd = {m.queryIdx: m.trainIdx for m, n in m1 if m.distance < 0.8 * n.distance}
    bwd = {m.queryIdx: m.trainIdx for m, n in m2 if m.distance < 0.8 * n.distance}
    mm = np.array([(q, t) for q, t in fwd.items() if bwd.get(t) == q], np.int32).reshape(-1, 2)
    if len(mm) < 20:
        return a, b, mm, None, 0
    pa, pb = fa['pts'][mm[:, 0]], fb['pts'][mm[:, 1]]
    Fm, inl = cv2.findFundamentalMat(pa, pb, cv2.USAC_MAGSAC, 1.5, 0.9999, 20000)
    if Fm is None:
        return a, b, mm, None, 0
    inl = inl.ravel().astype(bool)
    return a, b, mm[inl], Fm, int(inl.sum())
if __name__ == '__main__':
    pairs = list(itertools.combinations(ids, 2))
    t0 = time.time()
    res = {}
    with Pool(2) as p:
        for k, (a, b, mm, Fm, n) in enumerate(p.imap_unordered(match, pairs, chunksize=4)):
            res[(a, b)] = (mm, Fm, n)
            if k % 50 == 0:
                print(k, len(pairs), round(time.time() - t0), flush=True)
    pickle.dump(dict(ids=ids, res=res), open('matches.pkl', 'wb'))
    print('done', round(time.time() - t0))
EOF
nohup python3 match.py > match.log 2>&1 &
echo started
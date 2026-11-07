cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > lgtest.py <<'EOF'
import cv2, numpy as np, onnxruntime as ort, time, sys
from lm import UP, ID
MODEL = '../models/lg/sp_lg.onnx'
so = ort.SessionOptions(); so.intra_op_num_threads = 2
S = ort.InferenceSession(MODEL, so, providers=['CPUExecutionProvider'])
L = 1280
def prep(i, mask=True):
    im = cv2.imread(UP + i + '-image.jpg', cv2.IMREAD_GRAYSCALE)
    s = L / max(im.shape)
    g = cv2.resize(im, (int(round(im.shape[1] * s)), int(round(im.shape[0] * s))), interpolation=cv2.INTER_AREA)
    g = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(g)
    if mask:
        import glob
        mf = glob.glob(f'masks/*_{i}.png')[0]
        m = cv2.resize(cv2.imread(mf, 0), (g.shape[1], g.shape[0]), interpolation=cv2.INTER_NEAREST)
        g[m > 0] = 0
    pad = np.zeros((L, L), np.float32)
    pad[:g.shape[0], :g.shape[1]] = g / 255.0
    return pad, s
def match(a, b):
    pa, sa = prep(a); pb, sb = prep(b)
    kp, m, sc = S.run(None, {'images': np.stack([pa, pb])[:, None]})
    m = m[sc > 0.2]
    ka = kp[0][m[:, 1]] / sa
    kb = kp[1][m[:, 2]] / sb
    if len(ka) < 12:
        return ka, kb, None
    Fm, inl = cv2.findFundamentalMat(ka.astype(np.float32), kb.astype(np.float32), cv2.USAC_MAGSAC, 3.0, 0.9999, 20000)
    return ka, kb, inl
for na, nb in [(26, 7), (33, 6), (24, 9), (37, 17), (29, 38), (26, 31), (33, 27), (24, 26), (33, 37), (21, 5), (3, 29)]:
    t = time.time()
    ka, kb, inl = match(ID[na], ID[nb])
    print(na, nb, len(ka), 'inliers', int(inl.sum()) if inl is not None else 0, round(time.time() - t, 1), flush=True)
EOF
python3 lgtest.py
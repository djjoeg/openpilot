mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > feats.py <<'EOF'
import cv2, glob, os, numpy as np, pickle, time
UP = '/root/.claude/uploads/29de5e81-e3b9-5428-a15c-fac1d206c0d4/'
refs = sorted(glob.glob('../ref/[0-9][0-9]_*.jpg'))
ids = [os.path.basename(f)[3:11] for f in refs]
sift = cv2.SIFT_create(nfeatures=12000, contrastThreshold=0.02)
out = {}
t0 = time.time()
for n, i in enumerate(ids):
    im = cv2.imread(UP + i + '-image.jpg', cv2.IMREAD_GRAYSCALE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    g = clahe.apply(im)
    kp, des = sift.detectAndCompute(g, None)
    pts = np.array([k.pt for k in kp], np.float32)
    out[i] = dict(n=n, shape=im.shape, pts=pts, des=des.astype(np.float32), size=np.array([k.size for k in kp], np.float32))
    print(n, i, im.shape, len(kp), round(time.time() - t0, 1), flush=True)
pickle.dump(dict(ids=ids, f=out), open('feats.pkl', 'wb'))
EOF
python3 feats.py 2>&1 | tail -42
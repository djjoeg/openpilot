cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > masks.py <<'EOF'
import cv2, numpy as np, pickle, os
from lm import UP, NUM
D = pickle.load(open('feats.pkl', 'rb'))
os.makedirs('masks', exist_ok=True)
stats = {}
for i in D['ids']:
    im = cv2.imread(UP + i + '-image.jpg')
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # tape: yellow (OpenCV hue 15..38 of 180), saturated, bright
    tape = ((h >= 14) & (h <= 38) & (s >= 90) & (v >= 110)).astype(np.uint8)
    tape = cv2.morphologyEx(tape, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    # keep only big yellow blobs (the tape), not small specks (dash LEDs, wood pegboard is excluded later by size?)
    n, lab, st, _ = cv2.connectedComponentsWithStats(tape)
    keep = np.zeros_like(tape)
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] > 3000:
            keep[lab == k] = 1
    keep = cv2.dilate(keep, np.ones((41, 41), np.uint8))
    cv2.imwrite(f'masks/{NUM[i]:02d}_{i}.png', keep * 255)
    stats[i] = keep.mean()
    print(NUM[i], i, round(100 * keep.mean(), 1), '% masked')
EOF
python3 masks.py
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > grip_b.py <<'EOF'
import cv2, numpy as np
from lm import UP, ID, OUT
def scan(n, axis, lines, rng, smooth=6, direction=1, min_step=25):
    """axis='x': for each row y in lines, scan x over rng; 'y': for each column x in lines, scan y over rng.
    Returns points at the steepest drop (bright grip -> darker background) in the scan direction."""
    im = cv2.imread(UP + ID[n] + '-image.jpg', cv2.IMREAD_GRAYSCALE).astype(np.float32)
    im = cv2.GaussianBlur(im, (0, 0), smooth)
    out = []
    for L in lines:
        s = np.arange(rng[0], rng[1])
        v = im[L, s] if axis == 'x' else im[s, L]
        if direction < 0:
            v = v[::-1]; s = s[::-1]
        g = np.gradient(v)
        k = np.argmin(g)                  # biggest drop going along the scan
        if -g[k] * smooth < min_step:
            continue
        p = (s[k], L) if axis == 'x' else (L, s[k])
        out.append((p[0], p[1], -g[k]))
    return np.array(out, float)
def show(n, pts, name, scale=0.35):
    im = cv2.imread(UP + ID[n] + '-image.jpg')
    for p in pts: cv2.circle(im, (int(p[0]), int(p[1])), 7, (0, 255, 255), -1)
    cv2.imwrite(OUT + name, cv2.resize(im, None, fx=scale, fy=scale))
EOF
python3 - <<'EOF'
import numpy as np
from grip_b import scan, show
g = {}
g[26] = scan(26, 'x', range(60, 1900, 60), (100, 800))
g[33] = scan(33, 'x', range(60, 2200, 60), (100, 800))
g[37] = scan(37, 'x', range(60, 1900, 60), (200, 1000))
g[24] = scan(24, 'y', range(60, 2500, 80), (100, 500))
g[29] = scan(29, 'x', range(60, 900, 50), (50, 900))
for n, p in g.items():
    print(n, len(p))
    show(n, p, 'gripB%d.jpg' % n)
np.save('gripB_raw.npy', g, allow_pickle=True)
EOF
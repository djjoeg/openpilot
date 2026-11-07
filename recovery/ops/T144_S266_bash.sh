cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > zoomgrid.py <<'EOF'
"""Several zoomed crops of one photo in one image, each with a fine pixel ruler (full-resolution coordinates)."""
import sys
import cv2, numpy as np
from lm import UP, ID, OUT

def tile(im, cx, cy, half, label, out=300, step=10):
    x0, y0 = int(cx - half), int(cy - half)
    x1, y1 = int(cx + half), int(cy + half)
    pad = np.zeros((y1 - y0, x1 - x0, 3), np.uint8)
    sx0, sy0 = max(x0, 0), max(y0, 0)
    sx1, sy1 = min(x1, im.shape[1]), min(y1, im.shape[0])
    pad[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = im[sy0:sy1, sx0:sx1]
    s = out / (2 * half)
    t = cv2.resize(pad, (out, out), interpolation=cv2.INTER_CUBIC)
    for v in range((x0 // step + 1) * step, x1, step):
        X = int((v - x0) * s); big = v % (step * 5) == 0
        cv2.line(t, (X, 0), (X, 10 if big else 4), (0, 0, 255), 1)
        cv2.line(t, (X, out - (10 if big else 4)), (X, out), (0, 0, 255), 1)
        if big: cv2.putText(t, str(v), (X + 1, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (80, 80, 255), 1)
    for v in range((y0 // step + 1) * step, y1, step):
        Y = int((v - y0) * s); big = v % (step * 5) == 0
        cv2.line(t, (0, Y), (10 if big else 4, Y), (255, 120, 0), 1)
        cv2.line(t, (out - (10 if big else 4), Y), (out, Y), (255, 120, 0), 1)
        if big: cv2.putText(t, str(v), (12, Y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 160, 60), 1)
    cv2.putText(t, label, (out - 110, out - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    return t

def grid(n, items, name, cols=3, out=300):
    im = cv2.imread(UP + ID[n] + '-image.jpg')
    tiles = [tile(im, cx, cy, half, lab, out) for lab, cx, cy, half in items]
    while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    g = np.vstack(rows)
    for i in range(1, cols): g[:, i * out - 1:i * out + 1] = 255
    for j in range(1, len(rows)): g[j * out - 1:j * out + 1, :] = 255
    cv2.imwrite(OUT + name, g)
EOF
python3 -c "
from zoomgrid import grid
grid(26, [('slot', 1095, 1435, 60), ('PUSH', 1350, 1325, 60), ('stalk hole', 1200, 930, 110),
          ('RH', 445, 1548, 60), ('stalk end', 1315, 150, 110), ('clip', 1545, 1575, 80)], 'z26.png')
"

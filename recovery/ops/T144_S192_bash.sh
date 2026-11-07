cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > grip.py <<'EOF'
"""Edge pixels of the steering wheel's grip: search along normals of a rough ellipse for the strongest brightness step."""
import cv2, numpy as np
from lm import UP, ID, OUT

def ellipse_pts(cx, cy, a, b, ang, n=360):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ca, sa = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    x = a * np.cos(t); y = b * np.sin(t)
    P = np.c_[cx + x * ca - y * sa, cy + x * sa + y * ca]
    # outward normals
    nx = np.cos(t) / a; ny = np.sin(t) / b
    N = np.c_[nx * ca - ny * sa, nx * sa + ny * ca]
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    return t, P, N

def search(n, ell, reach=40, sign=None, smooth=3, mask=None, tmin=None):
    im = cv2.imread(UP + ID[n] + '-image.jpg', cv2.IMREAD_GRAYSCALE).astype(np.float32)
    im = cv2.GaussianBlur(im, (0, 0), smooth)
    t, P, N = ellipse_pts(*ell)
    out = []
    for ti, p, nv in zip(t, P, N):
        s = np.arange(-reach, reach + 1)
        q = p[None] + s[:, None] * nv[None]
        if (q[:, 0] < 1).any() or (q[:, 1] < 1).any() or (q[:, 0] > im.shape[1] - 2).any() or (q[:, 1] > im.shape[0] - 2).any():
            continue
        v = cv2.remap(im, q[:, 0].astype(np.float32).reshape(1, -1), q[:, 1].astype(np.float32).reshape(1, -1), cv2.INTER_LINEAR).ravel()
        g = np.gradient(v)
        if sign is not None:
            g = g * sign
        k = np.argmax(np.abs(g) if sign is None else g)
        if abs(g[k]) < (tmin or 4.0):
            continue
        out.append((ti, q[k][0], q[k][1], g[k]))
    return np.array(out)

def show(n, pts, ell, name, scale=0.4):
    im = cv2.imread(UP + ID[n] + '-image.jpg')
    t, P, N = ellipse_pts(*ell)
    for p in P[::2]: cv2.circle(im, tuple(int(v) for v in p), 2, (255, 0, 0), -1)
    for r in pts: cv2.circle(im, (int(r[1]), int(r[2])), 4, (0, 255, 255), -1)
    cv2.imwrite(OUT + name, cv2.resize(im, None, fx=scale, fy=scale))
EOF
python3 - <<'EOF'
import numpy as np
from grip import *
# photo 36: outer edge of the grip: rough ellipse (cx, cy, a, b, angle)
ell = (963, 1265, 735, 828, 0)
pts = search(36, ell, reach=60, sign=None)
print(len(pts))
show(36, pts, ell, 'grip36.jpg')
np.save('grip36_outer.npy', pts)
EOF
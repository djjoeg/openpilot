cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > rim21b.py <<'EOF'
import pickle, numpy as np, cv2
from jba import basis
from lm import UP, ID, centre, OUT
F = 1917.0
sols = pickle.load(open('torus21_sols.pkl', 'rb'))
im0 = cv2.imread(UP + ID[21] + '-image.jpg')
def proj(X):
    return X[:, :2] / X[:, 2:3] * F + centre(ID[21]), X[:, 2]
tiles = []
for si in (0, 1):
    w, mL, mR, Cc, a = sols[si]
    # a points away from the camera; the driver side is towards the camera: wheel z = -a
    z = -a
    u1, u2 = basis(z)
    phi = np.linspace(0, 2 * np.pi, 720)
    im = im0.copy()
    for zr, col in ((-40, (255, 255, 0)), (-55, (0, 255, 0)), (-70, (0, 165, 255)), (-85, (0, 0, 255)), (-100, (255, 0, 255))):
        for rr in (70.0,):
            ring = Cc + zr * z + rr * (np.cos(phi)[:, None] * u1 + np.sin(phi)[:, None] * u2)
            p, d = proj(ring)
            for A, B, da, db in zip(p[:-1], p[1:], d[:-1], d[1:]):
                if da > 0 and db > 0:
                    cv2.line(im, tuple(int(v) for v in A), tuple(int(v) for v in B), col, 4)
    # the grip ring itself
    ring = Cc + 168.3 * (np.cos(phi)[:, None] * u1 + np.sin(phi)[:, None] * u2)
    p, d = proj(ring)
    for A, B in zip(p[:-1], p[1:]):
        cv2.line(im, tuple(int(v) for v in A), tuple(int(v) for v in B), (255, 255, 255), 3)
    cv2.putText(im, 'torus sol %d' % si, (40, 200), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 255), 8)
    tiles.append(cv2.resize(im[800:2200, 700:1700], None, fx=0.5, fy=0.5))
cv2.imwrite(OUT + 'rim21b.jpg', np.hstack(tiles))
EOF
python3 rim21b.py
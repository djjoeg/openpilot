cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > rim21c.py <<'EOF'
import pickle, numpy as np, cv2
from jba import basis
from lm import UP, ID, centre, OUT
F = 1917.0
sols = pickle.load(open('torus21_sols.pkl', 'rb'))
im0 = cv2.imread(UP + ID[21] + '-image.jpg')
RIM = np.array([(1092, 1097), (1035, 1242), (1011, 1403), (1003, 1532), (1011, 1677), (1044, 1806), (1092, 1903)], float)
def proj(X):
    return X[:, :2] / X[:, 2:3] * F + centre(ID[21]), X[:, 2]
tiles = []
for si in (0, 1):
    w, mL, mR, Cc, a = sols[si]
    z = -a; u1, u2 = basis(z)
    phi = np.linspace(0, 2 * np.pi, 1440)
    for rr in (80.0, 92.0):
        im = im0.copy()
        for zr, col in ((-50, (255, 255, 0)), (-65, (0, 255, 0)), (-80, (0, 165, 255)), (-95, (0, 0, 255)), (-110, (255, 0, 255))):
            ring = Cc + zr * z + rr * (np.cos(phi)[:, None] * u1 + np.sin(phi)[:, None] * u2)
            p, d = proj(ring)
            for A, B, da, db in zip(p[:-1], p[1:], d[:-1], d[1:]):
                if da > 0 and db > 0:
                    cv2.line(im, tuple(int(v) for v in A), tuple(int(v) for v in B), col, 4)
            # how far the ellipse's near half is from the picked rim points
            dd = [np.min(np.linalg.norm(p - q, axis=1)) for q in RIM]
            print('torus sol %d r %.0f z %d: rim points off by median %.0f px max %.0f' % (si, rr, zr, np.median(dd), np.max(dd)))
        for q in RIM: cv2.circle(im, (int(q[0]), int(q[1])), 10, (255, 255, 255), -1)
        cv2.putText(im, 'sol %d r %.0f' % (si, rr), (720, 900), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 255), 8)
        tiles.append(cv2.resize(im[800:2200, 700:1700], None, fx=0.4, fy=0.4))
cv2.imwrite(OUT + 'rim21c.jpg', np.hstack(tiles))
EOF
python3 rim21c.py
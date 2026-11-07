cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > draw_torus.py <<'EOF'
import pickle, numpy as np, cv2, sys
from jba import rot, unit_from_angles, basis
from lm import UP, ID, OUT
def project(pb, n, X):
    c = pb.cams[n]; R = rot(c['rv'])
    P = X @ R.T + c['t']
    return P[:, :2] / P[:, 2:3] * c['f'] + c['c'], P[:, 2]
def draw(pb, p, n, name, extra=(), R_core=168.3, r=17.7, scale=0.35, pts=None):
    im = cv2.imread(UP + ID[n] + '-image.jpg')
    Ct, nrm = p[:3], unit_from_angles(p[3], p[4]); u1, u2 = basis(nrm)
    phi = np.linspace(0, 2 * np.pi, 720)
    for rr, col in ((R_core + r, (0, 255, 0)), (R_core - r, (0, 160, 0)), (R_core, (0, 90, 255))):
        X = Ct + rr * (np.cos(phi)[:, None] * u1 + np.sin(phi)[:, None] * u2)
        q, z = project(pb, n, X)
        for a, b, za, zb in zip(q[:-1], q[1:], z[:-1], z[1:]):
            if za > 0 and zb > 0 and np.abs(a).max() < 1e5 and np.abs(b).max() < 1e5:
                cv2.line(im, tuple(int(v) for v in a), tuple(int(v) for v in b), col, 4)
    for X, lab in extra:
        q, z = project(pb, n, np.atleast_2d(X))
        if z[0] > 0:
            cv2.circle(im, tuple(int(v) for v in q[0]), 14, (255, 0, 255), 4)
            cv2.putText(im, lab, (int(q[0][0]) + 15, int(q[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 4)
    if pts is not None:
        for q in pts: cv2.circle(im, (int(q[0]), int(q[1])), 8, (0, 255, 255), -1)
    cv2.imwrite(OUT + name, cv2.resize(im, None, fx=scale, fy=scale))
EOF
python3 - <<'EOF'
import pickle, numpy as np
from draw_torus import draw
from grip_pts import G36
pb = pickle.load(open('jba2.pkl', 'rb'))
p = pickle.load(open('torus36.pkl', 'rb'))
GB = np.load('gripB_clean.npy', allow_pickle=True).item()
extra = [(p[:3], 'C'), (pb.pts[('B', 'outer')], 'key')]
draw(pb, p, 36, 't36.jpg', extra, pts=G36)
draw(pb, p, 26, 't26.jpg', extra, pts=GB[26])
draw(pb, p, 33, 't33.jpg', extra, pts=GB[33])
for n in sorted(pb.cams): print(n, np.round(pb.centre_of(n), 0))
EOF
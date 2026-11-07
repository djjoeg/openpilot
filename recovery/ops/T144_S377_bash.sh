cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > tri_front.py <<'EOF'
import numpy as np, sys
from keyfit import SOLS36, wheel_from_cam36, fr
from jba import rot
from lm import ID, centre
def cam_wheel(n, s, sel=1):
    Rw, C = wheel_from_cam36(SOLS36[sel])
    R36, t36 = rot(fr.cams[36]['rv']), fr.cams[36]['t']
    Rn, tn = rot(fr.cams[n]['rv']), fr.cams[n]['t']
    # camera centre in front frame, then wheel frame
    cf = -Rn.T @ tn
    cw = Rw @ (s * (R36 @ cf + t36) - C)
    # ray direction for a pixel: front-frame direction Rn^T x -> camera-36 frame R36 (.) -> wheel Rw (.)
    def ray(uv):
        x = np.r_[(np.asarray(uv, float) - centre(ID[n])) / fr.cams[n]['f'], 1.0]
        d = Rw @ (R36 @ (Rn.T @ x))
        return cw, d / np.linalg.norm(d)
    return ray
def tri(obs, s):
    A = np.zeros((3, 3)); b = np.zeros(3)
    rays = []
    for n, uv in obs:
        o, d = cam_wheel(n, s)(uv)
        Pm = np.eye(3) - np.outer(d, d)
        A += Pm; b += Pm @ o
        rays.append((o, d))
    X = np.linalg.solve(A, b)
    miss = [np.linalg.norm((X - o) - ((X - o) @ d) * d) for o, d in rays]
    return X, miss
for s in (1.0, 1.164, 1.28, 1.407):
    X, miss = tri([(36, (1455, 995)), (22, (2320, 590))], s)
    Y, miss2 = tri([(36, (1455, 995)), (22, (2320, 590)), (35, (1090, 360))], s)
    print('s %.3f  stalk end from 36+22: %s miss %s | +35: %s miss %s' % (s, np.round(X, 1), np.round(miss, 1), np.round(Y, 1), np.round(miss2, 1)))
EOF
python3 tri_front.py
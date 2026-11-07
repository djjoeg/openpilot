cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > badge_s.py <<'EOF'
import numpy as np
from keyfit import SOLS36, wheel_from_cam36, fr, F
from jba import rot
from lm import ID, centre
Rw, C = wheel_from_cam36(SOLS36[1])
# camera 36 in the wheel frame: X_w = Rw (X_c36 - C) -> camera centre at Rw(-C)
def ray36(uv):
    x = np.r_[(np.asarray(uv, float) - centre(ID[36])) / F, 1.0]
    return Rw @ (-C), Rw @ (x / np.linalg.norm(x))
def on_plane(uv, z0):
    o, d = ray36(uv)
    t = (z0 - o[2]) / d[2]
    return o + t * d
pts36 = {'H right bar top': (885, 1190), 'frame top-right': (938, 1180), 'frame top-left': (762, 1162), 'badge centre': (848, 1255)}
W = {k: on_plane(v, 3.0) for k, v in pts36.items()}
for k, v in W.items(): print(k, np.round(v, 1))
R36, t36 = rot(fr.cams[36]['rv']), fr.cams[36]['t']
R22, t22 = rot(fr.cams[22]['rv']), fr.cams[22]['t']
def proj22(Xw, s):
    Xc36 = (Rw.T @ Xw + C) / s           # camera-36 frame, front units
    Xf = R36.T @ (Xc36 - t36)
    Xc = R22 @ Xf + t22
    return Xc[:2] / Xc[2] * fr.cams[22]['f'] + centre(ID[22]), Xc[2]
for s in (0.9, 1.0, 1.1, 1.164, 1.25, 1.35, 1.45):
    print('s %.3f' % s, {k: tuple(int(q) for q in proj22(v, s)[0]) for k, v in W.items()})
EOF
python3 badge_s.py
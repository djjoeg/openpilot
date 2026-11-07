cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/comp && cat > fit00.py <<'EOF'
import os, sys, pickle
import numpy as np
SFM = "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm"
sys.path.insert(0, SFM); here = os.getcwd(); os.chdir(SFM)
import torus36 as T
from jba import basis
from lm import ID, centre
os.chdir(here)
from PIL import Image, ImageDraw
n = 0
out = {}
for f in (1800.0, 1917.0, 2050.0):
    sols = T.solve(n, f, T.SIL[n]['pts'], seeds=80)
    out[f] = sols[:4]
    for C, a, m in sols[:4]:
        print('f', f, 'centre', np.round(C, 1), '|%.0f|' % np.linalg.norm(C), 'axis', np.round(a, 3), 'median px %.2f' % m)
pickle.dump(out, open('torus00.pkl', 'wb'))
# draw the best two at f 1917
im = Image.open(T.__dict__.get('UP', '/root/.claude/uploads/29de5e81-e3b9-5428-a15c-fac1d206c0d4/') + ID[n] + '-image.jpg').convert('RGB')
d = ImageDraw.Draw(im)
cc = centre(ID[n])
cols = [(255, 0, 0), (0, 255, 0), (0, 128, 255), (255, 255, 0)]
for (C, a, m), col in zip(out[1917.0][:2], cols):
    u1, u2 = basis(a)
    phi = np.linspace(0, 2 * np.pi, 400)
    for r in (186.0, 150.6):
        X = C + r * (np.cos(phi)[:, None] * u1 + np.sin(phi)[:, None] * u2)
        p = X[:, :2] / X[:, 2:3] * 1917.0 + cc
        d.line([tuple(q) for q in p], fill=col, width=4)
    # a point 60 mm along the axis towards the camera (the hub face)
    for zoff in (40, 70, 100):
        X = C - zoff * a
        p = X[:2] / X[2] * 1917.0 + cc
        d.ellipse([p[0] - 10, p[1] - 10, p[0] + 10, p[1] + 10], outline=col, width=4)
for q in T.SIL[n]['pts'][::3]:
    d.ellipse([q[0] - 3, q[1] - 3, q[0] + 3, q[1] + 3], fill=(255, 0, 255))
im.thumbnail((1000, 1300)); im.save('fit00.jpg', quality=88)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 fit00.py
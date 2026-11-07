cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && sed -i 's/^F0 = 1900.0/F0 = 1880.0/' sfm.py && timeout 1200 python3 sfm.py 24,26,29,33,37 26,37 20 sfm_B3.pkl 2>&1 | tail -20 && python3 - <<'EOF'
import numpy as np, pickle
from lm import *
E = pickle.load(open('bezel_ellipses.pkl', 'rb'))
C = load('sfm_B3.pkl')['clusters'][0]
cams = [NUM[c] for c in C['cams']]
obs = [(ID[n], np.array(E[n]['outer'][0])) for n in cams]
X, e = triangulate(C, obs)
print(cams, 'bezel centre', np.round(X, 3), 'err', np.round(e, 1))
for n in cams:
    R, t, fl = cam(C, ID[n]); cc = -R.T @ t
    d = np.linalg.norm(X - cc); rad_px = np.sqrt(E[n]['outer'][1][0] * E[n]['outer'][1][1]) / 2
    print('   cam', n, 'f', round(fl), 'scale mm/unit if r=18.5:', round(18.5 / (d * rad_px / fl), 1))
EOF
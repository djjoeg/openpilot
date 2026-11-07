cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > circ_cam.py <<'EOF'
"""Each key photo's camera relative to the key bezel, from the bezel's outline alone (f fixed): both solutions."""
import pickle, numpy as np, cv2
from circpose import fit_circle
from lm import ID, centre
E = pickle.load(open('bezel_ellipses.pkl', 'rb'))
F = 1917.0
out = {}
for n in (24, 26, 33, 37):
    sols = fit_circle(E[n]['outer_pts'], F, centre(ID[n]), 18.5)
    solc = fit_circle(E[n]['chrome_pts'], F, centre(ID[n]), 12.5)
    out[n] = (sols[:2], solc[:2])
    for tag, ss in (('outer', sols[:2]), ('chrome', solc[:2])):
        for C, nn, rms in ss:
            print(n, tag, 'centre (camera frame)', np.round(C, 1), 'dist %.0f' % np.linalg.norm(C), 'normal', np.round(nn, 3), 'rms %.2f' % rms)
pickle.dump(out, open('circ_cam.pkl', 'wb'))
EOF
python3 circ_cam.py
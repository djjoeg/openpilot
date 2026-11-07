cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > rimcheck.py <<'EOF'
import pickle, sys
import numpy as np
from scipy.optimize import least_squares
import __main__
from stage2 import Stage2
__main__.Stage2 = Stage2
from jba import rot
RIM = np.load('rim_pts.npy', allow_pickle=True).item()
out = pickle.load(open('stage2_1.164_1.280_1.407.pkl', 'rb'))
for s, cost, pb in out:
    sets = []
    for n in (24, 26, 33):
        c = pb.cams[n]; R = rot(c['rv'])
        x = np.c_[(RIM[n] - c['c']) / c['f'], np.ones(len(RIM[n]))]
        d = x @ R; d /= np.linalg.norm(d, axis=1, keepdims=True)
        sets.append((-R.T @ c['t'], d, c['f']))
    def res(p):
        zr, rr = p
        out = []
        for o, d, f in sets:
            t = (zr - o[2]) / d[:, 2]
            Q = o + t[:, None] * d
            out.append((np.hypot(Q[:, 0], Q[:, 1]) - rr) * f / np.abs(t))
        return np.concatenate(out)
    best = None
    for z0 in (-40, -60, -80, -100, -120):
        for r0 in (60, 80, 100, 120):
            q = least_squares(res, [z0, r0], loss='soft_l1', f_scale=3.0)
            if best is None or q.cost < best.cost: best = q
    r = res(best.x)
    bz = pb.pts[('B', 'outer')]
    print('s %.3f: rim z %.1f radius %.1f (median px %.1f) | bezel z %.1f -> bezel behind rim %.1f mm (tape: 39-41) | bezel r %.1f' %
          (s, best.x[0], best.x[1], np.median(np.abs(r)), bz[2], best.x[0] - bz[2], np.hypot(bz[0], bz[1])))
EOF
python3 rimcheck.py
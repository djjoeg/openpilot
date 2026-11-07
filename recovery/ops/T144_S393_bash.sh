cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > stage2b.py <<'EOF'
"""Stage 2 with camera 36 added (fixed where the grip ring puts it) seeing the wiper stalk's end, for several s."""
import pickle, sys
import numpy as np, cv2
import __main__
from stage2 import Stage2, solve_for, summary
__main__.Stage2 = Stage2
from keyfit import SOLS36, wheel_from_cam36, F, GB
from jba import rot, unit_from_angles, lm_solve
from lm import ID, centre
from scipy.optimize import least_squares
RIM = np.load('rim_pts.npy', allow_pickle=True).item()
Rw, C = wheel_from_cam36(SOLS36[1])
R36w = Rw.T                      # wheel -> camera 36: X_c = Rw^T X_w + C  (since X_w = Rw (X_c - C))
t36w = C
ST36 = (1455.0, 995.0)

def run(s, init):
    import stage2
    pb, cost = solve_for(s, 1, init)
    # add camera 36, fixed, and its view of the stalk end
    pb.cams[36] = dict(rv=cv2.Rodrigues(R36w)[0].ravel(), t=t36w.copy(), f=F, fprior=(F, 1.0), c=centre(ID[36]))
    pb.fixed_cams = {36}
    pb.obs.append((36, ('L', 'ST'), np.array(ST36), 12.0))
    cost = lm_solve(pb, iters=40, verbose=False)
    return pb, cost

def rimfit(pb):
    sets = []
    for n in (24, 26, 33):
        c = pb.cams[n]; R = rot(c['rv'])
        x = np.c_[(RIM[n] - c['c']) / c['f'], np.ones(len(RIM[n]))]
        d = x @ R; d /= np.linalg.norm(d, axis=1, keepdims=True)
        sets.append((-R.T @ c['t'], d, c['f']))
    def res(p):
        zr, rr = p
        return np.concatenate([(np.hypot(*(o + ((zr - o[2]) / d[:, 2])[:, None] * d)[:, :2].T) - rr) * f / np.abs((zr - o[2]) / d[:, 2]) for o, d, f in sets])
    best = None
    for z0 in (-60, -90, -120, -150):
        for r0 in (60, 80, 100):
            q = least_squares(res, [z0, r0], loss='soft_l1', f_scale=3.0)
            if best is None or q.cost < best.cost: best = q
    return best.x, np.median(np.abs(res(best.x)))

if __name__ == '__main__':
    rows = pickle.load(open('keyfit2_1.pkl', 'rb'))
    out = []
    for s in [float(v) for v in sys.argv[1].split(',')]:
        s0, tot, per = min(rows, key=lambda r: abs(r[0] - s))
        init = {n: (p[:3], p[3:]) for n, (cost, p) in per.items()}
        pb, cost = run(s, init)
        sm = summary(pb)
        L = {k[1]: v for k, v in pb.pts.items() if k[0] == 'L'}
        bz = pb.pts[('B', 'outer')]; nb = unit_from_angles(*pb.circles['outer']['ang'])
        (zr, rr), rm = rimfit(pb)
        rep = pb.point_residuals()
        st36 = [e for c, k, e, sg in rep if c == 36]
        print('s %.3f cost %.0f | tracks %.2f cluster %.1f/%.1f grip %.1f | ST in 36 %.1f px | bezel %s n %s | rim z %.0f r %.0f (%.1f px) bezel-behind-rim %.0f | SH %s ST %s stalk %.0f mm | RH %s CUP %s' %
              (s, cost, sm['tracks'], sm['cluster_med'], sm['cluster_max'], sm['grip_med'], st36[0] if st36 else -1, np.round(bz, 0), np.round(nb, 2),
               zr, rr, rm, zr - bz[2], np.round(L['SH'], 0), np.round(L['ST'], 0), np.linalg.norm(L['ST'] - L['SH']), np.round(L['RH'], 0), np.round(L['CUP'], 0)), flush=True)
        out.append((s, cost, pb))
    pickle.dump(out, open('stage2b_%s.pkl' % sys.argv[1].replace(',', '_'), 'wb'))
EOF
timeout 3500 python3 stage2b.py 1.30,1.36,1.42,1.48 > stage2b.log 2>&1; cat stage2b.log | tail -20
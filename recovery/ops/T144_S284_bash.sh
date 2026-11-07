cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > picksF.py <<'EOF'
"""Night photos from the driver's side: instrument-cluster numerals (centres of the printed figures), full-res px."""
PF = {
    21: {'T5': (210.5, 597.9, 3), 'T6': (281, 663, 3), 'T7': (313.7, 752.6, 3), 'T8': (313.7, 854.7, 3),
         'P': (426.3, 637.9, 3), 'R': (428.4, 671.6, 3), 'N': (430.5, 703.2, 3), 'D': (431.6, 731.6, 3),
         'D3': (435.8, 760, 3), 'S0': (549.5, 802.1, 3), 'S20': (536.8, 726.3, 3), 'S40': (536.8, 642.1, 3),
         'S60': (570.5, 576.8, 3), 'S80': (626.3, 547.4, 3), 'S100': (685.3, 569.5, 3), 'S120': (752.6, 631.6, 3),
         'S140': (776.8, 703.2, 3), 'S160': (742.1, 776.8, 3), 'FF': (838.9, 689.5, 3)},
    36: {'S0': (1095, 997, 3), 'S20': (1082, 952, 3), 'S40': (1080, 895, 3), 'S60': (1110, 846, 3), 'S80': (1162, 814, 3),
         'S100': (1224, 816, 3), 'S120': (1270, 849, 3), 'S140': (1293, 901, 3), 'S160': (1291, 956, 3),
         'P': (981, 910, 3), 'R': (984, 926, 3), 'N': (989, 941, 3), 'D': (993, 959, 3), 'D3': (996, 986, 3),
         'T2': (719, 989, 3), 'T3': (746, 943, 3), 'T4': (792, 914, 3), 'T5': (847, 916, 3), 'T6': (893, 945, 3),
         'T7': (917, 990, 3), 'FF': (1397, 867, 3)},
    22: {'S0': (881, 614, 7), 'S20': (828, 548, 7), 'S40': (800, 457, 7), 'S120': (1061, 314, 7), 'S140': (1128, 376, 7),
         'S160': (1144, 459, 7), 'T7': (570, 690, 7), 'T8': (600, 790, 7)},
}
EOF
cat > front.py <<'EOF'
import pickle, numpy as np, cv2
from scipy.optimize import least_squares
from picksF import PF
from jba import Problem, lm_solve, rot
from lm import ID, centre, load, triangulate
import jinit
F0 = 1917.0
pbA, L3 = jinit.build()
names = sorted({k for p in PF.values() for k in p})
pb = Problem()
# cameras by PnP on the day-session cluster shape (scale arbitrary)
for n in (36, 21, 22):
    ks = [k for k in PF[n] if k in L3]
    obj = np.array([L3[k] for k in ks]); img = np.array([PF[n][k][:2] for k in ks], float)
    K = np.array([[F0, 0, centre(ID[n])[0]], [0, F0, centre(ID[n])[1]], [0, 0, 1]])
    ok, rv, tv = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_SQPNP)
    rv, tv = cv2.solvePnPRefineLM(obj, img, K, None, rv, tv)
    p, _ = cv2.projectPoints(obj, rv, tv, K, None)
    e = np.linalg.norm(p.reshape(-1, 2) - img, axis=1)
    print('camera', n, 'from', len(ks), 'points: errors', np.round(e, 1))
    pb.cams[n] = dict(rv=rv.ravel(), t=tv.ravel(), f=F0, fprior=(F0, 60.0), c=centre(ID[n]))
cv = {'cams': {ID[n]: (pb.cams[n]['rv'], pb.cams[n]['t'], pb.cams[n]['f']) for n in pb.cams}, 'k1': 0.0}
for k in names:
    obs = [(n, PF[n][k]) for n in PF if k in PF[n]]
    if len(obs) < 2:
        continue
    X, e = triangulate(cv, [(ID[n], o[:2]) for n, o in obs])
    pb.pts[('L', k)] = X
    for n, o in obs:
        pb.obs.append((n, ('L', k), np.array(o[:2], float), float(o[2])))
pb.fixed_cams = {36}
lm_solve(pb, iters=60, verbose=False)
rep = pb.point_residuals()
for n in (36, 21, 22):
    e = [r[2] for r in rep if r[0] == n]
    print('photo', n, 'f %.0f' % pb.cams[n]['f'], 'residuals median %.1f max %.1f' % (np.median(e), np.max(e)), 'centre', np.round(pb.centre_of(n), 2))
pickle.dump(pb, open('front.pkl', 'wb'))
EOF
timeout 900 python3 front.py 2>&1 | grep -v "^camera 2[2-9] \|^landmarks\|^camera 3[3-7] \|^camera 26"
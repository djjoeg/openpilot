"""Joint adjustment of the driver views (A) and the key photos (B), B placed from the resection against the dash."""
import pickle

import cv2
import numpy as np

import brun
import jinit
import picks
from jba import Problem, angles_from_unit, lm_solve, rot, unit_from_angles
from lm import ID, NUM, centre, load

P = picks.P


def to_A(pbB, x):
    """B frame -> A frame (A pre-scaled by jinit.SCALE_A): X_B = s R X_A + t."""
    s, R, t = np.exp(x[0]), rot(x[1:4]), x[4:7]
    out = Problem()
    for n, c in pbB.cams.items():
        Rk = rot(c['rv'])
        # x_cam = Rk X_B + tk = Rk (s R X_A + t) + tk  ->  scale camera: divide by s
        Rn = Rk @ R
        tn = (Rk @ t + c['t']) / s
        out.cams[n] = dict(rv=cv2.Rodrigues(Rn)[0].ravel(), t=tn, f=c['f'], fprior=c['fprior'], c=c['c'])
    return out, s


if __name__ == '__main__':
    pbB = pickle.load(open('bjba.pkl', 'rb'))
    x = pickle.load(open('resect.pkl', 'rb'))['x']
    pbBA, s = to_A(pbB, x)
    pb, L3 = jinit.build()
    for n in list(pb.cams):
        if n not in (36, 32, 6, 7, 9, 0, 17):
            del pb.cams[n]
    for n, c in pbBA.cams.items():
        pb.cams[n] = c
        pb.cams[n]['fprior'] = (1030.0, 60.0) if n == 29 else (2150.0, 200.0)
    # drop known-bad picks
    P[24].pop('P', None)
    P[37].pop('CUP', None)
    for n in (24, 26):
        if 'ST' in P[n]:
            P[n]['ST'] = P[n]['ST'][:2] + (15,)
    brun.add_all(pb)
    print('cameras', sorted(pb.cams), 'points', len(pb.pts), 'obs', len(pb.obs))
    lm_solve(pb, iters=40, verbose=True)
    brun.prune(pb)
    lm_solve(pb, iters=40, verbose=True)
    brun.report(pb, worst=30)
    pickle.dump(pb, open('jba2.pkl', 'wb'))

"""Builds the joint problem: the driver-view cameras from the SIFT reconstruction, the key-photo cameras placed from
the dash landmarks (PnP), hand-picked landmarks, SIFT tracks, the bezel rings."""
import pickle
import sys

import cv2
import numpy as np

import picks
from jba import Problem, angles_from_unit, rot
from lm import ID, NUM, centre, load, triangulate

SCALE_A = 80.0          # rough mm per unit of the driver-view reconstruction (refined by the known sizes)
F_MAIN = (1880.0, 80.0)
F_WIDE = (1040.0, 60.0)
WIDE = {1, 11}


def build(include_tracks=True, extra_cams=(), bezel=True, use=None):
    pb = Problem()
    SA = load('sfm_A.pkl')['clusters'][0]
    A = {NUM[c]: v for c, v in SA['cams'].items()}
    use_a = [0, 1, 6, 7, 9, 11, 17, 32, 36]
    for n in use_a:
        rv, t, f = A[n]
        pb.cams[n] = dict(rv=np.array(rv, float), t=np.array(t, float) * SCALE_A, f=float(f),
                          fprior=F_WIDE if n in WIDE else F_MAIN, c=centre(ID[n]))
    # landmarks seen by two or more of these cameras
    P = picks.P

    class Cview:   # adapter for lm.triangulate
        pass
    cv = {'cams': {ID[n]: (pb.cams[n]['rv'], pb.cams[n]['t'], pb.cams[n]['f']) for n in pb.cams}, 'k1': 0.0}
    names = sorted({k for p in P.values() for k in p})
    L3 = {}
    for k in names:
        obs = [(ID[ph], P[ph][k][:2]) for ph in P if k in P[ph] and ph in pb.cams]
        if len(obs) >= 2:
            X, e = triangulate(cv, obs)
            if e.max() < 15:
                L3[k] = X
    print('landmarks from the driver views:', sorted(L3))
    # key-photo and other cameras by PnP on known landmarks
    for n in [24, 26, 29, 33, 37, 35, 22] + list(extra_cams):
        if n not in P:
            continue
        ks = [k for k in P[n] if k in L3]
        if len(ks) < 5:
            print('camera', n, 'has only', len(ks), 'known landmarks')
            continue
        obj = np.array([L3[k] for k in ks])
        img = np.array([P[n][k][:2] for k in ks], float)
        best = None
        for f in (1700, 1880, 2050, 2250):
            K = np.array([[f, 0, centre(ID[n])[0]], [0, f, centre(ID[n])[1]], [0, 0, 1]])
            ok, rv, tv = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_SQPNP)
            if not ok:
                continue
            rv, tv = cv2.solvePnPRefineLM(obj, img, K, None, rv, tv)
            p, _ = cv2.projectPoints(obj, rv, tv, K, None)
            e = np.linalg.norm(p.reshape(-1, 2) - img, axis=1)
            if best is None or e.mean() < best[0]:
                best = (e.mean(), f, rv.ravel(), tv.ravel(), e)
        print('camera', n, 'pnp', len(ks), 'pts, f', best[1], 'mean err', round(best[0], 1), np.round(best[4], 1))
        pb.cams[n] = dict(rv=best[2], t=best[3], f=float(best[1]), fprior=F_MAIN, c=centre(ID[n]))
    return pb, L3


if __name__ == '__main__':
    build()

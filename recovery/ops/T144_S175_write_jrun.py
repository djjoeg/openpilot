import pickle
import sys

import cv2
import numpy as np

import jinit
import picks
from jba import Problem, angles_from_unit, rot
from lm import ID, NUM, centre, load, triangulate

P = picks.P
ELL = pickle.load(open('bezel_ellipses.pkl', 'rb'))
TRACKS = load('sfm_A.pkl')['tracks']
FEATS = pickle.load(open('feats.pkl', 'rb'))['f']


def cv_of(pb):
    return {'cams': {ID[n]: (pb.cams[n]['rv'], pb.cams[n]['t'], pb.cams[n]['f']) for n in pb.cams}, 'k1': pb.k1}


def add_landmarks(pb, max_err=12.0):
    cv = cv_of(pb)
    names = sorted({k for p in P.values() for k in p})
    for k in names:
        obs = [(ph, P[ph][k]) for ph in P if k in P[ph] and ph in pb.cams]
        if len(obs) < 2:
            continue
        key = ('L', k)
        if key not in pb.pts:
            X, e = triangulate(cv, [(ID[ph], o[:2]) for ph, o in obs])
            if e.max() > max_err * 3:
                print('  landmark', k, 'inconsistent at start', np.round(e, 1), [ph for ph, _ in obs])
            pb.pts[key] = X
        have = {(c, kk) for c, kk, _, _ in pb.obs}
        for ph, o in obs:
            if (ph, key) not in have:
                pb.obs.append((ph, key, np.array(o[:2], float), float(o[2])))


def add_bezel(pb, rings=('outer', 'chrome'), radii={'outer': 18.5, 'chrome': 12.5}):
    cams = [n for n in ELL if n in pb.cams]
    if len(cams) < 2:
        return
    cv = cv_of(pb)
    for ring in rings:
        key = ('B', ring)
        if key not in pb.pts:
            obs = [(ID[n], np.array(ELL[n][ring][0])) for n in cams]
            X, e = triangulate(cv, obs)
            pb.pts[key] = X
            # normal: towards the mean camera centre
            cc = np.mean([pb.centre_of(n) for n in cams], axis=0)
            nrm = (cc - X) / np.linalg.norm(cc - X)
            pb.circles[ring] = dict(centre=key, ang=angles_from_unit(nrm), r=radii[ring], r0=radii[ring], r_sigma=0.5)
        have = {(c, r) for c, r, _, _ in pb.cobs}
        for n in cams:
            if (n, ring) in have:
                continue
            pts = ELL[n][ring + '_pts']
            sel = pts[np.linspace(0, len(pts) - 1, min(80, len(pts))).astype(int)]
            pb.cobs.append((n, ring, sel.astype(float), 2.0))


def add_tracks(pb, max_err=4.0, min_views=2, sigma=1.5):
    cv = cv_of(pb)
    nums = set(pb.cams)
    n_add = 0
    for tid, t in enumerate(TRACKS):
        vs = [(NUM[i], k) for i, k in t.items() if NUM[i] in nums]
        if len(vs) < min_views:
            continue
        obs = [(ID[n], FEATS[ID[n]]['pts'][k]) for n, k in vs]
        X, e = triangulate(cv, obs)
        if e.max() > max_err:
            continue
        # depth positive in all
        ok = True
        for n, _ in vs:
            R = rot(pb.cams[n]['rv'])
            if (R @ X + pb.cams[n]['t'])[2] <= 0:
                ok = False
        if not ok:
            continue
        key = ('T', tid)
        pb.pts[key] = X
        for n, k in vs:
            pb.obs.append((n, key, FEATS[ID[n]]['pts'][k].astype(float), sigma))
        n_add += 1
    print('  tracks added', n_add)


def place_by_pnp(pb, n, min_pts=5, fs=(1600, 1880, 2200)):
    ks = [k for k in P.get(n, {}) if ('L', k) in pb.pts]
    obj = [pb.pts[('L', k)] for k in ks]
    img = [P[n][k][:2] for k in ks]
    if n in ELL:
        for ring in ('outer', 'chrome'):
            if ('B', ring) in pb.pts:
                obj.append(pb.pts[('B', ring)])
                img.append(ELL[n][ring][0])
    if len(obj) < min_pts:
        print('  camera', n, ': only', len(obj), 'known points')
        return False
    obj, img = np.array(obj, float), np.array(img, float)
    best = None
    for f in fs:
        K = np.array([[f, 0, centre(ID[n])[0]], [0, f, centre(ID[n])[1]], [0, 0, 1]])
        ok, rv, tv = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_SQPNP)
        if not ok:
            continue
        rv, tv = cv2.solvePnPRefineLM(obj, img, K, None, rv, tv)
        p, _ = cv2.projectPoints(obj, rv, tv, K, None)
        e = np.linalg.norm(p.reshape(-1, 2) - img, axis=1)
        if best is None or np.median(e) < best[0]:
            best = (np.median(e), f, rv.ravel(), tv.ravel(), e)
    print('  camera', n, 'placed from', len(obj), 'points, f', best[1], 'errors', np.round(best[4], 1))
    pb.cams[n] = dict(rv=best[2], t=best[3], f=float(best[1]), fprior=jinit.F_MAIN, c=centre(ID[n]))
    return True


def report(pb, worst=25):
    rep = pb.point_residuals()
    lm = [(c, k[1], e, s) for c, k, e, s in rep if k[0] == 'L']
    tr = [e for c, k, e, s in rep if k[0] == 'T']
    print('  landmark residuals (px): median %.1f, worst:' % np.median([e for *_, e, s in lm]))
    for c, k, e, s in sorted(lm, key=lambda r: -r[2] / r[3])[:worst]:
        print('     photo %2d %-5s %.1f (sigma %g)' % (c, k, e, s))
    if tr:
        print('  track residuals: median %.2f, 90%% %.2f, n %d' % (np.median(tr), np.percentile(tr, 90), len(tr)))
    for n, c in pb.circles.items():
        print('  circle', n, 'r %.2f' % c['r'], 'centre', np.round(pb.pts[c['centre']], 1))
    print('  focal lengths', {n: round(pb.cams[n]['f']) for n in sorted(pb.cams)})


if __name__ == '__main__':
    pb, L3 = jinit.build()
    add_landmarks(pb)
    add_bezel(pb)
    add_tracks(pb)
    print('cameras', sorted(pb.cams), 'points', len(pb.pts), 'obs', len(pb.obs))
    pb.solve(max_nfev=60, verbose=0)
    print('cost', pb._sol.cost)
    report(pb)
    for n in (24, 29, 22):
        if n not in pb.cams:
            place_by_pnp(pb, n)
    add_landmarks(pb)
    add_bezel(pb)
    add_tracks(pb)
    pb.solve(max_nfev=100)
    print('cost', pb._sol.cost)
    report(pb)
    pickle.dump(pb, open('jba1.pkl', 'wb'))

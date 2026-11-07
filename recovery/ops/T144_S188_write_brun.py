"""The key photos (24, 26, 29, 33, 37) reconstructed on their own, in millimetres: start from 24 + 26 (SIFT pair, scaled
by the bezel), add the others by PnP on everything already placed, refine with the bezel rings, landmarks, tracks."""
import pickle

import cv2
import numpy as np

import picks
from jba import Problem, angles_from_unit, lm_solve, rot
from lm import ID, NUM, centre, load, triangulate

P = picks.P
ELL = pickle.load(open('bezel_ellipses.pkl', 'rb'))
TRACKS = load('sfm_A.pkl')['tracks']
FEATS = pickle.load(open('feats.pkl', 'rb'))['f']
F_MAIN = (1880.0, 80.0)
B = (24, 26, 29, 33, 37)


def cv_of(pb):
    return {'cams': {ID[n]: (pb.cams[n]['rv'], pb.cams[n]['t'], pb.cams[n]['f']) for n in pb.cams}, 'k1': pb.k1}


def known_points(pb, n):
    """(3D, 2D) pairs for photo n from everything placed so far."""
    obj, img = [], []
    for k, o in P.get(n, {}).items():
        if ('L', k) in pb.pts:
            obj.append(pb.pts[('L', k)])
            img.append(o[:2])
    for ring in ('outer', 'chrome'):
        if ('B', ring) in pb.pts and n in ELL:
            obj.append(pb.pts[('B', ring)])
            img.append(ELL[n][ring][0])
    i = ID[n]
    for key, X in pb.pts.items():
        if key[0] == 'T' and i in TRACKS[key[1]]:
            obj.append(X)
            img.append(FEATS[i]['pts'][TRACKS[key[1]][i]])
    return np.array(obj, float), np.array(img, float)


def pnp(pb, n, fs=(1700, 1880, 2050)):
    obj, img = known_points(pb, n)
    best = None
    for f in fs:
        K = np.array([[f, 0, centre(ID[n])[0]], [0, f, centre(ID[n])[1]], [0, 0, 1]])
        ok, rv, tv, inl = cv2.solvePnPRansac(obj, img, K, None, iterationsCount=5000, reprojectionError=8.0,
                                             flags=cv2.SOLVEPNP_SQPNP)
        if not ok or inl is None:
            continue
        inl = inl.ravel()
        rv, tv = cv2.solvePnPRefineLM(obj[inl], img[inl], K, None, rv, tv)
        p, _ = cv2.projectPoints(obj, rv, tv, K, None)
        e = np.linalg.norm(p.reshape(-1, 2) - img, axis=1)
        score = (e < 8).sum()
        if best is None or score > best[0]:
            best = (score, f, rv.ravel(), tv.ravel(), e)
    print('  photo', n, ':', len(obj), 'known points,', best[0], 'within 8 px, f', best[1])
    pb.cams[n] = dict(rv=best[2], t=best[3], f=float(best[1]), fprior=F_MAIN, c=centre(ID[n]))


def add_all(pb, track_err=4.0):
    cv = cv_of(pb)
    have = {(c, k) for c, k, _, _ in pb.obs}
    # landmarks
    for k in sorted({k for p in P.values() for k in p}):
        obs = [(ph, P[ph][k]) for ph in P if k in P[ph] and ph in pb.cams]
        if len(obs) < 2:
            continue
        key = ('L', k)
        if key not in pb.pts:
            X, e = triangulate(cv, [(ID[ph], o[:2]) for ph, o in obs])
            pb.pts[key] = X
        for ph, o in obs:
            if (ph, key) not in have:
                pb.obs.append((ph, key, np.array(o[:2], float), float(o[2])))
    # bezel rings
    cams = [n for n in ELL if n in pb.cams]
    for ring, r in (('outer', 18.5), ('chrome', 12.5)):
        key = ('B', ring)
        if key not in pb.pts and len(cams) >= 2:
            X, e = triangulate(cv, [(ID[n], np.array(ELL[n][ring][0])) for n in cams])
            pb.pts[key] = X
            cc = np.mean([pb.centre_of(n) for n in cams], axis=0)
            nrm = (cc - X) / np.linalg.norm(cc - X)
            pb.circles[ring] = dict(centre=key, ang=angles_from_unit(nrm), r=r, r0=r, r_sigma=0.4)
        done = {(c, rr) for c, rr, _, _ in pb.cobs}
        for n in cams:
            if (n, ring) not in done and key in pb.pts:
                pts = ELL[n][ring + '_pts']
                sel = pts[np.linspace(0, len(pts) - 1, min(80, len(pts))).astype(int)]
                pb.cobs.append((n, ring, sel.astype(float), 2.0))
    # tracks
    nums = set(pb.cams)
    for tid, t in enumerate(TRACKS):
        vs = [(NUM[i], k) for i, k in t.items() if NUM[i] in nums]
        if len(vs) < 2:
            continue
        key = ('T', tid)
        if key not in pb.pts:
            obs = [(ID[n], FEATS[ID[n]]['pts'][k]) for n, k in vs]
            X, e = triangulate(cv, obs)
            if e.max() > track_err:
                continue
            if any((rot(pb.cams[n]['rv']) @ X + pb.cams[n]['t'])[2] <= 0 for n, _ in vs):
                continue
            pb.pts[key] = X
        for n, k in vs:
            if (n, key) not in have:
                pb.obs.append((n, key, FEATS[ID[n]]['pts'][k].astype(float), 1.5))


def prune(pb, thresh=6.0):
    rep = pb.point_residuals()
    bad = {(c, k) for c, k, e, s in rep if e / s > thresh}
    pb.obs = [o for o in pb.obs if (o[0], o[1]) not in bad]
    used = {o[1] for o in pb.obs}
    for k in list(pb.pts):
        if k[0] == 'T' and sum(1 for o in pb.obs if o[1] == k) < 2:
            pb.obs = [o for o in pb.obs if o[1] != k]
            del pb.pts[k]
    keep = {o[1] for o in pb.obs} | {c['centre'] for c in pb.circles.values()}
    for k in list(pb.pts):
        if k not in keep:
            del pb.pts[k]
    return bad


def report(pb, worst=20):
    rep = pb.point_residuals()
    lm = [(c, k[1], e, s) for c, k, e, s in rep if k[0] == 'L']
    tr = [e for c, k, e, s in rep if k[0] == 'T']
    print('  landmarks: median %.1f px; worst:' % np.median([r[2] for r in lm]))
    for c, k, e, s in sorted(lm, key=lambda r: -r[2] / r[3])[:worst]:
        print('     photo %2d %-5s %.1f (sigma %g)' % (c, k, e, s))
    if tr:
        print('  tracks: median %.2f px, 90%% %.2f, n %d' % (np.median(tr), np.percentile(tr, 90), len(tr)))
    for n, c in pb.circles.items():
        print('  ring', n, 'r %.2f' % c['r'], 'centre', np.round(pb.pts[c['centre']], 1), 'normal',
              np.round(angles_to(c['ang']), 3))
    print('  focal', {n: round(pb.cams[n]['f']) for n in sorted(pb.cams)})


def angles_to(a):
    from jba import unit_from_angles
    return unit_from_angles(*a)


if __name__ == '__main__':
    S = load('sfm_B2.pkl')['clusters'][0]
    scale = 23.5
    pb = Problem()
    for i, (rv, t, f) in S['cams'].items():
        pb.cams[NUM[i]] = dict(rv=np.array(rv, float), t=np.array(t, float) * scale, f=float(f), fprior=F_MAIN,
                               c=centre(i))
    add_all(pb)
    lm_solve(pb, iters=15, verbose=False)
    prune(pb)
    report(pb)
    for n in (37, 33, 29):
        pnp(pb, n)
        add_all(pb)
        lm_solve(pb, iters=20, verbose=False)
        bad = prune(pb)
        lm_solve(pb, iters=10, verbose=False)
        print(' after adding', n, 'pruned', len(bad))
        report(pb, worst=10)
    lm_solve(pb, iters=40, verbose=False)
    report(pb, worst=30)
    pickle.dump(pb, open('bjba.pkl', 'wb'))

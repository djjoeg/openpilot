"""Incremental structure from motion over the car photos (SIFT matches from match.py).

Camera: pinhole, principal point at the image centre, one focal length per photo (kept near the shared one), one
shared radial term k1. Output: sfm.pkl with poses, focal lengths, 3D points and their observations, per cluster.
"""
import itertools
import pickle
import sys
import time

import cv2
import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix

D = pickle.load(open('feats.pkl', 'rb'))
M = pickle.load(open('matches.pkl', 'rb'))
F = D['f']
ids = M['ids']
MIN_INL = 40
F0 = 1860.0


def shape(i):
    return F[i]['shape']           # (rows, cols)


def centre(i):
    r, c = shape(i)
    return np.array([c / 2.0, r / 2.0])


# ---------- tracks (union-find over (image, keypoint)) ----------
parent = {}


def find(x):
    while parent.get(x, x) != x:
        parent[x] = parent.get(parent[x], parent[x])
        x = parent[x]
    return x


def unite(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb


pairs = {k: v for k, v in M['res'].items() if v[2] >= MIN_INL}
for (a, b), (mm, Fm, n) in pairs.items():
    for q, t in mm:
        unite((a, int(q)), (b, int(t)))
groups = {}
for x in list(parent.keys()):
    groups.setdefault(find(x), []).append(x)
tracks = []
for g in groups.values():
    imgs = [x[0] for x in g]
    if len(set(imgs)) != len(imgs):     # inconsistent track (two keypoints in one photo): drop
        continue
    if len(g) >= 2:
        tracks.append(dict(g))           # image -> keypoint index
print('pairs', len(pairs), 'tracks', len(tracks), 'len>=3', sum(len(t) >= 3 for t in tracks), flush=True)
obs_of = {i: {} for i in ids}            # image -> {keypoint: track id}
for tid, t in enumerate(tracks):
    for i, k in t.items():
        obs_of[i][k] = tid


# ---------- camera model ----------
def project(X, rvec, tvec, f, k1, c):
    R, _ = cv2.Rodrigues(rvec)
    P = X @ R.T + tvec
    z = P[:, 2:3]
    xy = P[:, :2] / z
    r2 = (xy ** 2).sum(1, keepdims=True)
    xy = xy * (1 + k1 * r2)
    return xy * f + c, z.ravel()


def triangulate(obs, cams):
    """Linear triangulation from (image, pixel) pairs."""
    A = []
    for i, uv in obs:
        rvec, tvec, f = cams[i]
        R, _ = cv2.Rodrigues(rvec)
        P = np.hstack([R, tvec.reshape(3, 1)])
        x = (uv - centre(i)) / f
        A.append(x[0] * P[2] - P[0])
        A.append(x[1] * P[2] - P[1])
    _, _, Vt = np.linalg.svd(np.array(A))
    X = Vt[-1]
    return X[:3] / X[3]


def ray_angle(X, i, j, cams):
    ci = -cv2.Rodrigues(cams[i][0])[0].T @ cams[i][1]
    cj = -cv2.Rodrigues(cams[j][0])[0].T @ cams[j][1]
    a, b = X - ci, X - cj
    return np.degrees(np.arccos(np.clip(a @ b / np.linalg.norm(a) / np.linalg.norm(b), -1, 1)))


# ---------- bundle adjustment ----------
def bundle(cams, pts, k1, fixed_first, max_nfev=60, verbose=0):
    cam_ids = list(cams.keys())
    cidx = {c: n for n, c in enumerate(cam_ids)}
    pid = list(pts.keys())
    pidx = {p: n for n, p in enumerate(pid)}
    obs = []
    for p in pid:
        for i, k in tracks[p].items():
            if i in cams:
                obs.append((cidx[i], pidx[p], F[i]['pts'][k]))
    ci = np.array([o[0] for o in obs])
    pi = np.array([o[1] for o in obs])
    uv = np.array([o[2] for o in obs])
    cc = np.array([centre(cam_ids[c]) for c in ci])
    nC, nP = len(cam_ids), len(pid)
    x0 = np.concatenate([np.concatenate([np.hstack([cams[c][0], cams[c][1], [cams[c][2] / F0]]) for c in cam_ids]),
                         [k1], np.concatenate([pts[p] for p in pid])])
    fmean = np.mean([cams[c][2] for c in cam_ids])

    def unpack(x):
        C = x[:nC * 7].reshape(nC, 7)
        kk = x[nC * 7]
        X = x[nC * 7 + 1:].reshape(nP, 3)
        return C, kk, X

    def res(x):
        C, kk, X = unpack(x)
        out = np.empty((len(obs), 2))
        Rs = [cv2.Rodrigues(C[n, :3])[0] for n in range(nC)]
        R = np.array(Rs)[ci]
        P = np.einsum('nij,nj->ni', R, X[pi]) + C[ci, 3:6]
        xy = P[:, :2] / P[:, 2:3]
        r2 = (xy ** 2).sum(1, keepdims=True)
        xy = xy * (1 + kk * r2)
        out = xy * (C[ci, 6:7] * F0) + cc - uv
        prior = 20.0 * (C[:, 6] * F0 - fmean) / fmean     # weak pull of each focal length towards the mean
        anchor = []
        if fixed_first is not None:
            n0 = cidx[fixed_first[0]]
            anchor = np.concatenate([1e3 * (C[n0, :6] - fixed_first[1]),
                                     [1e3 * (np.linalg.norm(C[cidx[fixed_first[2]], 3:6] - 0) - fixed_first[3])]])
        return np.concatenate([out.ravel(), prior, anchor])

    m = 2 * len(obs) + nC + (7 if fixed_first is not None else 0)
    S = lil_matrix((m, len(x0)), dtype=int)
    r = np.arange(len(obs))
    for k in range(7):
        S[2 * r, ci * 7 + k] = 1
        S[2 * r + 1, ci * 7 + k] = 1
    S[2 * r, nC * 7] = 1
    S[2 * r + 1, nC * 7] = 1
    for k in range(3):
        S[2 * r, nC * 7 + 1 + pi * 3 + k] = 1
        S[2 * r + 1, nC * 7 + 1 + pi * 3 + k] = 1
    for n in range(nC):
        S[2 * len(obs) + n, :nC * 7] = 1
    if fixed_first is not None:
        base = 2 * len(obs) + nC
        n0 = cidx[fixed_first[0]]
        for k in range(6):
            S[base + k, n0 * 7 + k] = 1
        n1 = cidx[fixed_first[2]]
        S[base + 6, n1 * 7 + 3:n1 * 7 + 6] = 1
    sol = least_squares(res, x0, jac_sparsity=S, loss='huber', f_scale=2.0, x_scale='jac', max_nfev=max_nfev,
                        verbose=verbose, method='trf', tr_solver='lsmr')
    C, kk, X = unpack(sol.x)
    for n, c in enumerate(cam_ids):
        cams[c] = (C[n, :3].copy(), C[n, 3:6].copy(), C[n, 6] * F0)
    for n, p in enumerate(pid):
        pts[p] = X[n].copy()
    rr = res(sol.x)[:2 * len(obs)].reshape(-1, 2)
    e = np.linalg.norm(rr, axis=1)
    return kk, e, ci, pi, cam_ids, pid


def reconstruct(pool, log):
    """One cluster from the photos in pool."""
    # initial pair: most inliers among pairs with enough parallax (homography explains few of the matches)
    best = None
    for (a, b), (mm, Fm, n) in sorted(pairs.items(), key=lambda kv: -kv[1][2]):
        if a not in pool or b not in pool or n < 80:
            continue
        pa, pb = F[a]['pts'][mm[:, 0]], F[b]['pts'][mm[:, 1]]
        H, hin = cv2.findHomography(pa, pb, cv2.RANSAC, 4.0)
        hr = hin.sum() / len(mm) if H is not None else 1.0
        if hr < 0.75:
            best = (a, b, mm)
            break
    if best is None:
        return None
    a, b, mm = best
    pa, pb = F[a]['pts'][mm[:, 0]], F[b]['pts'][mm[:, 1]]
    # normalise with each photo's centre and the starting focal length
    na = (pa - centre(a)) / F0
    nb = (pb - centre(b)) / F0
    E, inl = cv2.findEssentialMat(na, nb, np.eye(3), cv2.RANSAC, 0.999, 1.5 / F0)
    _, R, t, inl2 = cv2.recoverPose(E, na, nb, np.eye(3), mask=inl)
    cams = {a: (np.zeros(3), np.zeros(3), F0), b: (cv2.Rodrigues(R)[0].ravel(), t.ravel(), F0)}
    pts = {}
    for (q, t_), ok in zip(mm, inl2.ravel()):
        if not ok:
            continue
        tid = obs_of[a].get(int(q))
        if tid is None or tid in pts:
            continue
        X = triangulate([(a, F[a]['pts'][q]), (b, F[b]['pts'][t_])], cams)
        if ray_angle(X, a, b, cams) > 1.0:
            pts[tid] = X
    log(f'start {a} {b} matches {len(mm)} points {len(pts)}')
    k1 = 0.0
    anchor = (a, np.zeros(6), b, 1.0)
    k1, e, *_ = bundle(cams, pts, k1, anchor)
    log(f'  ba rms {np.sqrt(np.mean(e**2)):.2f}')
    failed = set()
    while True:
        # the next photo: most matches to existing points
        cand = []
        for i in pool:
            if i in cams or i in failed:
                continue
            n = sum(1 for k, tid in obs_of[i].items() if tid in pts)
            cand.append((n, i))
        cand.sort(reverse=True)
        if not cand or cand[0][0] < 30:
            break
        n, i = cand[0]
        ks = [(k, tid) for k, tid in obs_of[i].items() if tid in pts]
        obj = np.array([pts[tid] for _, tid in ks])
        img = np.array([F[i]['pts'][k] for k, _ in ks])
        bestp = None
        for f in (F0 * 0.55, F0 * 0.8, F0, F0 * 1.2, F0 * 1.6, F0 * 2.0):
            K = np.array([[f, 0, centre(i)[0]], [0, f, centre(i)[1]], [0, 0, 1]])
            ok, rv, tv, inl = cv2.solvePnPRansac(obj, img, K, None, iterationsCount=3000, reprojectionError=6.0,
                                                 flags=cv2.SOLVEPNP_EPNP)
            if ok and inl is not None and (bestp is None or len(inl) > bestp[0]):
                bestp = (len(inl), f, rv.ravel(), tv.ravel(), inl.ravel())
        if bestp is None or bestp[0] < 25:
            failed.add(i)
            log(f'  {i}: pnp failed ({n} matches)')
            continue
        ninl, f, rv, tv, inl = bestp
        cams[i] = (rv, tv, f)
        log(f'  add {i}: {ninl}/{n} inliers f0 {f:.0f}')
        # triangulate new tracks seen by this photo and an earlier one
        new = 0
        for k, tid in obs_of[i].items():
            if tid in pts:
                continue
            others = [j for j in tracks[tid] if j in cams and j != i]
            if not others:
                continue
            ob = [(j, F[j]['pts'][tracks[tid][j]]) for j in others + [i]]
            X = triangulate(ob, cams)
            ang = max(ray_angle(X, i, j, cams) for j in others)
            if ang < 1.5:
                continue
            good = True
            for j, uv in ob:
                p, z = project(X[None], cams[j][0], cams[j][1], cams[j][2], k1, centre(j))
                if z[0] <= 0 or np.linalg.norm(p[0] - uv) > 8.0:
                    good = False
                    break
            if good:
                pts[tid] = X
                new += 1
        k1, e, ci, pi, cam_ids, pid = bundle(cams, pts, k1, anchor, max_nfev=40)
        # drop bad points
        bad = set(np.array(pid)[pi[e > 8.0]])
        for p in bad:
            pts.pop(p, None)
        log(f'    new points {new}, total {len(pts)}, rms {np.sqrt(np.mean(np.minimum(e, 8)**2)):.2f}, dropped {len(bad)}, '
            f'f {cams[i][2]:.0f} k1 {k1:.3f}')
    k1, e, ci, pi, cam_ids, pid = bundle(cams, pts, k1, anchor, max_nfev=100)
    bad = set(np.array(pid)[pi[e > 4.0]])
    for p in bad:
        pts.pop(p, None)
    k1, e, ci, pi, cam_ids, pid = bundle(cams, pts, k1, anchor, max_nfev=100)
    log(f'final: cams {len(cams)} points {len(pts)} rms {np.sqrt(np.mean(e**2)):.2f} k1 {k1:.3f}')
    return dict(cams=cams, pts=pts, k1=k1, anchor=anchor)


if __name__ == '__main__':
    logf = open('sfm.log', 'w')

    def log(s):
        print(s, flush=True)
        logf.write(s + '\n')
        logf.flush()

    pool = set(ids)
    clusters = []
    while True:
        c = reconstruct(pool, log)
        if c is None or len(c['cams']) < 2:
            break
        clusters.append(c)
        pool -= set(c['cams'].keys())
        log(f'cluster {len(clusters)}: {sorted(c["cams"].keys())}; left {len(pool)}')
    pickle.dump(dict(clusters=clusters, tracks=tracks), open('sfm.pkl', 'wb'))

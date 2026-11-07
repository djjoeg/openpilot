"""Stage 2: the four key photos solved together in the steering wheel's frame (mm), the cluster's numerals fixed where
photo 36 and scale s put them, the grip ring fixed at the origin; the key region's points (feature tracks, hand
picks, the bezel's two rings) free. Run for a few values of s; the best fit picks s."""
import pickle
import sys

import cv2
import numpy as np

import brun
import picks
from jba import Problem, angles_from_unit, lm_solve, rot, unit_from_angles
from keyfit import (F, GB, P, R_CORE, R_TUBE, SOLS36, cluster_in_wheel, wheel_from_cam36)
from lm import ID, NUM, centre, load, triangulate
from picksB import PB

PHI = np.linspace(0, 2 * np.pi, 1440, endpoint=False)
RING = np.c_[R_CORE * np.cos(PHI), R_CORE * np.sin(PHI), np.zeros_like(PHI)]


class Stage2(Problem):
    def __init__(self):
        super().__init__()
        self.fobs = []     # (cam, X fixed, uv, sigma)
        self.gobs = []     # (cam, pixels, sigma): edges of the grip ring fixed at the origin

    def residuals(self, x):
        base = super().residuals(x)
        out = [base[:self.n_robust]]
        for c, X, uv, sig in self.fobs:
            R, t, f, cc = self._cam(x, c)
            p, z = self._proj(R, t, f, cc, X[None])
            out.append(((p[0] - uv) / sig) if z[0] > 0 else np.array([50.0, 50.0]))
        for c, uv, sig in self.gobs:
            R, t, f, cc = self._cam(x, c)
            o, d = self._rays(R, t, f, cc, uv)
            w = RING - o
            al = d @ w.T
            perp = np.sqrt(np.maximum((w ** 2).sum(1)[None] - al ** 2, 0))
            k = np.argmin(perp, axis=1)
            i = np.arange(len(k))
            out.append((perp[i, k] - R_TUBE) * f / np.maximum(al[i, k], 1e-6) / sig)
        n_rob = sum(len(o) for o in out)
        res = np.concatenate(out + [base[self.n_robust:]])
        self.n_robust = n_rob
        return res

    def sparsity(self, m):
        # rows: [base robust | fixed obs | grip | base rest]
        nb = self._nb_robust
        nf = 2 * len(self.fobs)
        ng = sum(len(g[1]) for g in self.gobs)
        base_m = m - nf - ng
        Sb = super().sparsity(base_m).tolil()
        from scipy.sparse import lil_matrix
        S = lil_matrix((m, self.n_par), dtype=np.int8)
        S[:nb] = Sb[:nb]
        row = nb
        for c, X, uv, sig in self.fobs:
            for rr in (row, row + 1):
                S[rr, self.ci[c] * 7:self.ci[c] * 7 + 7] = 1
            row += 2
        for c, uv, sig in self.gobs:
            for i in range(len(uv)):
                S[row, self.ci[c] * 7:self.ci[c] * 7 + 7] = 1
                row += 1
        S[row:] = Sb[nb:]
        return S

    def _prepare(self):
        super()._prepare()
        x = self.pack()
        Problem.residuals(self, x)
        self._nb_robust = self.n_robust


def solve_for(s, sel=1, init=None, verbose=False):
    Rw, C = wheel_from_cam36(SOLS36[sel])
    LW = cluster_in_wheel(s, Rw, C)
    b3 = pickle.load(open('b3_1917.pkl', 'rb'))
    pb = Stage2()
    for n, (rv, t) in init.items():
        pb.cams[n] = dict(rv=np.array(rv, float), t=np.array(t, float), f=F, fprior=(F, 40.0), c=centre(ID[n]))
    # the key region's points from the b3 rig, moved into the wheel frame through camera 26
    R26b, t26b = rot(b3.cams[26]['rv']), b3.cams[26]['t']
    R26w, t26w = rot(pb.cams[26]['rv']), pb.cams[26]['t']
    def b2w(X):
        return R26w.T @ (R26b @ X + t26b - t26w)
    for k, X in b3.pts.items():
        pb.pts[k] = b2w(X)
    for c, k, uv, sg in b3.obs:
        if c in pb.cams:
            pb.obs.append((c, k, uv, sg))
    for name, c in b3.circles.items():
        nb = unit_from_angles(*c['ang'])
        pb.circles[name] = dict(centre=c['centre'], ang=angles_from_unit(R26w.T @ R26b @ nb), r=c['r'], r0=c['r0'],
                                r_sigma=c['r_sigma'])
    for c, ring, uv, sg in b3.cobs:
        if c in pb.cams:
            pb.cobs.append((c, ring, uv, sg))
    for n in pb.cams:
        for k, o in P[n].items():
            if k in LW:
                pb.fobs.append((n, LW[k], np.array(o[:2], float), float(o[2])))
        if n in GB:
            pb.gobs.append((n, GB[n].astype(float), 8.0))
    cost = lm_solve(pb, iters=40, verbose=verbose)
    return pb, cost


def summary(pb):
    rep = pb.point_residuals()
    tr = [e for c, k, e, s in rep if k[0] == 'T']
    lm = {(c, k[1]): e for c, k, e, s in rep if k[0] == 'L'}
    x = pb.pack()
    fo = []
    for c, X, uv, sig in pb.fobs:
        R, t, f, cc = pb._cam(x, c)
        p, z = pb._proj(R, t, f, cc, X[None])
        fo.append(np.linalg.norm(p[0] - uv))
    go = []
    for c, uv, sig in pb.gobs:
        R, t, f, cc = pb._cam(x, c)
        o, d = pb._rays(R, t, f, cc, uv)
        w = RING - o
        al = d @ w.T
        perp = np.sqrt(np.maximum((w ** 2).sum(1)[None] - al ** 2, 0))
        k = np.argmin(perp, axis=1)
        i = np.arange(len(k))
        go += list(np.abs(perp[i, k] - R_TUBE) * f / np.maximum(al[i, k], 1e-6))
    return dict(tracks=np.median(tr) if tr else 0, cluster_med=np.median(fo), cluster_max=np.max(fo), grip_med=np.median(go),
                landmarks=lm)


if __name__ == '__main__':
    sel = 1
    rows = pickle.load(open('keyfit2_1.pkl', 'rb'))
    out = []
    for s_target in [float(v) for v in sys.argv[1].split(',')]:
        s, tot, per = min(rows, key=lambda r: abs(r[0] - s_target))
        init = {n: (p[:3], p[3:]) for n, (cost, p) in per.items()}
        pb, cost = solve_for(s, sel, init)
        sm = summary(pb)
        bz = pb.pts[('B', 'outer')]
        nb = unit_from_angles(*pb.circles['outer']['ang'])
        print('s %.3f cost %.1f | tracks %.2f px, cluster med %.1f max %.1f, grip med %.1f | bezel %s normal %s' %
              (s, cost, sm['tracks'], sm['cluster_med'], sm['cluster_max'], sm['grip_med'], np.round(bz, 1), np.round(nb, 2)))
        for k in ('SH', 'ST', 'RH', 'CUP', 'PU', 'KS1', 'KS2'):
            if ('L', k) in pb.pts:
                print('     %-4s %s' % (k, np.round(pb.pts[('L', k)], 1)))
        print('     cameras', {n: np.round(pb.centre_of(n), 0) for n in pb.cams}, 'f', {n: round(pb.cams[n]['f']) for n in pb.cams})
        out.append((s, cost, pb))
    pickle.dump(out, open('stage2_%s.pkl' % sys.argv[1].replace(',', '_'), 'wb'))

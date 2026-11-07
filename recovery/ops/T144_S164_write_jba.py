"""Joint bundle adjustment: cameras (pose + focal length), 3D points (hand-picked landmarks and SIFT tracks), circles
(the key bezel's rings: edge pixels must lie on a circle of known radius) and the steering wheel's grip (a torus:
edge pixels are where view rays graze the tube). Units: millimetres once a known size is in."""
import cv2
import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix

from lm import centre as img_centre


def rot(rv):
    return cv2.Rodrigues(np.asarray(rv, float))[0]


def unit_from_angles(a, b):
    return np.array([np.cos(a) * np.cos(b), np.sin(a) * np.cos(b), np.sin(b)])


def angles_from_unit(n):
    n = n / np.linalg.norm(n)
    return np.arctan2(n[1], n[0]), np.arcsin(np.clip(n[2], -1, 1))


def basis(n):
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(n, a)
    u /= np.linalg.norm(u)
    return u, np.cross(n, u)


class Problem:
    def __init__(self):
        self.cams = {}         # name -> dict(rv, t, f, fprior=(mean, sigma), c=(cx, cy))
        self.pts = {}          # key -> X
        self.obs = []          # (cam, key, uv, sigma)
        self.circles = {}      # name -> dict(centre=key, ang=(a, b), r, r_sigma or None)
        self.cobs = []         # (cam, circle, pixels (N, 2), sigma)
        self.torus = None      # dict(c=(3), ang=(a, b), R, r)
        self.tobs = []         # (cam, pixels (N, 2), sigma)
        self.dists = []        # (key a, key b, distance, sigma)
        self.k1 = 0.0
        self.fixed_cams = set()

    # ---------- packing ----------
    def _layout(self):
        self.cam_names = list(self.cams)
        self.pt_keys = list(self.pts)
        self.circ_names = list(self.circles)
        self.ci = {c: n for n, c in enumerate(self.cam_names)}
        self.pi = {k: n for n, k in enumerate(self.pt_keys)}
        nC, nP = len(self.cam_names), len(self.pt_keys)
        self.off_cam = 0
        self.off_pt = nC * 7
        self.off_circ = self.off_pt + nP * 3
        self.off_tor = self.off_circ + len(self.circ_names) * 3       # angles a, b and radius
        self.n_par = self.off_tor + (6 if self.torus else 0)

    def pack(self):
        self._layout()
        x = np.zeros(self.n_par)
        for c in self.cam_names:
            d = self.cams[c]
            x[self.ci[c] * 7:self.ci[c] * 7 + 7] = np.r_[d['rv'], d['t'], d['f'] / 1000.0]
        for k in self.pt_keys:
            x[self.off_pt + self.pi[k] * 3:self.off_pt + self.pi[k] * 3 + 3] = self.pts[k]
        for n, c in enumerate(self.circ_names):
            d = self.circles[c]
            x[self.off_circ + 3 * n:self.off_circ + 3 * n + 3] = [d['ang'][0], d['ang'][1], d['r']]
        if self.torus:
            t = self.torus
            x[self.off_tor:self.off_tor + 6] = np.r_[t['c'], t['ang'][0], t['ang'][1], t['R']]
        return x

    def unpack(self, x):
        for c in self.cam_names:
            v = x[self.ci[c] * 7:self.ci[c] * 7 + 7]
            self.cams[c].update(rv=v[:3].copy(), t=v[3:6].copy(), f=v[6] * 1000.0)
        for k in self.pt_keys:
            self.pts[k] = x[self.off_pt + self.pi[k] * 3:self.off_pt + self.pi[k] * 3 + 3].copy()
        for n, c in enumerate(self.circ_names):
            v = x[self.off_circ + 3 * n:self.off_circ + 3 * n + 3]
            self.circles[c].update(ang=(v[0], v[1]), r=v[2])
        if self.torus:
            v = x[self.off_tor:self.off_tor + 6]
            self.torus.update(c=v[:3].copy(), ang=(v[3], v[4]), R=v[5])

    # ---------- residuals ----------
    def _cam(self, x, c):
        v = x[self.ci[c] * 7:self.ci[c] * 7 + 7]
        return rot(v[:3]), v[3:6], v[6] * 1000.0, self.cams[c]['c']

    def _proj(self, R, t, f, cc, X):
        P = X @ R.T + t
        xy = P[:, :2] / P[:, 2:3]
        r2 = (xy ** 2).sum(1, keepdims=True)
        return xy * (1 + self.k1 * r2) * f + cc, P[:, 2]

    def _rays(self, R, t, f, cc, uv):
        xd = (uv - cc) / f
        xu = xd.copy()
        for _ in range(5):
            xu = xd / (1 + self.k1 * (xu ** 2).sum(1, keepdims=True))
        d = np.c_[xu, np.ones(len(xu))] @ R          # rows: R^T [x, y, 1]
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        o = -R.T @ t
        return o, d

    def residuals(self, x):
        out = []
        # points
        if self.obs:
            for c, idx in self._obs_by_cam.items():
                R, t, f, cc = self._cam(x, c)
                keys = self._obs_keys[c]
                X = np.array([x[self.off_pt + self.pi[k] * 3:self.off_pt + self.pi[k] * 3 + 3] for k in keys])
                p, z = self._proj(R, t, f, cc, X)
                r = (p - self._obs_uv[c]) / self._obs_sig[c][:, None]
                r[z <= 0] = 50.0
                out.append(r.ravel())
        # circles
        for c, circ, uv, sig in self.cobs:
            R, t, f, cc = self._cam(x, c)
            n = self.circ_names.index(circ)
            a, b, rad = x[self.off_circ + 3 * n:self.off_circ + 3 * n + 3]
            nrm = unit_from_angles(a, b)
            k = self.circles[circ]['centre']
            C = x[self.off_pt + self.pi[k] * 3:self.off_pt + self.pi[k] * 3 + 3]
            o, d = self._rays(R, t, f, cc, uv)
            s = (nrm @ (C - o)) / (d @ nrm)
            Q = o + s[:, None] * d
            depth = (Q @ R.T + t)[:, 2]
            r = (np.linalg.norm(Q - C, axis=1) - rad) * f / np.maximum(depth, 1e-6) / sig
            out.append(r)
        # torus
        if self.torus:
            v = x[self.off_tor:self.off_tor + 6]
            Ct, nrm, Rc = v[:3], unit_from_angles(v[3], v[4]), v[5]
            u1, u2 = basis(nrm)
            phi = np.linspace(0, 2 * np.pi, 720, endpoint=False)
            ring = Ct + Rc * (np.cos(phi)[:, None] * u1 + np.sin(phi)[:, None] * u2)
            for c, uv, sig in self.tobs:
                R, t, f, cc = self._cam(x, c)
                o, d = self._rays(R, t, f, cc, uv)
                w = ring - o                                     # (720, 3)
                along = d @ w.T                                  # (N, 720)
                perp2 = (w ** 2).sum(1)[None, :] - along ** 2
                k = np.argmin(perp2, axis=1)
                # refine: parabola through the neighbours
                km, kp = (k - 1) % 720, (k + 1) % 720
                y0, ym, yp = perp2[np.arange(len(k)), k], perp2[np.arange(len(k)), km], perp2[np.arange(len(k)), kp]
                den = ym - 2 * y0 + yp
                dk = np.where(np.abs(den) > 1e-12, 0.5 * (ym - yp) / den, 0.0)
                ph = phi[k] + np.clip(dk, -1, 1) * (2 * np.pi / 720)
                P = Ct + Rc * (np.cos(ph)[:, None] * u1 + np.sin(ph)[:, None] * u2)
                w = P - o
                al = (w * d).sum(1)
                dist = np.sqrt(np.maximum((w ** 2).sum(1) - al ** 2, 0))
                depth = np.maximum(al, 1e-6)
                out.append((dist - self.torus['r']) * f / depth / sig)
        # distances
        for a, b, L, sig in self.dists:
            A = x[self.off_pt + self.pi[a] * 3:self.off_pt + self.pi[a] * 3 + 3]
            B = x[self.off_pt + self.pi[b] * 3:self.off_pt + self.pi[b] * 3 + 3]
            out.append(np.array([(np.linalg.norm(A - B) - L) / sig]))
        # circle radius priors
        for n, c in enumerate(self.circ_names):
            d = self.circles[c]
            if d.get('r_sigma'):
                out.append(np.array([(x[self.off_circ + 3 * n + 2] - d['r0']) / d['r_sigma']]))
        # focal priors, fixed cameras
        for c in self.cam_names:
            m, s = self.cams[c]['fprior']
            out.append(np.array([(x[self.ci[c] * 7 + 6] * 1000.0 - m) / s]))
            if c in self.fixed_cams:
                v0 = self._fixed0[c]
                out.append(1e4 * (x[self.ci[c] * 7:self.ci[c] * 7 + 6] - v0))
        if self.torus and self.torus.get('R_sigma'):
            out.append(np.array([(x[self.off_tor + 5] - self.torus['R0']) / self.torus['R_sigma']]))
        return np.concatenate(out)

    def _prepare(self):
        self._obs_by_cam, self._obs_keys, self._obs_uv, self._obs_sig = {}, {}, {}, {}
        for c, k, uv, s in self.obs:
            self._obs_by_cam.setdefault(c, []).append(len(self._obs_keys.setdefault(c, [])))
            self._obs_keys[c].append(k)
        for c in self._obs_keys:
            rows = [(uv, s) for cc, k, uv, s in self.obs if cc == c]
            self._obs_uv[c] = np.array([r[0] for r in rows], float)
            self._obs_sig[c] = np.array([r[1] for r in rows], float)
        self._fixed0 = {c: np.r_[self.cams[c]['rv'], self.cams[c]['t']] for c in self.fixed_cams}

    def sparsity(self, m):
        S = lil_matrix((m, self.n_par), dtype=np.int8)
        row = 0

        def camcols(c):
            return range(self.ci[c] * 7, self.ci[c] * 7 + 7)

        for c in self._obs_by_cam:
            for k in self._obs_keys[c]:
                for rr in (row, row + 1):
                    for j in camcols(c):
                        S[rr, j] = 1
                    for j in range(3):
                        S[rr, self.off_pt + self.pi[k] * 3 + j] = 1
                row += 2
        for c, circ, uv, sig in self.cobs:
            n = self.circ_names.index(circ)
            k = self.circles[circ]['centre']
            for i in range(len(uv)):
                for j in camcols(c):
                    S[row, j] = 1
                for j in range(3):
                    S[row, self.off_circ + 3 * n + j] = 1
                    S[row, self.off_pt + self.pi[k] * 3 + j] = 1
                row += 1
        if self.torus:
            for c, uv, sig in self.tobs:
                for i in range(len(uv)):
                    for j in camcols(c):
                        S[row, j] = 1
                    for j in range(6):
                        S[row, self.off_tor + j] = 1
                    row += 1
        for a, b, L, sig in self.dists:
            for j in range(3):
                S[row, self.off_pt + self.pi[a] * 3 + j] = 1
                S[row, self.off_pt + self.pi[b] * 3 + j] = 1
            row += 1
        for n, c in enumerate(self.circ_names):
            if self.circles[c].get('r_sigma'):
                S[row, self.off_circ + 3 * n + 2] = 1
                row += 1
        for c in self.cam_names:
            S[row, self.ci[c] * 7 + 6] = 1
            row += 1
            if c in self.fixed_cams:
                for j in range(6):
                    S[row, self.ci[c] * 7 + j] = 1
                    row += 1
        if self.torus and self.torus.get('R_sigma'):
            S[row, self.off_tor + 5] = 1
            row += 1
        assert row == m, (row, m)
        return S

    def solve(self, max_nfev=200, loss='huber', f_scale=1.5, verbose=0):
        self._prepare()
        x0 = self.pack()
        r0 = self.residuals(x0)
        S = self.sparsity(len(r0))
        sol = least_squares(self.residuals, x0, jac_sparsity=S, loss=loss, f_scale=f_scale, x_scale='jac',
                            max_nfev=max_nfev, verbose=verbose, method='trf', tr_solver='lsmr')
        self.unpack(sol.x)
        self._sol = sol
        return sol

    # ---------- reports ----------
    def point_residuals(self):
        x = self.pack()
        rep = []
        for c, k, uv, s in self.obs:
            R, t, f, cc = self._cam(x, c)
            p, z = self._proj(R, t, f, cc, self.pts[k][None])
            rep.append((c, k, float(np.linalg.norm(p[0] - uv)), s))
        return rep

    def centre_of(self, c):
        d = self.cams[c]
        return -rot(d['rv']).T @ d['t']

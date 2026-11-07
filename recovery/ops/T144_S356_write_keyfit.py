"""The key photos placed in the steering wheel's own frame, through the instrument cluster and the wheel's grip.

Wheel frame (mm): origin at the middle of the grip ring, z along the column towards the driver, y up (12 o'clock),
x to the driver's right. Photo 36 (straight on, the whole grip ring sharp) gives where camera 36 is relative to the
grip ring (a ring 372 mm across, 35.4 mm thick: two mirror solutions, both tried); the badge sets which way is up.
The cluster's numerals come from the night cluster model (photos 36, 21, 22; its own units) and scale s converts them
to mm. Each key photo (24, 26, 33, 37) then gets its camera from the cluster numerals it sees and the part of the
grip ring it sees (blurred, close up), with s shared. Last, the key's bezel (37 mm across) from each photo's view.
"""
import pickle
import sys

import cv2
import numpy as np
from scipy.optimize import least_squares

import picks
from circpose import fit_circle
from jba import basis, rot, unit_from_angles
from lm import ID, centre

F = 1917.0
R_CORE, R_TUBE = 186.0 - 17.7, 17.7
P = picks.P
fr = pickle.load(open('front.pkl', 'rb'))
LF = {k[1]: v for k, v in fr.pts.items() if k[0] == 'L'}
SOLS36 = pickle.load(open('torus36_sols.pkl', 'rb'))
GB = np.load('gripB_clean.npy', allow_pickle=True).item()
GB[33] = GB[33][(GB[33][:, 1] < 560) | (GB[33][:, 1] > 1240)]
ELL = pickle.load(open('bezel_ellipses.pkl', 'rb'))
PHI = np.linspace(0, 2 * np.pi, 1440, endpoint=False)
RING = np.c_[R_CORE * np.cos(PHI), R_CORE * np.sin(PHI), np.zeros_like(PHI)]


def wheel_from_cam36(sol):
    C, a, _ = sol
    z = -a / np.linalg.norm(a)                    # towards the driver (camera 36)
    up = np.array([0.0, -1.0, 0.0])               # camera 36's up
    y = up - (up @ z) * z
    y /= np.linalg.norm(y)
    x = np.cross(y, z)
    Rw = np.vstack([x, y, z])                     # rows: wheel axes in camera-36 coordinates
    return Rw, C


def cluster_in_wheel(s, Rw, C):
    R36, t36 = rot(fr.cams[36]['rv']), fr.cams[36]['t']
    return {k: Rw @ (s * (R36 @ v + t36) - C) for k, v in LF.items()}


def project(rv, t, X):
    R = rot(rv)
    Pc = np.atleast_2d(X) @ R.T + t
    return Pc[:, :2] / Pc[:, 2:3] * F, Pc[:, 2]


def torus_res(rv, t, uv, n):
    R = rot(rv)
    o = -R.T @ t
    x = np.c_[(uv - centre(ID[n])) / F, np.ones(len(uv))]
    d = x @ R
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    w = RING - o
    al = d @ w.T
    perp = np.sqrt(np.maximum((w ** 2).sum(1)[None] - al ** 2, 0))
    k = np.argmin(perp, axis=1)
    i = np.arange(len(k))
    return (perp[i, k] - R_TUBE) * F / np.maximum(al[i, k], 1e-6)


def residuals(x, Rw, C, cams, w_grip=1.0 / 8.0):
    s = np.exp(x[0])
    LW = cluster_in_wheel(s, Rw, C)
    out = []
    for j, n in enumerate(cams):
        rv, t = x[1 + 6 * j:4 + 6 * j], x[4 + 6 * j:7 + 6 * j]
        ks = [k for k in P[n] if k in LW]
        X = np.array([LW[k] for k in ks])
        uv = np.array([P[n][k][:2] for k in ks], float) - centre(ID[n])
        sig = np.array([P[n][k][2] for k in ks], float)
        p, z = project(rv, t, X)
        r = (p - uv) / sig[:, None]
        r[z <= 0] = 100.0
        out.append(r.ravel())
        if n in GB:
            out.append(torus_res(rv, t, GB[n], n) * w_grip)
    return np.concatenate(out)


def look_at(cam, target, up=np.array([0.0, 1.0, 0.0])):
    f = target - cam
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    d = np.cross(f, r)                    # image down
    R = np.vstack([r, d, f])
    return cv2.Rodrigues(R)[0].ravel(), -R @ cam


def bezel_in_wheel(rv, t, n):
    sols = fit_circle(ELL[n]['outer_pts'], F, centre(ID[n]), 18.5)
    C, nrm, _ = sols[0]
    R = rot(rv)
    return R.T @ (C - t), [R.T @ s[1] for s in sols[:2]]


if __name__ == '__main__':
    cams = [24, 26, 33, 37]
    rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
    results = []
    for si, sol in enumerate(SOLS36[:2]):
        Rw, C = wheel_from_cam36(sol)
        best = None
        for trial in range(40):
            s0 = np.exp(rng.uniform(np.log(0.5), np.log(2.0)))
            x0 = [np.log(s0)]
            for n in cams:
                cam = np.array([rng.uniform(180, 330), rng.uniform(-160, 40), rng.uniform(-130, 20)])
                tgt = np.array([75.0, -10.0, -100.0]) + rng.normal(size=3) * 20
                up = np.array([0.0, 1.0, 0.0]) if n != 24 else np.array([0.0, 0.0, -1.0])
                up = up + rng.normal(size=3) * 0.3
                rv, t = look_at(cam, tgt, up)
                x0 += list(rv) + list(t)
            x0 = np.array(x0)
            try:
                r = least_squares(residuals, x0, args=(Rw, C, cams), loss='soft_l1', f_scale=1.5, max_nfev=600)
            except Exception as e:
                continue
            res = residuals(r.x, Rw, C, cams)
            m = np.median(np.abs(res))
            if best is None or r.cost < best[0]:
                best = (r.cost, r.x, m)
        cost, x, m = best
        s = np.exp(x[0])
        print('photo-36 solution %d: cost %.1f median |res| %.2f, s %.3f mm per cluster unit' % (si, cost, m, s))
        LW = cluster_in_wheel(s, Rw, C)
        for j, n in enumerate(cams):
            rv, t = x[1 + 6 * j:4 + 6 * j], x[4 + 6 * j:7 + 6 * j]
            ks = [k for k in P[n] if k in LW]
            p, _ = project(rv, t, np.array([LW[k] for k in ks]))
            e = np.linalg.norm(p - (np.array([P[n][k][:2] for k in ks]) - centre(ID[n])), axis=1)
            g = torus_res(rv, t, GB[n], n)
            b, nrms = bezel_in_wheel(rv, t, n)
            camc = -rot(rv).T @ t
            print('   photo %d: cluster px median %.1f max %.1f | grip px median %.1f | camera %s | bezel %s | normals %s'
                  % (n, np.median(e), e.max(), np.median(np.abs(g)), np.round(camc, 0), np.round(b, 1),
                     [np.round(q, 2) for q in nrms]))
        results.append((si, cost, x))
    pickle.dump(results, open('keyfit.pkl', 'wb'))

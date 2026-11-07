"""Helpers for picking landmarks in the photos and placing them with the solved cameras."""
import pickle

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.optimize import least_squares

UP = '/root/.claude/uploads/29de5e81-e3b9-5428-a15c-fac1d206c0d4/'
OUT = '/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm/look/'
NUM = {}
import glob, os
for f in sorted(glob.glob('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/ref/[0-9][0-9]_*.jpg')):
    b = os.path.basename(f)
    NUM[b[3:11]] = int(b[:2])
ID = {v: k for k, v in NUM.items()}
os.makedirs(OUT, exist_ok=True)


def load(path='sfm.pkl'):
    return pickle.load(open(path, 'rb'))


def size(i):
    return Image.open(UP + i + '-image.jpg').size      # (w, h)


def centre(i):
    w, h = size(i)
    return np.array([w / 2.0, h / 2.0])


def cam(C, i):
    rvec, tvec, f = C['cams'][i]
    R, _ = cv2.Rodrigues(np.asarray(rvec, float))
    return R, np.asarray(tvec, float), f


def project(C, i, X):
    R, t, f = cam(C, i)
    X = np.atleast_2d(X)
    P = X @ R.T + t
    xy = P[:, :2] / P[:, 2:3]
    r2 = (xy ** 2).sum(1, keepdims=True)
    xy = xy * (1 + C['k1'] * r2)
    return xy * f + centre(i), P[:, 2]


def undistort_norm(C, i, uv):
    """Pixel -> normalised camera ray (x, y, 1), undoing k1 by iteration."""
    R, t, f = cam(C, i)
    xd = (np.asarray(uv, float) - centre(i)) / f
    x = xd.copy()
    for _ in range(10):
        r2 = (x ** 2).sum()
        x = xd / (1 + C['k1'] * r2)
    return np.array([x[0], x[1], 1.0])


def ray(C, i, uv):
    R, t, f = cam(C, i)
    d = R.T @ undistort_norm(C, i, uv)
    o = -R.T @ t
    return o, d / np.linalg.norm(d)


def triangulate(C, obs):
    """obs: list of (image, (u, v)). Least-squares point, then reprojection refinement. Returns X, per-view errors."""
    A, b = np.zeros((3, 3)), np.zeros(3)
    for i, uv in obs:
        o, d = ray(C, i, uv)
        P = np.eye(3) - np.outer(d, d)
        A += P
        b += P @ o
    X = np.linalg.solve(A, b)

    def res(X):
        return np.concatenate([project(C, i, X)[0][0] - np.asarray(uv, float) for i, uv in obs])

    s = least_squares(res, X)
    e = res(s.x).reshape(-1, 2)
    return s.x, np.linalg.norm(e, axis=1)


def crop(i, box, name, marks=(), step=None, scale=1.0, lines=()):
    """Crop (x0, y0, x1, y1) of photo i with a pixel ruler; marks: (u, v, label, colour)."""
    im = Image.open(UP + i + '-image.jpg').convert('RGB')
    x0, y0, x1, y1 = [int(v) for v in box]
    im = im.crop((x0, y0, x1, y1))
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    w = x1 - x0
    step = step or (10 if w <= 300 else 20 if w <= 600 else 50 if w <= 1200 else 100)
    font = ImageFont.load_default(size=max(10, int(12 * scale ** 0.5)))
    for x in range((x0 // step + 1) * step, x1, step):
        X = (x - x0) * scale
        big = x % (step * 5) == 0
        d.line([(X, 0), (X, 14 if big else 6)], fill=(255, 0, 0), width=1)
        d.line([(X, im.height - (14 if big else 6)), (X, im.height)], fill=(255, 0, 0), width=1)
        if big:
            d.text((X + 2, 14), str(x), fill=(255, 40, 40), font=font)
    for y in range((y0 // step + 1) * step, y1, step):
        Y = (y - y0) * scale
        big = y % (step * 5) == 0
        d.line([(0, Y), (14 if big else 6, Y)], fill=(0, 90, 255), width=1)
        d.line([(im.width - (14 if big else 6), Y), (im.width, Y)], fill=(0, 90, 255), width=1)
        if big:
            d.text((16, Y + 1), str(y), fill=(60, 140, 255), font=font)
    for (a, b, col) in lines:
        d.line([((a[0] - x0) * scale, (a[1] - y0) * scale), ((b[0] - x0) * scale, (b[1] - y0) * scale)], fill=col, width=2)
    for m in marks:
        u, v, lab = m[:3]
        col = m[3] if len(m) > 3 else (255, 255, 0)
        X, Y = (u - x0) * scale, (v - y0) * scale
        d.ellipse([X - 5, Y - 5, X + 5, Y + 5], outline=col, width=2)
        d.line([(X - 9, Y), (X - 3, Y)], fill=col)
        d.line([(X + 3, Y), (X + 9, Y)], fill=col)
        d.text((X + 7, Y - 16), lab, fill=col, font=font)
    im.save(OUT + name)
    return OUT + name


def epiline(C, i, uv, j, depths=np.linspace(50, 3000, 300)):
    """The ray through (u, v) in photo i, seen in photo j, as a polyline of pixels."""
    o, d = ray(C, i, uv)
    pts = o + depths[:, None] * d
    p, z = project(C, j, pts)
    return p[z > 0]

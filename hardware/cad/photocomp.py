"""
Your own photos with the new parts drawn in (2 Nov 2026): the machinery.

Each photo comes with its camera (where the phone was, which way it pointed, its zoom), solved from the photo itself
(incar.py says how). The parts are drawn with that camera into a window of the photo, then laid over it:

  - lit as the photo was lit (the phone's flash for the night photos, the cabin's daylight for the day one), the
    brightness matched to a light grey patch of the same photo (incar.py says which);
  - hidden where the car (a rough model: the grip, the column covers, the key) is nearer the camera than the part;
  - a soft darkening where a part sits close to something (ambient occlusion), on the part and on the car round it;
  - blurred as the phone's lens blurs things at that distance, and given the photo's grain.

  layers(cam, parts, occluders, box, ...) -> the drawn window;  composite(photo, layers, ...) -> the finished photo
"""
import math

import cv2
import numpy as np

import photorender as PR


def srgb_to_lin(x):
  x = np.asarray(x, np.float64)
  return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(x):
  x = np.clip(np.asarray(x, np.float64), 0.0, None)
  return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)


class PhotoCam:
  """A pinhole camera in the OpenCV way: pixel = f * (R X + t)[:2] / (R X + t)[2] + c, x right, y down, pixel centres
  on whole numbers. X in the steering wheel frame (mm)."""

  def __init__(self, R, t, f, c, size, raster_shift=0.0):
    self.R = np.asarray(R, float)
    self.t = np.asarray(t, float)
    self.f = float(f)
    self.c = np.asarray(c, float)
    self.W, self.H = int(size[0]), int(size[1])
    self.shift = raster_shift

  @property
  def eye(self):
    return -self.R.T @ self.t

  def sub(self, x0, y0, w, h, ss):
    """The camera of a window of the photo (x0, y0, w, h), ss samples per pixel each way, in the rasteriser's units
    (sample centres at whole numbers + 0.5)."""
    return PhotoCam(self.R, self.t, self.f * ss, (self.c - np.array([x0, y0], float) + 0.5) * ss, (w * ss, h * ss))

  def view(self, P):
    return np.asarray(P, float) @ self.R.T + self.t

  def project(self, P):
    q = self.view(P)
    z = q[:, 2]
    zz = np.where(np.abs(z) < 1e-9, 1e-9, z)
    return q[:, 0] / zz * self.f + self.c[0], q[:, 1] / zz * self.f + self.c[1], z


def _tris(scene):
  P, N, M = [], [], []
  mats = []
  for m, mat in scene:
    v, t = PR.mesh_of(m)
    if len(t) == 0:
      mats.append(mat)             # keep the material numbers lined up with the scene's items
      continue
    _, cn = PR.corner_normals(v, t, mat.smooth, mat.crease)
    P.append(v[t])
    N.append(cn)
    M.append(np.full(len(t), len(mats), np.int32))
    mats.append(mat)
  if not P:
    return np.zeros((0, 3, 3)), np.zeros((0, 3, 3)), np.zeros(0, np.int32), mats
  return np.concatenate(P), np.concatenate(N), np.concatenate(M), mats


def _raster(cam, P):
  if len(P) == 0:
    return (np.full((cam.H, cam.W), np.inf, np.float32), np.full((cam.H, cam.W), -1, np.int32),
            np.zeros((cam.H, cam.W), np.float32), np.zeros((cam.H, cam.W), np.float32))
  u, v, z = cam.project(P.reshape(-1, 3))
  return PR._raster(u.reshape(-1, 3), v.reshape(-1, 3), z.reshape(-1, 3), cam.W, cam.H)


def _surface(P, N, tid, ba, bb, ii):
  t = tid[ii]
  wa, wb = ba[ii].astype(np.float64), bb[ii].astype(np.float64)
  wc = 1.0 - wa - wb
  pts = P[t, 0] * wa[:, None] + P[t, 1] * wb[:, None] + P[t, 2] * wc[:, None]
  nrm = N[t, 0] * wa[:, None] + N[t, 1] * wb[:, None] + N[t, 2] * wc[:, None]
  nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
  return pts, nrm, t


def _facing(cam, pts, nrm):
  vdir = cam.eye - pts
  vdir /= np.linalg.norm(vdir, axis=1, keepdims=True)
  back = np.einsum("ij,ij->i", nrm, vdir) < 0
  nrm = nrm.copy()
  nrm[back] *= -1
  return nrm, vdir


def _ssao(cam, pts, nrm, zbuf, radius, samples, rng):
  """The share of a small hemisphere round each point that is open (1 = nothing near), read off a depth buffer."""
  q0 = cam.view(pts)
  nv = nrm @ cam.R.T
  occl = np.zeros(len(pts))
  dirs = rng.normal(size=(samples, 3))
  dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
  lens = (np.arange(1, samples + 1) / samples) ** 1.5
  H, W = zbuf.shape
  for d, s in zip(dirs, lens):
    dd = np.tile(d, (len(pts), 1))
    flip = np.einsum("ij,ij->i", dd, nv) < 0
    dd[flip] *= -1
    q = q0 + dd * (radius * s) + nv * 0.6
    qz = np.maximum(q[:, 2], 1.0)
    px = np.clip((q[:, 0] / qz * cam.f + cam.c[0]).astype(int), 0, W - 1)
    py = np.clip((q[:, 1] / qz * cam.f + cam.c[1]).astype(int), 0, H - 1)
    zs = zbuf[py, px]
    occl += (zs < qz - 0.4) & (np.abs(zs - qz) < radius * 1.5)
  return 1.0 - occl / samples


def _grain(pts, mm):
  def vnoise(q):
    c = np.floor(q)
    f = q - c
    f = f * f * (3 - 2 * f)
    out = 0.0
    for ox in (0, 1):
      for oy in (0, 1):
        for oz in (0, 1):
          k = c + np.array([ox, oy, oz], float)
          h = np.modf(np.abs(np.sin(k @ np.array([12.9898, 78.233, 37.719])) * 43758.5453))[0]
          w = (f[:, 0] if ox else 1 - f[:, 0]) * (f[:, 1] if oy else 1 - f[:, 1]) * (f[:, 2] if oz else 1 - f[:, 2])
          out = out + w * h
    return out
  return 0.65 * vnoise(pts / mm) + 0.35 * vnoise(pts / (mm * 0.45) + 17.0)


def shade(mats, mid, pts, nrm, vdir, ao, lights):
  """Linear radiance. lights: {"flash": {"pos", "power", "d0", "p"}, "sun": {"dir", "power", "rgb"},
  "sky": {"up", "sky", "ground", "power"}}."""
  alb = np.stack([mats[i].albedo for i in mid]).astype(np.float64) if len(mid) else np.zeros((0, 3))
  spec = np.array([mats[i].spec for i in mid], float)
  shine = np.array([mats[i].shine for i in mid], float)
  grain = np.array([mats[i].grain for i in mid], float)
  if grain.any():
    gmm = np.array([mats[i].grain_mm for i in mid], float)
    nz = _grain(pts, gmm[:, None])
    alb = alb * (1 + grain[:, None] * (nz[:, None] - 0.5) * 2)
  ndv = np.clip(np.einsum("ij,ij->i", nrm, vdir), 0, 1)
  fres = spec + (1 - spec) * (1 - ndv) ** 5 * 0.25
  col = np.zeros_like(alb)
  sk = lights.get("sky")
  if sk:
    up = np.asarray(sk["up"], float)
    up /= np.linalg.norm(up)
    hemi = 0.5 + 0.5 * (nrm @ up)
    amb = np.asarray(sk["sky"])[None] * hemi[:, None] + np.asarray(sk["ground"])[None] * (1 - hemi[:, None])
    col += alb * amb * (sk["power"] * ao)[:, None]
    rdir = 2 * ndv[:, None] * nrm - vdir
    col += (fres * 0.5 * ao)[:, None] * np.asarray(sk["sky"])[None] * (0.5 + 0.5 * (rdir @ up))[:, None] * sk["power"]

  def direct(L, E, rgb):
    ndl = np.clip(np.einsum("ij,ij->i", nrm, L), 0, 1)
    h = L + vdir
    h /= np.linalg.norm(h, axis=1, keepdims=True)
    ndh = np.clip(np.einsum("ij,ij->i", nrm, h), 0, 1)
    c = alb * (E * ndl)[:, None] * rgb[None]
    c += (E * fres * ndh ** shine * (shine + 8) / 8 * ndl * 0.5)[:, None] * rgb[None]
    return c
  ws = lights.get("wheel_shade")
  if ws:
    # behind the steering wheel the hub and spokes keep most of the cabin's light off: less light the further in
    r = np.hypot(pts[:, 0], pts[:, 1])
    f = ws["k"] + (1 - ws["k"]) * np.clip((r - ws["r0"]) / (ws["r1"] - ws["r0"]), 0, 1)
    col *= np.where(pts[:, 2] < ws["z"], f, 1.0)[:, None]
  fl = lights.get("flash")
  if fl:
    L = np.asarray(fl["pos"], float)[None] - pts
    d = np.linalg.norm(L, axis=1)
    L /= d[:, None]
    E = fl["power"] * (fl["d0"] / d) ** fl["p"] * (0.4 + 0.6 * ao)
    col += direct(L, E, np.asarray(fl.get("rgb", (1, 1, 1)), float))
  sn = lights.get("sun")
  if sn:
    L = np.asarray(sn["dir"], float)
    L = np.tile(L / np.linalg.norm(L), (len(pts), 1))
    E = sn["power"] * (0.3 + 0.7 * ao)
    col += direct(L, E, np.asarray(sn.get("rgb", (1, 1, 1)), float))
  return col


def layers(cam_full, parts, occluders, box, ss=2, lights=None, ao_radius=9.0, ao_samples=16, seed=1, max_blur_px=40,
           calib=None):
  """Draw the parts in the window box = (x0, y0, w, h) of the photo. Returns, per photo pixel of the window: C (the
  parts' linear colour, premultiplied), A (how much of the pixel the parts cover, before anything in front), Z (their
  distance), occ (how much of it the car hides, the car in front), Zocc, ratio (the car's darkening from the parts'
  nearness) and, if calib = a list of occluder indices, K: those occluders' own linear shading (for matching the
  photo's brightness), with Km their coverage."""
  rng = np.random.default_rng(seed)
  x0, y0, w, h = box
  cam = cam_full.sub(x0, y0, w, h, ss)
  Pp, Np, Mp, matp = _tris(parts)
  Po, No, Mo, mato = _tris(occluders)
  zp, tp, bap, bbp = _raster(cam, Pp)
  zo, to, bao, bbo = _raster(cam, Po)
  zall = np.minimum(zp, zo)
  out = {}

  part = tp >= 0
  ii = np.nonzero(part)
  pts, nrm, t = _surface(Pp, Np, tp, bap, bbp, ii)
  nrm, vdir = _facing(cam, pts, nrm)
  ao = _ssao(cam, pts, nrm, zall, ao_radius, ao_samples, rng)
  col = shade(matp, Mp[t], pts, nrm, vdir, ao, lights)
  C = np.zeros((cam.H, cam.W, 3))
  C[ii] = col
  Z = np.where(part, zp, 0.0)

  # the car in front of a part, or of the space round it (so the car's blurred edge can cover the part)
  r = max(1, int(max_blur_px * ss))
  zp_near = cv2.erode(np.where(part, zp, 1e9).astype(np.float32), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
  occ = (to >= 0) & np.where(part, zo < zp - 0.5, zo < zp_near - 0.5)
  Zocc = np.where(occ, zo, 0.0)

  # the car's darkening where a part comes close to it
  carv = (to >= 0) & (zo <= zp)
  jj = np.nonzero(carv)
  ratio = np.ones((cam.H, cam.W))
  if len(jj[0]):
    cpts, cnrm, ct = _surface(Po, No, to, bao, bbo, jj)
    cnrm, cvd = _facing(cam, cpts, cnrm)
    near = np.isfinite(zp_near[jj]) & (zp_near[jj] < 1e8)
    if near.any():
      sel = np.nonzero(near)[0]
      a1 = _ssao(cam, cpts[sel], cnrm[sel], zall, ao_radius * 1.6, ao_samples, rng)
      a0 = _ssao(cam, cpts[sel], cnrm[sel], zo, ao_radius * 1.6, ao_samples, rng)
      rr = np.clip((0.25 + 0.75 * a1) / (0.25 + 0.75 * a0), 0.45, 1.0)
      ratio[jj[0][sel], jj[1][sel]] = rr
    if calib is not None:
      Kc = np.zeros((cam.H, cam.W, 3))
      Km = np.zeros((cam.H, cam.W))
      ids = np.isin(Mo[ct], np.asarray(calib))
      if ids.any():
        sel = np.nonzero(ids)[0]
        ao0 = _ssao(cam, cpts[sel], cnrm[sel], zo, ao_radius, ao_samples, rng)
        kc = shade(mato, Mo[ct][sel], cpts[sel], cnrm[sel], cvd[sel], ao0, lights)
        Kc[jj[0][sel], jj[1][sel]] = kc
        Km[jj[0][sel], jj[1][sel]] = 1.0

  def down(x):
    if x.ndim == 3:
      return x.reshape(h, ss, w, ss, x.shape[2]).mean(axis=(1, 3))
    return x.reshape(h, ss, w, ss).mean(axis=(1, 3))
  A = down(part.astype(float))
  out["C"] = down(C)
  out["A"] = A
  out["Z"] = down(Z) / np.maximum(A, 1e-6)
  o = down(occ.astype(float))
  out["occ"] = o
  out["Zocc"] = down(Zocc) / np.maximum(o, 1e-6)
  out["ratio"] = down(ratio)
  if calib is not None:
    km = down(Km)
    out["K"] = down(Kc) / np.maximum(km, 1e-6)[..., None]
    out["Km"] = km
  out["box"] = box
  return out


def disk_blur(img, r):
  if r < 0.6:
    return img
  R = math.ceil(r)
  yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
  k = np.clip(r + 0.5 - np.hypot(xx, yy), 0, 1).astype(np.float32)
  k /= k.sum()
  return cv2.filter2D(img.astype(np.float32), -1, k, borderType=cv2.BORDER_REFLECT)


def coc_px(d, focus, aperture_mm, f_px):
  """The blur disc's diameter in pixels for something d mm from the lens, focused at focus mm."""
  return aperture_mm * f_px * np.abs(1.0 / np.maximum(d, 1.0) - 1.0 / focus)


def composite(photo, L, gain, wb=(1.0, 1.0, 1.0), focus=250.0, aperture_mm=3.4, f_px=1900.0, noise=0.0,
              occ_depth=None, levels_n=10, seed=2, knee=0.55):
  """photo: uint8 RGB. gain: the parts' linear colour -> the photo's. Returns uint8 RGB."""
  rng = np.random.default_rng(seed)
  x0, y0, w, h = L["box"]
  img = srgb_to_lin(photo.astype(np.float64) / 255.0)
  bg = img[y0:y0 + h, x0:x0 + w] * L["ratio"][..., None]
  C = L["C"] * gain * np.asarray(wb)[None, None]
  A = L["A"].copy()
  # a soft shoulder on the brightest parts, as the phone rolls off its highlights
  cu = C / np.maximum(A, 1e-6)[..., None]
  cu = np.where(cu > knee, knee + (1 - knee) * (1 - np.exp(-(cu - knee) / (1 - knee))), cu)
  C = cu * A[..., None]
  # the parts blurred as the lens blurs them: each pixel spread over its own disc (the discs sorted into a few sizes,
  # each pixel shared between the two nearest sizes so nothing shows a seam), the spreads added up
  m = A > 1e-4
  Cs = np.zeros_like(C)
  As = np.zeros_like(A)
  if m.any():
    r = np.where(m, coc_px(L["Z"], focus, aperture_mm, f_px) / 2, 0.0)
    lo, hi = max(float(r[m].min()), 0.5), max(float(r[m].max()), 0.6)
    levels = np.unique(np.round(np.geomspace(lo, hi, levels_n), 3))
    idx = np.interp(r, levels, np.arange(len(levels), dtype=float))
    for k, rk in enumerate(levels):
      wk = np.clip(1.0 - np.abs(idx - k), 0.0, 1.0) * m
      if not wk.any():
        continue
      Cs += disk_blur(C * wk[..., None], rk)
      As += disk_blur(A * wk, rk)
  Cn = Cs / np.maximum(As, 1.0)[..., None]
  An = np.clip(As, 0.0, 1.0)
  # the car in front of a part hides it, its edge blurred as the photo blurs it
  vis = np.ones_like(An)
  if L["occ"].max() > 0:
    sel = L["occ"] > 0.5 if (L["occ"] > 0.5).any() else L["occ"] > 0
    zo = occ_depth if occ_depth is not None else float(np.median(L["Zocc"][sel]))
    ro = coc_px(zo, focus, aperture_mm, f_px) / 2
    vis = 1.0 - np.clip(disk_blur(L["occ"], ro), 0, 1)
  acc = bg * (1.0 - An * vis)[..., None] + Cn * vis[..., None]
  out = lin_to_srgb(acc)
  if noise > 0:
    cover = (An * vis)[..., None]
    out = out + rng.normal(scale=noise, size=out.shape) * cover
  res = photo.copy()
  res[y0:y0 + h, x0:x0 + w] = np.clip(out * 255.0 + 0.5, 0, 255).astype(np.uint8)
  return res

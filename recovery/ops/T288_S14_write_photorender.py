"""
Photo-style pictures: a small perspective renderer written with numpy (no other renderer is installed here).
Smooth shading that keeps sharp edges sharp, a key light with soft shadows (a shadow map), a sky light with ambient
occlusion read off the depth buffer, glossy highlights, filmic tone mapping and 2x supersampling.

  img = render(scene, camera, lights)      # scene: list of (Manifold, Mat); returns an RGB float image
"""
import math

import numpy as np


class Mat:
  def __init__(self, albedo, spec=0.04, shine=30.0, smooth=True, crease=40.0):
    self.albedo = np.asarray(albedo, dtype=np.float32)
    self.spec, self.shine, self.smooth, self.crease = float(spec), float(shine), bool(smooth), float(crease)


def mesh_of(m):
  mesh = m.to_mesh()
  return np.asarray(mesh.vert_properties)[:, :3].astype(np.float64), np.asarray(mesh.tri_verts).astype(np.int64)


def corner_normals(v, t, smooth, crease_deg):
  """Per-corner normals: the area-weighted average of the faces round the corner's vertex whose normals are within
  crease_deg of this face's (so a cylinder is smooth and a box's edges stay sharp)."""
  p0, p1, p2 = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
  raw = np.cross(p1 - p0, p2 - p0)
  fn = raw / np.maximum(np.linalg.norm(raw, axis=1, keepdims=True), 1e-12)
  if not smooth or len(t) == 0:
    return fn, np.repeat(fn[:, None, :], 3, axis=1)
  cf = np.repeat(np.arange(len(t)), 3)            # each corner's face
  cv = t.ravel()                                    # each corner's vertex
  order = np.argsort(cv, kind="stable")
  cf_s, cv_s = cf[order], cv[order]
  _, start, count = np.unique(cv_s, return_index=True, return_counts=True)
  grp = np.repeat(np.arange(len(start)), count)    # the group of each sorted corner
  L = count[grp]
  S0 = start[grp]
  total = int(L.sum())
  i = np.repeat(np.arange(len(cf_s)), L)
  off = np.arange(total) - np.repeat(np.cumsum(L) - L, L)
  j = np.repeat(S0, L) + off
  fi, fj = cf_s[i], cf_s[j]
  w = (np.einsum("ij,ij->i", fn[fi], fn[fj]) > math.cos(math.radians(crease_deg))).astype(np.float64)
  acc = np.zeros((len(cf_s), 3))
  np.add.at(acc, i, raw[fj] * w[:, None])
  acc /= np.maximum(np.linalg.norm(acc, axis=1, keepdims=True), 1e-12)
  out = np.zeros((len(cf), 3))
  out[order] = acc
  return fn, out.reshape(-1, 3, 3)


class Camera:
  def __init__(self, eye, target, up, fov_deg, size):
    self.eye = np.asarray(eye, float)
    f = np.asarray(target, float) - self.eye
    self.f = f / np.linalg.norm(f)
    r = np.cross(self.f, np.asarray(up, float))
    self.r = r / np.linalg.norm(r)
    self.u = np.cross(self.r, self.f)
    self.W, self.H = size
    self.focal = (self.H / 2) / math.tan(math.radians(fov_deg) / 2)

  def to_view(self, p):
    d = p - self.eye
    return d @ self.r, d @ self.u, d @ self.f

  def project(self, p):
    x, y, z = self.to_view(p)
    return self.W / 2 + x / z * self.focal, self.H / 2 - y / z * self.focal, z


def _raster(xs, ys, ds, W, H, perspective=True, want_bary=True):
  """Depth-buffered triangle fill. ds: per-corner depth (view z, nearer = smaller). Returns depth, triangle id and
  (if asked) the perspective-correct barycentric weights of the first two corners."""
  zbuf = np.full((H, W), np.inf, dtype=np.float32)
  tid = np.full((H, W), -1, dtype=np.int32)
  ba = np.zeros((H, W), dtype=np.float32) if want_bary else None
  bb = np.zeros((H, W), dtype=np.float32) if want_bary else None
  inv = 1.0 / ds if perspective else ds
  x0s, x1s = np.floor(xs.min(axis=1)).astype(int), np.ceil(xs.max(axis=1)).astype(int)
  y0s, y1s = np.floor(ys.min(axis=1)).astype(int), np.ceil(ys.max(axis=1)).astype(int)
  ok = (x1s >= 0) & (x0s < W) & (y1s >= 0) & (y0s < H) & (ds.min(axis=1) > 1.0)
  for k in np.nonzero(ok)[0]:
    xa, xb, xc = xs[k]
    ya, yb, yc = ys[k]
    den = (yb - yc) * (xa - xc) + (xc - xb) * (ya - yc)
    if abs(den) < 1e-12:
      continue
    lx, hx = max(x0s[k], 0), min(x1s[k], W - 1)
    ly, hy = max(y0s[k], 0), min(y1s[k], H - 1)
    X, Y = np.meshgrid(np.arange(lx, hx + 1) + 0.5, np.arange(ly, hy + 1) + 0.5)
    a = ((yb - yc) * (X - xc) + (xc - xb) * (Y - yc)) / den
    b = ((yc - ya) * (X - xc) + (xa - xc) * (Y - yc)) / den
    c = 1.0 - a - b
    inside = (a >= -1e-7) & (b >= -1e-7) & (c >= -1e-7)
    if not inside.any():
      continue
    if perspective:
      iz = a * inv[k, 0] + b * inv[k, 1] + c * inv[k, 2]
      z = 1.0 / iz
    else:
      z = a * ds[k, 0] + b * ds[k, 1] + c * ds[k, 2]
    sub = zbuf[ly:hy + 1, lx:hx + 1]
    upd = inside & (z < sub)
    if not upd.any():
      continue
    sub[upd] = z[upd]
    tid[ly:hy + 1, lx:hx + 1][upd] = k
    if want_bary:
      if perspective:
        pa, pb = a * inv[k, 0] * z, b * inv[k, 1] * z
      else:
        pa, pb = a, b
      ba[ly:hy + 1, lx:hx + 1][upd] = pa[upd]
      bb[ly:hy + 1, lx:hx + 1][upd] = pb[upd]
  return zbuf, tid, ba, bb


def _aces(x):
  a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
  return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)


def render(scene, cam: Camera, key_dir, key_rgb=(1.0, 0.97, 0.92), key_power=2.2, sky_up=(0, 1, 0),
           sky_rgb=(0.62, 0.66, 0.72), ground_rgb=(0.20, 0.19, 0.18), ambient=0.9, fill_dir=None, fill_power=0.35,
           ss=2, shadow_res=4096, ao_radius=22.0, ao_samples=14, exposure=1.0, background_top=(0.06, 0.06, 0.07),
           background_bottom=(0.02, 0.02, 0.02), seed=1):
  rng = np.random.default_rng(seed)
  W, H = cam.W * ss, cam.H * ss
  cam = Camera(cam.eye, cam.eye + cam.f, cam.u, math.degrees(2 * math.atan((cam.H / 2) / cam.focal)), (W, H))
  # gather every triangle
  P, N, ALB, SPEC, SHINE = [], [], [], [], []
  for m, mat in scene:
    v, t = mesh_of(m)
    if len(t) == 0:
      continue
    _, cn = corner_normals(v, t, mat.smooth, mat.crease)
    P.append(v[t])
    N.append(cn)
    ALB.append(np.tile(mat.albedo, (len(t), 1)))
    SPEC.append(np.full(len(t), mat.spec))
    SHINE.append(np.full(len(t), mat.shine))
  P = np.concatenate(P)
  N = np.concatenate(N)
  ALB = np.concatenate(ALB).astype(np.float32)
  SPEC = np.concatenate(SPEC).astype(np.float32)
  SHINE = np.concatenate(SHINE).astype(np.float32)

  # camera pass
  flat = P.reshape(-1, 3)
  sx, sy, sz = cam.project(flat)
  zbuf, tid, ba, bb = _raster(sx.reshape(-1, 3), sy.reshape(-1, 3), sz.reshape(-1, 3), W, H)
  hit = tid >= 0

  # shadow pass: an orthographic depth map along the key light
  L = np.asarray(key_dir, float)
  L = L / np.linalg.norm(L)
  lu = np.cross(L, [0.0, 0.0, 1.0] if abs(L[2]) < 0.9 else [1.0, 0.0, 0.0])
  lu /= np.linalg.norm(lu)
  lv = np.cross(L, lu)
  # only what the camera sees, and what lies between it and the light, matters: frame the map on the visible points
  ii = np.nonzero(hit)
  t_hit = tid[ii]
  wa, wb = ba[ii].astype(np.float64), bb[ii].astype(np.float64)
  wc = 1.0 - wa - wb
  pts = P[t_hit, 0] * wa[:, None] + P[t_hit, 1] * wb[:, None] + P[t_hit, 2] * wc[:, None]
  lo_u, hi_u = np.percentile(pts @ lu, [0.2, 99.8])
  lo_v, hi_v = np.percentile(pts @ lv, [0.2, 99.8])
  pad = 40.0
  lo_u, hi_u, lo_v, hi_v = lo_u - pad, hi_u + pad, lo_v - pad, hi_v + pad
  scale = shadow_res / max(hi_u - lo_u, hi_v - lo_v)
  def to_map(p):
    return (p @ lu - lo_u) * scale, (hi_v - p @ lv) * scale, -(p @ L)
  mx, my, md = to_map(flat)
  smap, _, _, _ = _raster(mx.reshape(-1, 3), my.reshape(-1, 3), md.reshape(-1, 3) + 1e4, shadow_res, shadow_res,
                          perspective=False, want_bary=False)
  smap = smap - 1e4

  # per-pixel normal, position, view direction
  nrm = N[t_hit, 0] * wa[:, None] + N[t_hit, 1] * wb[:, None] + N[t_hit, 2] * wc[:, None]
  nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
  vdir = cam.eye - pts
  vdir /= np.linalg.norm(vdir, axis=1, keepdims=True)
  back = np.einsum("ij,ij->i", nrm, vdir) < 0
  nrm[back] *= -1

  # soft shadow: percentage-closer filtering over a small disc
  qx, qy, qd = to_map(pts)
  bias = 0.6 + 1.2 * (1 - np.clip(np.einsum("ij,j->i", nrm, L), 0, 1))
  lit = np.zeros(len(pts))
  taps = [(0, 0)] + [(2.2 * math.cos(a), 2.2 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]] + \
         [(4.4 * math.cos(a + 0.4), 4.4 * math.sin(a + 0.4)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
  for dx, dy in taps:
    ix = np.clip((qx + dx).astype(int), 0, shadow_res - 1)
    iy = np.clip((qy + dy).astype(int), 0, shadow_res - 1)
    lit += (qd - bias <= smap[iy, ix]).astype(float)
  lit /= len(taps)

  # ambient occlusion from the depth buffer (view space)
  vx, vy, vz = cam.to_view(pts)
  vn = np.stack([nrm @ cam.r, nrm @ cam.u, nrm @ cam.f], axis=1)
  occl = np.zeros(len(pts))
  dirs = rng.normal(size=(ao_samples, 3))
  dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
  lens = (np.arange(1, ao_samples + 1) / ao_samples) ** 1.6
  for d, s in zip(dirs, lens):
    dd = np.tile(d, (len(pts), 1))
    flip = np.einsum("ij,ij->i", dd, vn) < 0
    dd[flip] *= -1
    q = np.stack([vx, vy, vz], axis=1) + dd * (ao_radius * s) + vn * 0.8
    qz = np.maximum(q[:, 2], 1.0)
    px = np.clip((W / 2 + q[:, 0] / qz * cam.focal).astype(int), 0, W - 1)
    py = np.clip((H / 2 - q[:, 1] / qz * cam.focal).astype(int), 0, H - 1)
    zs = zbuf[py, px]
    in_front = zs < qz - 0.5
    near = np.abs(zs - qz) < ao_radius * 1.5
    occl += in_front & near
  ao = 1.0 - occl / ao_samples
  ao = 0.35 + 0.65 * ao

  # shading
  alb = ALB[t_hit].astype(np.float64)
  up = np.asarray(sky_up, float)
  up /= np.linalg.norm(up)
  hemi = 0.5 + 0.5 * (nrm @ up)
  amb = (np.asarray(sky_rgb)[None, :] * hemi[:, None] + np.asarray(ground_rgb)[None, :] * (1 - hemi[:, None])) * ambient
  ndl = np.clip(nrm @ L, 0, 1)
  hvec = L[None, :] + vdir
  hvec /= np.linalg.norm(hvec, axis=1, keepdims=True)
  ndh = np.clip(np.einsum("ij,ij->i", nrm, hvec), 0, 1)
  spec_k = SPEC[t_hit].astype(np.float64)
  shine = SHINE[t_hit].astype(np.float64)
  fres = spec_k + (1 - spec_k) * (1 - np.clip(np.einsum("ij,ij->i", nrm, vdir), 0, 1)) ** 5 * 0.25
  key = np.asarray(key_rgb)[None, :] * key_power * lit[:, None]
  col = alb * (amb * ao[:, None] + key * ndl[:, None])
  col += key * (fres * ndh ** shine * (shine + 8) / 8 * ndl)[:, None] * 0.5
  if fill_dir is not None:
    F = np.asarray(fill_dir, float)
    F /= np.linalg.norm(F)
    col += alb * (np.clip(nrm @ F, 0, 1) * fill_power)[:, None] * ao[:, None]
  # sky reflection on glossy things
  rdir = 2 * np.einsum("ij,ij->i", nrm, vdir)[:, None] * nrm - vdir
  sky_ref = 0.5 + 0.5 * (rdir @ up)
  col += (fres * 0.6)[:, None] * (np.asarray(sky_rgb)[None, :] * sky_ref[:, None] * 0.6) * ao[:, None]

  img = np.zeros((H, W, 3))
  rows = np.linspace(0, 1, H)[:, None, None]
  img[:] = np.asarray(background_top) * (1 - rows) + np.asarray(background_bottom) * rows
  img[ii] = col * exposure
  img = _aces(img)
  img = img ** (1 / 2.2)
  # down-sample (box) and a faint grain
  img = img.reshape(cam.H // ss if False else H // ss, ss, W // ss, ss, 3).mean(axis=(1, 3))
  img += rng.normal(scale=0.006, size=img.shape)
  return np.clip(img, 0, 1)


def save_png(path, img):
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  plt.imsave(path, img)

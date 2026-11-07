"""
Pictures of the parts: a small depth-buffered renderer (orthographic view, flat shading) written with numpy,
so parts that overlap on screen are drawn correctly. Saves PNG files with matplotlib's image writer.
"""
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def view_matrix(azimuth_deg: float, elevation_deg: float) -> np.ndarray:
  """Rows: screen right, screen up, towards the viewer. azimuth turns about +Z, elevation tilts towards +Z."""
  az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
  # direction from the scene towards the viewer
  d = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
  up_world = np.array([0.0, 0.0, 1.0]) if abs(el) < math.radians(89) else np.array([0.0, 1.0, 0.0])
  right = np.cross(up_world, d)
  right /= np.linalg.norm(right)
  up = np.cross(d, right)
  return np.stack([right, up, d])


def look(direction_to_viewer, up) -> np.ndarray:
  """View matrix looking along -direction_to_viewer, with 'up' (projected) pointing up on screen."""
  d = np.asarray(direction_to_viewer, dtype=float)
  d /= np.linalg.norm(d)
  u = np.asarray(up, dtype=float)
  u = u - (u @ d) * d
  u /= np.linalg.norm(u)
  right = np.cross(u, d)
  return np.stack([right, u, d])


def render(parts, rot: np.ndarray, size=(900, 700), margin=0.06, light=(0.35, 0.55, 0.75), background=(1, 1, 1)):
  """parts: list of (manifold, rgb). rot: 3x3 view matrix (screen right, up, towards viewer). Returns an RGB image."""
  w, h = size
  tris, cols = [], []
  for m, color in parts:
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3] @ rot.T
    t = np.asarray(mesh.tri_verts)
    tris.append(v[t])
    cols.append(np.tile(np.asarray(color, dtype=float), (len(t), 1)))
  tri = np.concatenate(tris)
  col = np.concatenate(cols)
  lo, hi = tri.reshape(-1, 3).min(axis=0), tri.reshape(-1, 3).max(axis=0)
  scale = min(w * (1 - 2 * margin) / max(hi[0] - lo[0], 1e-9), h * (1 - 2 * margin) / max(hi[1] - lo[1], 1e-9))
  cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
  px = (tri[:, :, 0] - cx) * scale + w / 2
  py = h / 2 - (tri[:, :, 1] - cy) * scale
  pz = tri[:, :, 2]
  n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
  nn = np.linalg.norm(n, axis=1, keepdims=True)
  n = n / np.maximum(nn, 1e-12)
  lt = np.asarray(light, dtype=float)
  lt /= np.linalg.norm(lt)
  shade = 0.30 + 0.55 * np.abs(n @ lt) + 0.15 * np.clip(n[:, 2], 0, 1)
  rgb = np.clip(col * shade[:, None], 0, 1)

  zbuf = np.full((h, w), -np.inf)
  img = np.ones((h, w, 3)) * np.asarray(background, dtype=float)
  for i in range(len(tri)):
    x0, x1, x2 = px[i]
    y0, y1, y2 = py[i]
    xmin, xmax = int(max(0, math.floor(min(x0, x1, x2)))), int(min(w - 1, math.ceil(max(x0, x1, x2))))
    ymin, ymax = int(max(0, math.floor(min(y0, y1, y2)))), int(min(h - 1, math.ceil(max(y0, y1, y2))))
    if xmax < xmin or ymax < ymin:
      continue
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(den) < 1e-12:
      continue
    xs, ys = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
    a = ((y1 - y2) * (xs - x2) + (x2 - x1) * (ys - y2)) / den
    b = ((y2 - y0) * (xs - x2) + (x0 - x2) * (ys - y2)) / den
    c = 1 - a - b
    inside = (a >= -1e-6) & (b >= -1e-6) & (c >= -1e-6)
    if not inside.any():
      continue
    z = a * pz[i, 0] + b * pz[i, 1] + c * pz[i, 2]
    sub = zbuf[ymin:ymax + 1, xmin:xmax + 1]
    upd = inside & (z > sub)
    sub[upd] = z[upd]
    img[ymin:ymax + 1, xmin:xmax + 1][upd] = rgb[i]
  # dark outline where depth jumps, so edges read clearly
  zf = np.where(np.isfinite(zbuf), zbuf, np.nan)
  edge = np.zeros((h, w), dtype=bool)
  thr = 2.0 / scale * 3
  for dy, dx in ((0, 1), (1, 0)):
    a1 = zf[: h - dy, : w - dx]
    a2 = zf[dy:, dx:]
    jump = (np.isnan(a1) != np.isnan(a2)) | (np.abs(np.nan_to_num(a1) - np.nan_to_num(a2)) > thr)
    edge[: h - dy, : w - dx] |= jump
  img[edge] = img[edge] * 0.35
  return img


def save(path, panels, titles=None, suptitle=None, size=(900, 700), cols=None):
  """panels: list of (parts, rot). Saves them side by side, or in rows of cols."""
  imgs = [render(parts, rot, size=size) for parts, rot in panels]
  ncol = len(imgs) if not cols else min(cols, len(imgs))
  nrow = -(-len(imgs) // ncol)
  if suptitle:
    import textwrap
    width = max(60, int(ncol * size[0] / 12))      # about the characters that fit one line at this width
    suptitle = textwrap.fill(suptitle, width)
  lines = suptitle.count("\n") + 1 if suptitle else 0
  height = nrow * size[1] / 150 + (0.3 + 0.2 * lines if suptitle else 0.2)
  fig, axes = plt.subplots(nrow, ncol, figsize=(ncol * size[0] / 150, height), dpi=150)
  axes = np.atleast_1d(axes).ravel()
  for ax in axes[len(imgs):]:
    ax.set_axis_off()
  for i, (ax, im) in enumerate(zip(axes, imgs)):
    ax.imshow(im)
    ax.set_axis_off()
    if titles:
      ax.set_title(titles[i], fontsize=9)
  if suptitle:
    fig.suptitle(suptitle, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 1 - (0.12 + 0.2 * lines) / height))   # the panels' titles clear of the suptitle
  else:
    fig.tight_layout()
  fig.savefig(path)
  plt.close(fig)

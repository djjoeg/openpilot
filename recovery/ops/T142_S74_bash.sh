mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > mindist.py <<'EOF'
"""Smallest distance between two solids' surfaces (mm), by dense sampling plus exact point-to-triangle distances."""
import numpy as np
from scipy.spatial import cKDTree


def _tris(m):
  mesh = m.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3].astype(float)
  t = np.asarray(mesh.tri_verts).astype(int)
  return v, t


def _sample(v, t, spacing=1.0):
  a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
  area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
  n = np.maximum(1, np.ceil(area / (spacing * spacing))).astype(int)
  idx = np.repeat(np.arange(len(t)), n)
  r1 = np.sqrt(np.random.rand(len(idx)))
  r2 = np.random.rand(len(idx))
  p = (1 - r1)[:, None] * a[idx] + (r1 * (1 - r2))[:, None] * b[idx] + (r1 * r2)[:, None] * c[idx]
  return np.vstack([p, v])


def _pt_tri(p, a, b, c):
  """Distances from points p (n,3) to triangles (n,3 each), vectorised (Ericson's closest point)."""
  ab, ac, ap = b - a, c - a, p - a
  d1, d2 = np.einsum("ij,ij->i", ab, ap), np.einsum("ij,ij->i", ac, ap)
  bp = p - b
  d3, d4 = np.einsum("ij,ij->i", ab, bp), np.einsum("ij,ij->i", ac, bp)
  cp = p - c
  d5, d6 = np.einsum("ij,ij->i", ab, cp), np.einsum("ij,ij->i", ac, cp)
  vc = d1 * d4 - d3 * d2
  vb = d5 * d2 - d1 * d6
  va = d3 * d6 - d5 * d4
  denom = va + vb + vc
  denom = np.where(np.abs(denom) < 1e-12, 1e-12, denom)
  v = vb / denom
  w = vc / denom
  q = a + ab * v[:, None] + ac * w[:, None]
  # region tests
  m = (d1 <= 0) & (d2 <= 0); q[m] = a[m]
  m = (d3 >= 0) & (d4 <= d3); q[m] = b[m]
  m = (d6 >= 0) & (d5 <= d6); q[m] = c[m]
  m = (vc <= 0) & (d1 >= 0) & (d3 <= 0)
  t_ = np.where(m, d1 / np.where(d1 - d3 == 0, 1e-12, d1 - d3), 0); q[m] = (a + ab * t_[:, None])[m]
  m = (vb <= 0) & (d2 >= 0) & (d6 <= 0)
  t_ = np.where(m, d2 / np.where(d2 - d6 == 0, 1e-12, d2 - d6), 0); q[m] = (a + ac * t_[:, None])[m]
  m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0)
  t_ = np.where(m, (d4 - d3) / np.where((d4 - d3) + (d5 - d6) == 0, 1e-12, (d4 - d3) + (d5 - d6)), 0)
  q[m] = (b + (c - b) * t_[:, None])[m]
  return np.linalg.norm(p - q, axis=1)


def min_dist(A, B, spacing=1.0, k=12):
  """Smallest gap between solids A and B (0 if they overlap). Returns (gap, point on A)."""
  if A.is_empty() or B.is_empty():
    return float("inf"), None
  if (A ^ B).volume() > 1e-3:
    return 0.0, None
  va, ta = _tris(A)
  vb, tb = _tris(B)
  pa = _sample(va, ta, spacing)
  cent = (vb[tb[:, 0]] + vb[tb[:, 1]] + vb[tb[:, 2]]) / 3.0
  tree = cKDTree(cent)
  # first a coarse pass to find the close region
  d0, _ = cKDTree(_sample(vb, tb, spacing)).query(pa)
  near = d0 < d0.min() + 3.0 * spacing + 2.0
  p = pa[near]
  _, idx = tree.query(p, k=min(k, len(cent)))
  best = np.inf
  arg = None
  for j in range(idx.shape[1]):
    ti = tb[idx[:, j]]
    d = _pt_tri(p, vb[ti[:, 0]], vb[ti[:, 1]], vb[ti[:, 2]])
    i = int(np.argmin(d))
    if d[i] < best:
      best, arg = float(d[i]), p[i]
  return best, arg
EOF
echo ok
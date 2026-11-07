"""
Voxel finite-element check of the right arm v4 under the motor's push (3 Nov 2026).

The arm (bar, foot, tower) and the carrier (bar, web, plate) as one PETG solid: the carrier's bar bonded into the
tower's tube over its engaged length (the push bolt and friction hold it), the motor rigid, bolted to the plate.
The arm's bar is held fixed inside the receiver (x <= 120): stiffer than the real receiver (one wing bolt, 0.2 mm
clearance), so the gear's movement found here is the least it can be.

Load: the gear's reaction at the pitch point (radius 166 on the face gear, 16 above the gear's axis): the tangential
force F_t = torque at the steering wheel / 0.166 m, along -V or +V, and the separating force F_t * tan(20 deg) along -z.

  python3 armfea.py [voxel_mm] [E_MPa]
"""
import math
import sys
import time

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from matplotlib.path import Path

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import rightarm as RA  # noqa: E402

H = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
E = float(sys.argv[2]) if len(sys.argv) > 2 else 1800.0
NU = 0.38
R_PITCH = 166.0
TAN_PA = math.tan(math.radians(20.0))


def solid_model(variant=None):
  arm = RA.arm()
  car = RA.carrier(0.0)
  fill = RA.uvz(RA.CH_U[0], RA.CH_U[1], RA.CH_V0, RA.CH_V1, RA.BAR_Z[0], RA.TOWER_Z[1])
  return arm + car + fill


def voxelize(m, h):
  bb = m.bounding_box()
  lo = np.array(bb[:3]) - h
  hi = np.array(bb[3:]) + h
  n = np.ceil((hi - lo) / h).astype(int)
  xs = lo[0] + (np.arange(n[0]) + 0.5) * h
  ys = lo[1] + (np.arange(n[1]) + 0.5) * h
  zs = lo[2] + (np.arange(n[2]) + 0.5) * h
  gx, gy = np.meshgrid(xs, ys, indexing="ij")
  pts = np.column_stack([gx.ravel(), gy.ravel()])
  vox = np.zeros(n, dtype=bool)
  for k, z in enumerate(zs):
    polys = m.slice(float(z)).to_polygons()
    inside = np.zeros(len(pts), dtype=bool)
    for poly in polys:
      p = np.asarray(poly)
      if len(p) < 3:
        continue
      inside ^= Path(p).contains_points(pts)
    vox[:, :, k] = inside.reshape(n[0], n[1])
  return vox, lo, h


def hex8_ke(e, nu):
  """Stiffness of a unit cube 8-node brick, 2x2x2 Gauss; scale by h for a cube of side h."""
  lam = e * nu / ((1 + nu) * (1 - 2 * nu))
  mu = e / (2 * (1 + nu))
  D = np.zeros((6, 6))
  D[:3, :3] = lam
  D[np.arange(3), np.arange(3)] = lam + 2 * mu
  D[3, 3] = D[4, 4] = D[5, 5] = mu
  corners = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]], float)
  sgn = corners * 2 - 1
  g = 1 / math.sqrt(3)
  K = np.zeros((24, 24))
  for a in (-g, g):
    for b in (-g, g):
      for c in (-g, g):
        # shape function derivatives in natural coords, mapped to a unit cube (dx/dxi = 0.5)
        dN = np.zeros((8, 3))
        for i in range(8):
          sx, sy, sz = sgn[i]
          dN[i, 0] = sx * (1 + sy * b) * (1 + sz * c) / 8 * 2
          dN[i, 1] = sy * (1 + sx * a) * (1 + sz * c) / 8 * 2
          dN[i, 2] = sz * (1 + sx * a) * (1 + sy * b) / 8 * 2
        B = np.zeros((6, 24))
        for i in range(8):
          dx, dy, dz = dN[i]
          B[0, 3 * i] = dx
          B[1, 3 * i + 1] = dy
          B[2, 3 * i + 2] = dz
          B[3, 3 * i] = dy
          B[3, 3 * i + 1] = dx
          B[4, 3 * i + 1] = dz
          B[4, 3 * i + 2] = dy
          B[5, 3 * i] = dz
          B[5, 3 * i + 2] = dx
        K += B.T @ D @ B * (0.5 ** 3)   # det J = 1/8 for the unit cube, weight 1 each
  return K, corners.astype(int)


def assemble(vox, h, e, nu):
  ke, corners = hex8_ke(e, nu)
  ke *= h
  nx, ny, nz = vox.shape
  ei = np.argwhere(vox)
  node_id = -np.ones((nx + 1, ny + 1, nz + 1), dtype=np.int64)
  en = np.zeros((len(ei), 8), dtype=np.int64)
  allc = (ei[:, None, :] + corners[None, :, :]).reshape(-1, 3)
  uniq, inv = np.unique(allc, axis=0, return_inverse=True)
  en = inv.reshape(len(ei), 8)
  node_id[uniq[:, 0], uniq[:, 1], uniq[:, 2]] = np.arange(len(uniq))
  edof = (en[:, :, None] * 3 + np.arange(3)[None, None, :]).reshape(len(ei), 24)
  rows = np.repeat(edof, 24, axis=1).ravel()
  cols = np.tile(edof, (1, 24)).ravel()
  vals = np.tile(ke.ravel(), len(ei))
  ndof = 3 * len(uniq)
  K = sp.csr_matrix((vals, (rows, cols)), shape=(ndof, ndof))
  return K, uniq, en


def main():
  t0 = time.time()
  m = solid_model()
  vox, lo, h = voxelize(m, H)
  print(f"voxels {H} mm: {vox.sum()} solid of {vox.size}; volume {vox.sum() * H**3 / 1000:.1f} cm3 "
        f"(model {m.volume() / 1000:.1f}); {time.time() - t0:.0f} s")
  K, nodes, en = assemble(vox, h, E, NU)
  xyz = lo + nodes * h
  print(f"nodes {len(nodes)}, dof {K.shape[0]}, nnz {K.nnz}; {time.time() - t0:.0f} s")

  U, V = RA.U, RA.V
  u_of = xyz[:, 0] * U[0] + xyz[:, 1] * U[1]
  v_of = xyz[:, 0] * V[0] + xyz[:, 1] * V[1]
  z_of = xyz[:, 2]
  # fixed: the arm's bar inside the receiver
  fixed = xyz[:, 0] <= 120.0 + 1e-6
  # loaded: the carrier plate behind the motor's face
  load = (u_of >= RA.PLATE_U[0] - h) & (u_of <= RA.PLATE_U[1] + h) & (np.abs(v_of) <= RA.H) & \
         (np.abs(z_of - RA.Z_AXIS) <= RA.H)
  print(f"fixed nodes {fixed.sum()}, loaded nodes {load.sum()}")

  P = np.array([R_PITCH * U[0], R_PITCH * U[1], RA.Z_AXIS + 16.0])     # the pitch point
  Vv = np.array([V[0], V[1], 0.0])
  Uv = np.array([U[0], U[1], 0.0])
  zhat = np.array([0.0, 0.0, 1.0])
  li = np.where(load)[0]
  c = xyz[li].mean(axis=0)
  r = xyz[li] - c
  I = (r ** 2).sum() * np.eye(3) - r.T @ r

  free_dof = np.ones(K.shape[0], dtype=bool)
  free_dof[(np.where(fixed)[0][:, None] * 3 + np.arange(3)).ravel()] = False
  fd = np.where(free_dof)[0]
  Kf = K[fd][:, fd].tocsc()
  print(f"free dof {len(fd)}; factorizing ... {time.time() - t0:.0f} s")
  lu = spla.splu(Kf, permc_spec="COLAMD")
  print(f"factorized; {time.time() - t0:.0f} s")

  torque = 3.9                           # N m at the steering wheel: lane keeping's most
  Ft = torque / (R_PITCH / 1000.0)
  Fs = Ft * TAN_PA
  out = {}
  for name, sgn in (("left (teeth pushed +V)", -1.0), ("right (teeth pushed -V)", 1.0)):
    F = sgn * Ft * Vv - Fs * zhat                    # on the gear
    M = np.cross(P - c, F)
    om = np.linalg.solve(I, M)
    f_nodes = F / len(li) + np.cross(om, r)
    f = np.zeros(K.shape[0])
    for k in range(3):
      f[li * 3 + k] = f_nodes[:, k]
    uf = lu.solve(f[fd])
    u = np.zeros(K.shape[0])
    u[fd] = uf
    ul = u.reshape(-1, 3)[li]
    # rigid fit: ul = t + w x r
    A = np.zeros((3 * len(li), 6))
    for i in range(len(li)):
      rx, ry, rz = r[i]
      A[3 * i:3 * i + 3, :3] = np.eye(3)
      A[3 * i:3 * i + 3, 3:] = np.array([[0, rz, -ry], [-rz, 0, rx], [ry, -rx, 0]])
    sol, *_ = np.linalg.lstsq(A, ul.ravel(), rcond=None)
    t, w = sol[:3], sol[3:]
    dP = t + np.cross(w, P - c)
    out[name] = dP
    print(f"{name}: F_t {Ft:.1f} N, F_s {Fs:.1f} N -> the gear's pitch point moves: along the column (into the "
          f"teeth +) {dP @ zhat:+.2f} mm, along the rim {dP @ Vv:+.2f} mm, out from the wheel {dP @ Uv:+.2f} mm; "
          f"motor turned {np.degrees(np.linalg.norm(w)):.2f} deg")
  umax = np.abs(u.reshape(-1, 3)).max()
  print(f"largest node movement {umax:.2f} mm; {time.time() - t0:.0f} s")


if __name__ == "__main__":
  main()

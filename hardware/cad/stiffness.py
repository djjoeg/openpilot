"""
How far the motor's push moves the gear in and out of the teeth (3 Nov 2026): a finite-element model of the arm, the
tower and the motor carrier (v6, the fit print), and of the frame plate (v5) holding them; at the drawn place and at
the slides' ends that bend it most (the arm slid 17.5 mm out of the receiver, the motor slid 12 mm up the tower).

The parts are cut into 2 mm cubes of PETG (E 1800 MPa, Poisson 0.38). The carrier's bar is taken as bonded into the
tower's tube over its length in it (the slide's wing bolt and friction hold it), the motor as rigid. The load is the
gear's reaction at its pitch point (radius 166 on the teeth, 16 above the gear's axis) at lane keeping's strongest
push, 3.9 Nm at the steering wheel: along the rim F_t = 3.9 / 0.166 = 23.5 N each way, and the teeth's separating
force F_t tan 20 = 8.6 N pushing the gear out. Two ways of holding it, which bracket the car:

  receiver  the arm's bar held rigidly inside the receiver: stiffer than the car (no receiver, plate or cover);
  plate     the frame plate added, the arm's bar bonded into its receiver (the wing bolt pulls it tight against the
            wall), the plate held only under the fender washers on its two screws (25 mm across): softer than the
            car, which also has the column cover under the plate.

Pass: in both, at 3.9 Nm, the gear moves at most 1.0 mm deeper into the teeth (its tips clear the bottom of the teeth
by 1 mm at the drawn depth) and at most 1.5 mm out of them (of 3.5 mm in mesh). The grip test pushes 1.9 times as
hard (7.3 Nm); the gear's movement then is 1.9 times these.

For the record: v4 (the 10 mm arm) receiver +0.85 to +0.99 / -1.41 to -1.63 mm (1.5 and 2 mm cubes), plate
+1.32 / -2.08 mm: it failed. v5 (the arm 50 deep, 10 x 30 in the receiver) +0.20 / -0.49 and +0.56 / -1.00: passed.

  python3 stiffness.py        # 15 to 20 minutes; prints the movements and PASS or FAIL; exit 1 on FAIL
  python3 stiffness.py quick  # the drawn place only, a few minutes
"""
import math
import sys
import time

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from matplotlib.path import Path

import rightarm as RA
from cadlib import box

H = 2.0                    # the cube's side, mm
E, NU = 1800.0, 0.38       # PETG printed solid (MPa)
R_PITCH = 166.0
TAN_PA = math.tan(math.radians(20.0))
TORQUE = 3.9               # N m at the steering wheel: lane keeping's most
GRIP_TEST = 7.3            # N m: the car setup's grip test
LIMIT_IN, LIMIT_OUT = 1.0, 1.5
WASHER_R = 12.5            # the plate held this far round each cover screw: a fender washer, 25 mm across (v6;
                           # v5's model had 18 mm washers: at the slides' far ends that gave 1.51 mm out, at the mark)


def model(with_plate: bool, dx: float = 0.0, dz: float = 0.0):
  """The arm slid dx across in the receiver, the carrier dz up the tower; the carrier's bar bonded in the tube."""
  bar_end = max(RA.BAR_Z[0] + dz, RA.TOWER_Z[0])
  m = RA.arm() + RA.carrier(dz) + RA.uvz(RA.CH_U[0], RA.CH_U[1], RA.CH_V0, RA.CH_V1, bar_end, RA.TOWER_Z[1])
  m = m.translate((dx, 0.0, 0.0))
  if with_plate:                                   # the plate, the arm's bar bonded into its receiver
    m = m + RA.plate_to_wheel(RA.frame_plate_v5()) + \
      box(RA.ARM_X[0] + dx, RA.RECEIVER_MOUTH, RA.ARM_Y[0] - 0.4, RA.ARM_Y[1], RA.ARM_Z[0] - 0.2, RA.ARM_Z[1] + 0.2)
  return m


def voxelize(m, h):
  bb = m.bounding_box()
  lo = np.array(bb[:3]) - h
  hi = np.array(bb[3:]) + h
  ref = np.array([120.0, -143.0, RA.ARM_Z[0]])     # grid planes on the arm bar's faces: its section is exact
  lo = ref - np.ceil((ref - lo) / h) * h
  n = np.ceil((hi - lo) / h).astype(int)
  xs = lo[0] + (np.arange(n[0]) + 0.5) * h
  ys = lo[1] + (np.arange(n[1]) + 0.5) * h
  zs = lo[2] + (np.arange(n[2]) + 0.5) * h
  gx, gy = np.meshgrid(xs, ys, indexing="ij")
  pts = np.column_stack([gx.ravel(), gy.ravel()])
  vox = np.zeros(n, dtype=bool)
  for k, z in enumerate(zs):
    inside = np.zeros(len(pts), dtype=bool)
    for poly in m.slice(float(z)).to_polygons():
      p = np.asarray(poly)
      if len(p) >= 3:
        inside ^= Path(p).contains_points(pts)
    vox[:, :, k] = inside.reshape(n[0], n[1])
  return vox, lo


def brick_stiffness(e, nu):
  """The 24 x 24 stiffness of a unit cube 8-node brick (2 x 2 x 2 Gauss points); a cube of side h is h times it."""
  lam = e * nu / ((1 + nu) * (1 - 2 * nu))
  mu = e / (2 * (1 + nu))
  D = np.zeros((6, 6))
  D[:3, :3] = lam
  D[range(3), range(3)] = lam + 2 * mu
  D[3, 3] = D[4, 4] = D[5, 5] = mu
  corners = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
  sg = corners * 2 - 1
  g = 1 / math.sqrt(3)
  K = np.zeros((24, 24))
  for a in (-g, g):
    for b in (-g, g):
      for c in (-g, g):
        B = np.zeros((6, 24))
        for i in range(8):
          sx, sy, sz = sg[i]
          dx = sx * (1 + sy * b) * (1 + sz * c) / 4
          dy = sy * (1 + sx * a) * (1 + sz * c) / 4
          dz = sz * (1 + sx * a) * (1 + sy * b) / 4
          B[0, 3 * i], B[1, 3 * i + 1], B[2, 3 * i + 2] = dx, dy, dz
          B[3, 3 * i], B[3, 3 * i + 1] = dy, dx
          B[4, 3 * i + 1], B[4, 3 * i + 2] = dz, dy
          B[5, 3 * i], B[5, 3 * i + 2] = dz, dx
        K += B.T @ D @ B / 8
  return K, corners


def solve(with_plate: bool, dx: float = 0.0, dz: float = 0.0) -> dict:
  t0 = time.time()
  vox, lo = voxelize(model(with_plate, dx, dz), H)
  ke, corners = brick_stiffness(E, NU)
  ei = np.argwhere(vox)
  nodes, inv = np.unique((ei[:, None, :] + corners[None, :, :]).reshape(-1, 3), axis=0, return_inverse=True)
  en = inv.reshape(len(ei), 8)
  edof = (en[:, :, None] * 3 + np.arange(3)).reshape(len(ei), 24)
  K = sp.csr_matrix((np.tile(ke.ravel() * H, len(ei)), (np.repeat(edof, 24, axis=1).ravel(), np.tile(edof, (1, 24)).ravel())),
                    shape=(3 * len(nodes), 3 * len(nodes)))
  xyz = lo + nodes * H
  xy_m = xyz[:, :2] - np.array([dx, 0.0])          # in the motor's frame, which moves with the arm
  u_of = xy_m @ RA.U
  v_of = xy_m @ RA.V
  if with_plate:                                   # round the cup screw and slot 1's screw, on the plate's thickness
    fixed = np.zeros(len(xyz), dtype=bool)
    for sx, sz in ((RA.CUP_X, RA.CUP_Z), (RA.CUP_X - 97.0, RA.CUP_Z + 40.0)):
      fixed |= ((xyz[:, 0] - sx) ** 2 + (xyz[:, 2] - sz) ** 2 <= WASHER_R ** 2) & (xyz[:, 1] >= RA.COVER_Y - RA.PLATE_T - 0.5)
  else:
    fixed = xyz[:, 0] <= RA.RECEIVER_MOUTH + 1e-6  # the bar inside the receiver
  load = (u_of >= RA.PLATE_U[0] - H) & (u_of <= RA.PLATE_U[1] + H) & (np.abs(v_of) <= RA.H) & \
         (np.abs(xyz[:, 2] - RA.Z_AXIS - dz) <= RA.H)  # the carrier's plate behind the motor's face
  li = np.where(load)[0]
  c = xyz[li].mean(axis=0)
  r = xyz[li] - c
  inertia = (r ** 2).sum() * np.eye(3) - r.T @ r
  free = np.ones(K.shape[0], dtype=bool)
  free[(np.where(fixed)[0][:, None] * 3 + np.arange(3)).ravel()] = False
  fd = np.where(free)[0]
  Kf = K[fd][:, fd].tocsr()
  dinv = 1.0 / Kf.diagonal()
  pre = spla.LinearOperator(Kf.shape, matvec=lambda x: dinv * x)
  P = np.array([R_PITCH * RA.U[0] + dx, R_PITCH * RA.U[1], RA.Z_AXIS + 16.0 + dz])
  Vv, Uv, zh = np.array([*RA.V, 0.0]), np.array([*RA.U, 0.0]), np.array([0.0, 0.0, 1.0])
  Ft = TORQUE / (R_PITCH / 1000.0)
  out = {}
  for name, sgn in (("pushing the wheel left", -1.0), ("pushing the wheel right", 1.0)):
    F = sgn * Ft * Vv - Ft * TAN_PA * zh             # on the gear
    om = np.linalg.solve(inertia, np.cross(P - c, F))
    fn = F / len(li) + np.cross(om, r)              # the motor's push shared over its face, as a rigid motor would
    f = np.zeros(K.shape[0])
    for k in range(3):
      f[li * 3 + k] = fn[:, k]
    x, info = spla.cg(Kf, f[fd], rtol=1e-9, maxiter=80000, M=pre)
    if info != 0:
      raise RuntimeError(f"the solver did not settle ({info})")
    u = np.zeros(K.shape[0])
    u[fd] = x
    ul = u.reshape(-1, 3)[li]
    A = np.zeros((3 * len(li), 6))                  # the motor's own movement: a rigid fit to its face
    for i, (rx, ry, rz) in enumerate(r):
      A[3 * i:3 * i + 3, :3] = np.eye(3)
      A[3 * i:3 * i + 3, 3:] = [[0, rz, -ry], [-rz, 0, rx], [ry, -rx, 0]]
    sol = np.linalg.lstsq(A, ul.ravel(), rcond=None)[0]
    d = sol[:3] + np.cross(sol[3:], P - c)
    out[name] = {"in": float(d @ zh), "rim": float(d @ Vv), "out from the wheel": float(d @ Uv),
                 "motor turned deg": float(np.degrees(np.linalg.norm(sol[3:])))}
  print(f"  {'with the frame plate' if with_plate else 'held in the receiver'}: {vox.sum()} cubes, {len(fd)} unknowns, "
        f"{time.time() - t0:.0f} s")
  return out


CASES = ((0.0, 0.0, "as drawn"), (RA.ARM_SLIDE, 0.0, "the arm slid 17.5 out"),
         (0.0, RA.DZ_DEEP, "the motor slid 12 up"), (RA.ARM_SLIDE, RA.DZ_DEEP, "both"))


def main() -> int:
  ok = True
  cases = CASES[:1] if "quick" in sys.argv[1:] else CASES
  k = GRIP_TEST / TORQUE
  for dx, dz, label in cases:
    print(f"{label} (the arm {dx:+.1f} across, the motor {dz:+.0f} along the column):")
    for with_plate in (False, True):
      for name, d in solve(with_plate, dx, dz).items():
        deeper, out_ = max(d["in"], 0.0), max(-d["in"], 0.0)
        good = deeper <= LIMIT_IN and out_ <= LIMIT_OUT
        ok = ok and good
        print(f"    {name}: the gear {d['in']:+.2f} mm along the column (+ deeper into the teeth), {d['rim']:+.2f} along "
              f"the rim, the motor turned {d['motor turned deg']:.2f} deg; in the grip test {k * d['in']:+.2f} mm  "
              f"{'pass' if good else 'FAIL'}")
  print("PASS" if ok else "FAIL")
  return 0 if ok else 1


if __name__ == "__main__":
  sys.exit(main())

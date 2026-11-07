mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2 && cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2/proto.py <<'EOF'
"""Prototype of the front lift lever's cam: QR-style cam on a pivot carried by the motor carrier, pressing the hinge
block's top. Carrier frame (y, z). Lever frame: pivot at origin, handle along +z."""
import math, sys
import numpy as np
from manifold3d import CrossSection

H = np.array([37.65, -40.0])     # hinge
HB_TOP = 50.65
SPRING_Z, SPRING_ARM = -4.0, 36.0
SPRING_RATE, SPRING_FREE, SPRING_LEN = 1.98, 28.5, 18.5
DROP, LIFT = 3.0, 8.0

def rot2(d):
  a = math.radians(d); return np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])

def spring_torque(th):
  f = SPRING_RATE * (SPRING_FREE - SPRING_LEN + SPRING_ARM * math.sin(math.radians(th)))
  return f * SPRING_ARM * math.cos(math.radians(th))

def pad(th):
  """pad point and normal (up) in the carrier frame with the carrier lifted th degrees"""
  c = H + rot2(th) @ (np.array([HB_TOP, 0.0]) - H)
  n = rot2(th) @ np.array([1.0, 0.0])
  return c, n

def k_of(V, th):
  c, n = pad(th); return float((V - c) @ n)

def make_cam(V, rho_n, phi_n, a_off, th_peak, th_up, seg=720):
  r_d = k_of(V, -DROP)
  e = k_of(V, th_peak) - rho_n
  nose_c = e * np.array([-math.cos(math.radians(phi_n)), -math.sin(math.radians(phi_n))])
  dwell = CrossSection.circle(r_d, seg)
  nose = CrossSection.circle(rho_n, seg).translate((float(nose_c[0]), float(nose_c[1])))
  hull = CrossSection.batch_hull([dwell, nose])
  # up face
  c, n = pad(th_up)
  f = rot2(a_off) @ (-n)
  h_up = k_of(V, th_up)
  # half plane q.f <= h_up : build a big square and cut
  big = 200
  # square on the far side of the line, removed
  ang = math.degrees(math.atan2(f[1], f[0]))
  sq = CrossSection.square((big, 2 * big)).translate((h_up, -big)).rotate(ang)
  cam = hull - sq
  return cam, dict(r_d=r_d, e=e, nose_c=nose_c, h_up=h_up)

def cam_pts(cam):
  return np.array([p for poly in cam.to_polygons() for p in poly])

def clearance(pts, V, alpha, th):
  pc = pts @ rot2(-alpha).T + V
  c, n = pad(th)
  return float(((pc - c) @ n).min())

def cam_lift(pts, V, alpha):
  lo, hi = -DROP - 2.0, LIFT + 8.0
  if clearance(pts, V, alpha, lo) >= 0: return lo
  for _ in range(50):
    mid = (lo + hi) / 2
    if clearance(pts, V, alpha, mid) >= 0: hi = mid
    else: lo = mid
  return hi

def table(pts, V, L, end, step=1.0):
  rows = []; prev = None
  for a in np.arange(0, end + 1e-9, step):
    th = max(0.0, cam_lift(pts, V, a))
    F = 0.0
    if prev is not None:
      F = spring_torque((th + prev[1]) / 2) * math.radians(th - prev[1]) / math.radians(a - prev[0]) / L
    rows.append((a, th, F)); prev = (a, th)
  return rows

if __name__ == "__main__":
  yv = float(sys.argv[1]) if len(sys.argv) > 1 else 59.8
  phi_n = float(sys.argv[2]) if len(sys.argv) > 2 else 70.0
  a_off = float(sys.argv[3]) if len(sys.argv) > 3 else 78.0
  rho_n = float(sys.argv[4]) if len(sys.argv) > 4 else 2.5
  th_peak = float(sys.argv[5]) if len(sys.argv) > 5 else 8.4
  L = 37.0
  V = np.array([yv, 0.0])
  cam, info = make_cam(V, rho_n, phi_n, a_off, th_peak, LIFT)
  print({k: (np.round(v, 3) if isinstance(v, np.ndarray) else round(v, 3)) for k, v in info.items()}, "gap at 0:", round(k_of(V, 0) - info['r_d'], 3))
  pts = cam_pts(cam)
  rows = table(pts, V, L, a_off + 10, 1.0)
  for a, th, F in rows:
    if a % 2 == 0 or a > a_off - 3:
      print(f"{a:5.1f} {th:6.3f} {F:6.2f}")
  print("extent: y", pts[:,0].min().round(2), pts[:,0].max().round(2), " z", pts[:,1].min().round(2), pts[:,1].max().round(2))
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2 && PYTHONPATH=/home/claude/pylib python3 proto.py
cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2/proto2.py <<'EOF'
import math, sys
import numpy as np
from manifold3d import CrossSection
sys.path.insert(0, '.')
from proto import H, HB_TOP, DROP, LIFT, rot2, spring_torque, pad, k_of, cam_pts, clearance, cam_lift

def make_cam(V, rho_n, a_peak, th_peak, a_off, th_up, w_far, heel_r=2.0, seg=720):
  r_d = k_of(V, -DROP)
  phi_n = a_peak + th_peak
  e = k_of(V, th_peak) - rho_n
  dirn = lambda b: np.array([-math.cos(math.radians(b)), -math.sin(math.radians(b))])   # b degrees from down toward the back
  nose_c = e * dirn(phi_n)
  f = dirn(a_off + th_up)                     # face normal, lever frame
  t = dirn(a_off + th_up + 90.0)              # along the face, towards the far (heel) side
  h_up = k_of(V, th_up)
  heel_c = h_up * f + w_far * t - heel_r * f * 1.0 + 0.0 * t
  shapes = [CrossSection.circle(r_d, seg), CrossSection.circle(rho_n, seg).translate(tuple(nose_c)),
            CrossSection.circle(heel_r, seg).translate(tuple(heel_c + heel_r * t))]
  hull = CrossSection.batch_hull(shapes)
  ang = math.degrees(math.atan2(f[1], f[0]))
  big = 200
  sq = CrossSection.square((big, 2 * big)).translate((h_up, -big)).rotate(ang)
  return hull - sq, dict(r_d=r_d, e=e, phi_n=phi_n, h_up=h_up, nose_c=nose_c, heel_c=heel_c)

def table(pts, V, L, end, step=0.5):
  rows = []; prev = None
  for a in np.arange(0, end + 1e-9, step):
    th = max(0.0, cam_lift(pts, V, a))
    F = 0.0
    if prev is not None:
      F = spring_torque((th + prev[1]) / 2) * math.radians(th - prev[1]) / math.radians(a - prev[0]) / L
    rows.append((a, th, F)); prev = (a, th)
  return rows

if __name__ == "__main__":
  yv, a_peak, th_peak, a_off, rho_n, w_far = [float(x) for x in sys.argv[1:7]]
  L = 37.0
  V = np.array([yv, 0.0])
  cam, info = make_cam(V, rho_n, a_peak, th_peak, a_off, LIFT, w_far)
  pts = cam_pts(cam)
  rows = table(pts, V, L, a_off + 8)
  start = next(a for a, th, F in rows if th > 0.02)
  peak = max(rows, key=lambda r: r[1])
  rest = min((r for r in rows if r[0] >= peak[0]), key=lambda r: r[1])
  fmax = max(r[2] for r in rows)
  back = [r for r in rows if peak[0] < r[0] <= rest[0]]
  fback = -min(r[2] for r in back) if back else 0
  after = [r for r in rows if r[0] > rest[0]]
  fstop = max(r[2] for r in after) if after else 0
  print(f"r_d {info['r_d']:.2f} e {info['e']:.2f} phi_n {info['phi_n']:.1f} | lift starts {start} | peak {peak[0]} at {peak[1]:.2f} | rest {rest[0]} at {rest[1]:.2f} | max lift force {fmax:.2f} N | push back down {fback:.2f} N | stop {fstop:.2f} N")
  print("cam extent y", pts[:,0].min().round(2), pts[:,0].max().round(2), "z", pts[:,1].min().round(2), pts[:,1].max().round(2))
  if len(sys.argv) > 7:
    for r in rows:
      if r[0] % 2 == 0 or abs(r[0]-a_off) < 3: print(f"{r[0]:5.1f} {r[1]:6.3f} {r[2]:6.2f}")
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2 && for args in "59.8 62 9.0 72 2.5 4" "59.8 62 9.0 74 2.5 4" "59.8 62 9.5 74 2.5 4" "59.8 60 9.5 72 3 4" "59.8 64 9.5 76 2.5 5"; do PYTHONPATH=/home/claude/pylib python3 proto2.py $args; done
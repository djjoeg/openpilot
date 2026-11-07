cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > platecalc.py <<'EOF'
import sys, math, itertools
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import params as P
import faceparts as FP
import faceassembly as FA
import mountparts as MP
t = FP.FaceTeeth(P.WHEEL_OD, P.GRIP, P.RIGHT_SPOKE_DEG)
fit = FA.solve_face(t, P.COVER_BOTTOM)
print("j1", fit.j1, "j2", fit.j2)
y_top = FP.plate_top_y()
front = P.PLATE_FRONT_Z
x0, x1 = FP.PL_X
pads_x = (x0 + 1, x1 - 1)
pads_z = (front - FP.PL_LEN + 2, front - 2)
Pg = np.array([FP.R_F, 0.0, t.z_p])          # the pitch point at 3 o'clock
Pm = np.array([FP.R_FACE + 20.0, 0.0, t.z_axis])   # about the motor's middle
ft = 33.0; dash = 55.0; wt = 16.0; spring_dash = 42.0
cases = {"push up": [(Pg, np.array([0, ft, -dash]))], "push down": [(Pg, np.array([0, -ft, -dash]))],
         "bump": [(Pm, np.array([0, -wt, 0])), (Pg, np.array([0, 0, -spring_dash]))]}
C = np.array([(x0 + x1) / 2, y_top, front - FP.PL_LEN / 2])
def pivots():
  out = []
  for xp in pads_x:
    out.append((np.array([xp, y_top, 0.0]), np.array([0, 0, 1.0])))
  for zp in pads_z:
    out.append((np.array([0.0, y_top, zp]), np.array([1.0, 0, 0])))
  return out
def tensions(screws, loads):
  T = np.zeros(len(screws))
  for A, u in pivots():
    # orient u so that the plate's middle moves away from the cover (-y)
    if np.dot(np.cross(u, C - A), np.array([0, -1.0, 0])) < 0:
      u = -u
    M = sum(np.dot(np.cross(p - A, f), u) for p, f in loads)
    if M <= 0:
      continue
    d = np.array([np.linalg.norm(np.cross(u, s - A)) for s in screws])   # distance from the line (u unit)
    # only screws on the plate's side of the pivot matter; all are
    T += M * d / np.sum(d ** 2)
  return T
for xs in ((40, 40), (14, 14), (14, 40)):
  for zs in ((40, 120), (29, 69), (29, 139), (99, 139)):
    screws = [np.array([xs[0], y_top, front - zs[0]]), np.array([xs[1], y_top, front - zs[1]])]
    worst = max(max(tensions(screws, L)) for L in cases.values())
    print(f"screws x {xs} z {zs}: worst {worst:6.1f} N  factor {250 / worst:.2f}")
EOF
PYTHONPATH=/home/claude/pylib python3 platecalc.py
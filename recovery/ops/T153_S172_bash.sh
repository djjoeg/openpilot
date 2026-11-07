cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && cat > levplot.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
import popparts as PP, slideparts as SP, slideassembly as SA
from manifold3d import Manifold
A = SA.SlideAssembly(110.0)
ring = A.teeth_ring()
# wheel -> carrier frame for this mount
Rm = PP.rot_z(A.mount); R = Rm @ PP.R_POP; T = Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P])
Rt = R.T; off = -Rt @ T
ring_c = ring.transform([[float(Rt[i,0]), float(Rt[i,1]), float(Rt[i,2]), float(off[i])] for i in range(3)])
blk = SP.slide_block()
car = SP.slide_carrier()
fig, axs = plt.subplots(1, 3, figsize=(21, 7))
def sl(m, x):
  return [np.asarray(p) for p in m.transform([[0,1,0,0],[0,0,1,0],[1,0,0,0]]).slice(x).to_polygons() if len(p) >= 3]
for ax, x in zip(axs, (-50.0, -47.0, -44.0)):
  for p in sl(ring_c, x): ax.add_patch(Polygon(p, fc="#999", ec="#555", alpha=0.4))
  for p in sl(blk, x): ax.add_patch(Polygon(p, fc="#e80", ec="#a50", alpha=0.3))
  for p in sl(car, x): ax.add_patch(Polygon(p, fc="#36c", ec="#036", alpha=0.2))
  for d, c in ((0, "#d00"), (10, "#f60"), (25, "#a0a"), (40, "#06a"), (60, "#0a6"), (85, "#333")):
    st = SP.cam_state(float(d), 0.0)
    lev = SP.slide_lever(SP.SWING_SIGN * d).translate((0, st["carrier_off"], 0))
    for p in sl(lev, x): ax.add_patch(Polygon(p, fill=False, ec=c, lw=1.2))
    ax.text(-40, 30 - d/3, f"{d} short", color=c)
  ax.set_xlim(-45, 60); ax.set_ylim(-40, 30); ax.set_aspect("equal"); ax.grid(alpha=0.3)
  ax.set_title(f"x_c = {x}"); ax.set_xlabel("y_c (to dash)"); ax.set_ylabel("z_c (out)")
plt.tight_layout()
plt.savefig("levplot.png", dpi=60)
print("ok")
EOF
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache
timeout 600 python3 levplot.py
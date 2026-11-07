cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/lever2d.py << 'EOF'
import sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mountparts as MP
cs = MP.lever_outline()
fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), dpi=110)
def draw(ax, polys, color, alpha=1.0):
  for poly in polys:
    p = np.array(poly)
    ax.fill(p[:, 1], p[:, 0], color=color, alpha=alpha, lw=0.5, ec="k")   # z right, y up
# lever frame
draw(axes[0], cs.to_polygons(), "#d55")
axes[0].set_aspect("equal"); axes[0].set_title("lift lever (lever frame: handle along -z)")
# in the hinge block at down / up, with the fin's top face
for ax, a, title in ((axes[1], 0.0, "down"), (axes[2], MP.A_OFF, "up")):
  b = MP.LEVER_ON + a
  R = MP.rot2(b)
  polys = [[tuple(R @ np.array(q) + np.array(MP.LEVER_PIVOT)) for q in poly] for poly in cs.to_polygons()]
  draw(ax, polys, "#d55")
  th = max(0.0, MP.cam_lift(a))
  c, n = MP.fin_plane(th)
  tdir = np.array([-n[1], n[0]])
  # fin top face segment, and the fin's sides
  hy, hz = MP.HINGE
  Rc = MP.rot2(-th)
  fin = [(MP.TOP_Y[1], MP.LEVER_PIVOT[1] - MP.FIN_LEN/2), (MP.FIN_TOP, MP.LEVER_PIVOT[1] - MP.FIN_LEN/2), (MP.FIN_TOP, MP.LEVER_PIVOT[1] + MP.FIN_LEN/2), (MP.TOP_Y[1], MP.LEVER_PIVOT[1] + MP.FIN_LEN/2)]
  fin = [tuple(Rc @ (np.array(p) - np.array([hy, hz])) + np.array([hy, hz])) for p in fin]
  draw(ax, [fin], "#58c", 0.8)
  ax.axhline(MP.HB_BOTTOM, color="g", lw=0.8); ax.axhline(MP.HB_TOP, color="g", lw=0.8)
  ax.plot([MP.LEVER_PIVOT[1]], [MP.LEVER_PIVOT[0]], "k+")
  ax.set_aspect("equal"); ax.set_title(f"lever {title}: carrier lift {th:.2f} deg")
  ax.set_xlim(-110, -35); ax.set_ylim(25, 85)
plt.tight_layout(); plt.savefig("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/lever2d.png")
pts = np.array(MP.cam_points(5.0))
print(np.round(np.c_[np.degrees(np.arctan2(pts[:,0], pts[:,1])), np.hypot(pts[:,0], pts[:,1])], 2))
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/lever2d.py
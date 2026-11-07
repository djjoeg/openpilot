cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/render3d.py <<'EOF'
"""3D pictures of the side-slide mount with part names: motor in, slid in; and the printed parts on their own."""
import math, sys, os
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import render as R
import sideparts as S
import sideassembly as SA
import popparts as PP
import faceparts as FP
from cadlib import revolve, on_bed

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
parts = SA.build_parts()
A = SA.SideAssembly(parts)
t = A.t
grip_pts = [(t.rr + (PP.GRIP_P / 2) * math.cos(a), (PP.GRIP_P / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 36, endpoint=False)]
grip = revolve(grip_pts, S.MOUNT_DEG - 50, S.MOUNT_DEG + 50, step_deg=1.5)
teeth = A.teeth(0.0)
C = {"grip": (0.22, 0.22, 0.24), "teeth": (0.80, 0.80, 0.78), "motor": (0.36, 0.42, 0.50), "bracket": (0.25, 0.50, 0.82),
     "gear": (0.90, 0.58, 0.18), "plate": (0.47, 0.66, 0.35), "rail": (0.72, 0.72, 0.76), "block": (0.50, 0.50, 0.55),
     "plunger": (0.82, 0.28, 0.28), "switch": (0.15, 0.15, 0.15), "spring": (0.80, 0.72, 0.25)}


def scene(s):
  mv, fx = A.movers(s), A.fixed(s)
  W = A.W
  sp = S.spring_parts(s)
  return [(grip, C["grip"]), (teeth, C["teeth"]),
          (W(mv["motor, board and plugs"]), C["motor"]), (W(mv["motor bracket"]), C["bracket"]), (W(mv["gear"]), C["gear"]),
          (W(mv["block"]), C["block"]), (W(parts["plate"]), C["plate"]), (W(parts["rail"]), C["rail"]),
          (W(fx["plunger and nut"] + fx["plunger's knob"] + fx["plunger's pin"]), C["plunger"]),
          (W(fx["switch"] + fx["switch's lever and roller"]), C["switch"]),
          (W(fx["spring's coil and spool"] + sp["strip"]), C["spring"])]


def projector(parts_list, rot, size, margin=0.06):
  w, h = size
  pts = np.concatenate([np.asarray(m.to_mesh().vert_properties)[:, :3] @ rot.T for m, _ in parts_list])
  lo, hi = pts.min(axis=0), pts.max(axis=0)
  scale = min(w * (1 - 2 * margin) / (hi[0] - lo[0]), h * (1 - 2 * margin) / (hi[1] - lo[1]))
  cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
  def f(p):
    q = np.asarray(p, float) @ rot.T
    return ((q[0] - cx) * scale + w / 2, h / 2 - (q[1] - cy) * scale)
  return f


a = math.radians(S.MOUNT_DEG)
radial = np.array([math.cos(a), math.sin(a), 0.0])
tang4 = np.array([-math.sin(a), math.cos(a), 0.0])     # towards 4 o'clock
zdir = np.array([0.0, 0.0, 1.0])
rot = R.look(-0.95 * zdir + 0.45 * tang4 - 0.30 * radial, [0, 1, 0])
size = (1100, 900)
W = A.W
labels_in = [
  ("steering wheel", W.__self__.W if False else None),
]
def cpt(x, y, z):
  return S.to_wheel(__import__("manifold3d").Manifold.cube((0.01, 0.01, 0.01)).translate((x, y, z))).bounding_box()[:3]
anchors = {
  "steering wheel (the round part you hold)": tuple((PP.WHEEL_OD_P / 2 - 8) * np.array([math.cos(a + 0.55), math.sin(a + 0.55), 0.0]) + np.array([0, 0, -10.0])),
  "teeth piece": tuple((t.rr + 10) * np.array([math.cos(a - 0.30), math.sin(a - 0.30), 0.0]) + np.array([0, 0, -40.0])),
  "gear (inside the finger guard)": cpt(0.0, 22.0, 14.0),
  "motor bracket": cpt(-27.0, 0.0, -30.0),
  "motor": cpt(0.0, 21.2, -20.0),
  "board cover": cpt(10.0, 25.0, -45.0),
  "mounting plate (fixed)": cpt(S.X_PL[0], 0.0, -60.0),
  "rail and block": cpt(S.X_RAIL_TOP, S.Y_RAIL, -70.0),
  "latch knob: pull to let go": cpt(S.X_COLLAR - 30.0, S.PIN_Y, S.PIN_Z),
  "power switch": cpt(-27.0, 34.0, 16.0),
  "spring": cpt(S.SPOOL_X, 45.4, S.SPOOL_Z),
}
offsets = {
  "steering wheel (the round part you hold)": (-60, -90), "teeth piece": (-40, 110), "gear (inside the finger guard)": (-160, 60),
  "motor bracket": (120, 90), "motor": (150, -40), "board cover": (150, -10), "mounting plate (fixed)": (-150, -40),
  "rail and block": (-170, 40), "latch knob: pull to let go": (-170, -60), "power switch": (-120, -100), "spring": (120, -60),
}

fig, axes = plt.subplots(1, 2, figsize=(2 * size[0] / 110, size[1] / 110 + 0.6), dpi=110)
for ax, s, title in ((axes[0], 0.0, "motor in: the latch holds it, the gear in the teeth"),
                     (axes[1], S.STROKE, f"latch let go: the spring has pulled it {S.STROKE:.0f} mm in")):
  sc = scene(s)
  img = R.render(sc, rot, size=size)
  ax.imshow(img)
  ax.set_axis_off()
  ax.set_title(title, fontsize=11)
  if s == 0.0:
    f = projector(sc, rot, size)
    for name, p in anchors.items():
      x, y = f(p)
      dx, dy = offsets[name]
      ax.annotate(name, xy=(x, y), xytext=(x + dx, y + dy), fontsize=9, ha="center", va="center",
                  bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#888", lw=0.6, alpha=0.9),
                  arrowprops=dict(arrowstyle="-", lw=0.8, color="#333"))
fig.suptitle("From behind the steering wheel (the dash side), a little from 4 o'clock", fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "side-slide-3d.png"))
print("3d ok", flush=True)

# the printed parts, each as it sits on the print bed
pr = [("motor bracket", parts["bracket"], (180, 0, 0)), ("mounting plate", parts["plate"], (0, -90, 0)),
      ("gear", parts["gear"], (0, 0, 0)), ("spool", parts["spool"], (90, 0, 0)), ("board cover", S.side_board_cap(), (0, 0, 0))]
view = R.view_matrix(-60, 35)
R.save(os.path.join(OUT, "side-slide-parts.png"), [([(on_bed(m, r), (.55, .7, .9))], view) for _, m, r in pr],
       titles=[f"{n}" for n, _, _ in pr], suptitle="The new printed parts, each as it sits on the print bed (the teeth piece is the slide mount's, with pointed tooth ends)",
       size=(700, 600), cols=3)
print("parts ok")
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 1800 python3 render3d.py . 2>&1 | tail -3
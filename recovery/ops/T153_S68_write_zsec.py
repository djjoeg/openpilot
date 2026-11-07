"""Cross-sections across the column (steering wheel frame x, y) at several z: the car (D), the motor and its board with
the mount at MOUNT, engaged and slid back, and the old column plate moved with the cover: where the slide's fixed block
can go."""
import math
import sys

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

import carscene as CS  # noqa: E402
import popassembly as PA  # noqa: E402
import popparts as PP  # noqa: E402
import study90 as S  # noqa: E402

MOUNT = float(sys.argv[1]) if len(sys.argv) > 1 else -70.0
D = float(sys.argv[2]) if len(sys.argv) > 2 else 106.0
zs = [float(v) for v in (sys.argv[3].split(",") if len(sys.argv) > 3 else ["-42", "-60", "-78", "-90", "-102", "-114"])]
stroke = 6.0
sc, car = S.car_for(D)
fixed = S.fixed_car(MOUNT)
car.update(fixed)
car["old plate (moved)"] = sc.moved(PP.pop_column_plate())
parts = S.radial_parts(MOUNT, "car")
on = {k: S.place(v, MOUNT) for k, v in parts.items()}
off = {k: S.place(v, MOUNT, (0.0, stroke, 0.0)) for k, v in parts.items()}
colors = {"column cover": "#888", "back cover (swept)": "#c3c", "dash face": "#555", "wiper stalk": "#2a8",
          "adjustment tab, its swing, fingers": "#3a3", "spokes' sweep": "#fc8", "teeth (swept)": "#777",
          "fingers on the grip": "#fdd", "old plate (moved)": "#a52", "key bulge and bezel": "#d33", "the key in it": "#d33",
          "room to turn the key": "#f99"}


def polys(cs):
  return [np.asarray(p) for p in cs.to_polygons() if len(p) >= 3]


n = len(zs)
cols = 3
rows = (n + cols - 1) // cols
fig, axs = plt.subplots(rows, cols, figsize=(6.5 * cols, 6.5 * rows))
axs = np.atleast_1d(axs).ravel()
for ax, z in zip(axs, zs):
  for name, m in car.items():
    for p in polys(m.slice(z)):
      ax.add_patch(Polygon(p, closed=True, fc=colors.get(name, "#999"), ec=colors.get(name, "#999"), alpha=0.25, lw=0.6))
  for name, m in on.items():
    for p in polys(m.slice(z)):
      ax.add_patch(Polygon(p, closed=True, fill=False, ec="#036", lw=1.2))
  for name, m in off.items():
    for p in polys(m.slice(z)):
      ax.add_patch(Polygon(p, closed=True, fill=False, ec="#39f", lw=0.8, ls="--"))
  for r in (100, 125, 150, 175):
    th = np.linspace(0, 2 * np.pi, 300)
    ax.plot(r * np.cos(th), r * np.sin(th), color="k", lw=0.3, alpha=0.4)
  a = math.radians(MOUNT)
  ax.plot([0, 190 * math.cos(a)], [0, 190 * math.sin(a)], "k:", lw=0.6)
  ax.set_xlim(-80, 140)
  ax.set_ylim(-200, 20)
  ax.set_aspect("equal")
  ax.grid(alpha=0.3)
  ax.set_title(f"z = {z:+.0f}  (D {D:.0f}, mount {MOUNT:+.0f})")
handles = [plt.Rectangle((0, 0), 1, 1, fc=c, alpha=0.4) for c in colors.values()]
fig.legend(handles, list(colors), loc="lower center", ncol=6, fontsize=8)
plt.tight_layout(rect=(0, 0.05, 1, 1))
out = f"/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap/zsec_{int(-MOUNT)}_{int(D)}.png"
plt.savefig(out, dpi=60)
print(out)

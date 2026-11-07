"""Sections of the draft slide mount with the car: mode w = across the column at wheel z values; mode y = carrier-frame
planes y_c = const; mode x = carrier-frame planes x_c = const."""
import math
import sys

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

import popparts as PP  # noqa: E402
import study90 as S  # noqa: E402
import sp  # noqa: E402

mode = sys.argv[1]
D = float(sys.argv[2])
cuts = [float(v) for v in sys.argv[3].split(",")]
tag = sys.argv[4] if len(sys.argv) > 4 else ""
PP.MOUNT_DEG = sp.MOUNT
sc, car = S.car_for(D)
car.update(S.fixed_car(sp.MOUNT))
car["old plate (moved)"] = sc.moved(PP.pop_column_plate())
mb = sp.motor_board()
moving = {"carrier": sp.carrier(), "rods": sp.rods(), "motor": mb["motor"], "board+cap": mb["board+cap"],
          "car plug": mb["car plug (to dash)"], "motor plug": mb["motor plug (4 o'clock)"], "own plug": mb["motor's own plug"],
          "gear": mb["gear"]}
fixed = {"block": sp.block()}
colors = {"column cover": "#888", "back cover (swept)": "#c3c", "dash face": "#555", "wiper stalk": "#2a8",
          "adjustment tab, its swing, fingers": "#3a3", "spokes' sweep": "#fc8", "teeth (swept)": "#777",
          "fingers on the grip": "#fdd", "old plate (moved)": "#a52", "key bulge and bezel": "#d33", "the key in it": "#d33",
          "room to turn the key": "#f99"}


def polys(cs):
  return [np.asarray(p) for p in cs.to_polygons() if len(p) >= 3]


if mode == "w":
  def cut(m, c, frame):
    if frame == "c":
      m = S.place(m, sp.MOUNT)
    return m.slice(c)
  xl, yl, xlab, ylab = (-80, 140), (-200, 0), "x (driver's right)", "y (up)"
elif mode == "y":
  def cut(m, c, frame):
    if frame == "w":
      m = PP.wheel_to_carrier(m)
    return m.transform([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]]).slice(c)
  xl, yl, xlab, ylab = (-80, 60), (-90, 45), "x_c (+ towards the tab's side)", "z_c (out from the column)"
else:
  def cut(m, c, frame):
    if frame == "w":
      m = PP.wheel_to_carrier(m)
    return m.transform([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]).slice(c)
  xl, yl, xlab, ylab = (-30, 110), (-90, 45), "y_c (towards the dash)", "z_c (out from the column)"

n = len(cuts)
cols = 3
rows = (n + cols - 1) // cols
fig, axs = plt.subplots(rows, cols, figsize=(6.5 * cols, 6.0 * rows))
axs = np.atleast_1d(axs).ravel()
for ax, c in zip(axs, cuts):
  for name, m in car.items():
    for p in polys(cut(m, c, "w")):
      ax.add_patch(Polygon(p, closed=True, fc=colors.get(name, "#999"), ec=colors.get(name, "#999"), alpha=0.25, lw=0.6))
  for name, m in fixed.items():
    for p in polys(cut(m, c, "c")):
      ax.add_patch(Polygon(p, closed=True, fc="#e80", ec="#a50", alpha=0.35, lw=1.0))
  for name, m in moving.items():
    for p in polys(cut(m, c, "c")):
      ax.add_patch(Polygon(p, closed=True, fill=False, ec="#036", lw=1.1))
    for p in polys(cut(m.translate((0.0, sp.STROKE, 0.0)), c, "c")):
      ax.add_patch(Polygon(p, closed=True, fill=False, ec="#39f", lw=0.7, ls="--"))
  ax.set_xlim(*xl)
  ax.set_ylim(*yl)
  ax.set_aspect("equal")
  ax.grid(alpha=0.3)
  ax.set_xlabel(xlab)
  ax.set_ylabel(ylab)
  ax.set_title(f"{mode} = {c:+.0f}  (D {D:.0f})")
handles = [plt.Rectangle((0, 0), 1, 1, fc=c, alpha=0.4) for c in colors.values()]
fig.legend(handles, list(colors), loc="lower center", ncol=6, fontsize=8)
plt.tight_layout(rect=(0, 0.05, 1, 1))
out = f"/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide/v_{mode}_{int(D)}{tag}.png"
plt.savefig(out, dpi=60)
print(out)

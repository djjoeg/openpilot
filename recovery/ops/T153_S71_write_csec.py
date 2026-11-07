"""Carrier-frame cross-sections at the mount MOUNT, for key depth D: slices across the slide (planes y_c = const,
drawn x_c across, z_c up = out from the column) and along it on the right side (planes x_c = const, drawn y_c across
towards the dash, z_c up). The car parts are brought into the carrier frame; the motor, its board and plugs engaged
(solid) and slid back (dashed)."""
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
import popparts as PP  # noqa: E402
import study90 as S  # noqa: E402

MOUNT = float(sys.argv[1]) if len(sys.argv) > 1 else -70.0
D = float(sys.argv[2]) if len(sys.argv) > 2 else 106.0
mode = sys.argv[3] if len(sys.argv) > 3 else "y"
cuts = [float(v) for v in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
stroke = 6.0
PP.MOUNT_DEG = MOUNT
sc, car = S.car_for(D)
car.update(S.fixed_car(MOUNT))
car["old plate (moved)"] = sc.moved(PP.pop_column_plate())
carc = {k: PP.wheel_to_carrier(v) for k, v in car.items()}
parts = S.radial_parts(MOUNT, "car")
offp = {k: v.translate((0.0, stroke, 0.0)) for k, v in parts.items()}
colors = {"column cover": "#888", "back cover (swept)": "#c3c", "dash face": "#555", "wiper stalk": "#2a8",
          "adjustment tab, its swing, fingers": "#3a3", "spokes' sweep": "#fc8", "teeth (swept)": "#777",
          "fingers on the grip": "#fdd", "old plate (moved)": "#a52", "key bulge and bezel": "#d33", "the key in it": "#d33",
          "room to turn the key": "#f99"}


def polys(cs):
  return [np.asarray(p) for p in cs.to_polygons() if len(p) >= 3]


if mode == "y":       # planes y_c = c: draw (x_c, z_c)
  cuts = cuts or [-20.0, 0.0, 20.0, 30.0, 45.0, 60.0]
  to2 = lambda m, c: m.transform([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]]).slice(c)   # (x, z, y): slice at y
  xl, yl, xlab, ylab = (-90, 70), (-90, 40), "x_c (+ towards the tab's side)", "z_c (out from the column)"
else:                  # planes x_c = c: draw (y_c, z_c)
  cuts = cuts or [-24.0, -30.0, -36.0, -42.0, -50.0, 24.0]
  to2 = lambda m, c: m.transform([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]).slice(c)   # (y, z, x): slice at x
  xl, yl, xlab, ylab = (-40, 110), (-90, 40), "y_c (towards the dash)", "z_c (out from the column)"
n = len(cuts)
cols = 3
rows = (n + cols - 1) // cols
fig, axs = plt.subplots(rows, cols, figsize=(6.5 * cols, 5.8 * rows))
axs = np.atleast_1d(axs).ravel()
for ax, c in zip(axs, cuts):
  for name, m in carc.items():
    for p in polys(to2(m, c)):
      ax.add_patch(Polygon(p, closed=True, fc=colors.get(name, "#999"), ec=colors.get(name, "#999"), alpha=0.25, lw=0.6))
  for name, m in parts.items():
    for p in polys(to2(m, c)):
      ax.add_patch(Polygon(p, closed=True, fill=False, ec="#036", lw=1.2))
  for name, m in offp.items():
    for p in polys(to2(m, c)):
      ax.add_patch(Polygon(p, closed=True, fill=False, ec="#39f", lw=0.8, ls="--"))
  ax.set_xlim(*xl)
  ax.set_ylim(*yl)
  ax.set_aspect("equal")
  ax.grid(alpha=0.3)
  ax.set_xlabel(xlab)
  ax.set_ylabel(ylab)
  ax.set_title(f"{'y_c' if mode == 'y' else 'x_c'} = {c:+.0f}  (D {D:.0f}, mount {MOUNT:+.0f})")
handles = [plt.Rectangle((0, 0), 1, 1, fc=c, alpha=0.4) for c in colors.values()]
fig.legend(handles, list(colors), loc="lower center", ncol=6, fontsize=8)
plt.tight_layout(rect=(0, 0.05, 1, 1))
out = f"/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap/csec_{mode}_{int(-MOUNT)}_{int(D)}.png"
plt.savefig(out, dpi=60)
print(out)

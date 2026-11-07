"""Carrier-frame sections of the slide mount's parts (no car): x = const planes (y across, z up) and y = const planes."""
import sys

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

import popparts as PP  # noqa: E402
import slideparts as S  # noqa: E402

mode = sys.argv[1]
cuts = [float(v) for v in sys.argv[2].split(",")]
state = sys.argv[3] if len(sys.argv) > 3 else "on"
dy = 0.0 if state == "on" else S.STROKE
mb = S.motor_board()
moving = {"carrier": S.slide_carrier(), "motor": mb["motor"], "board+cap": mb["board+cap"], "gear": PP.pop_motor_gear(),
          "rods": S.rods(), "collars": S.collars(), "car plug": mb["car plug"], "motor plug": mb["motor plug"],
          "own plug": mb["motor's own plug"]}
lever = S.slide_lever(0.0 if state == "on" else S.SWING_SIGN * S.LEVER_SWING)
fixed = {"block": S.slide_block(), "pusher": S.pusher().translate((0.0, S.PUSH_TRAVEL_ON if state == "on" else 0.0, 0.0)),
         "plug": S.plug(), "switch": S.switch_body(), "bearings": S.bearings(), "release springs": S.release_springs(dy)}
col = {"carrier": "#36c", "motor": "#555", "board+cap": "#2a2", "gear": "#a52", "rods": "#000", "collars": "#900",
       "block": "#e80", "pusher": "#c0c", "plug": "#c0c", "switch": "#0aa", "bearings": "#888", "release springs": "#f55",
       "lever": "#d00", "car plug": "#080", "motor plug": "#080", "own plug": "#080"}


def to2(m, c):
  if mode == "x":
    return m.transform([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]).slice(c)
  return m.transform([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]]).slice(c)


n = len(cuts)
cols = 3
rows = (n + cols - 1) // cols
fig, axs = plt.subplots(rows, cols, figsize=(6.5 * cols, 6.0 * rows))
axs = np.atleast_1d(axs).ravel()
items = [(k, v.translate((0.0, dy, 0.0))) for k, v in moving.items()] + [("lever", lever.translate((0.0, dy, 0.0)))] + \
  list(fixed.items())
for ax, c in zip(axs, cuts):
  for name, m in items:
    for p in to2(m, c).to_polygons():
      p = np.asarray(p)
      if len(p) >= 3:
        ax.add_patch(Polygon(p, closed=True, fc=col[name], ec=col[name], alpha=0.3, lw=0.8))
  if mode == "x":
    ax.set_xlim(-30, 110)
    ax.set_ylim(-60, 40)
    ax.set_xlabel("y (towards the dash)")
  else:
    ax.set_xlim(-65, 35)
    ax.set_ylim(-60, 40)
    ax.set_xlabel("x (+ towards 6 o'clock)")
  ax.set_ylabel("z (out from the column)")
  ax.set_aspect("equal")
  ax.grid(alpha=0.3)
  ax.set_title(f"{mode} = {c:+.0f} ({state})")
handles = [plt.Rectangle((0, 0), 1, 1, fc=c, alpha=0.4) for c in col.values()]
fig.legend(handles, list(col), loc="lower center", ncol=8, fontsize=8)
plt.tight_layout(rect=(0, 0.04, 1, 1))
out = f"/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide/pv_{mode}_{state}.png"
plt.savefig(out, dpi=60)
print(out)

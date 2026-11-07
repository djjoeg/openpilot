cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/drawing.py <<'EOF'
"""Two plain drawings of the side-slide mount, made from the CAD solids: from behind the steering wheel (the motor at
5:20 turned to lie flat on the page) and a cut along the motor's shaft. Facts only: our parts and the steering wheel's
measurements."""
import math, sys, os
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Wedge, FancyArrowPatch
import sideparts as S
import sideassembly as SA
import popparts as PP
import faceparts as FP

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
parts = SA.build_parts()
A = SA.SideAssembly(parts)
t = A.t
R_IN, R_OUT, R_MID = PP.WHEEL_OD_P / 2 - PP.GRIP_P, PP.WHEEL_OD_P / 2, t.rr
BACK = -PP.GRIP_P / 2          # the back of the steering wheel's round part (z)
F = PP.R_FACE_P
ZA = PP.Z_AXIS_P

TOP = [[0, 0, 1, 0], [-1, 0, 0, 0], [0, -1, 0, 0]]      # carrier -> (z_c, -x_c, -y_c): look along the column from behind
CUT = [[0, 0, 1, 0], [0, -1, 0, 0], [1, 0, 0, 0]]       # carrier -> (z_c, -y_c, x_c): slice at x_c = 0


def polys_top(m):
  return [np.array(p) for p in m.transform(TOP).project().to_polygons()]


def polys_cut(m, x=0.0):
  return [np.array(p) for p in m.transform(CUT).slice(x).to_polygons()]


def draw(ax, polys, fc, ec, ls="-", alpha=1.0, lw=1.0, z=2, hatch=None, transform_v=lambda v: v):
  for p in polys:
    if len(p) < 3:
      continue
    q = np.c_[F + p[:, 0], transform_v(p[:, 1])]
    ax.add_patch(Polygon(q, closed=True, fc=fc if ls == "-" else "none", ec=ec, lw=lw, ls=ls, alpha=alpha, zorder=z, hatch=hatch))


C = {"wheel": "#2b2b2e", "teeth": "#c9ccd1", "motor": "#5b6b7d", "cap": "#8064c8", "bracket": "#3f7fd0", "gear": "#e0962b",
     "plate": "#78a85a", "rail": "#9aa0a8", "block": "#6d7179", "plunger": "#d04a4a", "switch": "#333333", "spring": "#c8b040"}
mv_in, mv_out = A.movers(0.0), A.movers(S.STROKE)
fx = A.fixed(0.0)
sp_in, sp_out = S.spring_parts(0.0), S.spring_parts(S.STROKE)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(17, 8.6), gridspec_kw={"width_ratios": [1.05, 1.0]})

# ---------- left: from behind the steering wheel ----------
ax = a1
ang = np.radians(np.linspace(-40, 40, 160))
def band(r0, r1, a0, a1):
  a = np.radians(np.linspace(a0, a1, 120))
  return np.r_[np.c_[r0 * np.cos(a), r0 * np.sin(a)], np.c_[r1 * np.cos(a[::-1]), r1 * np.sin(a[::-1])]]
ax.add_patch(Polygon(band(R_IN, R_OUT, -40, 40), closed=True, fc=C["wheel"], ec=C["wheel"], alpha=0.85, zorder=1))
ax.add_patch(Polygon(band(t.w_in, t.w_out, -t.half, t.half), closed=True, fc=C["teeth"], ec="#777", alpha=0.55, zorder=1.5))
ax.add_patch(Polygon(band(FP.FACE_BAND[0], FP.FACE_BAND[1], -t.teeth_half, t.teeth_half), closed=True, fc="none", ec="#777",
                     hatch="////", lw=0.6, zorder=1.6))
# fixed parts (light), then the moving ones: motor in solid, slid in dashed
for m, c in ((parts["plate"], C["plate"]), (parts["rail"], C["rail"]), (fx["plunger and nut"] + fx["plunger's knob"], C["plunger"]),
             (fx["switch"], C["switch"]), (fx["spring's coil and spool"], C["spring"])):
  draw(ax, polys_top(m), c, c, alpha=0.55, z=3)
draw(ax, polys_top(sp_in["strip"]), C["spring"], C["spring"], alpha=0.9, z=3.5)
for mv, ls in ((mv_in, "-"), (mv_out, "--")):
  for name, c in (("block", C["block"]), ("motor bracket", C["bracket"]), ("motor, board and plugs", C["motor"]), ("gear", C["gear"])):
    draw(ax, polys_top(mv[name]), c, c, ls=ls, alpha=0.95 if ls == "-" else 1.0, lw=1.0 if ls == "-" else 1.4, z=4 if ls == "-" else 5)
ax.annotate("", xy=(F - 50.5 - S.STROKE, -36), xytext=(F - 50.5, -36), arrowprops=dict(arrowstyle="->", lw=2.2, color="#c0392b"), zorder=8)
ax.text(F - 50.5 - S.STROKE / 2, -41.5, f"the spring pulls it in {S.STROKE:.0f} mm", ha="center", va="top", color="#c0392b", fontsize=10)
lab = dict(fontsize=9, color="#222", zorder=9)
ax.text(R_MID + 2, 60, "steering wheel\n(the round part\nyou hold)", ha="center", va="bottom", **lab)
ax.text(t.w_out + 2, -48, "teeth piece", ha="left", va="center", rotation=90, **lab)
ax.text(F + 14, -24, "gear\n(no roller now)", ha="center", va="top", **lab)
ax.text(F - 20, 0, "motor", ha="center", va="center", color="white", fontsize=9, zorder=9)
ax.text(F - 45, 0, "board\ncover", ha="center", va="center", color="white", fontsize=8, zorder=9)
ax.text(F - 75, 48, "mounting plate\n(fixed: the rail on it)", ha="center", va="bottom", **lab)
ax.text(F - 15, 76, "latch knob:\npull it to let go", ha="center", va="bottom", color=C["plunger"], fontsize=9, zorder=9)
ax.text(F + 13, 38, "power\nswitch", ha="center", va="bottom", **lab)
ax.text(F - 100, 13, "spring", ha="center", va="bottom", **lab)
ax.set_xlim(225, 30)
ax.set_ylim(-62, 92)
ax.set_aspect("equal")
ax.grid(alpha=0.2)
ax.set_xlabel("mm from the middle of the steering wheel, along the motor's shaft")
ax.set_ylabel("towards 4 o'clock  (mm)  towards 6 o'clock", fontsize=9)
ax.set_title("From behind the steering wheel (the dash side), the motor at 5:20\nturned to lie flat on the page", fontsize=11)

# ---------- right: cut along the shaft ----------
ax = a2
ax.add_patch(Circle((R_MID, 0.0), PP.GRIP_P / 2, fc=C["wheel"], ec=C["wheel"], alpha=0.85, zorder=1))
ax.add_patch(Polygon(np.array(t.profile()), closed=True, fc=C["teeth"], ec="#555", alpha=0.6, lw=0.8, zorder=1.5))
v = lambda y: y + ZA * 0 - 0.0
for mv, ls in ((mv_in, "-"), (mv_out, "--")):
  for name, c in (("motor bracket", C["bracket"]), ("motor, board and plugs", C["motor"]), ("gear", C["gear"])):
    draw(ax, polys_cut(mv[name]), c, c, ls=ls, alpha=0.95 if ls == "-" else 1.0, lw=1.0 if ls == "-" else 1.4, z=4 if ls == "-" else 5,
         transform_v=lambda y: y + ZA)
# the room it needs, in from the steering wheel's inside edge
cap_in = F - 50.5
z_hi = ZA + 23.4 + 0.0
z_lo = ZA - 25.94
ax.axhspan(z_lo, z_hi, color="#f3d9a6", alpha=0.35, zorder=0)
ax.plot([R_IN, R_IN], [-128, 22], color="#333", lw=0.8, ls=":")
for x0, txt, y in ((cap_in, f"motor in: its back end {R_IN - cap_in:.0f} mm in from the inside edge", -106),
                   (cap_in - S.STROKE, f"slid in: {R_IN - cap_in + S.STROKE:.0f} mm in", -121)):
  ax.annotate("", xy=(x0, y + 5), xytext=(R_IN, y + 5), arrowprops=dict(arrowstyle="<->", lw=1, color="#333"))
  ax.text((x0 + R_IN) / 2 + 6, y, txt, ha="center", va="top", fontsize=9)
ax.text(R_IN - 1, 24, "inside edge of the\nsteering wheel", ha="left", va="bottom", fontsize=9)
f_hi, f_lo = BACK - z_hi, BACK - z_lo
ax.annotate("", xy=(212, z_hi), xytext=(212, BACK), arrowprops=dict(arrowstyle="<->", lw=1, color="#333"))
ax.annotate("", xy=(220, z_lo), xytext=(220, BACK), arrowprops=dict(arrowstyle="<->", lw=1, color="#333"))
ax.plot([206, 224], [BACK, BACK], color="#333", lw=0.8)
ax.text(210, (z_hi + BACK) / 2, f"{f_hi:.0f}", fontsize=9, va="center", ha="right")
ax.text(218, z_lo + 8, f"{f_lo:.0f}", fontsize=9, va="center", ha="right")
ax.text(52, ZA, "?\nis this\nclear, all the\nway round as the\nsteering wheel\nturns?", ha="center", va="center", fontsize=10, color="#8a5a00")
ax.text(226, 21, "towards you", fontsize=9, color="#555", ha="left")
ax.text(226, -125, "forward (towards the nose)", fontsize=9, color="#555", ha="left")
ax.text(R_MID, -27, "teeth piece", ha="center", fontsize=9)
ax.set_xlim(228, 35)
ax.set_ylim(-130, 30)
ax.set_aspect("equal")
ax.grid(alpha=0.2)
ax.set_xlabel("mm from the middle of the steering wheel")
ax.set_ylabel("mm from the middle of the round part you hold")
ax.set_title("Cut along the motor's shaft: the motor, its cover, bracket and gear\n(the mounting plate is beside it, towards 4 o'clock)", fontsize=11)
from matplotlib.patches import Rectangle
handles = [Rectangle((0, 0), 1, 1, fc=C[k], alpha=0.9) for k in ("motor", "bracket", "gear", "teeth", "plate", "plunger", "spring")] + \
          [Rectangle((0, 0), 1, 1, fc="none", ec="#333", ls="--")]
fig.legend(handles, ["motor and board cover", "motor bracket and finger guard", "gear", "teeth piece", "mounting plate and rail",
                     "latch", "spring", f"slid in {S.STROKE:.0f} mm"], loc="lower center", ncol=8, fontsize=9, frameon=False)
plt.tight_layout(rect=(0, 0.04, 1, 1))
plt.savefig(os.path.join(OUT, "side-slide-drawing.png"), dpi=110)
print("ok", f_hi, f_lo)
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 900 python3 drawing.py . 2>&1 | tail -3
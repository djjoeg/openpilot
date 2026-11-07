mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && cat > layout.py <<'EOF'
"""The sideways slide drawn from facts only: our parts (motor, board cover, plate and finger guard, gear and roller,
teeth piece) and your tape numbers (wheel 372 across, grip 35.4 thick). Nothing from my car estimates."""
import math, sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch
import numpy as np
import slideparts as SP, popparts as PP, mountparts as MP

S = 17.0                                   # slide in, to free the gear from the teeth (with its roller)
R_IN = PP.WHEEL_OD_P / 2 - PP.GRIP_P       # 150.6: the inside edge of the grip
R_MID = PP.WHEEL_OD_P / 2 - PP.GRIP_P / 2  # 168.3
F = PP.R_FACE_P                            # 153: the motor's front face
ZA = PP.Z_AXIS_P                           # -59.5: the shaft's depth (0 = middle of the grip, + towards you)
H = 42.3 / 2
t = SP.SlideTeeth()
prof = t.profile()

C_GRIP, C_TEETH, C_MOT, C_CAP, C_GEAR, C_GUARD = "#2b2b2b", "#9aa3ad", "#3d3f44", "#7d62c8", "#e0962b", "#3f7fd0"
fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 7.2), gridspec_kw={"width_ratios": [1, 1.15]})

def parts(ax, dx, ls, alpha, side):
  """side: True for the cut along the shaft (depth up/down), False for the view from the key hole (width up/down)."""
  def box(r0, r1, w0, w1, c, lab=None):
    ax.add_patch(Rectangle((r0 - dx, w0), r1 - r0, w1 - w0, fc=c if ls == "-" else "none", ec=c, lw=1.6, ls=ls,
                           alpha=alpha, label=lab))
  if side:
    z0, z1 = ZA - H, ZA + H
    box(F - 50.5, F - 40.0, z0 - 1.0, z1 + 1.0, C_CAP)          # board cover
    box(F - 40.0, F, z0, z1, C_MOT)                              # motor
    box(F, F + 5.0, ZA - 23.65, ZA + 20.0, C_GUARD)              # plate
    box(F + 5.0, F + MP.GUARD_FRONT, ZA - MP.GUARD_OUT, ZA - MP.GUARD_IN, C_GUARD)   # guard (the side away from the teeth)
    box(F + 7.0, F + 19.0, ZA - 17.76, ZA + 17.76, C_GEAR)       # gear's teeth
    box(F + 20.0, F + 24.0, ZA - 16.87, ZA + 16.87, C_GEAR)      # roller
  else:
    box(F - 50.5, F - 40.0, -23.5, 23.5, C_CAP)
    box(F - 40.0, F, -H, H, C_MOT)
    box(F, F + 5.0, -23.65, 23.65, C_GUARD)
    box(F + 5.0, F + MP.GUARD_FRONT, -MP.GUARD_OUT, MP.GUARD_OUT, C_GUARD)
    box(F + 7.0, F + 19.0, -17.76, 17.76, C_GEAR)
    box(F + 20.0, F + 24.0, -16.87, 16.87, C_GEAR)

# ----- left: from the key hole, looking back at the wheel (your sketch's view) -----
ax = a1
ang = np.radians(np.linspace(-32, 32, 200))
for r0, r1, c, a in ((R_IN, PP.WHEEL_OD_P / 2, C_GRIP, 0.85), (t.w_in, t.w_out, C_TEETH, 0.35)):
  pts = [(r0 * math.cos(q), r0 * math.sin(q)) for q in ang] + [(r1 * math.cos(q), r1 * math.sin(q)) for q in ang[::-1]]
  ax.add_patch(Polygon(pts, closed=True, fc=c, ec=c, alpha=a))
parts(ax, 0.0, "-", 0.9, False)
parts(ax, S, "--", 0.9, False)
ax.annotate("", xy=(F - 50.5 - S, 36), xytext=(F - 50.5, 36), arrowprops=dict(arrowstyle="->", lw=2, color="#c0392b"))
ax.text(F - 50.5 - S / 2, 39, f"springs pull it in {S:.0f} mm", ha="center", color="#c0392b", fontsize=10)
ax.text(R_MID, -44, "grip", ha="center", color="white", fontsize=10, rotation=90, va="center")
ax.text(t.w_out + 3, -34, "teeth piece\non its back", fontsize=9, color="#555")
ax.set_xlim(220, 55)
ax.set_ylim(-60, 60)
ax.set_aspect("equal")
ax.set_title("From the key hole, looking back at the wheel\n(the motor at 5:20 turned to lie flat on the page)", fontsize=11)
ax.set_xlabel("mm from the middle of the column (along the motor's shaft)")
ax.set_yticks([])
ax.grid(alpha=0.25)

# ----- right: cut along the motor's shaft -----
ax = a2
ax.add_patch(Circle((R_MID, 0.0), PP.GRIP_P / 2, fc=C_GRIP, ec=C_GRIP, alpha=0.85))
ax.add_patch(Polygon(prof, closed=True, fc=C_TEETH, ec="#555", alpha=0.45, lw=1))
parts(ax, 0.0, "-", 0.9, True)
parts(ax, S, "--", 0.9, True)
# where the motor sits (depth), and the unknown room inside
z_top, z_bot = ZA + H + 1.0, ZA - H - 1.0
ax.axhspan(z_bot, z_top, xmin=0, xmax=1, color="#f3d9a6", alpha=0.25, zorder=0)
ax.annotate("", xy=(F - 50.5 - S, ZA), xytext=(F - 50.5, ZA), arrowprops=dict(arrowstyle="->", lw=2, color="#c0392b"))
# dimensions from the inside edge of the grip
for x0, lab, y in ((F - 50.5, "engaged: 48 mm in from the\ninside edge of the grip", -100), (F - 50.5 - S, f"slid in {S:.0f} mm: 65 mm in", -118)):
  ax.annotate("", xy=(x0, y + 6), xytext=(R_IN, y + 6), arrowprops=dict(arrowstyle="<->", lw=1, color="#333"))
  ax.text((x0 + R_IN) / 2, y - 6, lab, ha="center", fontsize=9)
ax.plot([R_IN, R_IN], [-125, 20], color="#333", lw=0.8, ls=":")
ax.text(R_IN, 23, "inside edge\nof the grip", ha="center", fontsize=9)
ax.text(78, ZA, "?\nwhat's in here,\nand how far in\nis clear?", ha="center", va="center", fontsize=11, color="#8a5a00")
ax.text(214, z_top - 2, f"the motor's depth:\n{-(z_top + 17.7) / 10:.0f}" if False else "", fontsize=8)
ax.annotate("", xy=(205, z_top), xytext=(205, -17.7), arrowprops=dict(arrowstyle="<->", lw=1, color="#333"))
ax.text(207, (z_top - 17.7) / 2, f"{-(z_top + 17.7):.0f} mm", fontsize=9, va="center")
ax.annotate("", xy=(205, z_bot), xytext=(205, -17.7), arrowprops=dict(arrowstyle="<->", lw=1, color="#333", alpha=0.0))
ax.text(207, z_bot + 2, f"to {-(z_bot + 17.7):.0f} mm forward\nof the back of the grip", fontsize=9, va="bottom")
ax.text(R_MID, 26, "towards you (front of the wheel)", ha="center", fontsize=9, color="#555")
ax.text(R_MID, -128, "forward (towards the nose)", ha="center", fontsize=9, color="#555")
ax.set_xlim(220, 55)
ax.set_ylim(-132, 34)
ax.set_aspect("equal")
ax.set_title("Cut along the motor's shaft (side view)", fontsize=11)
ax.set_xlabel("mm from the middle of the column")
ax.set_ylabel("mm from the middle of the grip")
ax.grid(alpha=0.25)
handles = [Rectangle((0, 0), 1, 1, fc=c, alpha=0.85) for c in (C_MOT, C_CAP, C_GUARD, C_GEAR, C_TEETH)] + \
          [Rectangle((0, 0), 1, 1, fc="none", ec="#333", ls="--")]
fig.legend(handles, ["motor", "board cover", "plate and finger guard", "gear and roller", "teeth piece",
                     f"slid in {S:.0f} mm (gear out of the teeth)"], loc="lower center", ncol=6, fontsize=9, frameon=False)
plt.tight_layout(rect=(0, 0.05, 1, 1))
plt.savefig("sideways-layout.png", dpi=110)
print("ok")
EOF
export PYTHONPATH=/home/claude/pylib && python3 layout.py
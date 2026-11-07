cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > xyplot.py <<'EOF'
"""Looking along the column from the driver's seat: the key, its hand room, the adjustment tab and your fingers, the
covers, and the mount's parts turned to a given angle (each part's outline, projected)."""
import os, sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import carref as CR
import popassembly as PA, popparts as PP
from run_u import build
target = float(sys.argv[1]) if len(sys.argv) > 1 else -60.0
t, parts = build()
A = PA.PopAssembly(t, parts)
d = target - PP.MOUNT_DEG
def outline(m, zlim=None):
    v = np.asarray(m.to_mesh().vert_properties)[:, :3]
    if zlim is not None:
        v = v[(v[:, 2] >= zlim[0]) & (v[:, 2] <= zlim[1])]
    if len(v) < 3:
        return None
    h = ConvexHull(v[:, :2])
    return v[h.vertices, :2]
fig, ax = plt.subplots(figsize=(9, 9))
def draw(m, color, label, alpha=0.35, rot=0.0, fill=True):
    if rot:
        m = m.rotate((0, 0, rot))
    p = outline(m)
    if p is None:
        return
    ax.fill(p[:, 0], p[:, 1], color=color, alpha=alpha, label=label, lw=1.2, ec=color) if fill else ax.plot(np.r_[p[:, 0], p[0, 0]], np.r_[p[:, 1], p[0, 1]], color=color, lw=1.5, label=label)
draw(A.covers(), "#666", "column covers", alpha=0.15)
a = (CR.KEY_CLOCK_DEG, CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG)
b = CR.bezel(*a)
draw(CR.key_bulge(*a) + b["ring"], "#222", "key bulge and bezel", alpha=0.5)
draw(CR.key_in(*a), "#000", "the key", alpha=0.6)
draw(CR.key_turn_room(*a), "#d33", "hand on the key", alpha=0.2)
draw(PA.tab_lever(0.0), "#2a2", "adjustment tab", alpha=0.4)
draw(A.tilt_lever(), "#2a2", "tab pulled + fingers", alpha=0.15)
draw(A.motor() + A.carrier(), "#36c", "motor + carrier (on)", rot=d)
draw(A.springs() + A.bolts(), "#c6c", "springs + bolts (on)", rot=d)
draw(A.block() + A.switch(), "#e90", "hinge block (as at 3:20)", rot=d)
draw(A.motor(PP.LIFT_OFF) + A.carrier(PP.LIFT_OFF), "#39f", "motor popped off", rot=d, fill=False)
th = np.linspace(0, 2 * np.pi, 400)
for rr in (168.3 - 17.7, 186.0):
    ax.plot(rr * np.cos(th), rr * np.sin(th), color="#999", lw=0.8)
for ang, lab in ((CR.RIGHT_SPOKE_DEG, "right spoke"), (CR.RIGHT_BAR_DEG, "silver bar")):
    for a_ in ang:
        ax.plot([150 * math.cos(math.radians(a_)), 205 * math.cos(math.radians(a_))], [150 * math.sin(math.radians(a_)), 205 * math.sin(math.radians(a_))], color="#a60", lw=2)
    am = math.radians(sum(ang) / 2)
    ax.text(212 * math.cos(am), 212 * math.sin(am), lab, color="#a60", fontsize=8, ha="center")
ax.set_aspect("equal"); ax.grid(alpha=0.3); ax.legend(fontsize=7, loc="upper left")
ax.set_xlim(-120, 230); ax.set_ylim(-230, 120)
ax.set_title(f"From the driver's seat (wheel removed): mount turned to {target:+.0f}° ({'%d:%02d' % (3 + int((-target) // 30), int(((-target) % 30) * 2))})")
plt.savefig(f"/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm/look/xy_{int(-target)}.png", dpi=90, bbox_inches="tight")
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 xyplot.py -60
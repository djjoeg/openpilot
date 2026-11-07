mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > layout.py <<'EOF'
"""Side view of the hinge region in the carrier frame (y_c along the column towards the dash, z_c out from the column),
sliced at several x_c, with the mount at MOUNT: what's free for the new snap."""
import os, sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from manifold3d import Manifold, CrossSection
import carref as CR
import popparts as PP
MOUNT = float(sys.argv[1]) if len(sys.argv) > 1 else -63.0
PP.MOUNT_DEG = MOUNT
import popassembly as PA
from run_u import build
from cadlib import cyl, union, box

t, parts = build()
A = PA.PopAssembly(t, parts)

def xslice(m, x):
    # carrier-frame solid -> cross-section in (y, z) at x
    mm = m.transform([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]])
    return mm.slice(x)

def polys(cs):
    out = []
    for p in cs.to_polygons():
        p = np.asarray(p)
        if len(p) >= 3:
            out.append(p)
    return out

W2C = lambda m: PP.wheel_to_carrier(m)
carrier_c = parts["carrier"] + parts["motor"] + parts["gear"]
lifts = list(np.arange(-5.0, 75.01, 2.5))
sweep = union([PP.swung(carrier_c, float(L)) for L in lifts])
cars = {
  "covers": W2C(A.covers()),
  "plate (as at 3:20)": W2C(A.plate()),
  "tab + fingers": W2C(A.tilt_lever()),
  "back cover (r90, rim -80)": W2C(cyl(CR.BACK_COVER_R, CR.BACK_COVER_RIM_Z, -25.0, segments=96)),
  "back cover worst (r100, rim -110)": W2C(cyl(100.0, -110.0, -25.0, segments=96)),
  "teeth ring": W2C(A.teeth_ring()),
  "bolster": W2C(A.bolster()),
}
a = (CR.KEY_CLOCK_DEG, CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG)
b = CR.bezel(*a)
cars["key + room"] = W2C(CR.key_bulge(*a) + b["ring"] + CR.key_in(*a) + CR.key_turn_room(*a))
colors = {"covers": "#888", "plate (as at 3:20)": "#a52", "tab + fingers": "#2a2", "back cover (r90, rim -80)": "#c3c",
          "back cover worst (r100, rim -110)": "#f9f", "teeth ring": "#777", "bolster": "#555", "key + room": "#d33"}
xs = [float(v) for v in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["-20", "-12", "-4", "4", "12", "20"])]
fig, axs = plt.subplots(2, (len(xs) + 1) // 2, figsize=(7 * ((len(xs) + 1) // 2), 14))
axs = np.atleast_1d(axs).ravel()
hy, hz = PP.HINGE_P
for ax, x in zip(axs, xs):
    for name, m in cars.items():
        for p in polys(xslice(m, x)):
            ax.add_patch(Polygon(p, closed=True, fc=colors[name], ec=colors[name], alpha=0.25 if "worst" not in name else 0.12, lw=0.8))
    for p in polys(xslice(sweep, x)):
        ax.add_patch(Polygon(p, closed=True, fc="#36c", ec="#36c", alpha=0.15, lw=0.6))
    for L, c in ((0.0, "#036"), (75.0, "#39f"), (-5.0, "#0a6")):
        for p in polys(xslice(PP.swung(carrier_c, L), x)):
            ax.add_patch(Polygon(p, closed=True, fill=False, ec=c, lw=1.2))
    ax.plot([hy], [hz], "k+", ms=12)
    for r in (10, 20, 30, 40):
        th = np.linspace(0, 2 * np.pi, 200)
        ax.plot(hy + r * np.cos(th), hz + r * np.sin(th), color="k", lw=0.3, alpha=0.4)
    ax.set_xlim(-20, 170); ax.set_ylim(-110, 40)
    ax.set_aspect("equal"); ax.grid(alpha=0.3)
    ax.set_title(f"x_c = {x:+.0f}  (mount {MOUNT:+.0f})")
    ax.set_xlabel("y_c (towards the dash)"); ax.set_ylabel("z_c (out from the column)")
handles = [plt.Rectangle((0, 0), 1, 1, fc=c, alpha=0.4) for c in colors.values()] + [plt.Rectangle((0, 0), 1, 1, fc="#36c", alpha=0.3)]
fig.legend(handles, list(colors) + ["carrier+motor swept -5..75"], loc="lower center", ncol=5)
plt.tight_layout(rect=(0, 0.04, 1, 1))
out = f"/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap/layout_{int(-MOUNT)}.png"
plt.savefig(out, dpi=70)
print(out)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 layout.py -63
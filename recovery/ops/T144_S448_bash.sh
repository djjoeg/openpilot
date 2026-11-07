cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > ringplot.py <<'EOF'
import os, sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import popparts as PP
t = PP.PopTeeth()
prof = np.array([(p[0], p[1]) for p in t.profile()])
fig, ax = plt.subplots(figsize=(7, 6))
ax.fill(prof[:, 0], prof[:, 1], color="#bbb", label="back teeth piece (swept all round as the wheel turns)")
th = np.linspace(0, 2 * np.pi, 100)
ax.plot(t.rr + 17.7 * np.cos(th), 17.7 * np.sin(th), "k-", label="grip")
ax.add_patch(plt.Rectangle((140.1, -21.7), 196.5 - 140.1, 25.7, fill=False, ls=":", color="k", label="zip ties' heads"))
for z, c in ((-30, "#d33"), (-45, "#e83"), (-60, "#3a3"), (-75, "#36c")):
    ax.add_patch(plt.Circle((148, z), 12, fill=False, color=c, lw=2))
    ax.text(162, z, "wiper stalk end at z %d" % z, color=c, fontsize=8, va="center")
ax.set_xlabel("distance from the column's centre (mm)"); ax.set_ylabel("z: + towards you, 0 = middle of the grip (mm)")
ax.set_aspect("equal"); ax.grid(alpha=0.3); ax.legend(fontsize=7, loc="lower left")
ax.set_xlim(120, 215); ax.set_ylim(-95, 25)
plt.savefig("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm/look/ring_vs_stalk.png", dpi=110, bbox_inches="tight")
EOF
PYTHONPATH=/home/claude/pylib python3 ringplot.py
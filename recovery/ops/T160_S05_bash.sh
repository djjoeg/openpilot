cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && python3 - <<'EOF'
import pathlib
p = pathlib.Path("layout.py")
s = p.read_text()
reps = [
('C_GRIP, C_TEETH, C_MOT, C_CAP, C_GEAR, C_GUARD = "#2b2b2b", "#9aa3ad", "#3d3f44", "#7d62c8", "#e0962b", "#3f7fd0"',
 'C_GRIP, C_TEETH, C_MOT, C_CAP, C_GEAR, C_GUARD = "#1d1d1f", "#b7bec6", "#5b6b7d", "#7d62c8", "#e0962b", "#3f7fd0"'),
('ax.text(R_MID, -44, "grip", ha="center", color="white", fontsize=10, rotation=90, va="center")',
 'ax.text(R_MID + 4, -52, "grip", ha="center", color="white", fontsize=10, rotation=90, va="center")'),
('ax.text(t.w_out + 3, -34, "teeth piece\\non its back", fontsize=9, color="#555")',
 'ax.text(t.w_out + 2, 52, "teeth piece (on the\\ngrip\'s back, facing you)", fontsize=9, color="#555", ha="left")\nax.text(56, 55, "along the grip", fontsize=9, color="#555", ha="right")'),
('ax.text(R_IN, 23, "inside edge\\nof the grip", ha="center", fontsize=9)',
 'ax.text(R_IN - 2, 28, "inside edge of the grip", ha="right", fontsize=9)'),
('ax.text(78, ZA, "?\\nwhat\'s in here,\\nand how far in\\nis clear?", ha="center", va="center", fontsize=11, color="#8a5a00")',
 'ax.text(58, ZA, "?\\nwhat\'s here,\\nand how far\\nin is clear?", ha="center", va="center", fontsize=11, color="#8a5a00")'),
('ax.text(214, z_top - 2, f"the motor\'s depth:\\n{-(z_top + 17.7) / 10:.0f}" if False else "", fontsize=8)\n', ''),
('ax.annotate("", xy=(205, z_top), xytext=(205, -17.7), arrowprops=dict(arrowstyle="<->", lw=1, color="#333"))\nax.text(207, (z_top - 17.7) / 2, f"{-(z_top + 17.7):.0f} mm", fontsize=9, va="center")\nax.annotate("", xy=(205, z_bot), xytext=(205, -17.7), arrowprops=dict(arrowstyle="<->", lw=1, color="#333", alpha=0.0))\nax.text(207, z_bot + 2, f"to {-(z_bot + 17.7):.0f} mm forward\\nof the back of the grip", fontsize=9, va="bottom")',
 'ax.plot([196, 212], [-17.7, -17.7], color="#333", lw=0.8)\nax.annotate("", xy=(204, z_top), xytext=(204, -17.7), arrowprops=dict(arrowstyle="<->", lw=1, color="#333"))\nax.annotate("", xy=(210, z_bot), xytext=(210, -17.7), arrowprops=dict(arrowstyle="<->", lw=1, color="#333"))\nax.text(203, (z_top - 17.7) / 2, f"{-(z_top + 17.7):.0f}", fontsize=9, va="center", ha="right")\nax.text(209, z_bot + 6, f"{-(z_bot + 17.7):.0f}", fontsize=9, va="center", ha="right")\nax.text(213, -110, f"the motor sits {-(z_top + 17.7):.0f} to {-(z_bot + 17.7):.0f} mm\\nforward of the back of the grip", fontsize=9, ha="left")'),
('ax.text(R_MID, 26, "towards you (front of the wheel)", ha="center", fontsize=9, color="#555")',
 'ax.text(212, 28, "towards you (front of the wheel)", ha="left", fontsize=9, color="#555")'),
('ax.set_xlim(220, 55)\nax.set_ylim(-132, 34)', 'ax.set_xlim(220, 40)\nax.set_ylim(-132, 36)'),
]
for a, b in reps:
  assert s.count(a) == 1, a[:70]
  s = s.replace(a, b)
p.write_text(s)
EOF
export PYTHONPATH=/home/claude/pylib && python3 layout.py
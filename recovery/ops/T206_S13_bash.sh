python3 - <<'EOF'
import re
p='frameplate.py'; s=open(p).read()
old_start=s.index('  ax.annotate("", xy=(RIGHT[1] + 10, -40)')
old_end=s.index('  # dimensions')
new='''  ax.annotate("", xy=(-32, -45), xytext=(-32, -20), arrowprops={"arrowstyle": "->", "color": "#444"})
  ax.text(-32, -48, "to the wheel\\n(127 mm from\\nthe cup)", ha="center", va="top", fontsize=8, color="#444")
  ax.text(-40, 30, "KEY SIDE", ha="center", va="center", fontsize=8, color="#444", rotation=-90)
  ax.text(STRIP[1] + 14, 0, "DRIVER'S-DOOR SIDE", ha="center", va="center", fontsize=8, color="#444", rotation=90)
'''
s=s[:old_start]+new+s[old_end:]
s=s.replace('''  ax.annotate("", xy=(146, STRIP[2]), xytext=(146, STRIP[3]), arrowprops={"arrowstyle": "<->", "color": "#444"})
  ax.text(148, (STRIP[2] + STRIP[3]) / 2, f"{STRIP[3] - STRIP[2]:.0f} mm", ha="left", va="center", fontsize=8, rotation=-90)
  ax.set_aspect("equal")
  ax.set_xlim(-45, 160)
  ax.set_ylim(-105, 66)
  ax.set_xlabel("across the car, mm (0 = cup screw, + towards the driver's door)")
  ax.set_ylabel("along the column, mm (0 = cup screw, + towards the dash)")
  ax.set_title("Frame plate v1, seen from below (as printed, labels up). Red dashed: the car, from the photos (rough).", fontsize=9)''',
'''  ax.annotate("", xy=(146, STRIP[2]), xytext=(146, STRIP[3]), arrowprops={"arrowstyle": "<->", "color": "#444"})
  ax.text(148, (STRIP[2] + STRIP[3]) / 2, f"{STRIP[3] - STRIP[2]:.0f} mm", ha="left", va="center", fontsize=8, rotation=90)
  ax.set_aspect("equal")
  ax.set_xlim(160, -50)          # seen from below: the key side is on the right, like the photos
  ax.set_ylim(-105, 66)
  ax.set_xlabel("across the car, mm (0 = cup screw)")
  ax.set_ylabel("along the column, mm (0 = cup screw, + towards the dash)")
  ax.set_title("Frame plate v1 seen from below, as in the photos (print labels up; in the car the labels face down).\\n"
               "Red dashed: the car, from the photos (rough).", fontsize=9)''')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 frameplate.py >/dev/null && echo ok
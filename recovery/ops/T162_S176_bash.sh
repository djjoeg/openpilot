python3 - <<'EOF'
import re
p = "sidebuild.py"
s = open(p).read()
orig = s
s = s.replace("import popassembly as PA\n", "")
s = s.replace('arrowprops=dict(arrowstyle="->", lw=2.2, color="#c0392b")', 'arrowprops={"arrowstyle": "->", "lw": 2.2, "color": "#c0392b"}')
s = s.replace('arrowprops=dict(arrowstyle="-", lw=0.7, color="#555", shrinkA=0, shrinkB=2)', 'arrowprops={"arrowstyle": "-", "lw": 0.7, "color": "#555", "shrinkA": 0, "shrinkB": 2}')
s = s.replace('arrowprops=dict(arrowstyle="<->", lw=1, color="#333")', 'arrowprops={"arrowstyle": "<->", "lw": 1, "color": "#333"}')
s = s.replace('bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#888", lw=0.6, alpha=0.9)', 'bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#888", "lw": 0.6, "alpha": 0.9}')
s = s.replace('arrowprops=dict(arrowstyle="-", lw=0.8, color="#333")', 'arrowprops={"arrowstyle": "-", "lw": 0.8, "color": "#333"}')
s = s.replace('  x0, y0, z0, x1, y1, z1 = S.side_board_cap().bounding_box()', '  _x0, y0, _z0, _x1, y1, _z1 = S.side_board_cap().bounding_box()')
s = s.replace('       f"spring pulls it in; you pull it back out along the shaft until the latch clicks. Pull the latch\'s knob and the",',
              '       "spring pulls it in; you pull it back out along the shaft until the latch clicks. Pull the latch\'s knob and the",')
print("dict( left:", s.count("dict("))
open(p, "w").write(s)
p = "sideassembly.py"
s = open(p).read()
s = s.replace("  def __init__(self, parts: dict = None, mount_deg: float = S.MOUNT_DEG):", "  def __init__(self, parts: dict | None = None, mount_deg: float = S.MOUNT_DEG):")
s = s.replace("def car_estimates(A: SideAssembly, D: float = None) -> list:", "def car_estimates(A: SideAssembly, D: float | None = None) -> list:")
s = s.replace('  t = A.t\n  T0 = A.p["teeth"]\n  worst, at = 0.0, 0.0\n', '  t = A.t\n  worst, at = 0.0, 0.0\n')
s = s.replace('  f = forces()\n  m = f["moving mass (kg, about)"]\n  w_along', '  f = forces()\n  w_along')
open(p, "w").write(s)
EOF
chmod +x sidebuild.py
sed -n 62,85p sidebuild.py
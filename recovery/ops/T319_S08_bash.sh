cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fea && python3 - <<'EOF'
import re
s = open('armfea.py').read()
# add a diagnostic after the solve: rigid rotation of slices along the load path
old = """    out[name] = dP
"""
new = """    out[name] = dP
    def rigid(mask):
      idx = np.where(mask)[0]
      cc = xyz[idx].mean(axis=0); rr = xyz[idx] - cc; uu = u.reshape(-1, 3)[idx]
      AA = np.zeros((3 * len(idx), 6))
      for q in range(len(idx)):
        x_, y_, z_ = rr[q]
        AA[3*q:3*q+3, :3] = np.eye(3)
        AA[3*q:3*q+3, 3:] = np.array([[0, z_, -y_], [-z_, 0, x_], [y_, -x_, 0]])
      s_, *_ = np.linalg.lstsq(AA, uu.ravel(), rcond=None)
      return np.degrees(s_[3:])
    groups = {
      "bar at x 125-130": (xyz[:, 0] >= 125) & (xyz[:, 0] <= 130),
      "bar at x 140-145": (xyz[:, 0] >= 140) & (xyz[:, 0] <= 145),
      "tower at z -160 (base, above the foot)": (z_of >= -162) & (z_of <= -158) & (u_of > 190),
      "tower at z -130": (z_of >= -132) & (z_of <= -128) & (u_of > 190),
      "tower top z -96": (z_of >= -98) & (z_of <= -94) & (u_of > 190),
      "carrier plate (motor)": load,
    }
    for gname, gm in groups.items():
      rot = rigid(gm)
      print(f"   {gname:40s} turned about x {rot[0]:+.2f}, y {rot[1]:+.2f}, z {rot[2]:+.2f} deg  ({gm.sum()} nodes)")
"""
assert s.count(old) == 1
s = s.replace(old, new)
open('armfea_diag.py', 'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 armfea_diag.py 2.0 2>&1 | tail -16
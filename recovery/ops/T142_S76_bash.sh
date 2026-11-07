cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > explore_parts.py <<'EOF'
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import popparts as PP
import popassembly as PA
import params as P
from cadlib import cyl_x, union
from mindist import min_dist
from explore_mount import bolts_c, carrier, motor, gear, stalk_cfgs, key_room, key

for mount in (-7.5, -11.25):
  PP.MOUNT_DEG = mount
  z_axis = -56.5
  for lift in (-3.0, 0.0, 40.0, 75.0):
    parts = {"carrier": PP.to_wheel(carrier, lift, z_axis), "motor": PP.to_wheel(motor, lift, z_axis),
             "gear": PP.to_wheel(gear, lift, z_axis), "springs": PP.to_wheel(PP.spring_solid(lift), 0.0, z_axis),
             "bolts": PP.to_wheel(bolts_c(lift), 0.0, z_axis)}
    row = []
    for pn, pm in parts.items():
      ds = []
      for on, ob in (("stalk36", stalk_cfgs[36.0]), ("keyroom", key_room)):
        d, p = min_dist(pm, ob, spacing=1.5)
        ds.append(f"{on} {d:.1f}" + (f"@({p[0]:.0f},{p[1]:.0f},{p[2]:.0f})" if p is not None else ""))
      row.append(f"{pn}: " + ", ".join(ds))
    print(f"mount {mount} lift {lift}: " + " | ".join(row), flush=True)
EOF
sed -i 's/^lifts = /if __name__ == "__main__":\n  pass\nlifts = /' explore_mount.py && python3 - <<'EOF'
# make explore_mount importable without running its loop
p = "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/explore_mount.py"
s = open(p).read()
s = s.replace('if __name__ == "__main__":\n  pass\nlifts = ', 'lifts = ')
head, loop = s.split("lifts = (-3.0", 1)
loop = "lifts = (-3.0" + loop
loop = "\n".join("  " + l if l.strip() else l for l in loop.splitlines())
s = head + 'if __name__ == "__main__":\n' + loop + "\n"
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 1200 python3 explore_parts.py 2>&1 | tail -12
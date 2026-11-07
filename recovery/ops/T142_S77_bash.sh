cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > explore_low.py <<'EOF'
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import popparts as PP
import popassembly as PA
import params as P
from cadlib import cyl_x, union, box
from mindist import min_dist
from explore_mount import bolts_c, carrier, motor, gear, stalk_cfgs, key_room, key
import columnassembly as CA

T0 = time.time()
side = CA.SideAssembly.__new__(CA.SideAssembly)
side.cover_w, side.cover_h, side.cover_front_w = P.COVER_W, P.COVER_H, P.COVER_FRONT_W
covers = CA.ColumnAssembly.covers(side, back_z=-400.0)
lever = box(*PA.TILT_LEVER_ZONE)
lifts = (-3.0, 0.0, 15.0, 30.0, 45.0, 60.0, 75.0)
for mount in (-22.5, -30.0, -37.5, -45.0, -52.5, -60.0, -67.5):
  PP.MOUNT_DEG = mount
  z_axis = -61.5
  worst = {}
  for lift in lifts:
    movers = union([PP.to_wheel(carrier, lift, z_axis), PP.to_wheel(motor, lift, z_axis), PP.to_wheel(gear, lift, z_axis),
                    PP.to_wheel(PP.spring_solid(lift), 0.0, z_axis), PP.to_wheel(bolts_c(lift), 0.0, z_axis)])
    for name, ob in [("stalk45", stalk_cfgs[45.0]), ("key room", key_room), ("key", key), ("covers", covers), ("lever", lever)]:
      d, p = min_dist(movers, ob, spacing=1.5)
      if name not in worst or d < worst[name][0]:
        worst[name] = (round(d, 1), lift)
  # where the motor sits, swung off: its lowest point and how far right
  off = PP.to_wheel(motor, 75.0, z_axis).bounding_box()
  on = PP.to_wheel(motor, 0.0, z_axis).bounding_box()
  print(f"mount {mount:6.1f} ({3 - mount / 30:.2f} o'clock): " + "  ".join(f"{k} {v[0]} (lift {v[1]})" for k, v in worst.items()) +
        f"  | motor on box x {on[0]:.0f}..{on[3]:.0f} y {on[1]:.0f}..{on[4]:.0f} z {on[2]:.0f}..{on[5]:.0f}; off box x {off[0]:.0f}..{off[3]:.0f} y {off[1]:.0f}..{off[4]:.0f} z {off[2]:.0f}..{off[5]:.0f}",
        round(time.time() - T0, 1), flush=True)
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 explore_low.py 2>&1 | tail -12
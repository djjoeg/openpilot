cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > explore_nominal.py <<'EOF'
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import popparts as PP
import popassembly as PA
import params as P
import columnassembly as CA
from cadlib import union
from mindist import min_dist
from explore_mount import bolts_c, carrier, motor, gear, stalk_cfgs, key

T0 = time.time()
kd = np.array(P.KEY_TO) - np.array(P.KEY_FROM); kd /= np.linalg.norm(kd)
key_head = CA.rod(np.array(P.KEY_TO), np.array(P.KEY_TO) + 45.0 * kd, 20.0)
key_room = PA.key_room()
z_axis = -59.5
for mount in (-8.0, -9.0, -10.0, -11.0, -12.0, -13.0):
  PP.MOUNT_DEG = mount
  w = {}
  for lift in (-3.0, 0.0, 10.0, 25.0, 40.0, 55.0, 75.0):
    movers = union([PP.to_wheel(carrier, lift, z_axis), PP.to_wheel(motor, lift, z_axis), PP.to_wheel(gear, lift, z_axis),
                    PP.to_wheel(PP.spring_solid(lift), 0.0, z_axis), PP.to_wheel(bolts_c(lift), 0.0, z_axis)])
    obs = [("stalk30", stalk_cfgs[30.0]), ("stalk36", stalk_cfgs[36.0]), ("stalk45", stalk_cfgs[45.0]), ("key", key), ("key head", key_head)]
    if lift >= 40.0:
      obs.append(("key room (off)", key_room))
    for n, ob in obs:
      d, p = min_dist(movers, ob, spacing=1.5)
      if n not in w or d < w[n][0]:
        w[n] = (round(d, 1), lift)
  print(f"mount {mount:6.1f} ({3 - mount / 30:.2f}): " + "  ".join(f"{k} {v[0]}@{v[1]}" for k, v in w.items()), round(time.time() - T0), "s", flush=True)
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 explore_nominal.py 2>&1 | grep -v "^car parts"
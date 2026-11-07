cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > explore_mount.py <<'EOF'
"""How far the motor and its parts stay from the wiper stalk (pushed down up to 45 degrees), the key and the spokes, for
a few clock positions and depths."""
import sys, time, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import popparts as PP
import popassembly as PA
import params as P
from cadlib import cyl_x, union
from mindist import min_dist

T0 = time.time()
mb = PP.motor_and_board()
carrier = PP.pop_carrier()
motor = mb["body"] + mb["board"] + mb["plugs"]
gear = PP.pop_motor_gear()


def bolts_c(lift):
  cy, cz = PP.turn(PP.C_BOLT, lift)
  x_out = PP.SPRING_X + PP.SPRING_WIRE_P / 2 + 1.0
  return (cyl_x(2.5, -x_out, x_out + 6.2, y=cy, z=cz, segments=16) + cyl_x(4.6, -x_out - 3.5, -x_out, y=cy, z=cz, segments=16) +
          cyl_x(4.6, x_out, x_out + 5.2, y=cy, z=cz, segments=6))


stalk_cfgs = {}
for down in (30.0, 36.0, 45.0):
  stalk_cfgs[down] = PA.stalk_positions(down=down, up=10.0, step=2.5)
key_room = PA.key_room()
key = PA.CA.rod(P.KEY_FROM, P.KEY_TO, P.KEY_R)
print("car parts", round(time.time() - T0, 1))

lifts = (-3.0, 0.0, 10.0, 25.0, 40.0, 55.0, 75.0)
for mount in (-7.5, -11.25, -15.0, -18.75):
  PP.MOUNT_DEG = mount
  for z_axis in (-56.5, -61.5):
    worst = {}
    for lift in lifts:
      movers = union([PP.to_wheel(carrier, lift, z_axis), PP.to_wheel(motor, lift, z_axis), PP.to_wheel(gear, lift, z_axis),
                      PP.to_wheel(PP.spring_solid(lift), 0.0, z_axis), PP.to_wheel(bolts_c(lift), 0.0, z_axis)])
      for name, ob in [("stalk30", stalk_cfgs[30.0]), ("stalk36", stalk_cfgs[36.0]), ("stalk45", stalk_cfgs[45.0]),
                       ("key room", key_room), ("key", key)]:
        d, _ = min_dist(movers, ob, spacing=1.5)
        if name not in worst or d < worst[name][0]:
          worst[name] = (round(d, 1), lift)
    print(f"mount {mount:7.2f} ({3 - mount / 30:.2f} o'clock)  z_axis {z_axis}: " +
          "  ".join(f"{k} {v[0]} (lift {v[1]})" for k, v in worst.items()), round(time.time() - T0, 1), "s", flush=True)
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 explore_mount.py 2>&1 | tail -20
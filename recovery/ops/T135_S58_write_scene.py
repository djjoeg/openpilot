"""Quick layout pictures of the pop-off mount in the car (numpy renderer, simplified meshes)."""
import math
import sys
import time

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np  # noqa: E402

import columnassembly as CA  # noqa: E402
import params as P  # noqa: E402
import popparts as PP  # noqa: E402
import render as RD  # noqa: E402
from cadlib import box, cyl, revolve, union  # noqa: E402

T0 = time.time()


def car_bits():
  side = CA.SideAssembly.__new__(CA.SideAssembly)
  side.cover_w, side.cover_h, side.cover_front_w = P.COVER_W, P.COVER_H, P.COVER_FRONT_W
  covers = CA.ColumnAssembly.covers(side, back_z=-260.0)
  hub = cyl(P.HUB_R, P.HUB_BACK_Z, 25.0, segments=48)
  rr = PP.WHEEL_OD_P / 2 - PP.GRIP_P / 2
  pts = [(rr + (PP.GRIP_P / 2) * math.cos(a), (PP.GRIP_P / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
  grip = revolve(pts, 0.0, 360.0, step_deg=4.0)
  base = np.array(P.STALK_FROM)
  d = np.array(P.STALK_TO) - base
  d /= np.linalg.norm(d)
  stalk = CA.rod(base, base + 105.0 * d, P.STALK_R, 16)
  ax = np.cross(d, [0.0, 1.0, 0.0])
  ax /= np.linalg.norm(ax)
  th = math.radians(-30.0)
  v = 105.0 * d
  v_rot = v * math.cos(th) + np.cross(ax, v) * math.sin(th) + ax * np.dot(ax, v) * (1 - math.cos(th))
  stalk_down = CA.rod(base, base + v_rot, P.STALK_R, 16)
  key = CA.rod(P.KEY_FROM, P.KEY_TO, P.KEY_R, 16)
  # right spoke, rough: from the hub to the grip between its junction angles
  a0, a1 = P.RIGHT_SPOKE_DEG
  sp = []
  for a in np.linspace(a0, a1, 6):
    sp.append(cyl(4.0, -30.0, 4.0, x=150 * math.cos(math.radians(a)), y=150 * math.sin(math.radians(a)), segments=8))
  from manifold3d import Manifold
  spoke = Manifold.batch_hull(sp + [cyl(4.0, -30.0, 4.0, x=80 * math.cos(math.radians(-10)), y=80 * math.sin(math.radians(-10)), segments=8),
                                    cyl(4.0, -30.0, 4.0, x=80 * math.cos(math.radians(-50)), y=80 * math.sin(math.radians(-50)), segments=8)])
  return {"covers": covers, "hub": hub, "grip": grip, "stalk": stalk, "stalk_down": stalk_down, "key": key, "spoke": spoke}


def pop_bits(lift):
  t = PP.PopTeeth()
  body = revolve(t.profile(), -t.half, t.half, step_deg=2.0)
  teeth = body.rotate((0, 0, PP.MOUNT_DEG))
  mb = PP.motor_and_board()
  motor = PP.to_wheel(mb["body"] + mb["board"] + mb["plugs"], lift)
  carrier = PP.to_wheel(PP.pop_carrier(), lift)
  gear = PP.to_wheel(PP.pop_motor_gear(), lift)
  springs = PP.to_wheel(PP.spring_solid(lift), 0.0)
  return {"teeth": teeth, "motor": motor, "carrier": carrier, "gear": gear, "springs": springs}


COL = {"covers": (.8, .78, .7), "hub": (.35, .35, .38), "grip": (.25, .25, .25), "stalk": (.5, .5, .55), "stalk_down": (.75, .6, .6),
       "key": (.75, .7, .3), "spoke": (.6, .6, .62), "teeth": (.85, .85, .85), "motor": (.2, .2, .22), "carrier": (.35, .55, .85),
       "gear": (.95, .6, .25), "springs": (.9, .3, .3), "block": (.45, .75, .45)}


def shoot(name, parts, rot, size=(1000, 760)):
  img = RD.render([(m, COL[k]) for k, m in parts.items() if not m.is_empty()], rot, size=size)
  import matplotlib.pyplot as plt
  plt.imsave(name, img)
  print("saved", name, round(time.time() - T0, 1), "s")


if __name__ == "__main__":
  car = car_bits()
  for lift in (0.0, 75.0):
    parts = dict(car)
    parts.update(pop_bits(lift))
    for k in list(parts):
      parts[k] = parts[k] ^ box(-40, 260, -150, 150, -200, 60)
    # from behind the wheel (the dash side), looking towards the driver, a little from the right and above
    shoot(f"behind_{int(lift)}.png", parts, RD.look((0.35, 0.25, -1.0), (0, 1, 0)))
    # from above, looking down along -y
    shoot(f"above_{int(lift)}.png", parts, RD.look((0.15, 1.0, 0.25), (0, 0, 1)))
    # from the driver's seat, looking at the wheel
    shoot(f"driver_{int(lift)}.png", parts, RD.look((0.0, 0.1, 1.0), (0, 1, 0)))

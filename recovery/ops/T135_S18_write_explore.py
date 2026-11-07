"""Quick kinematic exploration of the flipped pop-off motor: simple solids, overlap checks against the car estimates."""
import math
import sys

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np  # noqa: E402
from manifold3d import Manifold  # noqa: E402

import assembly as AS  # noqa: E402
import columnassembly as CA  # noqa: E402
import params as P  # noqa: E402
from cadlib import box, cyl, cyl_x, union  # noqa: E402

WOD, GRIP = 372.0, 35.4
RR = WOD / 2 - GRIP / 2
R_FACE = 153.0
H = 21.15


def rotz(deg):
  a = math.radians(deg)
  return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])


R_FLIP = np.array([[0.0, 0.0, 1.0], [-1.0, 0.0, 0.0], [0.0, -1.0, 0.0]])


def carrier_to_wheel(m, z_axis, mount_deg, hinge, lift):
  if lift:
    m = AS.turn_about_x(m, -lift, np.array([0.0, hinge[0], hinge[1]]))
  R = rotz(mount_deg) @ R_FLIP
  T = rotz(mount_deg) @ np.array([R_FACE, 0.0, z_axis])
  return AS.place(m, R, T)


def motor_parts():
  body = box(-H, H, -H, H, -40, 0) + cyl(11.0, 0.0, 2.0)
  board = box(-H, H, -H, H, -54, -40)
  # turned 180 degrees about the shaft: plugs face +y (the dash) and the sides
  plugs = box(-6, 6, H, H + 14, -52, -43) + box(H, H + 14, -6, 6, -52, -43) + box(-H - 14, -H, -6, 6, -52, -43)
  motor_plug = box(-8, 8, H, H + 12, -38, -22)
  return body + board + plugs + motor_plug


def carrier_rough(hinge):
  plate = box(-23.65, 23.65, -20, 23.65, 0, 5)
  guard = cyl(28.5, 5, 28.5) - cyl(26.5, 4, 30)
  walls = box(-24.55, -21.65, -21, 29.65, -39, 5) + box(21.65, 24.55, -21, 29.65, -39, 5)
  hy, hz = hinge
  cheeks = union([Manifold.batch_hull([box(s * 10, s * 24.55, 21.65, 29.65, -39, 5),
                                       cyl_x(7.5, s * 10, s * 24.55, y=hy, z=hz)]) for s in (1, -1)])
  return plate + guard + walls + cheeks


def gear_rough():
  return cyl(18.0, 7, 19) + cyl(16.87, 20, 24)


def car(stalk_down=30.0):
  side = CA.SideAssembly.__new__(CA.SideAssembly)
  side.cover_w, side.cover_h, side.cover_front_w = P.COVER_W, P.COVER_H, P.COVER_FRONT_W
  covers = CA.ColumnAssembly.covers(side)
  hub = cyl(P.HUB_R, P.HUB_BACK_Z, 25.0, segments=96)
  spokes = cyl(WOD / 2 - GRIP + 1.0, P.SPOKE_BACK_Z, 25.0, segments=180)
  base = np.array(P.STALK_FROM)
  d = np.array(P.STALK_TO) - base
  d = d / np.linalg.norm(d)
  tip = base + 105.0 * d
  stalks = [CA.rod(base, tip, P.STALK_R)]
  # pushed down: turn the stalk about a level axis across it, through its base
  ax = np.cross(d, [0.0, 1.0, 0.0])
  ax /= np.linalg.norm(ax)
  for a in np.arange(5.0, stalk_down + 0.1, 5.0):
    th = math.radians(-a)
    k = ax
    v = tip - base
    v_rot = v * math.cos(th) + np.cross(k, v) * math.sin(th) + k * np.dot(k, v) * (1 - math.cos(th))
    stalks.append(CA.rod(base, base + v_rot, P.STALK_R))
  stalk = union(stalks)
  key = CA.rod(P.KEY_FROM, P.KEY_TO, P.KEY_R)
  kd = np.array(P.KEY_TO) - np.array(P.KEY_FROM)
  kd /= np.linalg.norm(kd)
  key_room = CA.rod(np.array(P.KEY_TO), np.array(P.KEY_TO) + 60.0 * kd, 22.0)
  grip = AS.place(cyl(GRIP / 2 + 1, -1, 1), np.eye(3), (0, 0, 0))   # placeholder
  pts = [(RR + (GRIP / 2) * math.cos(a), (GRIP / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
  from cadlib import revolve
  grip = revolve(pts, 0.0, 360.0, step_deg=1.0)
  # fingers round the grip: a band behind the grip to 45 mm behind its middle, over the grip's radius range
  fingers = (cyl(WOD / 2 + 8, -45, 0, segments=180) - cyl(RR - GRIP / 2 - 12, -46, 1, segments=180))
  tilt = box(-45, 8, -130, -48, -200, -45)
  return {"covers": covers, "hub": hub, "spokes": spokes, "stalk": stalk, "key": key, "key room": key_room, "grip": grip,
          "fingers": fingers, "tilt lever": tilt}


def spring_rod(a, b, r=5.5):
  return CA.rod(a, b, r)


def run(mount_deg, z_axis, hinge, rc, beta_c, rb, theta_dc, x_s=31.0, park=75.0, verbose=True):
  C = car()
  M = motor_parts()
  CR = carrier_rough(hinge)
  G = gear_rough()
  hy, hz = hinge
  c0 = np.array([hy + rc * math.cos(math.radians(beta_c)), hz + rc * math.sin(math.radians(beta_c))])
  beta_b = beta_c + 180.0 - theta_dc
  b = np.array([hy + rb * math.cos(math.radians(beta_b)), hz + rb * math.sin(math.radians(beta_b))])
  res = {}
  for lift in [-3.0, 0.0] + list(np.arange(5.0, park + 0.1, 5.0)):
    parts = {"motor": M, "carrier": CR, "gear": G}
    for name, m in parts.items():
      w = carrier_to_wheel(m, z_axis, mount_deg, hinge, lift)
      for cn, cm in C.items():
        if lift <= 0 and name == "gear" and cn == "grip":
          continue
        if cn == "fingers" and lift < park - 0.1:
          continue
        v = (w ^ cm).volume()
        if v > 1e-3:
          res[f"{name}/{cn}"] = max(res.get(f"{name}/{cn}", 0.0), v)
          res.setdefault(f"{name}/{cn} at", []).append(lift)
    # springs
    th = math.radians(-lift)
    rot = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    c = np.array([hy, hz]) + rot @ (c0 - np.array([hy, hz]))
    for s in (1, -1):
      a3 = np.array([s * x_s, c[0], c[1]])
      b3 = np.array([s * x_s, b[0], b[1]])
      sp = carrier_to_wheel(spring_rod(a3, b3), z_axis, mount_deg, hinge, 0.0)
      for cn, cm in C.items():
        if cn == "fingers" and lift < park - 0.1:
          continue
        v = (sp ^ cm).volume()
        if v > 1e-3:
          key = f"spring {'+' if s > 0 else '-'}/{cn}"
          res[key] = max(res.get(key, 0.0), v)
          res.setdefault(key + " at", []).append(lift)
      for pn, pm in (("motor", M), ("carrier", CR)):
        w = carrier_to_wheel(pm, z_axis, mount_deg, hinge, lift)
        v = (sp ^ w).volume()
        if v > 1e-3:
          key = f"spring {'+' if s > 0 else '-'}/{pn}"
          res[key] = max(res.get(key, 0.0), v)
          res.setdefault(key + " at", []).append(lift)
  # where things are when parked
  wpark = carrier_to_wheel(M, z_axis, mount_deg, hinge, park)
  bb = wpark.bounding_box()
  # torque curve: per unit spring force, N mm per N
  out = []
  for lift in (-3.0, 0.0, 20.0, 40.0, theta_dc, park):
    th = math.radians(-lift)
    rot = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    c = np.array([hy, hz]) + rot @ (c0 - np.array([hy, hz]))
    L = float(np.linalg.norm(c - b))
    rcv = c - np.array([hy, hz])
    f = (b - c) / L
    tq = float(rcv[0] * f[1] - rcv[1] * f[0])     # about +x in the (y, z) plane: + turns +y towards +z
    out.append((lift, round(L, 2), round(tq, 2)))
  if verbose:
    print(f"mount {mount_deg} z_axis {z_axis} hinge {hinge} c0 {c0.round(1)} b {b.round(1)} beta_b {beta_b % 360:.0f}")
    print("  parked motor box", np.round(bb, 1))
    print("  (lift, spring length, torque arm mm [+ lowers the gear onto the teeth?])", out)
    for k, v in res.items():
      if not k.endswith(" at"):
        print(f"  {k}: {v:.1f} mm3 at lifts {res[k + ' at'][:3]}..{res[k + ' at'][-1:]}")
  return res, out


if __name__ == "__main__":
  import itertools
  for md, hinge in itertools.product((-10.0,), ((45.0, -50.0), (45.0, -45.0), (40.0, -55.0))):
    run(md, -56.5, hinge, 35.0, 135.0, 35.0, 55.0)

cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop && cat > explore2.py <<'EOF'
import math, sys
sys.path.insert(0, ".")
import numpy as np
import explore as E
from cadlib import box, cyl
import columnassembly as CA
import params as P
from cadlib import union

H = E.H

def motor_variant(stalk_side_plug, key_side_plug, dash_plug=14.0):
  body = box(-H, H, -H, H, -40, 0) + cyl(11.0, 0.0, 2.0)
  board = box(-H, H, -H, H, -54, -40)
  plugs = box(-6, 6, H, H + dash_plug, -52, -43) + box(-H - stalk_side_plug, -H, -6, 6, -52, -43) + box(H, H + key_side_plug, -6, 6, -52, -43)
  motor_plug = box(-8, 8, H, H + 12, -38, -22)
  return body + board + plugs + motor_plug

def stalk_solid(down, extra_r=0.0):
  base = np.array(P.STALK_FROM); d = np.array(P.STALK_TO) - base; d /= np.linalg.norm(d)
  tip = base + 105.0 * d
  ax = np.cross(d, [0.0, 1.0, 0.0]); ax /= np.linalg.norm(ax)
  out = [CA.rod(base, tip, P.STALK_R + extra_r)]
  for a in np.arange(2.5, down + 0.1, 2.5):
    th = math.radians(-a); v = tip - base
    v_rot = v * math.cos(th) + np.cross(ax, v) * math.sin(th) + ax * np.dot(ax, v) * (1 - math.cos(th))
    out.append(CA.rod(base, base + v_rot, P.STALK_R + extra_r))
  return union(out)

def key_solid(extra_r=0.0):
  kd = np.array(P.KEY_TO) - np.array(P.KEY_FROM); kd /= np.linalg.norm(kd)
  return CA.rod(P.KEY_FROM, P.KEY_TO, P.KEY_R + extra_r) + CA.rod(np.array(P.KEY_TO), np.array(P.KEY_TO) + 60.0 * kd, 22.0 + extra_r)

def margin(md, motor, fixed_fn, hinge=(45.0, -50.0), z_axis=-56.5, lifts=(-3.0, 0.0, 5, 10, 15, 20, 30, 40, 50, 60, 75)):
  car_parts = [E.carrier_to_wheel(m, z_axis, md, hinge, l) for l in lifts for m in (motor, E.carrier_rough(hinge))]
  best = None
  for extra in np.arange(0.0, 20.1, 1.0):
    f = fixed_fn(extra)
    if any((p ^ f).volume() > 1e-3 for p in car_parts):
      return extra - 1.0
  return 20.0

for arr, (sp, kp) in {"motor plug to 12, debug to key": (14.0, 5.0), "debug to 12, motor plug to key": (5.0, 14.0)}.items():
  m = motor_variant(sp, kp)
  for md in (-12.5, -10.0, -7.5, -5.0, -2.5):
    for down in (20.0, 30.0):
      ms = margin(md, m, lambda e: stalk_solid(down, e))
      mk = margin(md, m, lambda e: key_solid(e))
      print(f"{arr:32s} mount {md:6.1f} stalk down {down:.0f}: stalk margin {ms:5.1f}  key margin {mk:5.1f}")
EOF
PYTHONPATH=/home/claude/pylib:/home/claude/deliver/hardware/cad python3 explore2.py 2>&1 | tail -30
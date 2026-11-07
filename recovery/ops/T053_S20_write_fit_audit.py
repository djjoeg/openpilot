"""
Extra fit checks on top of the build's own: every part against the dash cover and dash clamp, the motor's screw
heads against the motor gear, the switch's screws, the setup gauge in place, bolt lengths, and the Bambu A1 bed.

Run from hardware/cad:  PYTHONPATH=/home/claude/pylib python3 fit_audit.py
"""
import json
import math
import sys

import numpy as np

sys.path.insert(0, ".")
import params as P  # noqa: E402
import assembly as AS  # noqa: E402
import mountparts as MP  # noqa: E402
import wheelparts as WP  # noqa: E402
from cadlib import box, cyl, cyl_x, cyl_y  # noqa: E402

t = WP.Teeth(P.WHEEL_OD, P.GRIP, 29)
t15 = WP.Teeth(P.WHEEL_OD, P.GRIP, 15)
parts = {"teeth": WP.teeth_solid(t), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "bracket": MP.lever_bracket(),
         "lever": MP.lift_lever(), "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(),
         "clamp": MP.dash_clamp()}
fits = {}
for tilt in P.COLUMN_TILT_RANGE[:1] + (P.COLUMN_TILT,) + P.COLUMN_TILT_RANGE[1:]:
  fits[tilt] = AS.solve(t, P.ARM_PIVOT_UP, P.ARM_PIVOT_FORWARD, tilt)

res = {}


def ov(a, b):
  return AS.overlap(a, b)


def check(tag, pairs):
  for k, (a, b) in pairs.items():
    res[f"{tag}: {k}"] = max(res.get(f"{tag}: {k}", 0.0), ov(a, b))


# ---- motor screw heads (carrier frame, then carried like the carrier) ----
# ISO 4762 M3 socket head: up to 5.5 mm across (5.68 knurled), 3.0 mm tall, sitting in the carrier's 2.6 mm counterbore
def screw_heads(dk=5.5, k=3.0):
  z0 = P.MOTOR_PLATE_T - 2.6
  m = None
  for sx in (-1, 1):
    for sy in (-1, 1):
      c = cyl(dk / 2, z0, z0 + k, sx * P.NEMA_HOLES / 2, sy * P.NEMA_HOLES / 2, 48)
      m = c if m is None else m + c
  return m


def gear_with(extra_r=0.0, gap_cut=0.0):
  """The motor gear, its roller grown by extra_r and moved gap_cut closer to the carrier's plate."""
  g = parts["gear"]
  if extra_r:
    off = -P.Z_MOTOR_FACE
    zr0, zr1 = (z + off for z in P.Z_GEAR_ROLLER)
    g = g + cyl(P.ROLLER_R + extra_r, zr0, zr1, segments=360)
  return g.translate((0, 0, -gap_cut))


heads_soc = screw_heads(5.5, 3.0)
heads_soc_max = screw_heads(5.68, 3.0)
heads_button = screw_heads(5.7, 1.65)      # ISO 7380 M3 button head
for name, heads in (("socket head", heads_soc), ("socket head, largest allowed", heads_soc_max), ("button head", heads_button)):
  res[f"motor screws ({name}) / motor gear, as designed (0.5 mm gap)"] = ov(heads, gear_with())
  res[f"motor screws ({name}) / motor gear, gear pushed to 0.2 mm, roller 0.1 mm oversize"] = ov(heads, gear_with(0.1, 0.3))
  res[f"motor screws ({name}) / motor gear, gear pushed against the plate, roller 0.15 mm oversize"] = ov(heads, gear_with(0.15, 0.5))

# ---- switch screws: M2 x 16 from the front wall's face, through to the back ----
def switch_screws():
  m = None
  for sx in (-1, 1):
    x = MP.SW_X + sx * P_SW_PITCH / 2 if False else MP.SW_X + sx * MP.SW_PITCH / 2
    shank = AS.cyl(1.0, MP.CAGE_FRONT[1] - 16.0, MP.CAGE_FRONT[1], x, MP.SW_HOLES, 24) if False else None
    # along z: from the front face (CAGE_FRONT[1]) back 16 mm; head 3.8 x 2 in front
    s = cyl(1.0, MP.CAGE_FRONT[1] - 16.0, MP.CAGE_FRONT[1], x, MP.SW_HOLES, 24)
    h = cyl(1.9, MP.CAGE_FRONT[1], MP.CAGE_FRONT[1] + 2.0, x, MP.SW_HOLES, 24)
    part = s + h
    m = part if m is None else m + part
  return m


SWS = switch_screws()

# ---- lever bolt: M4 x 35 along x through the bracket's legs, head 7 x 4, nyloc nut 7 AF x 5 ----
def lever_bolt():
  y, z = MP.LEVER_PIVOT
  half = MP.BR_LEG_X[1]
  w = 0.8
  shank = cyl_x(2.0, -half - w - 4.0, -half - w - 4.0 + 35.0, y=y, z=z, segments=24)
  head = cyl_x(3.5, -half - w - 4.0, -half - w, y=y, z=z, segments=24)
  nut = cyl_x(4.05, half + w, half + w + 5.0, y=y, z=z, segments=6)
  washers = cyl_x(4.5, -half - w, -half, y=y, z=z, segments=24) + cyl_x(4.5, half, half + w, y=y, z=z, segments=24)
  return shank + head + nut + washers


LB = lever_bolt()

for tilt, fit in fits.items():
  A = AS.Assembly(t, fit, dict(parts), tilt)
  hood, CL, HB, AR = A.hood(), A.clamp(), A.hinge_block(), A.arm()
  T, W = A.teeth(), A.wheel_grip()
  tag = f"tilt {tilt}"
  # lever down
  G, C, M, BR, SW = A.gear(), A.carrier(), A.motor(), A.bracket(), A.switch()
  LV = A.lever(0.0, 0.0)
  sws = A._carried(SWS, 0.0)
  lb = A._carried(MP.lever_in_carrier(LB, 0.0) if False else LB, 0.0)
  fixed = {"dash cover": hood, "dash clamp": CL}
  movers = {"motor gear": G, "carrier": C, "motor, board and plugs": M, "lever bracket": BR, "switch": SW, "lift lever": LV,
            "switch screws": sws, "lever bolt": lb, "hinge block": HB, "steering wheel teeth": T}
  for fn, f in fixed.items():
    check(f"{tag}, lever down", {f"{mn}/{fn}": (m, f) for mn, m in movers.items()})
  check(f"{tag}, lever down", {"switch screws/hinge block": (sws, HB), "lever bolt/hinge block": (lb, HB), "lever bolt/arm": (lb, AR),
                               "switch screws/arm": (sws, AR)})
  # lever up, and every angle on the way
  for alpha in list(np.arange(4.0, MP.A_OFF, 4.0)) + [MP.A_OFF]:
    th = max(0.0, MP.cam_lift(alpha)) + 0.05
    lv = A.lever(alpha, th, part="lever_no_tab")
    pieces = {"lift lever": lv, "carrier": A.carrier(th), "motor, board and plugs": A.motor(th), "lever bracket": A.bracket(th),
              "switch": A.switch(th), "switch screws": A._carried(SWS, th), "lever bolt": A._carried(LB, th)}
    for fn, f in fixed.items():
      check(f"{tag}, lever moving up", {f"{mn}/{fn}": (m, f) for mn, m in pieces.items()})
    check(f"{tag}, lever moving up", {"switch screws/hinge block": (A._carried(SWS, th), HB),
                                      "lever bolt/hinge block": (A._carried(LB, th), HB),
                                      "lever bolt/arm": (A._carried(LB, th), AR)})
  # steering wheel turned past the teeth, both sets, carrier dropped
  rest = A.rest_on_grip_lift()
  for ts, turn in ((t, 70.0), (t15, t15.half + 17.0)):
    Tt = WP.teeth_solid(ts).rotate((0, 0, turn))
    Tt2 = WP.teeth_solid(ts).rotate((0, 0, -turn))
    pieces = {"motor, board and plugs": A.motor(rest), "switch": A.switch(rest), "lift lever": A.lever(0.0, rest),
              "switch screws": A._carried(SWS, rest), "lever bolt": A._carried(LB, rest)}
    for side, TT in (("left", Tt), ("right", Tt2)):
      check(f"{tag}, {ts.reach} teeth turned {side}", {f"{mn}/turned teeth": (m, TT) for mn, m in pieces.items()})
    check(f"{tag}, carrier dropped", {"switch screws/hinge block": (A._carried(SWS, rest), HB),
                                     "lever bolt/hinge block": (A._carried(LB, rest), HB)})
  # setup gauge in place (lever down, gear on the teeth)
  gauge = A._carried(MP.setup_gauge(), 0.0)
  spring = A._carried(cyl_y(MP.SPRING_OD / 2, P.NEMA / 2 + 8.5 - MP.SPRING_SEAT_D, MP.HB_BOTTOM + MP.SPRING_POCKET_D, z=MP.SPRING_Z,
                            segments=48), 0.0)
  check(f"{tag}, setup gauge in", {"gauge/lever bracket": (gauge, BR), "gauge/spring": (gauge, spring), "gauge/switch": (gauge, SW),
                                   "gauge/carrier": (gauge, C), "gauge/hinge block": (gauge, HB), "gauge/arm": (gauge, AR),
                                   "gauge/lift lever": (gauge, LV)})

touching = {k: round(v, 3) for k, v in res.items() if v > 1e-3}
print(json.dumps({"checks": len(res), "touching": touching}, indent=1))
json.dump({k: round(v, 4) for k, v in res.items()}, open("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fitaudit/fit_audit.json", "w"), indent=1)

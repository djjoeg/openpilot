"""
Clearance checks for the right arm mount v2 (2 Nov 2026): every part, bolt and wing-bolt sweep against each other and
against the steering wheel's grip and the teeth piece, with the motor slid in (at the stop) and slid out, the stop
anywhere in its +-4 mm (the teeth piece moved the same way, as when the plate sits nearer or further than measured),
and the steering wheel turned.

  python3 rightcheck.py      # prints every check; exit 1 if any fails
"""
import math
import sys

from manifold3d import Manifold

import midteeth as MT
import rightarm as RA
import sideparts as S
from cadlib import box, cyl, cyl_y, hex_prism_z, revolve, union

TOL = 0.5    # mm^3: overlaps below this are touching faces


def grip() -> Manifold:
  grip_r = S.FP.GRIP / 2.0
  rr = S.FP.WHEEL_OD / 2.0 - grip_r
  circle = [(rr + grip_r * math.cos(math.radians(a)), grip_r * math.sin(math.radians(a))) for a in range(0, 360, 10)]
  return revolve(circle, -180.0, 180.0, step_deg=2.0)


def teeth_piece() -> Manifold:
  return MT.mid_teeth(MT.MidTeeth(n_teeth=10))


def wing_bolt(length: float = 20.0) -> Manifold:
  """An M5 wing bolt along -z from its head's underside at z = 0 (the shank down, the head and wings up)."""
  shank = cyl(2.45, -length, 0.05, segments=24)
  head = cyl(5.0, 0.05, 3.0, segments=32) + box(-9.0, 9.0, -1.2, 1.2, 2.0, 9.0)
  return shank + head


def sweep(length: float = 20.0) -> Manifold:
  """The room a wing bolt's wings need to be turned: a disc of their reach, as tall as the head."""
  return cyl(9.2, 0.05, 9.0, segments=48) + cyl(2.45, -length, 0.05, segments=24)


def nut() -> Manifold:
  return hex_prism_z(7.95, -2.0, 2.0) - cyl(2.5, -3.0, 3.0, segments=24)


def place_z(m: Manifold, x: float, y: float, z: float, down: bool = True) -> Manifold:
  """m (built along -z from z = 0) with its z = 0 at (x, y, z); pointing down the column, or up it."""
  if not down:
    m = m.rotate((180.0, 0.0, 0.0))
  return m.translate((x, y, z))


def hardware(dz: float, stop_p: float, swept: bool = False) -> dict:
  """The bolts and nuts in the steering wheel frame, the motor slid dz from the nominal depth and the stop poking
  stop_p below the cap. swept: the wing bolts as the room their wings need."""
  wb = sweep() if swept else wing_bolt()
  out = {}
  # the foot's two bolts: heads on the foot's face towards you, nuts in the arm's dash face
  for i, x in enumerate(RA.ARM_HOLES_X):
    out[f"foot bolt {i + 1}"] = place_z(wb, x, RA.ARM_HOLES_Y, RA.FOOT_Z[1])
    out[f"foot nut {i + 1}"] = place_z(nut(), x, RA.ARM_HOLES_Y, RA.ARM_Z[0] + 2.0)
  # the pivot and the arc bolt: heads on the tab, nuts in the flag's dash side
  for name, (x, y) in (("pivot", RA.PIVOT), ("arc", (RA.PIVOT[0] - RA.ARC_R, RA.PIVOT[1]))):
    out[f"{name} bolt"] = place_z(wb, x, y, RA.TAB_Z[1])
    out[f"{name} nut"] = place_z(nut(), x, y, RA.FLAG_Z[0] + 2.0)
  # the stop: down through the cap's nut, its tip stop_p below the cap
  su, sv = RA.STOP_UV
  sx, sy = RA.rad(su, sv)
  head_z = RA.CAP_Z[1] + (20.0 - (RA.CAP_Z[1] - RA.CAP_Z[0]) - stop_p)
  out["stop bolt"] = place_z(wb, sx, sy, head_z)
  out["stop nut"] = place_z(nut(), sx, sy, RA.CAP_Z[1] - 2.2)
  out["stop jam nut"] = place_z(nut(), sx, sy, RA.CAP_Z[1] + 2.05)
  # the pinch bolt: along v through the -V wall's nut onto the tongue's -V face
  pu, pz = RA.PINCH_UZ
  tip_v = RA.TONGUE_V[0]
  pin = (sweep() if swept else wing_bolt()).rotate((-90.0, 0.0, 0.0))          # -z -> +y (the shank along +v)
  out["pinch bolt"] = pin.translate((pu, tip_v - 20.0, pz)).rotate((0.0, 0.0, RA.THETA))
  pn = (hex_prism_z(7.95, -2.0, 2.0) - cyl(2.5, -3.0, 3.0, segments=24)).rotate((-90.0, 0.0, 0.0))
  out["pinch nut"] = pn.translate((pu, RA.PINCH_NUT_V, pz)).rotate((0.0, 0.0, RA.THETA))
  return out


def overlap(a: Manifold, b: Manifold) -> float:
  return (a ^ b).volume()


def run() -> bool:
  ok = True
  results = []

  def check(what: str, a: Manifold, b: Manifold, tol: float = TOL):
    nonlocal ok
    v = overlap(a, b)
    good = v <= tol
    ok = ok and good
    results.append((good, what, v))

  plate = RA.plate_to_wheel(RA.frame_plate_v4())
  arm, bar, bracket = RA.arm(), RA.bar(), RA.bracket()
  import carscene as CS
  cover = CS.CarScene(D=125.0).column_cover(back=130.0)
  fixed = {"plate": plate, "arm": arm, "bar": bar, "bracket": bracket, "column cover": cover}
  g, teeth = grip(), teeth_piece()

  # 1. the fixed parts against each other (the arm sits in the receiver, the foot on the arm, the tab on the flag)
  names = list(fixed)
  for i in range(len(names)):
    for j in range(i + 1, len(names)):
      check(f"{names[i]} / {names[j]}", fixed[names[i]], fixed[names[j]])

  # 2. the carrier, motor, board and gear, slid anywhere from the deepest stop to the bottom, against the fixed parts
  for dz in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW, RA.DZ_OUT):
    mg = RA.motor_and_gear(dz)
    moving = {"carrier": RA.carrier(dz), "motor": mg["motor"], "board": mg["board"], "gear": mg["gear"]}
    for mn, mm in moving.items():
      for fn, fm in fixed.items():
        check(f"slid {dz:+.0f}: {mn} / {fn}", mm, fm)
    check(f"slid {dz:+.0f}: carrier / motor", moving["carrier"], mg["motor"])

  # 3. the bolts and nuts, and the room to turn the wing bolts, with the motor at the deepest, nominal, shallowest
  # stop and slid out: against the parts and the motor (not against what they go through: holes are clear)
  for dz, p in ((RA.DZ_DEEP, RA.STOP_P - RA.DZ_DEEP), (0.0, RA.STOP_P), (RA.DZ_SHALLOW, RA.STOP_P - RA.DZ_SHALLOW)):
    for slid in (dz, RA.DZ_OUT):
      mg = RA.motor_and_gear(slid)
      moving = {"carrier": RA.carrier(slid), "motor": mg["motor"], "board": mg["board"], "gear": mg["gear"]}
      for swept in (False, True):
        hw = hardware(slid, p, swept)
        for hn, hm in hw.items():
          if swept and "nut" in hn:
            continue
          for on, om in {**fixed, **moving}.items():
            if swept and on in ("arm", "bar", "bracket", "plate") and hn.startswith(("foot", "pivot", "arc", "pinch", "stop")):
              # the sweep's own shank goes through its part; check only the head's room
              om = om - cyl(1000.0, -1000.0, -999.0)
              hm_head = hm - hardware_shank(hn, slid, p)
              check(f"stop {p:.0f}, slid {slid:+.0f}: {hn} {'wings turning' if swept else ''} / {on}", hm_head, om)
            elif not swept:
              check(f"stop {p:.0f}, slid {slid:+.0f}: {hn} / {on}", hm, om)
            else:
              check(f"stop {p:.0f}, slid {slid:+.0f}: {hn} wings turning / {on}", hm, om)

  # 4. the steering wheel turned, the teeth piece where the stop puts the gear in mesh (s = how far nearer you the
  # teeth piece sits than drawn): nothing but the gear may touch the grip or the teeth piece; slid out, not even the gear
  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_P - s
    mg = RA.motor_and_gear(s)
    near = {"carrier": RA.carrier(s), "motor": mg["motor"], "board": mg["board"], **fixed}
    hw = {k: v for k, v in hardware(s, p, True).items() if "nut" not in k}
    for a in range(-40, 41, 5):
      t = teeth.rotate((0.0, 0.0, RA.THETA + a)).translate((0.0, 0.0, s))
      gr = g.translate((0.0, 0.0, s))
      for n, m in {**near, **hw}.items():
        check(f"teeth {s:+.0f} mm, wheel {a:+d} deg: {n} / teeth piece", m, t)
        check(f"teeth {s:+.0f} mm, wheel {a:+d} deg: {n} / grip", m, gr)
      out = RA.motor_and_gear(s - 6.0)["gear"]
      check(f"teeth {s:+.0f} mm, wheel {a:+d} deg: gear slid out 6 mm / teeth piece", out, t)

  bad = [r for r in results if not r[0]]
  print(f"{len(results)} checks, {len(bad)} failed")
  for good, what, v in bad[:60]:
    print(f"  FAIL {what}: {v:.1f} mm3")
  return ok


def hardware_shank(name: str, dz: float, p: float) -> Manifold:
  """The shank of a swept wing bolt (it goes through its own part's hole)."""
  hw = hardware(dz, p, swept=True)
  m = hw[name]
  # everything of the sweep below its head's underside: the sweep's disc starts 0.05 above the underside
  if name.startswith("pinch"):
    pu, pz = RA.PINCH_UZ
    tip_v = RA.TONGUE_V[0]
    sh = cyl_y(2.46, tip_v - 20.1, tip_v + 0.1, x=pu, z=pz, segments=24).rotate((0.0, 0.0, RA.THETA))
    return sh
  bb = m.bounding_box()
  cx, cy = (bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2
  top = bb[5] - 9.0
  return cyl(2.46, top - 20.1, top + 0.1, x=cx, y=cy, segments=24)


if __name__ == "__main__":
  sys.exit(0 if run() else 1)

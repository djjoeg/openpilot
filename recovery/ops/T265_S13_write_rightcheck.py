"""
Checks for the right arm mount v3 (2 Nov 2026): that the motor carrier goes in, and that every part, bolt and
wing-bolt sweep clears the others, the steering wheel's grip and the teeth piece: the carrier slid anywhere from its
end on the tower's top to the deepest stop, the stop anywhere in its +-4 mm (the teeth piece moved the same way, as
when the plate sits nearer or further than measured), the arm slid 20 mm in or out across, and the steering wheel
turned. Then the gear in mesh over the teeth's whole arc.

  python3 rightcheck.py      # prints the count and every failure; exit 1 if any fails
"""
import math
import sys

import numpy as np
from manifold3d import Manifold

import midteeth as MT
import rightarm as RA
import sideparts as S
from cadlib import box, cyl, cyl_y, hex_prism_z, revolve

TOL = 0.5    # mm^3: overlaps below this are touching faces
MESH_PHASE = 10.5   # the gear's turn on its shaft that puts it in step with the teeth (found by a search, 2 Nov 2026)


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


def nut(rot: float = 30.0) -> Manifold:
  """An M5 nut along z, centred on z = 0."""
  return hex_prism_z(7.95, -2.0, 2.0, rot=rot) - cyl(2.5, -3.0, 3.0, segments=24)


def in_motor_frame(m: Manifold, u: float, v: float, z: float) -> Manifold:
  """m (built in the motor's frame at the origin) placed at (u, v, z) of the motor's frame, in the steering wheel frame."""
  return m.translate((u, v, z)).rotate((0.0, 0.0, RA.THETA))


def hardware(dz: float, stop_p: float, swept: bool = False, arm_dx: float = 0.0) -> dict:
  """The bolts and nuts in the steering wheel frame: the carrier slid dz from the nominal depth, the stop bolt
  poking stop_p above the lug, the arm slid arm_dx across (+ to your right). swept: the wing bolts as the room their
  wings need."""
  wb = sweep() if swept else wing_bolt()
  out = {}
  # the receiver's wing bolt: in the plate frame along -y through the dash-side wall at PINCH_X, its nut in the wall
  pz = RA.PLATE_T + RA.BORE_DEPTH / 2
  bolt = wb.rotate((-90.0, 0.0, 0.0)).translate((RA.PINCH_X, RA.TUBE_Y[1], pz))       # -z -> -y
  yn = (RA.BORE_Y[1] + RA.TUBE_Y[1]) / 2
  out["receiver bolt"] = RA.plate_to_wheel(bolt)
  out["receiver nut"] = RA.plate_to_wheel(nut().rotate((90.0, 0.0, 0.0)).translate((RA.PINCH_X, yn, pz)))
  # the push bolt: along -u through the tower's outer wall onto the bar's face, its nut in the slot in that wall
  pv, pzz = RA.PUSH_VZ
  out["push bolt"] = in_motor_frame(wb.rotate((0.0, 90.0, 0.0)), RA.BAR_U[1] + 20.0, pv, pzz)        # -z -> -u
  out["push nut"] = in_motor_frame(nut(rot=0.0).rotate((0.0, 90.0, 0.0)), sum(RA.PUSH_NUT_U) / 2, pv, pzz)
  # the stop: up through the lug's nut, its tip stop_p above the lug, the jam nut under the lug, the head below
  su, sv = RA.STOP_UV
  sx, sy = RA.rad(su, sv)
  lug_top = RA.TOWER_Z[0] - RA.STOP_P + dz
  out["stop bolt"] = (sweep() if swept else wing_bolt()).rotate((180.0, 0.0, 0.0)).translate((sx, sy, lug_top + stop_p - 20.0))
  out["stop nut"] = nut(rot=30.0 + RA.THETA).translate((sx, sy, lug_top - 2.4))
  out["stop jam nut"] = nut(rot=30.0 + RA.THETA).translate((sx, sy, lug_top - RA.LUG_T - 2.05))
  fixed = ("receiver bolt", "receiver nut")                 # in the plate; the rest move with the arm across
  return {k: (m if k in fixed else m.translate((arm_dx, 0.0, 0.0))) for k, m in out.items()}


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

  import carscene as CS
  plate = RA.plate_to_wheel(RA.frame_plate_v4())
  cover = CS.CarScene(D=125.0).column_cover(back=130.0)
  arm = RA.arm()
  fixed = {"plate": plate, "arm": arm, "column cover": cover}
  g, teeth = grip(), teeth_piece()

  def moving(dz: float) -> dict:
    mg = RA.motor_and_gear(dz)
    return {"carrier": RA.carrier(dz), "motor": mg["motor"], "board": mg["board"], "gear": mg["gear"]}

  # 1. the fixed parts against each other (the arm in the receiver), and the arm slid 20 mm in or out across
  check("plate / arm", plate, arm)
  check("plate / column cover", plate, cover)
  check("arm / column cover", arm, cover)
  for dx in (-20.0, 20.0):
    a = arm.translate((dx, 0.0, 0.0))
    check(f"arm slid {dx:+.0f} across / plate", a, plate)
    check(f"arm slid {dx:+.0f} across / column cover", a, cover)
    for hn, hm in hardware(0.0, RA.STOP_P, True, dx).items():
      if "receiver" not in hn and "nut" not in hn:
        check(f"arm slid {dx:+.0f} across: {hn} wings turning / receiver bolt",
              hm, hardware(0.0, RA.STOP_P, True)["receiver bolt"])

  # 2. the carrier goes in: with the motor on it, slid out, it comes in sideways from the motor's side (+v) into the
  # channel, past nothing
  for dz in (RA.DZ_OUT, RA.DZ_END):
    for t in np.arange(0.0, 42.0, 2.0):
      off = (float(t * RA.V[0]), float(t * RA.V[1]), 0.0)
      for mn, mm in moving(dz).items():
        for fn, fm in fixed.items():
          check(f"going in, slid {dz:+.0f}, {t:.0f} mm short: {mn} / {fn}", mm.translate(off), fm)

  # 3. the carrier, motor, board and gear slid anywhere from the web on the tower's top to the deepest stop
  dzs = [float(d) for d in np.arange(RA.DZ_END, RA.DZ_DEEP + 0.5, 1.0)]
  for dz in dzs:
    mv = moving(dz)
    for mn, mm in mv.items():
      for fn, fm in fixed.items():
        check(f"slid {dz:+.0f}: {mn} / {fn}", mm, fm)
    check(f"slid {dz:+.0f}: carrier / motor", mv["carrier"], mv["motor"])
    check(f"slid {dz:+.0f}: carrier / gear", mv["carrier"], mv["gear"])

  # 4. the bolts and nuts, and the room to turn the wing bolts: the stop set for the deepest, nominal and shallowest
  # depth, the carrier at its stop, slid out 10 and on the tower's top; against the parts and the motor (their
  # shanks go through clearance holes, so the bolts' own holes and nut pockets count as clear)
  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_P - s
    for slid in (s, RA.DZ_OUT, RA.DZ_END):
      mv = moving(slid)
      for swept in (False, True):
        hw = hardware(slid, p, swept)
        for hn, hm in hw.items():
          if swept and "nut" in hn:
            continue
          for on, om in {**fixed, **mv}.items():
            check(f"stop {p:.1f}, slid {slid:+.0f}: {hn}{' wings turning' if swept else ''} / {on}", hm, om)
        if not swept:
          names = list(hw)
          for i in range(len(names)):
            for j in range(i + 1, len(names)):
              check(f"stop {p:.1f}, slid {slid:+.0f}: {names[i]} / {names[j]}", hw[names[i]], hw[names[j]])

  # 5. the steering wheel turned, the teeth piece where the stop puts the gear in mesh (s = how far nearer you the
  # teeth piece sits than drawn): nothing but the gear may touch the grip or the teeth piece; slid out 6 mm, not even
  # the gear
  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_P - s
    mv = moving(s)
    near = {"carrier": mv["carrier"], "motor": mv["motor"], "board": mv["board"], **fixed}
    hw = {k: v for k, v in hardware(s, p, True).items() if "nut" not in k}
    out = RA.motor_and_gear(s - 6.0)["gear"]
    for a in range(-40, 41, 5):
      t = teeth.rotate((0.0, 0.0, RA.THETA + a)).translate((0.0, 0.0, s))
      gr = g.translate((0.0, 0.0, s))
      for n, m in {**near, **hw}.items():
        check(f"teeth {s:+.0f} mm, wheel {a:+d} deg: {n} / teeth piece", m, t)
        check(f"teeth {s:+.0f} mm, wheel {a:+d} deg: {n} / grip", m, gr)
      check(f"teeth {s:+.0f} mm, wheel {a:+d} deg: gear slid out 6 mm / teeth piece", out, t)

  # 6. the gear in mesh at the nominal depth, phased, over the teeth's whole arc (the 11 teeth)
  g0 = S.side_gear_teeth_only()
  t = MT.MidTeeth(n_teeth=10)
  c = RA.R_FACE_OUT * RA.U
  mat = [[0.0, RA.V[0], -RA.U[0], float(c[0])], [0.0, RA.V[1], -RA.U[1], float(c[1])], [1.0, 0.0, 0.0, RA.Z_AXIS]]
  w = -t.teeth_half
  while w <= t.teeth_half + 1e-9:
    gm = g0.rotate((0.0, 0.0, MESH_PHASE + S.FP.FACE_RATIO * w)).transform(mat)
    check(f"gear in mesh, wheel {w:+.1f} deg / teeth", gm, teeth.rotate((0.0, 0.0, RA.THETA + w)), tol=1e-3)
    w += 0.5

  bad = [r for r in results if not r[0]]
  print(f"{len(results)} checks, {len(bad)} failed")
  for good, what, v in bad[:80]:
    print(f"  FAIL {what}: {v:.1f} mm3")
  return ok


if __name__ == "__main__":
  sys.exit(0 if run() else 1)

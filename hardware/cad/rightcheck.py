"""
Checks for the right arm mount v6, the fit print, on the frame plate v5 (3 Nov 2026; v5, v4 and v3 before): that the
motor carrier goes down into the tower's tube (off the car) and the slide's wing bolt in through the groove, the arm
with everything on it into the receiver from the key side, past the plate, the column cover, the grip, the teeth
and the car's parts round the key, and the receiver's wing bolt in through its groove; and that every part, bolt
and wing-bolt sweep clears the others, the steering wheel's grip, the teeth piece and the car: the carrier slid
anywhere in the tower's groove, from its end on the tower's top to the groove's top, the teeth piece 12 mm nearer or
further than drawn (as when the plate sits nearer or further than measured) with the gear at the drawn depth in it,
the arm slid anywhere in the receiver's groove (17.5 mm either way across), and the steering wheel turned, with each
of the three teeth sets (11, 15 and 20; the 20 is the one on the car). Then the gear in mesh over each set's whole arc.

The car's parts are the photo estimates (carscene.py, D = 125, as the column cover): the key's bulge and bezel, the
key in it and the room to turn it, the wiper stalk through its whole swing (at rest while the arm goes in), and the
dash's face below the column (no nearer than the frame plate's dash-side edge, which your printed plate showed
clears it: 1.4 mm further than the estimate); and the cup screw's head with a fender washer under it, on the plate.
The arm is checked against the plate anywhere in the receiver's groove, and against the car where it can be when
the gear is in the teeth (GEAR_IN further in to GEAR_OUT further out than drawn) and on its way in from the key
side: when the plate sits off where it's drawn, the arm slides in the receiver to keep the gear on the teeth.

That the parts work, not only that they clear (v3's open channel and v4's turning nut passed every clearance
check): every captive nut too tight in its slot to turn, even a nut at the smallest size the standard allows; the
carrier and the arm held in every direction (each groove's ends stop its wing bolt, the tower's top stops the
carrier, the tube and the receiver's bore all round); and the slides' clearances. The stiffness under the motor's
push is checked by stiffness.py.

  python3 rightcheck.py      # prints the count and every failure; exit 1 if any fails
"""
import math
import sys

import numpy as np
from manifold3d import Manifold

import midteeth as MT
import rightarm as RA
import sideparts as S
from cadlib import box, cyl, cyl_x, hex_prism_z, revolve

TOL = 0.5    # mm^3: overlaps below this are touching faces
MESH_PHASE = 10.5   # the gear's turn on its shaft that puts it in step with the teeth (found by a search, 2 Nov 2026;
                    # every set has a tooth in its middle, so the same phase fits all three)
TEETH_SETS = ((18, "20"), (14, "15"), (10, "11"))   # MidTeeth's n_teeth and the set's name; the 20 is the one fitted
SCENE_D = 125.0      # the car scene's D, as for the column cover
GEAR_IN, GEAR_OUT = 4.0, 3.0   # lining the gear up along the teeth: the arm this far further in or out across than
                               # drawn, relative to the steering wheel (in by 5 the carrier meets the teeth piece;
                               # out by 4, the motor slid off, the wiper stalk pushed all the way down meets the gear)


def grip() -> Manifold:
  grip_r = S.FP.GRIP / 2.0
  rr = S.FP.WHEEL_OD / 2.0 - grip_r
  circle = [(rr + grip_r * math.cos(math.radians(a)), grip_r * math.sin(math.radians(a))) for a in range(0, 360, 10)]
  return revolve(circle, -180.0, 180.0, step_deg=2.0)


def teeth_piece(n_teeth: int = 18) -> Manifold:
  return MT.mid_teeth(MT.MidTeeth(n_teeth=n_teeth))


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


M5_E_MIN = 8.79      # the smallest across-corners an M5 nut may have (ISO 4032): the one most likely to turn
NUT_LOCK = 0.3       # mm^3 its corners must cut into the slot's walls when turned (both slots 8.3 across the flats:
                     # its corners go 0.25 mm into each wall)


def nut_min(rot: float) -> Manifold:
  """An M5 nut at the standard's smallest across-corners, along z, centred on z = 0 (to show it can't turn)."""
  return hex_prism_z(M5_E_MIN * math.cos(math.radians(30)), -1.9, 1.9, rot=rot)


def in_motor_frame(m: Manifold, u: float, v: float, z: float) -> Manifold:
  """m (built in the motor's frame at the origin) placed at (u, v, z) of the motor's frame, in the steering wheel frame."""
  return m.translate((u, v, z)).rotate((0.0, 0.0, RA.THETA))


def slide_nut(dz: float = 0.0, small_turned: bool = False) -> Manifold:
  """The slide's M5 nut in the carrier's bar, its axis along u, flats facing along the column (as in its slot);
  small_turned: the smallest standard nut turned 30 degrees, corners towards the slot's walls."""
  m = nut_min(0.0) if small_turned else nut(rot=30.0)
  return in_motor_frame(m.rotate((0.0, 90.0, 0.0)), sum(RA.SLIDE_NUT_U) / 2, RA.BAR_UV[1], RA.SLIDE_Z0 + dz)


def receiver_nut(arm_dx: float = 0.0, small_turned: bool = False) -> Manifold:
  """The receiver's M5 nut in the arm's bar, its axis along the column, flats facing along the bar (as in its slot)."""
  m = nut_min(0.0) if small_turned else nut(rot=30.0)
  return m.translate((RA.ARM_NUT_X + arm_dx, RA.ARM_BOLT_Y, sum(RA.ARM_NUT_Z) / 2))


RECEIVER_FACE = RA.CUP_Z - RA.TUBE_Y[0]      # -160: the receiver's wheel-side face, where its washer sits


def hardware(dz: float = 0.0, swept: bool = False, arm_dx: float = 0.0) -> dict:
  """The bolts, washers and nuts in the steering wheel frame: the carrier slid dz from the nominal depth, the arm
  slid arm_dx across (+ to your right). swept: the wing bolts as the room their wings need."""
  wb = sweep() if swept else wing_bolt()
  out = {}
  # the receiver's slide (v6): the wing bolt along -z, towards the dash, through a fender washer and the groove in
  # the receiver's wall on your side into the nut in the arm's bar; all three move with the arm
  x, y, f = RA.ARM_NUT_X, RA.ARM_BOLT_Y, RECEIVER_FACE
  out["receiver bolt"] = wb.translate((x, y, f + RA.WASHER_T))
  out["receiver washer"] = cyl(RA.WASHER_OD / 2, f, f + RA.WASHER_T, x=x, y=y, segments=48) - \
    cyl(2.7, f - 1.0, f + RA.WASHER_T + 1.0, x=x, y=y, segments=24)
  out["receiver nut"] = receiver_nut()
  # the motor's slide (v5): the wing bolt along -u through a fender washer and the tower's groove into the nut in the
  # carrier's bar; all three move with the carrier
  bv, zz = RA.BAR_UV[1], RA.SLIDE_Z0 + dz
  face = RA.TOWER_U[1]
  out["slide bolt"] = in_motor_frame(wb.rotate((0.0, 90.0, 0.0)), face + RA.WASHER_T, bv, zz)       # -z -> -u
  washer = cyl_x(RA.WASHER_OD / 2, face, face + RA.WASHER_T, y=bv, z=zz, segments=48) - \
    cyl_x(2.7, face - 1.0, face + RA.WASHER_T + 1.0, y=bv, z=zz, segments=24)
  out["slide washer"] = washer.rotate((0.0, 0.0, RA.THETA))
  out["slide nut"] = slide_nut(dz)
  return {k: m.translate((arm_dx, 0.0, 0.0)) for k, m in out.items()}


def cup_screw() -> Manifold:
  """The cup screw's head (#8 pan head) and a fender washer under it, on the plate's face (plate frame at the cup)."""
  T = RA.PLATE_T
  return RA.plate_to_wheel(cyl(6.25, T, T + 4.5, segments=48) + cyl(12.5, T, T + 1.6, segments=48))


def car_parts(stalk_at_rest: bool = False) -> dict:
  import carscene as CS
  sc = CS.CarScene(D=SCENE_D)
  edge = RA.CUP_Z - max(RA.BLOCK[3], RA.BAR[3])          # the frame plate's dash-side edge, -195
  dash = sc.bolster().translate((0.0, 0.0, min(0.0, edge - sc.dash_z)))
  stalk = ("wiper stalk at rest", sc.stalk(down=0.0, up=0.0)) if stalk_at_rest else ("wiper stalk, its whole swing", sc.stalk())
  return {**sc.key_parts(), stalk[0]: stalk[1], "dash face": dash}


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

  def blocked(what: str, a: Manifold, b: Manifold, least: float = 1.0):
    """a must run into b (a stop, a wall, a nut that can't turn)."""
    nonlocal ok
    v = overlap(a, b)
    good = v >= least
    ok = ok and good
    results.append((good, what + " (must be blocked)", v))

  def within(what: str, v: float, lo: float, hi: float):
    nonlocal ok
    good = lo <= v <= hi
    ok = ok and good
    results.append((good, f"{what} = {v:.2f}, wanted {lo} to {hi}", v))

  import carscene as CS
  plate = RA.plate_to_wheel(RA.frame_plate_v5())
  cover = CS.CarScene(D=SCENE_D).column_cover(back=130.0)
  arm = RA.arm()
  screw = cup_screw()
  fixed = {"plate": plate, "arm": arm, "column cover": cover, "cup screw": screw}
  car = car_parts()
  g = grip()
  pieces = {name: teeth_piece(n) for n, name in TEETH_SETS}

  def moving(dz: float) -> dict:
    mg = RA.motor_and_gear(dz)
    return {"carrier": RA.carrier(dz), "motor": mg["motor"], "board": mg["board"], "gear": mg["gear"]}

  # 1. the fixed parts against each other and the car (the arm in the receiver); then the arm slid anywhere in the
  # receiver's groove, with the carrier and every bolt on it (wings turning), against the plate and the cup screw;
  # and where it can be relative to the car with the gear on the teeth, against the cover and the car
  check("plate / arm", plate, arm)
  check("plate / column cover", plate, cover)
  check("arm / column cover", arm, cover)
  check("plate / cup screw", plate, screw)
  check("arm / cup screw", arm, screw)
  for cn, cm in car.items():
    check(f"plate / {cn}", plate, cm)
    check(f"arm / {cn}", arm, cm)

  def on_arm_all(dx: float) -> dict:
    sh = {"arm": arm.translate((dx, 0.0, 0.0))}
    for dz in (0.0, RA.DZ_OUT, RA.DZ_MAX):
      sh.update({f"{k} slid {dz:+.0f}": m.translate((dx, 0.0, 0.0)) for k, m in moving(dz).items()})
    sh.update({f"{k} wings turning": m for k, m in hardware(0.0, True, dx).items() if "nut" not in k and "washer" not in k})
    sh.update({k: m for k, m in hardware(0.0, False, dx).items() if "nut" in k or "washer" in k})
    return sh

  for dx in (-RA.ARM_SLIDE, -9.0, 9.0, RA.ARM_SLIDE):
    for n, m in on_arm_all(dx).items():
      for fn, fm in (("plate", plate), ("cup screw", screw)):
        check(f"arm slid {dx:+.1f} in the receiver: {n} / {fn}", m, fm)
  for dx in (-GEAR_IN, GEAR_OUT):
    for n, m in on_arm_all(dx).items():
      for fn, fm in {"column cover": cover, **car}.items():
        check(f"arm {dx:+.0f} across from drawn (the car): {n} / {fn}", m, fm)

  # 2. it goes together. (a) Off the car: the carrier, motor on it and the slide's nut in its slot, down into the
  # tower's tube from the top, till it sits on the tower (slid all the way out), past the arm; then the slide's wing
  # bolt and washer in along the groove from 20 mm out
  for dz in np.arange(RA.DZ_OUT, 170.0, 4.0):
    mv = {**moving(float(dz)), "slide nut": slide_nut(float(dz))}
    for mn, mm in mv.items():
      check(f"down the tower, {dz - RA.DZ_OUT:.0f} mm up: {mn} / arm", mm, arm)
  hw_out = hardware(RA.DZ_OUT)
  mv_out = moving(RA.DZ_OUT)
  for t in (0.0, 4.0, 8.0, 12.0, 16.0, 20.0):
    out_u = (t * float(RA.U[0]), t * float(RA.U[1]), 0.0)
    for bn in ("slide bolt", "slide washer"):
      for fn, fm in {"arm": arm, **mv_out}.items():
        check(f"slide bolt going in, {t:.0f} mm out: {bn} / {fn}", hw_out[bn].translate(out_u), fm)
  # (b) the arm, with all of that and the receiver's nut in its slot, into the receiver from the key side, the motor
  # slid all the way out, the receiver's wing bolt not in yet, the wheel straight, the wiper stalk at rest: from 104
  # mm out, past the car to GEAR_IN further in than drawn, and past the plate to slid all the way in
  on_arm = {"arm": arm, **mv_out, "receiver nut": hw_out["receiver nut"],
            **{k: v for k, v in hw_out.items() if k.startswith("slide")}}
  near20 = pieces["20"].rotate((0.0, 0.0, RA.THETA))
  past_car = {"column cover": cover, "grip": g, "teeth piece": near20, **car_parts(stalk_at_rest=True)}
  for dx in [float(d) for d in np.arange(-RA.ARM_SLIDE, 104.0, 4.0)] + [-GEAR_IN]:
    off = (dx, 0.0, 0.0)
    against = {"plate": plate, "cup screw": screw, **(past_car if dx >= -GEAR_IN else {})}
    for mn, mm in on_arm.items():
      for fn, fm in against.items():
        check(f"into the receiver, {dx:+.1f} mm out: {mn} / {fn}", mm.translate(off), fm)
  # (c) the receiver's wing bolt and its washer in along the column from your side, from 20 mm out, through the
  # groove into the nut, the arm anywhere in the groove
  for dx in (-RA.ARM_SLIDE, 0.0, RA.ARM_SLIDE):
    hw = hardware(0.0, False, dx)
    for t in (0.0, 4.0, 8.0, 12.0, 16.0, 20.0):
      for bn in ("receiver bolt", "receiver washer"):
        for fn, fm in {"plate": plate, "arm": arm.translate((dx, 0.0, 0.0)), "column cover": cover, "cup screw": screw}.items():
          check(f"receiver bolt going in, arm {dx:+.1f}, {t:.0f} mm out: {bn} / {fn}", hw[bn].translate((0.0, 0.0, t)), fm)

  # 3. the carrier, motor, board and gear slid anywhere in the tower's groove, from the web on the tower's top to its
  # top end
  dzs = [float(d) for d in np.arange(RA.DZ_OUT, RA.DZ_MAX + 0.5, 1.0)]
  for dz in dzs:
    mv = moving(dz)
    for mn, mm in mv.items():
      for fn, fm in {**fixed, **car}.items():
        check(f"slid {dz:+.0f}: {mn} / {fn}", mm, fm)
    check(f"slid {dz:+.0f}: carrier / motor", mv["carrier"], mv["motor"])
    check(f"slid {dz:+.0f}: carrier / gear", mv["carrier"], mv["gear"])

  # 4. the bolts and nuts, and the room to turn the wing bolts: the carrier all the way down, at the drawn depth for
  # the teeth piece 12 mm either side, and at the groove's top; against the parts, the car and the motor (their
  # shanks go through clearance holes, so the bolts' own holes and nut pockets count as clear)
  for slid in (RA.DZ_OUT, RA.DZ_SHALLOW, 0.0, RA.DZ_DEEP, RA.DZ_MAX):
    mv = moving(slid)
    for swept in (False, True):
      hw = hardware(slid, swept)
      for hn, hm in hw.items():
        if swept and ("nut" in hn or "washer" in hn):
          continue
        for on, om in {**fixed, **car, **mv}.items():
          check(f"slid {slid:+.0f}: {hn}{' wings turning' if swept else ''} / {on}", hm, om)
      if not swept:
        names = list(hw)
        for i in range(len(names)):
          for j in range(i + 1, len(names)):
            check(f"slid {slid:+.0f}: {names[i]} / {names[j]}", hw[names[i]], hw[names[j]])

  # 5. the steering wheel turned, the teeth piece where the gear meshes at the drawn depth (s = how far nearer you
  # the teeth piece sits than drawn, the carrier slid s to match): nothing but the gear may touch the grip or the teeth
  # piece; slid out 6 mm, not even the gear. Every teeth set; the grip once
  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    mv = moving(s)
    near = {"carrier": mv["carrier"], "motor": mv["motor"], "board": mv["board"], **fixed}
    hw = {k: v for k, v in hardware(s, True).items() if "nut" not in k}
    out = RA.motor_and_gear(s - 6.0)["gear"]
    for a in range(-40, 41, 5):
      gr = g.translate((0.0, 0.0, s))
      for n, m in {**near, **hw}.items():
        check(f"teeth {s:+.0f} mm, wheel {a:+d} deg: {n} / grip", m, gr)
      for name, piece in pieces.items():
        t = piece.rotate((0.0, 0.0, RA.THETA + a)).translate((0.0, 0.0, s))
        for n, m in {**near, **hw}.items():
          check(f"teeth {name} {s:+.0f} mm, wheel {a:+d} deg: {n} / teeth piece", m, t)
        check(f"teeth {name} {s:+.0f} mm, wheel {a:+d} deg: gear slid out 6 mm / teeth piece", out, t)
  # lining the gear up along the teeth (step 4): the arm GEAR_IN further in or GEAR_OUT further out than drawn,
  # relative to the steering wheel; the carrier, motor, board and slide bolt against the grip and each teeth piece
  for dx in (-GEAR_IN, GEAR_OUT):
    mv = moving(0.0)
    sh = {k: mv[k].translate((dx, 0.0, 0.0)) for k in ("carrier", "motor", "board")}
    sh["slide bolt wings turning"] = hardware(0.0, True, dx)["slide bolt"]
    for a in range(-40, 41, 5):
      for n, m in sh.items():
        check(f"arm {dx:+.0f} across from drawn, wheel {a:+d} deg: {n} / grip", m, g)
        for name, piece in pieces.items():
          check(f"arm {dx:+.0f} across from drawn, teeth {name}, wheel {a:+d} deg: {n} / teeth piece", m,
                piece.rotate((0.0, 0.0, RA.THETA + a)))

  # 6. the gear in mesh at the nominal depth, phased, over each set's whole arc
  g0 = S.side_gear_teeth_only()
  c = RA.R_FACE_OUT * RA.U
  mat = [[0.0, RA.V[0], -RA.U[0], float(c[0])], [0.0, RA.V[1], -RA.U[1], float(c[1])], [1.0, 0.0, 0.0, RA.Z_AXIS]]
  for n_teeth, name in TEETH_SETS:
    t = MT.MidTeeth(n_teeth=n_teeth)
    w = -t.teeth_half
    while w <= t.teeth_half + 1e-9:
      gm = g0.rotate((0.0, 0.0, MESH_PHASE + S.FP.FACE_RATIO * w)).transform(mat)
      check(f"gear in mesh with the {name}, wheel {w:+.1f} deg / teeth", gm, pieces[name].rotate((0.0, 0.0, RA.THETA + w)), tol=1e-3)
      w += 0.5

  # 7. that it works. (a) Nuts can't turn: the smallest standard M5 nut, turned 30 degrees so its corners point at its
  # slot's walls, must run into them: the slide's nut in the carrier's bar, the receiver's nut in the arm's bar
  car0 = RA.carrier(0.0)
  blocked("slide nut turned in its slot / carrier", slide_nut(0.0, small_turned=True), car0, NUT_LOCK)
  blocked("receiver nut turned in its slot / arm", receiver_nut(0.0, small_turned=True), arm, NUT_LOCK)
  # (b) the carrier held in every direction: past the groove's top the slide bolt meets the groove's end; below all
  # the way down the web meets the tower's top; and the tube stops the bar 1 mm across either way
  hi = RA.DZ_MAX + 1.0
  blocked(f"slid {hi:+.0f} (past the groove's top): slide bolt / arm", hardware(hi)["slide bolt"], arm)
  lo = RA.DZ_OUT - 1.0
  blocked(f"slid {lo:+.0f} (below all the way down): carrier / arm", RA.carrier(lo), arm)
  for du, dv in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)):
    sh = (du * float(RA.U[0]) + dv * float(RA.V[0]), du * float(RA.U[1]) + dv * float(RA.V[1]), 0.0)
    blocked(f"carrier moved 1 mm across ({du:+.0f} u, {dv:+.0f} v) / arm", car0.translate(sh), arm)
  # (c) the arm held: past either end of the receiver's groove its wing bolt meets the groove's end; within it, it
  # doesn't (section 1); the bore stops the bar 1 mm along the column either way and up and down
  for sgn in (-1.0, 1.0):
    dx = sgn * (RA.RG_STOP + 0.75)
    blocked(f"arm slid {dx:+.2f} (past the groove's end): receiver bolt / plate", hardware(0.0, False, dx)["receiver bolt"], plate)
  for d, dn in (((0.0, 0.0, 1.0), "towards you"), ((0.0, 0.0, -1.0), "towards the dash"), ((0.0, 1.0, 0.0), "up"),
                ((0.0, -1.0, 0.0), "down")):
    blocked(f"arm moved 1 mm {dn} in the receiver / plate", arm.translate(d), plate)
  # (d) the slides' clearances (mm a side): the carrier's bar in the tube, the arm's bar in the receiver, each wing
  # bolt in its groove and its bar's hole, and how far each wing bolt's end reaches past its nut (the bar pulled
  # against the wall)
  within("bar in the tube, inner side", RA.BAR_U[0] - RA.CH_U[0], 0.2, 0.5)
  within("bar in the tube, outer side", RA.CH_U[1] - RA.BAR_U[1], 0.2, 0.5)
  within("bar in the tube, back", RA.BAR_V[0] - RA.CH_V0, 0.2, 0.5)
  within("bar in the tube, motor side", RA.CH_V1 - RA.BAR_V[1], 0.2, 0.5)
  within("arm in the receiver, along the column", ((RA.BORE_Y[1] - RA.BORE_Y[0]) - (RA.ARM_Z[1] - RA.ARM_Z[0])) / 2, 0.15, 0.4)
  within("arm in the receiver, up and down (in all)", RA.BORE_DEPTH - (RA.ARM_Y[1] - RA.ARM_Y[0]), 0.3, 0.6)
  within("slide bolt in the tower's groove", (RA.SLOT_W - 4.9) / 2, 0.2, 0.6)
  within("receiver bolt in its groove", (RA.RSLOT_H - 4.9) / 2, 0.5, 1.0)
  within("wing bolts in the bars' holes", (RA.M5_HOLE - 4.9) / 2, 0.1, 0.6)
  within("the tower's groove: how far the gear can go past the deepest it may need", RA.DZ_MAX - RA.DZ_DEEP, 0.5, 2.0)
  within("the receiver's groove: the travel each way past ARM_SLIDE", RA.RG_STOP - RA.ARM_SLIDE, 0.5, 2.0)
  within("the arm's deep part clear of the receiver's mouth when the wing bolt stops it",
         RA.DEEP_X0 - RA.RG_STOP - RA.RECEIVER_MOUTH, 0.5, 2.0)
  nut_in = sum(RA.SLIDE_NUT_U) / 2 - 2.0                # the nut's inner face (4 thick, centred in its slot)
  bolt_end = RA.TOWER_U[1] + RA.WASHER_T - 20.0 - (RA.CH_U[1] - RA.BAR_U[1])   # the bar pulled against the wall
  within("slide bolt's end past its nut", nut_in - bolt_end, 0.5, 3.0)
  pull = RA.CUP_Z - RA.BORE_Y[0] - RA.ARM_Z[1]            # the arm's gap to the wall on your side, 0.2
  r_nut_far = RA.ARM_NUT_Z[0] + 0.2 + pull                # the nut's far face with the arm pulled to the wall
  r_bolt_end = RECEIVER_FACE + RA.WASHER_T - 20.0
  within("receiver bolt's end past its nut", r_nut_far - r_bolt_end, 0.5, 4.0)
  within("receiver bolt's end short of its hole's end", r_bolt_end - (RA.ARM_HOLE_END + pull), 0.3, 5.0)

  bad = [r for r in results if not r[0]]
  print(f"{len(results)} checks, {len(bad)} failed")
  for good, what, v in bad[:80]:
    print(f"  FAIL {what}: {v:.1f} mm3")
  return ok


if __name__ == "__main__":
  sys.exit(0 if run() else 1)

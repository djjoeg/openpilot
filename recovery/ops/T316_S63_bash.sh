python3 - <<'EOF'
p='rightarm.py'; s=open(p).read()
s = s.replace("  hex_prism_z,\n", "", 1)
open(p,'w').write(s)

p='rightcheck.py'; s=open(p).read()
rep = [
('''"""
Checks for the right arm mount v3 (2 Nov 2026): that the motor carrier goes in, and that every part, bolt and
wing-bolt sweep clears the others, the steering wheel's grip and the teeth piece: the carrier slid anywhere from its
end on the tower's top to the deepest stop, the stop anywhere in its +-4 mm (the teeth piece moved the same way, as
when the plate sits nearer or further than measured), the arm slid 20 mm in or out across, and the steering wheel
turned, with each of the three teeth sets (11, 15 and 20; the 20 is the one on the car). Then the gear in mesh over
each set's whole arc.''',
'''"""
Checks for the right arm mount v4 (3 Nov 2026; v3 2 Nov): that the motor carrier goes down into the tower's tube
(off the car), and the arm with everything on it into the receiver from the key side, past the plate, the column
cover, the grip and the teeth; and that every part, bolt and wing-bolt sweep clears the others, the steering wheel's
grip and the teeth piece: the carrier slid anywhere from its end on the tower's top to the deepest stop, the stop
anywhere in its +-4 mm (the teeth piece moved the same way, as when the plate sits nearer or further than measured),
the arm slid 20 mm in or out across, and the steering wheel turned, with each of the three teeth sets (11, 15 and 20;
the 20 is the one on the car). Then the gear in mesh over each set's whole arc.'''),
('''def nut(rot: float = 30.0) -> Manifold:
  """An M5 nut along z, centred on z = 0."""
  return hex_prism_z(7.95, -2.0, 2.0, rot=rot) - cyl(2.5, -3.0, 3.0, segments=24)''',
'''def nut(rot: float = 30.0) -> Manifold:
  """An M5 nut along z, centred on z = 0."""
  return hex_prism_z(7.95, -2.0, 2.0, rot=rot) - cyl(2.5, -3.0, 3.0, segments=24)


def m4_nut(z0: float, x: float, y: float) -> Manifold:
  """An M4 nut along z from z0, its corners along U (as it sits in the carrier's slot)."""
  return hex_prism_z(RA.M4_NUT_AF, z0, z0 + RA.M4_NUT_T, x=x, y=y, rot=RA.THETA) - cyl(2.0, z0 - 1.0, z0 + 5.0, x=x, y=y, segments=20)'''),
('''def hardware(dz: float, stop_p: float, swept: bool = False, arm_dx: float = 0.0) -> dict:
  """The bolts and nuts in the steering wheel frame: the carrier slid dz from the nominal depth, the stop bolt
  poking stop_p above the lug, the arm slid arm_dx across (+ to your right). swept: the wing bolts as the room their
  wings need."""''',
'''def hardware(dz: float, gap: float, swept: bool = False, arm_dx: float = 0.0) -> dict:
  """The bolts and nuts in the steering wheel frame: the carrier slid dz from the nominal depth, the stop set with
  `gap` from its washer's top to the bar's end (RA.STOP_GAP at the drawn depth), the arm slid arm_dx across (+ to
  your right). swept: the wing bolts as the room their wings need."""'''),
('''  # the stop: up through the lug's nut, its tip stop_p above the lug, the jam nut under the lug, the head below
  su, sv = RA.STOP_UV
  sx, sy = RA.rad(su, sv)
  lug_top = RA.TOWER_Z[0] - RA.STOP_P + dz
  out["stop bolt"] = (sweep() if swept else wing_bolt()).rotate((180.0, 0.0, 0.0)).translate((sx, sy, lug_top + stop_p - 20.0))
  out["stop nut"] = nut(rot=30.0 + RA.THETA).translate((sx, sy, lug_top - 2.4))
  out["stop jam nut"] = nut(rot=30.0 + RA.THETA).translate((sx, sy, lug_top - RA.LUG_T - 2.05))''',
'''  # the stop (v4): an M4 x 30 up the bar's middle from below, a fender washer under its hex head, the jam nut on it
  # against the bar's end, the nut in the slot 4 mm in
  sx, sy = RA.rad(*RA.BAR_UV)
  end = RA.BAR_Z[0] + dz
  w_top = end - gap
  under = w_top - RA.WASHER_T                       # the head's underside
  out["stop bolt"] = hex_prism_z(7.0, under - 2.8, under + 0.01, x=sx, y=sy, rot=RA.THETA) + \\
    cyl(1.95, under, under + 30.0, x=sx, y=sy, segments=20)
  out["stop washer"] = cyl(RA.WASHER_OD / 2, under, w_top, x=sx, y=sy, segments=48) - cyl(2.2, under - 1.0, w_top + 1.0, x=sx, y=sy, segments=20)
  out["stop jam nut"] = m4_nut(end - RA.M4_NUT_T, sx, sy)
  out["stop nut"] = m4_nut(end + RA.M4_SLOT_IN + 0.2, sx, sy)'''),
('''  rx = hardware(0.0, RA.STOP_P, True)["receiver bolt"]''', '''  rx = hardware(0.0, RA.STOP_GAP, True)["receiver bolt"]'''),
('''    sh.update({f"{k} wings turning": m for k, m in hardware(0.0, RA.STOP_P, True, dx).items()
               if "receiver" not in k and "nut" not in k})''',
'''    sh.update({f"{k} wings turning": m for k, m in hardware(0.0, RA.STOP_GAP, True, dx).items()
               if "receiver" not in k and "nut" not in k})'''),
('''  # 2. the carrier goes in: with the motor on it, slid out (6 mm and all the way), it comes in sideways from the
  # motor's side (+v) into the channel, past nothing
  for dz in (-6.0, RA.DZ_OUT):
    for t in np.arange(0.0, 42.0, 2.0):
      off = (float(t * RA.V[0]), float(t * RA.V[1]), 0.0)
      for mn, mm in moving(dz).items():
        for fn, fm in fixed.items():
          check(f"going in, slid {dz:+.0f}, {t:.0f} mm short: {mn} / {fn}", mm.translate(off), fm)''',
'''  # 2. it goes together. (a) Off the car: the carrier, motor on it and its stop nut in the slot, down into the
  # tower's tube from the top, till it sits on the tower (slid all the way out), past the arm, the tower's nut and its
  # wing bolt (a few turns in, 8 mm short of the bar)
  back = (8.0 * float(RA.U[0]), 8.0 * float(RA.U[1]), 0.0)
  hw0 = hardware(RA.DZ_OUT, RA.STOP_GAP)
  tower_hw = {"push nut": hw0["push nut"], "push bolt a few turns in": hw0["push bolt"].translate(back)}
  for dz in np.arange(RA.DZ_OUT, 170.0, 4.0):
    mv = {**moving(float(dz)), "stop nut": hardware(float(dz), RA.STOP_GAP)["stop nut"]}
    for mn, mm in mv.items():
      for fn, fm in {"arm": arm, **tower_hw}.items():
        check(f"down the tower, {dz - RA.DZ_OUT:.0f} mm up: {mn} / {fn}", mm, fm)
  # (b) the arm, with all of that and the stop on it, into the receiver from the key side, the motor slid all the way
  # out; the receiver's wing bolt backed out of the tube (6 mm); the wheel straight
  rb_out = hardware(0.0, RA.STOP_GAP)["receiver bolt"].translate((0.0, 0.0, -6.0))
  car = {"arm": arm, **moving(RA.DZ_OUT), **{k: v for k, v in hardware(RA.DZ_OUT, RA.STOP_GAP).items() if "receiver" not in k}}
  car["push bolt"] = car["push bolt"].translate(back)
  near20 = pieces["20"].rotate((0.0, 0.0, RA.THETA))
  for dx in np.arange(4.0, 104.0, 4.0):
    off = (float(dx), 0.0, 0.0)
    for mn, mm in car.items():
      for fn, fm in (("plate", plate), ("column cover", cover), ("receiver bolt backed out", rb_out), ("grip", g),
                     ("teeth piece", near20)):
        check(f"into the receiver, {dx:.0f} mm out: {mn} / {fn}", mm.translate(off), fm)'''),
('''  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_P - s
    for slid in (s, RA.DZ_OUT):''',
'''  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_GAP + s
    for slid in (s, RA.DZ_OUT):'''),
('''            check(f"stop {p:.1f}, slid {slid:+.0f}: {hn}{' wings turning' if swept else ''} / {on}", hm, om)''',
'''            check(f"stop gap {p:.1f}, slid {slid:+.0f}: {hn}{' wings turning' if swept else ''} / {on}", hm, om)'''),
('''              check(f"stop {p:.1f}, slid {slid:+.0f}: {names[i]} / {names[j]}", hw[names[i]], hw[names[j]])''',
'''              check(f"stop gap {p:.1f}, slid {slid:+.0f}: {names[i]} / {names[j]}", hw[names[i]], hw[names[j]])'''),
('''  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_P - s
    mv = moving(s)''',
'''  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_GAP + s
    mv = moving(s)'''),
]
for a,b in rep:
  assert a in s, a[:70]
  s = s.replace(a,b)
open(p,'w').write(s)
EOF
ruff check rightcheck.py rightarm.py --output-format concise | head
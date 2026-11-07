"""Patch rightcheck.py for v5: the helpers, sections 2 to 5, and the function checks (section 7)."""
p = "/home/claude/deliver/hardware/cad/rightcheck.py"
s = open(p, encoding="utf-8").read()
reps = [
  # the result helpers: must-touch and value checks too
  ("""  def check(what: str, a: Manifold, b: Manifold, tol: float = TOL):
    nonlocal ok
    v = overlap(a, b)
    good = v <= tol
    ok = ok and good
    results.append((good, what, v))
""",
   """  def check(what: str, a: Manifold, b: Manifold, tol: float = TOL):
    nonlocal ok
    v = overlap(a, b)
    good = v <= tol
    ok = ok and good
    results.append((good, what, v))

  def blocked(what: str, a: Manifold, b: Manifold, least: float = 1.0):
    \"\"\"a must run into b (a stop, a wall, a nut that can't turn).\"\"\"
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
"""),
  # section 2
  ("""  # 2. it goes together. (a) Off the car: the carrier, motor on it and its stop nut in the slot, down into the
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
  car["push bolt"] = car["push bolt"].translate(back)""",
   """  # 2. it goes together. (a) Off the car: the carrier, motor on it and the slide's nut in its slot, down into the
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
  # (b) the arm, with all of that on it, into the receiver from the key side, the motor slid all the way out; the
  # receiver's wing bolt backed out of the tube (6 mm); the wheel straight
  rb_out = hardware(0.0)["receiver bolt"].translate((0.0, 0.0, -6.0))
  car = {"arm": arm, **mv_out, **{k: v for k, v in hw_out.items() if "receiver" not in k}}"""),
  # section 3: anywhere in the groove
  ("""  # 3. the carrier, motor, board and gear slid anywhere from the web on the tower's top to the deepest stop
  dzs = [float(d) for d in np.arange(RA.DZ_OUT, RA.DZ_DEEP + 0.5, 1.0)]""",
   """  # 3. the carrier, motor, board and gear slid anywhere in the groove, from the web on the tower's top to its top end
  dzs = [float(d) for d in np.arange(RA.DZ_OUT, RA.DZ_MAX + 0.5, 1.0)]"""),
  # section 4: the slide's bolts at its positions
  ("""  # 4. the bolts and nuts, and the room to turn the wing bolts: the stop set for the deepest, nominal and shallowest
  # depth, the carrier at its stop and slid all the way out (on the tower's top); against the parts and the motor (their
  # shanks go through clearance holes, so the bolts' own holes and nut pockets count as clear)
  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_GAP + s
    for slid in (s, RA.DZ_OUT):
      mv = moving(slid)
      for swept in (False, True):
        hw = hardware(slid, p, swept)
        for hn, hm in hw.items():
          if swept and "nut" in hn:
            continue
          for on, om in {**fixed, **mv}.items():
            check(f"stop gap {p:.1f}, slid {slid:+.0f}: {hn}{' wings turning' if swept else ''} / {on}", hm, om)
        if not swept:
          names = list(hw)
          for i in range(len(names)):
            for j in range(i + 1, len(names)):
              check(f"stop gap {p:.1f}, slid {slid:+.0f}: {names[i]} / {names[j]}", hw[names[i]], hw[names[j]])""",
   """  # 4. the bolts and nuts, and the room to turn the wing bolts: the carrier all the way down, at the drawn depth for
  # the teeth piece 4 mm either side, and at the groove's top; against the parts and the motor (their shanks go through
  # clearance holes, so the bolts' own holes and nut pockets count as clear)
  for slid in (RA.DZ_OUT, RA.DZ_SHALLOW, 0.0, RA.DZ_DEEP, RA.DZ_MAX):
    mv = moving(slid)
    for swept in (False, True):
      hw = hardware(slid, swept)
      for hn, hm in hw.items():
        if swept and ("nut" in hn or "washer" in hn):
          continue
        for on, om in {**fixed, **mv}.items():
          check(f"slid {slid:+.0f}: {hn}{' wings turning' if swept else ''} / {on}", hm, om)
      if not swept:
        names = list(hw)
        for i in range(len(names)):
          for j in range(i + 1, len(names)):
            check(f"slid {slid:+.0f}: {names[i]} / {names[j]}", hw[names[i]], hw[names[j]])"""),
  # section 5: no stop gap any more
  ("""  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_GAP + s
    mv = moving(s)
    near = {"carrier": mv["carrier"], "motor": mv["motor"], "board": mv["board"], **fixed}
    hw = {k: v for k, v in hardware(s, p, True).items() if "nut" not in k}""",
   """  for s in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    mv = moving(s)
    near = {"carrier": mv["carrier"], "motor": mv["motor"], "board": mv["board"], **fixed}
    hw = {k: v for k, v in hardware(s, True).items() if "nut" not in k}"""),
  # section 7: the function checks, before the summary
  ("""  bad = [r for r in results if not r[0]]""",
   """  # 7. that it works (v5). (a) Nuts can't turn: the smallest standard M5 nut, turned 30 degrees so its corners point at
  # its slot's walls, must run into them: the slide's nut in the carrier's bar, the receiver's nut in the plate
  car0 = RA.carrier(0.0)
  blocked("slide nut turned in its slot / carrier", slide_nut(0.0, small_turned=True), car0)
  pz = RA.PLATE_T + RA.BORE_DEPTH / 2
  yn = (RA.BORE_Y[1] + RA.TUBE_Y[1]) / 2
  rn = RA.plate_to_wheel(nut_min(30.0).rotate((90.0, 0.0, 0.0)).translate((RA.PINCH_X, yn, pz)))
  blocked("receiver nut turned in its slot / plate", rn, plate)
  # (b) the carrier held in every direction: past the groove's top the slide bolt meets the groove's end; below all
  # the way down the web meets the tower's top; and the tube stops the bar 1 mm across either way
  hi = RA.DZ_MAX + 1.0
  blocked(f"slid {hi:+.0f} (past the groove's top): slide bolt / arm", hardware(hi)["slide bolt"], arm)
  lo = RA.DZ_OUT - 1.0
  blocked(f"slid {lo:+.0f} (below all the way down): carrier / arm", RA.carrier(lo), arm)
  for du, dv in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)):
    sh = (du * float(RA.U[0]) + dv * float(RA.V[0]), du * float(RA.U[1]) + dv * float(RA.V[1]), 0.0)
    blocked(f"carrier moved 1 mm across ({du:+.0f} u, {dv:+.0f} v) / arm", car0.translate(sh), arm)
  # (c) the slide's clearances (mm a side): the bar in the tube, the wing bolt in the groove and in the bar's hole,
  # and how far the wing bolt's end reaches past the nut
  within("bar in the tube, inner side", RA.BAR_U[0] - RA.CH_U[0], 0.2, 0.5)
  within("bar in the tube, outer side", RA.CH_U[1] - RA.BAR_U[1], 0.2, 0.5)
  within("bar in the tube, back", RA.BAR_V[0] - RA.CH_V0, 0.2, 0.5)
  within("bar in the tube, motor side", RA.CH_V1 - RA.BAR_V[1], 0.2, 0.5)
  within("wing bolt in the groove", (RA.SLOT_W - 4.9) / 2, 0.2, 0.6)
  within("wing bolt in the bar's hole", (RA.M5_HOLE - 4.9) / 2, 0.1, 0.6)
  nut_in = sum(RA.SLIDE_NUT_U) / 2 - 2.0                # the nut's inner face (4 thick, centred in its slot)
  bolt_end = RA.TOWER_U[1] + RA.WASHER_T - 20.0 - (RA.CH_U[1] - RA.BAR_U[1])   # the bar pulled against the wall
  within("wing bolt's end past the nut", nut_in - bolt_end, 0.5, 3.0)

  bad = [r for r in results if not r[0]]"""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:80]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")

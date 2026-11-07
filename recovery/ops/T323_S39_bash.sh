python3 - <<'EOF'
p = "rightarm.py"
s = open(p, encoding="utf-8").read()
reps = [
("""BLOCK = (-60.0, 28.0, -14.0, 45.4)       # v1's block (v5: ending level with the receiver's dash-side face, 4.6 short of
                                         # v4's, so it stays 3 mm clear of the dash in the photo estimates)""",
 """BLOCK = (-60.0, 28.0, -14.0, 50.0)       # v1's block, out to the receiver's far end on the key side"""),
("""RG_STOP = ARM_SLIDE + 0.5 + (RSLOT_H / 2 - 2.45)    # 18.75: the wing bolt meets the groove's end""",
 """RG_STOP = ARM_SLIDE + 0.5 + (RSLOT_H / 2 - 2.45)    # 18.75: the wing bolt meets the groove's end
RG_Z = PLATE_T + BORE_DEPTH / 2 + 3.0    # 24.2: the groove's middle, 3 below the bore's middle (in the car), so a fender
                                         # washer under its wing bolt passes the cup screw's head with the arm slid in"""),
("""ARM_MID_Y = (ARM_Y[0] + ARM_Y[1]) / 2    # -128: the receiver's wing bolt's line, the bar's mid-height""",
 """ARM_BOLT_Y = COVER_Y - RG_Z + 0.2        # -131: the receiver's wing bolt's line in the bar (the bar drawn against the
                                         # plate, 0.2 above the middle of its 0.4 of play, so on average it's centred)"""),
("""  pz = T + BORE_DEPTH / 2
  r = RSLOT_H / 2
  ends = [cyl_y(r, TUBE_Y[0] - 1.0, BORE_Y[0] + 1.0, x=x, z=pz, segments=32) for x in (RGROOVE_X[0] + r, RGROOVE_X[1] - r)]""",
 """  r = RSLOT_H / 2
  ends = [cyl_y(r, TUBE_Y[0] - 1.0, BORE_Y[0] + 1.0, x=x, z=RG_Z, segments=32) for x in (RGROOVE_X[0] + r, RGROOVE_X[1] - r)]"""),
("""  labels = [FR.text("< KEY", TUBE_X[1] + 3.0, BLOCK[3] - 8.0, T), FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, T, pix=0.9),
            FR.text("1", xc - FR.text_width("1", 0.9) / 2, LEG[2] + 3.0, T, pix=0.9)]
  return clean(body + union(labels))""",
 """  labels = [FR.text("< KEY", TUBE_X[1] + 3.0, BLOCK[3] - 8.0, T), FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, T, pix=0.9),
            FR.text("1", xc - FR.text_width("1", 0.9) / 2, LEG[2] + 3.0, T, pix=0.9)]
  # v5: cut in, not raised, so the screws' washers sit flat and the arm slides over the plate past the tube's end
  return clean(body - union(labels).translate((0.0, 0.0, -SL.LABEL_H - 0.01)))"""),
("""  hexp = CrossSection([[(ARM_NUT_X + r * math.cos(math.radians(90 + 60 * i)), ARM_MID_Y + r * math.sin(math.radians(90 + 60 * i)))
                        for i in range(6)]])                    # a corner down
  pocket = hexp.extrude(z1 - z0).translate((0.0, 0.0, z0))
  pocket = pocket + box(ARM_NUT_X - w / 2, ARM_NUT_X + w / 2, ARM_MID_Y, ARM_Y[1] + 1.0, z0, z1)
  hole = cyl(M5_HOLE / 2, ARM_HOLE_END, ARM_Z[1] + 1.0, x=ARM_NUT_X, y=ARM_MID_Y, segments=32)""",
 """  hexp = CrossSection([[(ARM_NUT_X + r * math.cos(math.radians(90 + 60 * i)), ARM_BOLT_Y + r * math.sin(math.radians(90 + 60 * i)))
                        for i in range(6)]])                    # a corner down
  pocket = hexp.extrude(z1 - z0).translate((0.0, 0.0, z0))
  pocket = pocket + box(ARM_NUT_X - w / 2, ARM_NUT_X + w / 2, ARM_BOLT_Y, ARM_Y[1] + 1.0, z0, z1)
  hole = cyl(M5_HOLE / 2, ARM_HOLE_END, ARM_Z[1] + 1.0, x=ARM_NUT_X, y=ARM_BOLT_Y, segments=32)"""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:70]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)

p = "rightcheck.py"
s = open(p, encoding="utf-8").read()
reps = [
("""The car's parts are the photo estimates (carscene.py, D = 125, as the column cover): the key's bulge and bezel, the
key in it and the room to turn it, the wiper stalk through its whole swing, and the dash's face below the column;
and the cup screw's head with a fender washer under it, on the plate.""",
 """The car's parts are the photo estimates (carscene.py, D = 125, as the column cover): the key's bulge and bezel, the
key in it and the room to turn it, the wiper stalk through its whole swing (at rest while the arm goes in), and the
dash's face below the column (no nearer than the frame plate's dash-side edge, which your printed plate showed
clears it: 1.4 mm further than the estimate); and the cup screw's head with a fender washer under it, on the plate.
The arm is checked against the plate anywhere in the receiver's groove, and against the car where it can be when
the gear is in the teeth (GEAR_IN further in to GEAR_OUT further out than drawn) and on its way in from the key
side: when the plate sits off where it's drawn, the arm slides in the receiver to keep the gear on the teeth."""),
("""def car_parts() -> dict:
  import carscene as CS
  sc = CS.CarScene(D=SCENE_D)
  return {**sc.key_parts(), "wiper stalk, its whole swing": sc.stalk(), "dash face": sc.bolster()}""",
 """def car_parts(stalk_at_rest: bool = False) -> dict:
  import carscene as CS
  sc = CS.CarScene(D=SCENE_D)
  edge = RA.CUP_Z - max(RA.BLOCK[3], RA.BAR[3])          # the frame plate's dash-side edge, -195
  dash = sc.bolster().translate((0.0, 0.0, min(0.0, edge - sc.dash_z)))
  stalk = ("wiper stalk at rest", sc.stalk(down=0.0, up=0.0)) if stalk_at_rest else ("wiper stalk, its whole swing", sc.stalk())
  return {**sc.key_parts(), stalk[0]: stalk[1], "dash face": dash}"""),
("""  return m.translate((RA.ARM_NUT_X + arm_dx, RA.ARM_MID_Y, sum(RA.ARM_NUT_Z) / 2))""",
 """  return m.translate((RA.ARM_NUT_X + arm_dx, RA.ARM_BOLT_Y, sum(RA.ARM_NUT_Z) / 2))"""),
("""  x, y, f = RA.ARM_NUT_X, RA.ARM_MID_Y, RECEIVER_FACE""", """  x, y, f = RA.ARM_NUT_X, RA.ARM_BOLT_Y, RECEIVER_FACE"""),
("""  # 1. the fixed parts against each other and the car (the arm in the receiver); then the arm slid anywhere in the
  # receiver's groove, with the carrier and every bolt on it (wings turning), against the plate, the cover, the cup
  # screw and the car
  check("plate / arm", plate, arm)
  check("plate / column cover", plate, cover)
  check("arm / column cover", arm, cover)
  check("plate / cup screw", plate, screw)
  check("arm / cup screw", arm, screw)
  for cn, cm in car.items():
    check(f"plate / {cn}", plate, cm)
    check(f"arm / {cn}", arm, cm)
  for dx in (-RA.ARM_SLIDE, -9.0, 9.0, RA.ARM_SLIDE):
    sh = {"arm": arm.translate((dx, 0.0, 0.0))}
    for dz in (0.0, RA.DZ_OUT, RA.DZ_MAX):
      sh.update({f"{k} slid {dz:+.0f}": m.translate((dx, 0.0, 0.0)) for k, m in moving(dz).items()})
    sh.update({f"{k} wings turning": m for k, m in hardware(0.0, True, dx).items() if "nut" not in k and "washer" not in k})
    sh.update({k: m for k, m in hardware(0.0, False, dx).items() if "nut" in k or "washer" in k})
    for n, m in sh.items():
      for fn, fm in {"plate": plate, "column cover": cover, "cup screw": screw, **car}.items():
        check(f"arm slid {dx:+.1f} across: {n} / {fn}", m, fm)
""",
 """  # 1. the fixed parts against each other and the car (the arm in the receiver); then the arm slid anywhere in the
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
"""),
("""  # (b) the arm, with all of that and the receiver's nut in its slot, into the receiver from the key side, the motor
  # slid all the way out, the receiver's wing bolt not in yet; the wheel straight; from 104 mm out to slid all the
  # way in
  on_arm = {"arm": arm, **mv_out, "receiver nut": hw_out["receiver nut"],
            **{k: v for k, v in hw_out.items() if k.startswith("slide")}}
  near20 = pieces["20"].rotate((0.0, 0.0, RA.THETA))
  for dx in np.arange(-RA.ARM_SLIDE, 104.0, 4.0):
    off = (float(dx), 0.0, 0.0)
    for mn, mm in on_arm.items():
      for fn, fm in {"plate": plate, "column cover": cover, "cup screw": screw, "grip": g, "teeth piece": near20, **car}.items():
        check(f"into the receiver, {dx:+.1f} mm out: {mn} / {fn}", mm.translate(off), fm)""",
 """  # (b) the arm, with all of that and the receiver's nut in its slot, into the receiver from the key side, the motor
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
        check(f"into the receiver, {dx:+.1f} mm out: {mn} / {fn}", mm.translate(off), fm)"""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:70]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
grep -n "ARM_MID_Y\|SL\.\|import slotplate" rightarm.py rightcheck.py visuals.py viewer3d.py incar.py carphoto.py stiffness.py | head
python3 - <<'EOF'
p = "/home/claude/deliver/hardware/cad/accord_lka_parts.py"
s = open(p).read()
old = """  P.WHEEL_OD, P.GRIP = args.wheel_od, args.grip
  P.BED = tuple(args.bed)
"""
new = """  P.WHEEL_OD, P.GRIP = args.wheel_od, args.grip
  P.BED = tuple(args.bed)
  P.COVER_BOTTOM = -args.cover_bottom
  P.RIGHT_SPOKE_DEG = (args.spoke_from, args.spoke_to)
"""
assert old in s
s = s.replace(old, new)

anchor = "def side_pictures(A, CA, MP, cparts, folder, on_bed):"
code = r'''def back_mount(args, base: dict, problems: list, on_bed, write_stl, part_rows: list, bed) -> dict:
  """The back-teeth mount's parts, checks and report (faceparts.py, faceassembly.py). Its STL files go to
  <out>/back-teeth-mount; the lever bracket and setup gauge are the dash mount's, already written."""
  import faceassembly as FA     # noqa: E402
  import faceparts as FP        # noqa: E402
  import margins as MG          # noqa: E402
  import mountparts as MP       # noqa: E402

  out = os.path.join(args.out, "back-teeth-mount")
  os.makedirs(out, exist_ok=True)
  t = FP.FaceTeeth(args.wheel_od, args.grip, P.RIGHT_SPOKE_DEG)
  rep = {"inputs": {"cover_bottom_below_column_axis_mm": args.cover_bottom, "right_spoke_meets_grip_deg": list(P.RIGHT_SPOKE_DEG),
                    "plate_front_behind_grip_mm": -P.PLATE_FRONT_Z,
                    "estimates": {"wiper_stalk_from_to_mm": [list(P.STALK_FROM), list(P.STALK_TO)],
                                  "key_cylinder_from_to_mm": [list(P.KEY_FROM), list(P.KEY_TO)],
                                  "covers_front_edge_behind_grip_mm": -P.COVER_FRONT_Z, "hub_radius_mm": P.HUB_R}}}
  whole = FP.face_solid(t)
  pieces = FP.face_pieces(t, whole)
  tests = FP.face_fit_tests(t, whole)
  fit = FA.solve_face(t, P.COVER_BOTTOM)
  front_down = "front face (the side towards you) down"
  bparts = {
    "back-teeth-upper": (pieces["upper"], (180, 0, 0), front_down, "none"),
    "back-teeth-lower": (pieces["lower"], (180, 0, 0), front_down, "none"),
    "back-teeth-one-piece": (pieces["one-piece"], (180, 0, 0), front_down + " (for print beds 330 mm across)", "none"),
    "back-motor-gear": (FP.face_motor_gear(), (180, 0, 0), "teeth down", "none"),
    "back-motor-carrier": (FP.face_carrier(), (180, 0, 0), "finger guard down",
                           "inside the finger guard only (supports touching the build plate only)"),
    "back-hinge-block": (FP.face_hinge_block(t), (180, 0, 0), "front end (the end towards the column) down",
                         "tree supports, everywhere (small areas under the hinge, the spring's pocket and the ears)"),
    "back-lift-lever": (FP.back_lift_lever(), (0, 90, 0), "on its side, the side with the thin tab under the handle down", "none"),
    "column-plate": (FP.column_plate(t), (-90, 0, 0), "the flat top (the cover's side) down", "none"),
    "fit-test-back-teeth": (tests["teeth"], (180, 0, 0), front_down, "none"),
    "fit-test-back-teeth-spoke": (tests["spoke"], (180, 0, 0), front_down, "none"),
  }
  for L in FP.ARM_LENGTHS_F:
    bparts[f"back-arm-{int(L):03d}"] = (FP.face_arm(L), (90, 0, 0), "flat", "none")
  rows = []
  for name, (m, rot, how, supports) in bparts.items():
    placed = on_bed(m, rot)
    best = None
    for zr in range(0, 91, 5):
      p2 = on_bed(placed, (0, 0, zr))
      x0, y0, z0, x1, y1, z1 = p2.bounding_box()
      sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
      fit_bed = sx <= bed[0] and sy <= bed[1] and sz <= bed[2]
      if best is None or (fit_bed and not best[0]):
        best = (fit_bed, p2, (sx, sy, sz), zr)
      if fit_bed:
        break
    fits, p2, size, zr = best
    n_pieces = len(m.decompose())
    status = str(m.status()).split(".")[-1]
    support_mm2, _ = support_area(p2)
    vol = m.volume() / 1000.0
    row = {"file": "back-teeth-mount/" + name + ".stl", "print": how + (f", turned {zr} degrees on the bed" if zr else ""),
           "supports": supports, "size_mm": [round(v, 1) for v in size], "fits_bed": fits, "solid_volume_cm3": round(vol, 1),
           "filament_if_solid_g": round(vol * PETG_DENSITY, 1), "pieces": n_pieces, "closed_solid": status == "NoError",
           "overhang_needing_support_mm2": round(support_mm2)}
    rows.append(row)
    part_rows.append(row)
    if n_pieces != 1 or status != "NoError":
      problems.append(f"back-teeth mount, {name}: not one closed solid ({n_pieces} pieces, {status})")
    if not fits and "one-piece" not in name:
      problems.append(f"back-teeth mount, {name}: {size[0]:.0f} x {size[1]:.0f} x {size[2]:.0f} mm does not fit the print bed")
    write_stl(p2, os.path.join(out, name + ".stl"), name)
  rep["parts"] = rows
  rep["teeth"] = {"teeth": FP.N_TEETH, "teeth_on_a_full_circle": FP.FACE_TEETH, "motor_gear_teeth": FP.FACE_MOTOR_TEETH,
                  "gear_ratio": round(FP.FACE_RATIO, 4), "pitch_radius_mm": FP.R_F, "teeth_from_to_radius_mm": list(FP.FACE_BAND),
                  "rolling_band_radius_mm": list(FP.ROLL_BAND), "steering_wheel_turn_with_teeth_deg": round(t.teeth_arc_deg, 1),
                  "steering_wheel_turn_tracked_deg": round(t.tracked_arc_deg, 2), "full_push_reach_deg": round(t.teeth_half, 1),
                  "piece_spans_deg": round(t.span_deg, 1), "joint_deg_above_3_oclock": round(t.joint_deg, 2),
                  "zip_tie_slots_deg": [round(a, 2) for a in FP.tie_angles(t)],
                  "notch_for_the_right_spoke_deg": [round(a, 1) for a in t.spoke], "notch_radius_mm": FP.NOTCH_R,
                  "teeth_behind_grip_middle_mm": [round(-t.z_root, 1), round(-t.z_tip, 1)],
                  "motor_face_from_column_axis_mm": FP.R_FACE, "motor_shaft_behind_grip_middle_mm": round(-t.z_axis, 1)}
  rep["fit"] = {"ok": fit.ok, "bolt_to_bolt_mm": round(fit.reach, 1),
                "arm_to_print": f"back-arm-{int(fit.arm_len):03d}.stl" if fit.arm_len else None,
                "slide_from_middle_mm": round(fit.slide, 1), "arm_up_from_level_deg": round(fit.j1_deg, 1),
                "joints_from_the_middle_of_their_slots_deg": round(fit.j1_off, 1),
                "plate_joint_mm": [round(v, 1) for v in fit.j1], "hinge_block_joint_mm": [round(v, 1) for v in fit.j2],
                "notes": fit.notes}
  checks = {}
  fparts = {"teeth": pieces["one-piece"], "gear": bparts["back-motor-gear"][0], "gear_teeth_only": FP.face_motor_gear_teeth_only(),
            "carrier": bparts["back-motor-carrier"][0], "bracket": base["bracket"], "lever": bparts["back-lift-lever"][0],
            "lever_no_tab": FP.back_lift_lever(with_finger=False), "tab": MP.lever_tab(),
            "hinge_block": bparts["back-hinge-block"][0], "plate": bparts["column-plate"][0]}
  if fit.ok:
    fparts["arm"] = bparts[f"back-arm-{int(fit.arm_len):03d}"][0]
    A = FA.FaceAssembly(t, fit, fparts, args.cover_width, args.cover_height, args.cover_front_width)
    mesh = FA.mesh_sweep(A, step=1.0)
    rep["mesh"] = mesh
    if mesh["worst_overlap_mm3"] > 1e-3:
      problems.append(f"back-teeth mount: the motor gear and the back teeth overlap by {mesh['worst_overlap_mm3']} mm3 at "
                      f"{mesh['worst_at_deg']} degrees")
    checks = FA.check_all(A)
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
    for k in bad:
      problems.append(f"back-teeth mount, parts touch: {k} ({checks[k]:.2f} mm3)")
    rep["clearances"] = FA.clearances(A)
    lift = MP.cam_lift(MP.A_OFF)
    tip_down = A.lever(0.0, 0.0).bounding_box()
    tip_up = A.lever(MP.A_OFF, lift).bounding_box()
    rep["clearances"]["lift_lever_nearest_you_down_mm_behind_grip"] = round(-tip_down[5], 0)
    rep["clearances"]["lift_lever_nearest_you_up_mm_behind_grip"] = round(-tip_up[5], 0)
    rep["clearances"]["parts_reach_out_from_column_mm"] = round(max(A.motor().bounding_box()[3], A.hinge_block().bounding_box()[3]), 0)
    if not args.no_pictures:
      back_pictures(A, FA, MP, bparts, args.report, on_bed)
  else:
    problems.append("back-teeth mount: the parts do not reach: " + "; ".join(fit.notes))
  rep["touching_checks_mm3"] = {k: round(v, 3) for k, v in checks.items()}
  rep["margins"] = MG.back_rows(t, fit)
  for r in rep["margins"]:
    if r["kind"] == "design" and r["status"] == "UNDER":
      problems.append(f"back-teeth mount, under the {MG.FLOOR} floor: {r['what']} ({r['factor']})")
  rep["fasteners"] = FA.fastener_rows()
  for r in rep["fasteners"]:
    if not r["ok"]:
      problems.append(f"back-teeth mount: {r['bolt']} is the wrong length")
  # where the cover's underside may be: the plate's joint moves with it; the arm and joints that still reach
  heights = {"cover_bottom_mm": [40, 45, 50, 55, 60, 65, 70], "fits": []}
  for h in heights["cover_bottom_mm"]:
    f_ = FA.solve_face(t, -h)
    heights["fits"].append(f"back-arm-{int(f_.arm_len):03d}, joints {f_.j1_off:+.0f} deg" if f_.ok else "no")
  rep["cover_heights"] = heights
  return rep


def back_pictures(A, FA, MP, bparts, folder, on_bed):
  import render as R
  from cadlib import box
  lift = MP.cam_lift(MP.A_OFF)
  front = R.look((0, 0, 1), (0, 1, 0))
  above = R.look((0, 1, 0), (0, 0, -1))
  R.save(os.path.join(folder, "back-assembly-front.png"),
         [(FA.parts_scene(A), front), (FA.parts_scene(A, lift, MP.A_OFF), front), (FA.parts_scene(A), above)],
         ["lift lever down: the motor gear on the back teeth", "lift lever up: the motor gear lifted off",
          "from above: the driver at the bottom, the dash at the top"],
         suptitle="Back-teeth mount from the driver's seat: the teeth on the back of the grip from 1 to 5 o'clock, the motor behind "
                  "the wheel at 3 o'clock, the arm down to the plate under the column (the wiper stalk and key cylinder are estimates)",
         size=(700, 700))
  iso = R.look((1.0, -0.6, -0.9), (0, 1, 0))
  crop = box(-60, 320, -200, 140, -260, 40)
  R.save(os.path.join(folder, "back-assembly-3d.png"),
         [([(m ^ crop, c) for m, c in FA.parts_scene(A) if not (m ^ crop).is_empty()], iso),
          ([(m ^ crop, c) for m, c in FA.parts_scene(A, lift, MP.A_OFF) if not (m ^ crop).is_empty()], iso)],
         ["lift lever down", "lift lever up"], size=(900, 760))
  view = R.look((0.8, -1.0, 0.7), (0, 0, 1))
  panels, titles = [], []
  for n, (m, rot, how, sup) in bparts.items():
    if n.startswith("back-arm-") and not n.endswith("165"):
      continue
    panels.append(([(on_bed(m, rot), (.55, .7, .9))], view))
    titles.append(n)
  R.save(os.path.join(folder, "back-parts.png"), panels, titles, size=(560, 500))


def back_text(c: dict, MG) -> list:
  L = [""]
  inp = c["inputs"]
  L.append("=" * 100)
  L.append("BACK-TEETH MOUNT: teeth on the back of a channel round the grip from 1 to 5 o'clock, facing the dash; the motor behind "
           "the wheel at 3 o'clock, its shaft pointing at the column; the arm down to a plate under the lower column cover")
  est = inp["estimates"]
  L.append(f"The lower column cover's underside {inp['cover_bottom_below_column_axis_mm']:.0f} mm below the column's axis where the "
           f"plate sits; the right spoke meets the grip from {inp['right_spoke_meets_grip_deg'][0]:.0f} to "
           f"{inp['right_spoke_meets_grip_deg'][1]:.0f} degrees from 3 o'clock (+ up); the plate's front end "
           f"{inp['plate_front_behind_grip_mm']:.0f} mm behind the middle of the grip. Estimates used for the checks: the wiper stalk "
           f"from {est['wiper_stalk_from_to_mm'][0]} to {est['wiper_stalk_from_to_mm'][1]}, the key cylinder from "
           f"{est['key_cylinder_from_to_mm'][0]} to {est['key_cylinder_from_to_mm'][1]} (steering wheel frame, mm: right, up, "
           "towards you from the middle of the grip).")
  L.append("")
  L.append("PARTS (back-teeth-mount folder; the lever bracket and setup gauge are the dash mount's)")
  for p in c["parts"]:
    s_ = p["size_mm"]
    L.append(f"  {p['file']:<48} {s_[0]:5.0f} x {s_[1]:4.0f} x {s_[2]:4.0f} mm  {'fits' if p['fits_bed'] else 'TOO BIG'}  "
             f"{p['filament_if_solid_g']:5.0f} g if solid")
    L.append(f"      print {p['print']}; supports: {p['supports']}")
  tt = c["teeth"]
  L.append("")
  L.append(f"BACK TEETH: {tt['teeth']} teeth of a {tt['teeth_on_a_full_circle']}-tooth face gear (2 mm teeth, {tt['pitch_radius_mm']:.0f} mm "
           f"from the column's axis), the motor gear {tt['motor_gear_teeth']} teeth: ratio {tt['gear_ratio']}. The teeth reach "
           f"{tt['full_push_reach_deg']} degrees each way; with the rolling band past them the motor gear turns with the wheel over "
           f"{tt['steering_wheel_turn_tracked_deg']} degrees. The piece spans {tt['piece_spans_deg']} degrees; its two pieces meet "
           f"{tt['joint_deg_above_3_oclock']} degrees above 3 o'clock. Zip tie slots at {tt['zip_tie_slots_deg']} degrees; no inner "
           f"wall inside {tt['notch_radius_mm']:.0f} mm from {tt['notch_for_the_right_spoke_deg'][0]} to "
           f"{tt['notch_for_the_right_spoke_deg'][1]} degrees, over the right spoke's junction. The teeth stand "
           f"{tt['teeth_behind_grip_middle_mm'][0]} to {tt['teeth_behind_grip_middle_mm'][1]} mm behind the middle of the grip; the "
           f"motor's front face {tt['motor_face_from_column_axis_mm']:.0f} mm from the column's axis, its shaft "
           f"{tt['motor_shaft_behind_grip_middle_mm']} mm behind the middle of the grip.")
  if "mesh" in c:
    m = c["mesh"]
    L.append(f"  Gear mesh through the whole arc (every 1 degree): worst overlap {m['worst_overlap_mm3']} mm3; free play "
             f"{m['free_play_steering_wheel_deg']} degrees of steering wheel (the motor gear turns {m['free_play_motor_gear_deg'][0][0]} "
             "degrees each way before its teeth touch).")
  f = c["fit"]
  L.append("")
  L.append("FIT IN THE CAR")
  if f["ok"]:
    L.append(f"  print {f['arm_to_print']}: bolt to bolt {f['bolt_to_bolt_mm']} mm, the arm slid {f['slide_from_middle_mm']:+.1f} mm "
             f"from the middle of its slot, rising {f['arm_up_from_level_deg']} degrees from the plate towards the motor; both "
             f"joints {f['joints_from_the_middle_of_their_slots_deg']:+.1f} degrees from the middle of their slots.")
  else:
    L.append("  does not fit: " + "; ".join(f["notes"]))
  if "clearances" in c:
    cl = c["clearances"]
    L.append(f"  lever up: the motor gear {cl['motor_gear_off_the_teeth_with_lever_up']} mm off the teeth (25 means more than 25); "
             f"the lift lever's paddle, lever down, {cl['lift_lever_nearest_you_down_mm_behind_grip']:.0f} mm behind the middle of "
             f"the grip, lever up {cl['lift_lever_nearest_you_up_mm_behind_grip']:.0f} mm; the parts reach "
             f"{cl['parts_reach_out_from_column_mm']:.0f} mm out from the column (the grip's outer edge is "
             f"{c['_wheel_r'] if '_wheel_r' in c else 184} mm); the column plate's corner {cl['joint_ears_to_the_key_cylinder']} mm "
             f"behind the key cylinder; the lever {cl['lift_lever_to_the_wiper_stalk']} mm and the hinge block and motor "
             f"{cl['hinge_block_and_motor_to_the_wiper_stalk']} mm below the wiper stalk.")
  touching = [k for k, v in c["touching_checks_mm3"].items() if ("should touch" not in k and v > 1e-3)]
  L.append(f"  {len(c['touching_checks_mm3'])} clearance checks, {len(touching)} touching")
  h = c["cover_heights"]
  L.append("")
  L.append("WHERE THE COVER'S UNDERSIDE MAY BE (mm below the column's axis): the arm and how far the joints turn from the middle of "
           "their slots")
  L.append("        " + "".join(f"{x:>26}" for x in h["cover_bottom_mm"]))
  L.append("        " + "".join(f"{x:>26}" for x in h["fits"]))
  L.append("")
  L.append("MARGINS (the back-teeth mount's own; the shared parts' margins are above)")
  L += MG.text_lines(c["margins"])
  L.append("")
  L.append("BOLTS, SCREWS, TIES AND DOWELS")
  for b in c["fasteners"]:
    if b["length"]:
      L.append(f"  {b['bolt']:20s} {b['use']}: through {b['through_mm']} mm, then a {b['nut_mm']} mm lock nut: {b['past_the_nut_mm']} mm "
               f"to spare{'' if b['ok'] else '  WRONG LENGTH'}")
    else:
      L.append(f"  {b['bolt']}: {b['use']}")
  return L


'''
assert anchor in s
s = s.replace(anchor, code + anchor)
open(p, "w").write(s)
print("ok")
EOF
grep -n "def back_mount\|def back_text\|def back_pictures" accord_lka_parts.py
cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/col_build_fn.py <<'PYEOF'
def column_mount(args, base: dict, arms: dict, problems: list, on_bed, write_stl, part_rows: list, bed) -> dict:
  """The column mount's parts, checks and report (columnparts.py, columnassembly.py). Its own STL files go to
  <out>/column-mount; the shared parts are the ones already written."""
  import columnassembly as CA   # noqa: E402
  import columnparts as CP      # noqa: E402
  import gears as GR            # noqa: E402
  import margins as MG          # noqa: E402
  import mountparts as MP       # noqa: E402
  import wheelparts as WP       # noqa: E402

  out = os.path.join(args.out, "column-mount")
  os.makedirs(out, exist_ok=True)
  rep = {"inputs": {"cover_width_mm": args.cover_width, "cover_height_mm": args.cover_height,
                    "clamp_middle_behind_grip_mm": args.clamp_behind, "motor_face_behind_grip_mm": -P.Z_MOTOR_FACE_C,
                    "estimates": {"hub_radius_mm": P.HUB_R, "hub_back_mm": -P.HUB_BACK_Z, "spokes_back_at_lever_mm": -P.SPOKE_BACK_Z,
                                  "dash_below_column_behind_grip_mm": -P.DASH_Z, "covers_front_edge_behind_grip_mm": -P.COVER_FRONT_Z,
                                  "open_arc_between_lower_spokes_deg": P.WINDOW_DEG}}}
  t = CP.RingTeeth(args.wheel_od, args.grip)
  front_down = "front face (the side towards you) down"
  cparts = {
    "ring-teeth": (CP.ring_teeth(t), (180, 0, 0), front_down, "none"),
    "fit-test-ring-teeth": (CP.ring_tooth_fit_test(t), (180, 0, 0), front_down, "none"),
    "column-clamp-upper": (CP.column_clamp_upper(), (0, 0, 0), "V up", "none"),
    "column-clamp-lower": (CP.column_clamp_lower(), (0, 0, 90), "on its side", "tree supports under the upper side plate, everywhere"),
    "hinge-block-column": (MP.hinge_block(CP.ARM_NOMINAL_C), (180, 0, 0), "front end (the end towards you) down",
                           "tree supports, everywhere (small areas under the hinge, the spring's pocket and the ears)"),
  }
  rows = []
  for name, (m, rot, how, supports) in cparts.items():
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
    pieces = len(m.decompose())
    status = str(m.status()).split(".")[-1]
    support_mm2, _ = support_area(p2)
    vol = m.volume() / 1000.0
    row = {"file": "column-mount/" + name + ".stl", "print": how + (f", turned {zr} degrees on the bed" if zr else ""),
           "supports": supports, "size_mm": [round(v, 1) for v in size], "fits_bed": fits, "solid_volume_cm3": round(vol, 1),
           "filament_if_solid_g": round(vol * PETG_DENSITY, 1), "pieces": pieces, "closed_solid": status == "NoError",
           "overhang_needing_support_mm2": round(support_mm2)}
    rows.append(row)
    part_rows.append(row)
    if pieces != 1 or status != "NoError":
      problems.append(f"column mount, {name}: not one closed solid ({pieces} pieces, {status})")
    if not fits:
      problems.append(f"column mount, {name}: {size[0]:.0f} x {size[1]:.0f} x {size[2]:.0f} mm does not fit the print bed")
    write_stl(p2, os.path.join(out, name + ".stl"), name)
  rep["parts"] = rows

  # the ring's teeth and the motor gear inside it: no overlap through the ring's whole arc, and the free play
  motor = GR.gear_outline(P.MOTOR_TEETH, P.BACKLASH)
  cd = CP.centre_distance()
  ring = CP.ring_teeth_outline(t)
  sweep = np.linspace(-t.teeth_half, t.teeth_half, 601)
  over = GR.mesh_sweep(ring, P.RING_TEETH, motor, P.MOTOR_TEETH, cd, sweep, WP.MOTOR_GEAR_PHASE, internal=True)
  ratio = P.RING_TEETH / P.MOTOR_TEETH
  plays = []
  for w in np.linspace(-t.teeth_half + 3 * t.pitch_deg, t.teeth_half - 3 * t.pitch_deg, 7):
    ccw, cw = CP.internal_free_play(ring.rotate(float(w)), motor, cd, WP.MOTOR_GEAR_PHASE + float(w) * ratio)
    plays.append((ccw + cw) / ratio)
  rep["gears"] = {"centre_distance_mm": round(cd, 2), "rolling_band_radius_mm": round(t.r_roll, 2), "teeth": t.n_teeth,
                  "steering_wheel_turn_with_teeth_deg": round(t.teeth_arc_deg, 1), "steering_wheel_turn_tracked_deg": round(t.tracked_arc_deg, 1),
                  "piece_spans_deg": round(t.span_deg, 1), "zip_ties_deg": list(t.tie_angles), "most_overlap_mm2": round(max(over), 4),
                  "free_play_steering_wheel_deg": [round(min(plays), 3), round(max(plays), 3)]}
  if max(over) > 1e-3:
    problems.append(f"column mount: the ring's teeth and the motor gear overlap by {max(over):.3f} mm2 somewhere in the ring's range")
  rep["window"] = CA.window_check(t)
  if not rep["window"]["ok"]:
    problems.append("column mount: the ring teeth don't fit between the steering wheel's lower spokes")

  # fit in the car for the given covers and clamp position, and the clearance checks
  cfit = CA.solve(args.cover_width, args.cover_height, -args.clamp_behind)
  rep["fit"] = {"ok": cfit.ok, "arm_to_steering_column_deg": round(cfit.arm_deg, 1), "bolt_to_bolt_mm": round(cfit.reach, 1),
                "arm_to_print": f"arm-{int(cfit.arm_len):03d}.stl" if cfit.arm_len else None,
                "slide_from_middle_mm": round(cfit.slide, 1), "saddle_middle_below_column_axis_mm": round(-CA.saddle_y(args.cover_width, args.cover_height), 1),
                "notes": cfit.notes}
  checks = {}
  cbase = dict(base, teeth=cparts["ring-teeth"][0], hinge_block=cparts["hinge-block-column"][0],
               clamp_lower=cparts["column-clamp-lower"][0], clamp_upper=cparts["column-clamp-upper"][0])
  cbase.pop("clamp", None)
  if cfit.ok:
    cbase["arm"] = arms.get(cfit.arm_len) or MP.arm(cfit.arm_len)
    A = CA.ColumnAssembly(t, cfit, cbase, args.cover_width, args.cover_height, -args.clamp_behind)
    checks = CA.check_all(A)
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
    for k in bad:
      problems.append(f"column mount, parts touch: {k} ({checks[k]:.2f} mm3)")
    rep["clearances"] = CA.margins(A)
    # how far back the parts reach: the dash panel below the column must be behind that
    rear = min(m.bounding_box()[2] for m in (A.motor(), A.hinge_block(), A.clamp(), A.clamp_upper(), A.rods(), A.arm()))
    rep["clearances"]["parts_reach_back_to_mm_behind_grip"] = round(-rear, 0)
    if not args.no_pictures:
      column_pictures(A, CA, MP, cparts, args.report, on_bed)
  else:
    problems.append("column mount: the parts do not reach from the clamp position: " + "; ".join(cfit.notes))
  rep["touching_checks_mm3"] = {k: round(v, 3) for k, v in checks.items()}

  # which clamp positions work, for a range of cover heights (the arm that fits, after the clearance checks)
  grid = {"clamp_behind_mm": [160, 180, 200, 220, 250, 280, 310, 340], "cover_height_mm": [70, 85, 95, 110, 125], "cells": []}
  for h in grid["cover_height_mm"]:
    row = []
    for behind in grid["clamp_behind_mm"]:
      f = CA.solve(args.cover_width, h, -behind)
      if not f.ok:
        row.append("no")
        continue
      assy = dict(cbase, arm=arms.get(f.arm_len) or MP.arm(f.arm_len))
      res = CA.check_all(CA.ColumnAssembly(t, f, assy, args.cover_width, h, -behind), lever_step=8.0)
      bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
      row.append(f"arm-{int(f.arm_len):03d}" if not bad else "no")
    grid["cells"].append(row)
  rep["clamp_positions"] = grid

  # margins and the rods
  rep["margins"] = MG.column_rows(t)
  for r in rep["margins"]:
    if r["kind"] == "design" and r["status"] == "UNDER":
      problems.append(f"column mount, under the {MG.FLOOR} floor: {r['what']} ({r['factor']})")
  rep["fasteners"] = CP.clamp_fastener_rows(args.cover_height)
  for r in rep["fasteners"]:
    if not r["ok"]:
      problems.append(f"column mount: {r['bolt']} is too short for the covers' height range")
  return rep


def column_pictures(A, CA, MP, cparts, folder, on_bed):
  import render as R
  from cadlib import box
  lift = MP.cam_lift(MP.A_OFF)
  side = R.look((1, 0, 0), (0, 1, 0))
  R.save(os.path.join(folder, "column-assembly-side.png"),
         [(CA.parts_scene(A), side), (CA.parts_scene(A, lift, MP.A_OFF), side), (CA.parts_scene(A), R.look((0, 0, 1), (0, 1, 0)))],
         ["lift lever down: motor gear in the ring", "lift lever up: motor gear lifted off", "from the driver's seat"],
         suptitle="Column mount, seen from the driver's right (the driver is on the left; the steering column covers at the top)",
         size=(700, 700))
  iso = R.look((1.0, -0.8, 0.9), (0, 1, 0))
  crop = box(-200, 200, -260, -40, -260, 40)
  R.save(os.path.join(folder, "column-assembly-3d.png"),
         [([(m ^ crop, c) for m, c in CA.parts_scene(A) if not (m ^ crop).is_empty()], iso),
          ([(m ^ crop, c) for m, c in CA.parts_scene(A, lift, MP.A_OFF) if not (m ^ crop).is_empty()], iso)],
         ["lift lever down", "lift lever up"], size=(900, 760))
  view = R.look((0.8, -1.0, 0.7), (0, 0, 1))
  panels, titles = [], []
  for n, (m, rot, how, sup) in cparts.items():
    panels.append(([(on_bed(m, rot), (.55, .7, .9))], view))
    titles.append(n)
  R.save(os.path.join(folder, "column-parts.png"), panels, titles, size=(560, 500))


def column_text(c: dict, MG) -> list:
  L = [""]
  inp = c["inputs"]
  L.append("=" * 100)
  L.append("COLUMN MOUNT: the motor under the steering wheel, behind it, its gear inside a ring of teeth; the arm up to a clamp "
           "round the steering column covers")
  est = inp["estimates"]
  L.append(f"Covers {inp['cover_width_mm']:.0f} wide, {inp['cover_height_mm']:.0f} tall; the clamp's middle {inp['clamp_middle_behind_grip_mm']:.0f} mm "
           f"behind the middle of the part of the wheel you hold; the motor's face {inp['motor_face_behind_grip_mm']:.0f} mm behind it. "
           f"Estimates used for the checks (measure yours): hub radius {est['hub_radius_mm']:.0f}, hub reaching {est['hub_back_mm']:.0f} back, "
           f"the lower spokes' back face {est['spokes_back_at_lever_mm']:.0f} back where the lift lever is, the covers' front edge "
           f"{est['covers_front_edge_behind_grip_mm']:.0f} back, the dash below the column {est['dash_below_column_behind_grip_mm']:.0f} back, "
           f"{est['open_arc_between_lower_spokes_deg']:.0f} degrees open between the lower spokes.")
  L.append("")
  L.append("PARTS (column-mount folder; the motor gear, carrier, lever bracket, lift lever, arm and setup gauge are shared)")
  for p in c["parts"]:
    s_ = p["size_mm"]
    L.append(f"  {p['file']:<42} {s_[0]:5.0f} x {s_[1]:4.0f} x {s_[2]:4.0f} mm  {'fits' if p['fits_bed'] else 'TOO BIG'}  "
             f"{p['filament_if_solid_g']:5.0f} g if solid")
    L.append(f"      print {p['print']}; supports: {p['supports']}")
  g = c["gears"]
  L.append("")
  L.append(f"RING TEETH: {g['teeth']} teeth facing the hub, the motor gear inside at {g['centre_distance_mm']} mm from the column (its roller "
           f"rides a band of radius {g['rolling_band_radius_mm']}). They cover {g['steering_wheel_turn_with_teeth_deg']} degrees of steering "
           f"wheel turn; the motor gear follows over {g['steering_wheel_turn_tracked_deg']}; the piece spans {g['piece_spans_deg']} degrees, "
           f"zip ties at {', '.join(str(a) for a in g['zip_ties_deg'])} degrees each side of 6 o'clock. Most overlap anywhere in the range: "
           f"{g['most_overlap_mm2']} mm2 (should be 0). Free play at the steering wheel: {g['free_play_steering_wheel_deg'][0]} to "
           f"{g['free_play_steering_wheel_deg'][1]} degrees.")
  w = c["window"]
  L.append(f"  Between the wheel's two lower spokes ({w['window_between_spokes_deg']:.0f} degrees open, an estimate from photos) the piece leaves "
           f"{w['room_each_side_deg']} degrees ({w['room_each_side_mm_along_the_grip']:.0f} mm along the grip) each side"
           + ("." if w["ok"] else ": NOT ENOUGH."))
  f = c["fit"]
  L.append("")
  L.append("FIT IN THE CAR (for the covers and clamp position above)")
  if f["ok"]:
    L.append(f"  print {f['arm_to_print']}: bolt to bolt {f['bolt_to_bolt_mm']} mm, the arm slid {f['slide_from_middle_mm']:+.1f} mm from the "
             f"middle of its slot, pointing {f['arm_to_steering_column_deg']} degrees below the column towards you. The lower saddle's V "
             f"sits {f['saddle_middle_below_column_axis_mm']} mm below the column's axis.")
  else:
    L.append("  does not fit: " + "; ".join(f["notes"]))
  if "clearances" in c:
    cl = c["clearances"]
    L.append(f"  lever up: motor gear {cl['motor_gear_to_ring_teeth_with_lever_up']} mm clear of the ring's teeth; the lift lever's handle "
             f"{cl['lift_lever_handle_to_the_spoke_sweep_zone']} mm behind where the spokes sweep; lever up, the handle {cl['lift_lever_up_to_the_hub']} mm "
             f"from the hub (25 means more than 25); the arm {cl['arm_to_the_column_covers']} mm below the covers; the parts reach "
             f"{cl['parts_reach_back_to_mm_behind_grip']:.0f} mm back from the middle of the grip (the dash below the column must be further).")
  touching = [k for k, v in c["touching_checks_mm3"].items() if ("should touch" not in k and v > 1e-3)]
  L.append(f"  {len(c['touching_checks_mm3'])} clearance checks, {len(touching)} touching")
  gr = c["clamp_positions"]
  L.append("")
  L.append("WHICH CLAMP POSITIONS WORK (rows: the covers' height; columns: the clamp's middle, mm behind the middle of the grip). "
           "Each arm named reaches with both joints in range and nothing touching.")
  L.append("        " + "".join(f"{x:>10}" for x in gr["clamp_behind_mm"]))
  for h, row in zip(gr["cover_height_mm"], gr["cells"]):
    L.append(f"  {h:5}  " + "".join(f"{x:>10}" for x in row))
  L.append("")
  L.append("MARGINS (the column mount's own; the shared parts' margins are above)")
  L += MG.text_lines(c["margins"])
  L.append("")
  L.append("RODS")
  for b in c["fasteners"]:
    L.append(f"  {b['bolt']:28s} {b['use']}: needs {b['needs_mm'][0]} to {b['needs_mm'][1]} mm over the covers' height range; "
             f"{b['used_for_your_cover_mm']} mm for yours{'' if b['ok'] else '  TOO SHORT'}")
  return L


PYEOF
python3 - <<'EOF'
p='/home/claude/deliver/hardware/cad/accord_lka_parts.py'; s=open(p).read()
fn=open('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/col_build_fn.py').read()
old='def support_area(m, max_angle: float = 45.0):'
assert old in s; s=s.replace(old, fn + old, 1)
old='''  L.append("")
  if r["problems"]:
    L.append("PROBLEMS")'''
new='''  if "column_mount" in r:
    L += column_text(r["column_mount"], MG)
  L.append("")
  if r["problems"]:
    L.append("PROBLEMS")'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s); print("ok part 2")
EOF
python3 - <<'EOF'
src = open('accord_lka_parts.py').read()
marker = "\n\ndef column_pictures(A, CA, MP, cparts, folder, on_bed):"
new = '''

def side_mount(args, base: dict, arms: dict, problems: list, on_bed, write_stl, part_rows: list, bed) -> dict:
  """The right-side mount's parts, checks and report (columnparts.py, columnassembly.py). Its own STL files go to
  <out>/column-mount-right; the hinge block, carrier and fit test are the column mount's, already written."""
  import columnassembly as CA   # noqa: E402
  import columnparts as CP      # noqa: E402
  import margins as MG          # noqa: E402
  import mountparts as MP       # noqa: E402

  out = os.path.join(args.out, "column-mount-right")
  os.makedirs(out, exist_ok=True)
  rep = {"inputs": {"screw_right_of_wheel_edge_mm": args.screw_right, "screw_below_that_mm": args.screw_down,
                    "screw_behind_rim_front_mm": args.screw_behind, "cover_width_mm": args.cover_width,
                    "cover_front_width_mm": args.cover_front_width, "cover_height_mm": args.cover_height,
                    "ring_above_3_oclock_deg": args.ring_at, "motor_face_behind_grip_mm": -P.Z_MOTOR_FACE_C,
                    "estimates": {"wiper_stalk_from_to_mm": [list(P.STALK_FROM), list(P.STALK_TO)],
                                  "key_cylinder_from_to_mm": [list(P.KEY_FROM), list(P.KEY_TO)],
                                  "covers_front_edge_behind_grip_mm": -P.COVER_FRONT_Z, "hub_radius_mm": P.HUB_R,
                                  "right_spoke_meets_grip_deg_below_3_oclock": [2, 25]}}}
  t = CP.RingTeeth(args.wheel_od, args.grip, shallow=True)
  sfit = CA.solve_side(args.cover_width, args.screw_right, args.screw_down, args.screw_behind, args.tab_length, args.ring_at)
  front_down = "front face (the side towards you) down"
  cparts = {
    "ring-teeth-right": (CP.ring_teeth(t), (180, 0, 0), front_down, "none"),
    "side-bracket": (CP.side_bracket(), (0, 90, 0), "the plate's inner face (the covers' side) down", "none"),
  }
  tab_lengths = list(CP.TAB_LENGTHS) + ([args.tab_length] if args.tab_length and args.tab_length not in CP.TAB_LENGTHS else [])
  for L in tab_lengths:
    cparts[f"screw-tab-{int(L):03d}"] = (CP.screw_tab(L, sfit.plate_y), (0, 0, 0), "back face (the dash's side) down", "none")
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
    row = {"file": "column-mount-right/" + name + ".stl", "print": how + (f", turned {zr} degrees on the bed" if zr else ""),
           "supports": supports, "size_mm": [round(v, 1) for v in size], "fits_bed": fits, "solid_volume_cm3": round(vol, 1),
           "filament_if_solid_g": round(vol * PETG_DENSITY, 1), "pieces": pieces, "closed_solid": status == "NoError",
           "overhang_needing_support_mm2": round(support_mm2)}
    rows.append(row)
    part_rows.append(row)
    if pieces != 1 or status != "NoError":
      problems.append(f"right-side mount, {name}: not one closed solid ({pieces} pieces, {status})")
    if not fits:
      problems.append(f"right-side mount, {name}: {size[0]:.0f} x {size[1]:.0f} x {size[2]:.0f} mm does not fit the print bed")
    write_stl(p2, os.path.join(out, name + ".stl"), name)
  rep["parts"] = rows
  slots = sorted(CP.slot_angles(t))
  rep["ring"] = {"teeth": t.n_teeth, "piece_spans_deg": round(t.span_deg, 1), "zip_tie_slots": len(slots),
                 "slots_every_deg": CP.SLOT_EVERY_DEG, "channel_walls_reach_in_mm": CP.SHALLOW_REACH,
                 "piece_reaches_below_3_oclock_deg": round(t.half - args.ring_at, 1),
                 "piece_reaches_above_3_oclock_deg": round(t.half + args.ring_at, 1),
                 "note": "the teeth, rolling band and lead-in are the column mount's ring teeth, so its mesh sweep and free play apply"}

  rep["fit"] = {"ok": sfit.ok, "arm_to_steering_column_deg": round(sfit.arm_deg, 1), "bolt_to_bolt_mm": round(sfit.reach, 1),
                "arm_to_print": f"arm-{int(sfit.arm_len):03d}.stl" if sfit.arm_len else None,
                "slide_from_middle_mm": round(sfit.slide, 1),
                "screw_tab_to_print": f"screw-tab-{int(sfit.tab_len):03d}.stl" if sfit.tab_len else None,
                "tab_start_along_the_bar_mm": round(sfit.tab_x0 - CP.tab_slide_range()[0], 1),
                "bracket_middle_behind_grip_mm": round(-sfit.bracket_z, 1),
                "bracket_back_face_behind_rim_front_mm": round(P.GRIP / 2 - (sfit.bracket_z + CP.SB_PLATE_Z[0]), 1),
                "notes": sfit.notes}
  checks = {}
  sbase = dict(base, teeth=cparts["ring-teeth-right"][0], hinge_block=MP.hinge_block(CP.ARM_NOMINAL_C),
               carrier=MP.motor_carrier(CP.GUARD_WINDOW_C), side_bracket=cparts["side-bracket"][0])
  sbase.pop("clamp", None)
  if sfit.ok:
    sbase["arm"] = arms.get(sfit.arm_len) or MP.arm(sfit.arm_len)
    sbase["screw_tab"] = cparts[f"screw-tab-{int(sfit.tab_len):03d}"][0]
    A = CA.SideAssembly(t, sfit, sbase, args.cover_width, args.cover_height, args.cover_front_width)
    checks = CA.check_all(A)
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
    for k in bad:
      problems.append(f"right-side mount, parts touch: {k} ({checks[k]:.2f} mm3)")
    rep["clearances"] = CA.margins(A)
    rep["clearances"]["parts_reach_back_to_mm_behind_grip"] = CA.reach_back(A)
    if not args.no_pictures:
      side_pictures(A, CA, MP, cparts, args.report, on_bed)
  else:
    problems.append("right-side mount: the parts do not reach: " + "; ".join(sfit.notes))
  rep["touching_checks_mm3"] = {k: round(v, 3) for k, v in checks.items()}

  # which screw positions work (the arm and tab that fit, after the clearance checks without the dash estimates)
  grid = {"screw_behind_mm": [200, 225, 250, 265, 280, 300, 320], "screw_right_mm": [20, 40, 60, 80, 100, 120], "cells": []}
  for right in grid["screw_right_mm"]:
    row = []
    for behind in grid["screw_behind_mm"]:
      f = CA.solve_side(args.cover_width, right, args.screw_down, behind, None, args.ring_at)
      if not f.ok:
        row.append("no")
        continue
      assy = dict(sbase, arm=arms.get(f.arm_len) or MP.arm(f.arm_len), screw_tab=cparts[f"screw-tab-{int(f.tab_len):03d}"][0])
      A_ = CA.SideAssembly(t, f, assy, args.cover_width, args.cover_height, args.cover_front_width)
      res = CA.check_all(A_, lever_step=8.0, dash=False)
      bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
      row.append(f"arm-{int(f.arm_len):03d}/tab-{int(f.tab_len):03d}" if not bad else "no")
    grid["cells"].append(row)
  rep["screw_positions"] = grid

  # the lift lever flipped up swings in beside the covers: how wide they can be at their front
  widths = {"cover_front_width_mm": [90, 95, 100, 105, 110, 115, 120, 125], "lever_up_clear_by_mm": []}
  if sfit.ok:
    lift = MP.cam_lift(MP.A_OFF)
    lever_up = A.lever(MP.A_OFF, lift + 0.05)
    for w in widths["cover_front_width_mm"]:
      A_ = CA.SideAssembly(t, sfit, sbase, max(args.cover_width, w), args.cover_height, w)
      cov = A_.covers()
      lo, hi = 0.0, 30.0
      if CA.overlap(lever_up, cov) > 1e-3:
        widths["lever_up_clear_by_mm"].append("touches")
        continue
      for _ in range(20):
        mid = (lo + hi) / 2
        if CA.overlap(lever_up.translate((-mid, 0, 0)), cov) > 1e-3:
          hi = mid
        else:
          lo = mid
      widths["lever_up_clear_by_mm"].append(round(lo, 1))
  rep["cover_widths"] = widths

  rep["margins"] = MG.side_rows(t, sfit, args.cover_width)
  for r in rep["margins"]:
    if r["kind"] == "design" and r["status"] == "UNDER":
      problems.append(f"right-side mount, under the {MG.FLOOR} floor: {r['what']} ({r['factor']})")
  rep["fasteners"] = CP.bracket_fastener_rows()
  for r in rep["fasteners"]:
    if not r["ok"]:
      problems.append(f"right-side mount: {r['bolt']} is the wrong length")
  return rep


def side_pictures(A, CA, MP, cparts, folder, on_bed):
  import render as R
  from cadlib import box
  lift = MP.cam_lift(MP.A_OFF)
  front = R.look((0, 0, 1), (0, 1, 0))
  R.save(os.path.join(folder, "side-assembly-front.png"),
         [(CA.parts_scene(A), front), (CA.parts_scene(A, lift, MP.A_OFF), front), (CA.parts_scene(A), R.look((0, 1, 0), (0, 0, 1)))],
         ["lift lever down: motor gear in the ring", "lift lever up: motor gear lifted off, the handle in towards the hub",
          "from above (the driver is at the bottom)"],
         suptitle="Right-side mount, from the driver's seat: the ring teeth at 3 o'clock, the motor behind the wheel, the side "
                  "bracket on the column covers and the screw tab out to the dash's screw (the wiper stalk and key cylinder are estimates)",
         size=(700, 700))
  iso = R.look((1.0, 0.8, 0.9), (0, 1, 0))
  crop = box(40, 320, -170, 130, -290, 40)
  R.save(os.path.join(folder, "side-assembly-3d.png"),
         [([(m ^ crop, c) for m, c in CA.parts_scene(A) if not (m ^ crop).is_empty()], iso),
          ([(m ^ crop, c) for m, c in CA.parts_scene(A, lift, MP.A_OFF) if not (m ^ crop).is_empty()], iso)],
         ["lift lever down", "lift lever up"], size=(900, 760))
  view = R.look((0.8, -1.0, 0.7), (0, 0, 1))
  panels, titles = [], []
  for n, (m, rot, how, sup) in cparts.items():
    panels.append(([(on_bed(m, rot), (.55, .7, .9))], view))
    titles.append(n)
  R.save(os.path.join(folder, "side-parts.png"), panels, titles, size=(560, 500))


def side_text(c: dict, MG) -> list:
  L = [""]
  inp = c["inputs"]
  L.append("=" * 100)
  L.append("RIGHT-SIDE MOUNT: the ring teeth at 3 o'clock on the back of the steering wheel, the motor behind the wheel there; the "
           "arm back to a side bracket zip-tied to the column covers' right-hand side, held to the dash's own screw by the screw tab")
  est = inp["estimates"]
  L.append(f"The dash's screw: {inp['screw_right_of_wheel_edge_mm']:.0f} mm right of the wheel's outer edge at 3 o'clock, "
           f"{inp['screw_below_that_mm']:.0f} mm below that point, {inp['screw_behind_rim_front_mm']:.0f} mm behind the front face of "
           f"the rim (estimates: measure yours). Covers {inp['cover_width_mm']:.0f} wide at the bracket, "
           f"{inp['cover_front_width_mm']:.0f} at their front edge, {inp['cover_height_mm']:.0f} tall; the mount "
           f"{inp['ring_above_3_oclock_deg']:.0f} degrees above 3 o'clock. Estimates used for the checks: the wiper stalk from "
           f"{est['wiper_stalk_from_to_mm'][0]} to {est['wiper_stalk_from_to_mm'][1]}, the key cylinder from "
           f"{est['key_cylinder_from_to_mm'][0]} to {est['key_cylinder_from_to_mm'][1]} (steering wheel frame, mm: right, up, "
           f"towards you from the middle of the grip), the right spoke meeting the grip {est['right_spoke_meets_grip_deg_below_3_oclock'][0]} "
           f"to {est['right_spoke_meets_grip_deg_below_3_oclock'][1]} degrees below 3 o'clock.")
  L.append("")
  L.append("PARTS (column-mount-right folder; the hinge block, motor carrier and fit test are the column mount's, the motor gear, "
           "lever bracket, lift lever, arm and setup gauge the dash mount's)")
  for p in c["parts"]:
    s_ = p["size_mm"]
    L.append(f"  {p['file']:<42} {s_[0]:5.0f} x {s_[1]:4.0f} x {s_[2]:4.0f} mm  {'fits' if p['fits_bed'] else 'TOO BIG'}  "
             f"{p['filament_if_solid_g']:5.0f} g if solid")
    L.append(f"      print {p['print']}; supports: {p['supports']}")
  r = c["ring"]
  L.append("")
  L.append(f"RING TEETH (right): {r['teeth']} teeth, the same teeth, rolling band and lead-in as the column mount's ring; the piece "
           f"spans {r['piece_spans_deg']} degrees ({r['piece_reaches_below_3_oclock_deg']} below 3 o'clock to "
           f"{r['piece_reaches_above_3_oclock_deg']} above), with {r['zip_tie_slots']} zip tie slots every {r['slots_every_deg']} degrees: "
           f"tie it wherever the spoke leaves room. Its channel's walls reach only {r['channel_walls_reach_in_mm']:.0f} mm in from "
           "the middle of the grip, so it can sit over the right spoke's junction with the grip.")
  f = c["fit"]
  L.append("")
  L.append("FIT IN THE CAR (for the screw and covers above)")
  if f["ok"]:
    L.append(f"  print {f['arm_to_print']} and {f['screw_tab_to_print']}: bolt to bolt {f['bolt_to_bolt_mm']} mm, the arm slid "
             f"{f['slide_from_middle_mm']:+.1f} mm from the middle of its slot, pointing {f['arm_to_steering_column_deg']} degrees out "
             f"from the column towards you; the screw tab's start {f['tab_start_along_the_bar_mm']} mm along the bracket's bar from "
             f"its innermost place. The bracket's back face sits {f['bracket_back_face_behind_rim_front_mm']:.0f} mm behind the front "
             "of the rim (at the screw's depth), its middle {:.0f} mm behind the middle of the grip.".format(f['bracket_middle_behind_grip_mm']))
  else:
    L.append("  does not fit: " + "; ".join(f["notes"]))
  if "clearances" in c:
    cl = c["clearances"]
    L.append(f"  lever up: motor gear {cl['motor_gear_to_ring_teeth_with_lever_up']} mm clear of the ring's teeth; the lift lever's "
             f"handle {cl['lift_lever_handle_to_the_spoke_sweep_zone']} mm behind where the spokes sweep; lever up, the handle "
             f"{cl['lift_lever_up_to_the_hub']} mm from the hub (25 means more than 25); the arm {cl['arm_to_the_column_covers']} mm "
             f"from the covers; the lift lever {cl['lift_lever_to_the_wiper_stalk']} mm and the hinge block and motor "
             f"{cl['hinge_block_and_motor_to_the_wiper_stalk']} mm below the wiper stalk; the arm and bracket "
             f"{cl['arm_and_bracket_to_the_key_cylinder']} mm behind the key cylinder; the parts reach "
             f"{cl['parts_reach_back_to_mm_behind_grip']:.0f} mm back from the middle of the grip.")
  touching = [k for k, v in c["touching_checks_mm3"].items() if ("should touch" not in k and v > 1e-3)]
  L.append(f"  {len(c['touching_checks_mm3'])} clearance checks, {len(touching)} touching")
  gr = c["screw_positions"]
  L.append("")
  L.append("WHICH SCREW POSITIONS WORK (rows: the screw right of the wheel's edge, mm; columns: behind the front of the rim, mm). "
           "Each cell names the arm and screw tab that reach with both joints in range and nothing touching (the dash estimates "
           "left out).")
  L.append("        " + "".join(f"{x:>16}" for x in gr["screw_behind_mm"]))
  for h, row in zip(gr["screw_right_mm"], gr["cells"]):
    L.append(f"  {h:5}  " + "".join(f"{x:>16}" for x in row))
  cw = c["cover_widths"]
  L.append("")
  L.append("THE COVERS' WIDTH AT THEIR FRONT: the lift lever, flipped up, swings in beside the covers about 85 mm behind the "
           "middle of the grip. How far the handle then clears them, for covers this wide at their front edge:")
  L.append("        " + "".join(f"{x:>10}" for x in cw["cover_front_width_mm"]))
  L.append("        " + "".join(f"{str(x):>10}" for x in cw["lever_up_clear_by_mm"]))
  L.append("  (wider: turn the mount up with --ring-at, or measure the covers 85 mm behind the rim and use that width)")
  L.append("")
  L.append("MARGINS (the right-side mount's own; the shared parts' margins are above)")
  L += MG.text_lines(c["margins"])
  L.append("")
  L.append("BOLTS, SCREW AND TIES")
  for b in c["fasteners"]:
    if b["length"]:
      L.append(f"  {b['bolt']:20s} {b['use']}: through {b['through_mm']} mm, then a {b['nut_mm']} mm lock nut: {b['past_the_nut_mm']} mm "
               f"to spare{'' if b['ok'] else '  WRONG LENGTH'}")
    else:
      L.append(f"  {b['bolt']:20s} {b['use']}")
  return L
'''
src = src.replace(marker, new + marker, 1)
open('accord_lka_parts.py', 'w').write(src)
print('ok')
EOF
grep -n "column_text(report\|column_text(rep\|def text_report" accord_lka_parts.py | head
python3 - <<'EOF'
import re
def wrap_file(path, fixes):
  s=open(path).read()
  for old,new in fixes:
    assert old in s, (path, old[:60])
    s=s.replace(old,new)
  open(path,'w').write(s)

wrap_file('accord_lka_parts.py', [
('''  ap.add_argument("--cover-width", type=float, default=P.COVER_W, help="column mount: the steering column covers, side to side, where the clamp sits (mm)")''',
'''  ap.add_argument("--cover-width", type=float, default=P.COVER_W,
                  help="column mount: the steering column covers, side to side, where the clamp sits (mm)")'''),
('''  rep = {"inputs": {"cover_width_mm": args.cover_width, "cover_height_mm": args.cover_height,
                    "clamp_middle_behind_grip_mm": args.clamp_behind, "motor_face_behind_grip_mm": -P.Z_MOTOR_FACE_C,
                    "estimates": {"hub_radius_mm": P.HUB_R, "hub_back_mm": -P.HUB_BACK_Z, "spokes_back_at_lever_mm": -P.SPOKE_BACK_Z,
                                  "dash_below_column_behind_grip_mm": -P.DASH_Z, "covers_front_edge_behind_grip_mm": -P.COVER_FRONT_Z,
                                  "open_arc_between_lower_spokes_deg": P.WINDOW_DEG}}}''',
'''  rep = {"inputs": {"cover_width_mm": args.cover_width, "cover_height_mm": args.cover_height,
                    "clamp_middle_behind_grip_mm": args.clamp_behind, "motor_face_behind_grip_mm": -P.Z_MOTOR_FACE_C,
                    "estimates": {"hub_radius_mm": P.HUB_R, "hub_back_mm": -P.HUB_BACK_Z,
                                  "spokes_back_at_lever_mm": -P.SPOKE_BACK_Z, "dash_below_column_behind_grip_mm": -P.DASH_Z,
                                  "covers_front_edge_behind_grip_mm": -P.COVER_FRONT_Z,
                                  "open_arc_between_lower_spokes_deg": P.WINDOW_DEG}}}'''),
('''    "column-clamp-lower": (CP.column_clamp_lower(), (0, 0, 90), "on its side", "tree supports under the upper side plate, everywhere"),''',
'''    "column-clamp-lower": (CP.column_clamp_lower(), (0, 0, 90), "on its side",
                           "tree supports under the upper side plate, everywhere"),'''),
('''  rep["gears"] = {"centre_distance_mm": round(cd, 2), "rolling_band_radius_mm": round(t.r_roll, 2), "teeth": t.n_teeth,
                  "steering_wheel_turn_with_teeth_deg": round(t.teeth_arc_deg, 1), "steering_wheel_turn_tracked_deg": round(t.tracked_arc_deg, 1),
                  "piece_spans_deg": round(t.span_deg, 1), "zip_ties_deg": list(t.tie_angles), "most_overlap_mm2": round(max(over), 4),
                  "free_play_steering_wheel_deg": [round(min(plays), 3), round(max(plays), 3)]}''',
'''  rep["gears"] = {"centre_distance_mm": round(cd, 2), "rolling_band_radius_mm": round(t.r_roll, 2), "teeth": t.n_teeth,
                  "steering_wheel_turn_with_teeth_deg": round(t.teeth_arc_deg, 1),
                  "steering_wheel_turn_tracked_deg": round(t.tracked_arc_deg, 1), "piece_spans_deg": round(t.span_deg, 1),
                  "zip_ties_deg": list(t.tie_angles), "most_overlap_mm2": round(max(over), 4),
                  "free_play_steering_wheel_deg": [round(min(plays), 3), round(max(plays), 3)]}'''),
('''  rep["fit"] = {"ok": cfit.ok, "arm_to_steering_column_deg": round(cfit.arm_deg, 1), "bolt_to_bolt_mm": round(cfit.reach, 1),
                "arm_to_print": f"arm-{int(cfit.arm_len):03d}.stl" if cfit.arm_len else None,
                "slide_from_middle_mm": round(cfit.slide, 1), "saddle_middle_below_column_axis_mm": round(-CA.saddle_y(args.cover_width, args.cover_height), 1),
                "notes": cfit.notes}''',
'''  rep["fit"] = {"ok": cfit.ok, "arm_to_steering_column_deg": round(cfit.arm_deg, 1), "bolt_to_bolt_mm": round(cfit.reach, 1),
                "arm_to_print": f"arm-{int(cfit.arm_len):03d}.stl" if cfit.arm_len else None,
                "slide_from_middle_mm": round(cfit.slide, 1),
                "saddle_middle_below_column_axis_mm": round(-CA.saddle_y(args.cover_width, args.cover_height), 1),
                "notes": cfit.notes}'''),
('''  L.append(f"Covers {inp['cover_width_mm']:.0f} wide, {inp['cover_height_mm']:.0f} tall; the clamp's middle {inp['clamp_middle_behind_grip_mm']:.0f} mm "
           f"behind the middle of the part of the wheel you hold; the motor's face {inp['motor_face_behind_grip_mm']:.0f} mm behind it. "
           f"Estimates used for the checks (measure yours): hub radius {est['hub_radius_mm']:.0f}, hub reaching {est['hub_back_mm']:.0f} back, "
           f"the lower spokes' back face {est['spokes_back_at_lever_mm']:.0f} back where the lift lever is, the covers' front edge "
           f"{est['covers_front_edge_behind_grip_mm']:.0f} back, the dash below the column {est['dash_below_column_behind_grip_mm']:.0f} back, "
           f"{est['open_arc_between_lower_spokes_deg']:.0f} degrees open between the lower spokes.")''',
'''  L.append(f"Covers {inp['cover_width_mm']:.0f} wide, {inp['cover_height_mm']:.0f} tall; the clamp's middle "
           f"{inp['clamp_middle_behind_grip_mm']:.0f} mm behind the middle of the part of the wheel you hold; the motor's face "
           f"{inp['motor_face_behind_grip_mm']:.0f} mm behind it. Estimates used for the checks (measure yours): hub radius "
           f"{est['hub_radius_mm']:.0f}, hub reaching {est['hub_back_mm']:.0f} back, the lower spokes' back face "
           f"{est['spokes_back_at_lever_mm']:.0f} back where the lift lever is, the covers' front edge "
           f"{est['covers_front_edge_behind_grip_mm']:.0f} back, the dash below the column "
           f"{est['dash_below_column_behind_grip_mm']:.0f} back, {est['open_arc_between_lower_spokes_deg']:.0f} degrees open "
           "between the lower spokes.")'''),
('''  L.append(f"RING TEETH: {g['teeth']} teeth facing the hub, the motor gear inside at {g['centre_distance_mm']} mm from the column (its roller "
           f"rides a band of radius {g['rolling_band_radius_mm']}). They cover {g['steering_wheel_turn_with_teeth_deg']} degrees of steering "
           f"wheel turn; the motor gear follows over {g['steering_wheel_turn_tracked_deg']}; the piece spans {g['piece_spans_deg']} degrees, "
           f"zip ties at {', '.join(str(a) for a in g['zip_ties_deg'])} degrees each side of 6 o'clock. Most overlap anywhere in the range: "
           f"{g['most_overlap_mm2']} mm2 (should be 0). Free play at the steering wheel: {g['free_play_steering_wheel_deg'][0]} to "
           f"{g['free_play_steering_wheel_deg'][1]} degrees.")
  w = c["window"]
  L.append(f"  Between the wheel's two lower spokes ({w['window_between_spokes_deg']:.0f} degrees open, an estimate from photos) the piece leaves "
           f"{w['room_each_side_deg']} degrees ({w['room_each_side_mm_along_the_grip']:.0f} mm along the grip) each side"
           + ("." if w["ok"] else ": NOT ENOUGH."))''',
'''  L.append(f"RING TEETH: {g['teeth']} teeth facing the hub, the motor gear inside at {g['centre_distance_mm']} mm from the column "
           f"(its roller rides a band of radius {g['rolling_band_radius_mm']}). They cover {g['steering_wheel_turn_with_teeth_deg']} "
           f"degrees of steering wheel turn; the motor gear follows over {g['steering_wheel_turn_tracked_deg']}; the piece spans "
           f"{g['piece_spans_deg']} degrees, zip ties at {', '.join(str(a) for a in g['zip_ties_deg'])} degrees each side of "
           f"6 o'clock. Most overlap anywhere in the range: {g['most_overlap_mm2']} mm2 (should be 0). Free play at the steering "
           f"wheel: {g['free_play_steering_wheel_deg'][0]} to {g['free_play_steering_wheel_deg'][1]} degrees.")
  w = c["window"]
  L.append(f"  Between the wheel's two lower spokes ({w['window_between_spokes_deg']:.0f} degrees open, an estimate from photos) "
           f"the piece leaves {w['room_each_side_deg']} degrees ({w['room_each_side_mm_along_the_grip']:.0f} mm along the grip) "
           "each side" + ("." if w["ok"] else ": NOT ENOUGH."))'''),
('''    L.append(f"  print {f['arm_to_print']}: bolt to bolt {f['bolt_to_bolt_mm']} mm, the arm slid {f['slide_from_middle_mm']:+.1f} mm from the "
             f"middle of its slot, pointing {f['arm_to_steering_column_deg']} degrees below the column towards you. The lower saddle's V "
             f"sits {f['saddle_middle_below_column_axis_mm']} mm below the column's axis.")''',
'''    L.append(f"  print {f['arm_to_print']}: bolt to bolt {f['bolt_to_bolt_mm']} mm, the arm slid {f['slide_from_middle_mm']:+.1f} mm "
             f"from the middle of its slot, pointing {f['arm_to_steering_column_deg']} degrees below the column towards you. The "
             f"lower saddle's V sits {f['saddle_middle_below_column_axis_mm']} mm below the column's axis.")'''),
('''    L.append(f"  lever up: motor gear {cl['motor_gear_to_ring_teeth_with_lever_up']} mm clear of the ring's teeth; the lift lever's handle "
             f"{cl['lift_lever_handle_to_the_spoke_sweep_zone']} mm behind where the spokes sweep; lever up, the handle {cl['lift_lever_up_to_the_hub']} mm "
             f"from the hub (25 means more than 25); the arm {cl['arm_to_the_column_covers']} mm below the covers; the parts reach "
             f"{cl['parts_reach_back_to_mm_behind_grip']:.0f} mm back from the middle of the grip (the dash below the column must be further).")''',
'''    L.append(f"  lever up: motor gear {cl['motor_gear_to_ring_teeth_with_lever_up']} mm clear of the ring's teeth; the lift lever's "
             f"handle {cl['lift_lever_handle_to_the_spoke_sweep_zone']} mm behind where the spokes sweep; lever up, the handle "
             f"{cl['lift_lever_up_to_the_hub']} mm from the hub (25 means more than 25); the arm {cl['arm_to_the_column_covers']} mm "
             f"below the covers; the parts reach {cl['parts_reach_back_to_mm_behind_grip']:.0f} mm back from the middle of the grip "
             "(the dash below the column must be further).")'''),
('''  L.append("WHICH CLAMP POSITIONS WORK (rows: the covers' height; columns: the clamp's middle, mm behind the middle of the grip). "
           "Each arm named reaches with both joints in range and nothing touching; in brackets, how far back the parts then "
           "reach (mm behind the middle of the grip): the dash below the column must be further than that.")''',
'''  L.append("WHICH CLAMP POSITIONS WORK (rows: the covers' height; columns: the clamp's middle, mm behind the middle of the "
           "grip). Each arm named reaches with both joints in range and nothing touching; in brackets, how far back the parts "
           "then reach (mm behind the middle of the grip): the dash below the column must be further than that. A row of "
           "no: the lift lever, flipped up, meets covers that tall (if their front edge is where estimated).")'''),
('''    L.append(f"  {b['bolt']:28s} {b['use']}: needs {b['needs_mm'][0]} to {b['needs_mm'][1]} mm over the covers' height range; "
             f"{b['used_for_your_cover_mm']} mm for yours{'' if b['ok'] else '  TOO SHORT'}")''',
'''    L.append(f"  {b['bolt']:28s} {b['use']}: needs {b['needs_mm'][0]} to {b['needs_mm'][1]} mm over the covers' height "
             f"range; {b['used_for_your_cover_mm']} mm for yours{'' if b['ok'] else '  TOO SHORT'}")'''),
])
wrap_file('columnparts.py', [
('''  zt0, zt1 = Z_TEETH_C
  zr0, zr1 = Z_ROLL_C
  zf = zt1 + t.teeth_chamfer + 2.0''', '''  zt1 = Z_TEETH_C[1]
  zr0, zr1 = Z_ROLL_C
  zf = zt1 + t.teeth_chamfer + 2.0'''),
('''    plate = CrossSection.batch_hull([pie, circle_yz(10.0, py, pz), rect_yz(SADDLE_BOTTOM - 0.01, SADDLE_BOTTOM + 1.0, -SADDLE_LEN / 2, SADDLE_LEN / 2)])''',
'''    plate = CrossSection.batch_hull([pie, circle_yz(10.0, py, pz),
                                     rect_yz(SADDLE_BOTTOM - 0.01, SADDLE_BOTTOM + 1.0, -SADDLE_LEN / 2, SADDLE_LEN / 2)])'''),
('''  rows = [{"bolt": f"M6 threaded rod x {ROD_LEN:.0f} (4)", "use": "column clamp: lower saddle, covers, upper saddle, a nut and washer each end",''',
'''  rows = [{"bolt": f"M6 threaded rod x {ROD_LEN:.0f} (4)",
           "use": "column clamp: lower saddle, covers, upper saddle, a nut and washer each end",'''),
])
wrap_file('margins.py', [
('''CLAMP_SQUEEZE_N = 300.0     # the four threaded rods tightened to "snug, then a quarter turn": about this much between the saddles (estimate)''',
'''CLAMP_SQUEEZE_N = 300.0     # the four threaded rods tightened to "snug, then a quarter turn": about this much between the
                            # saddles (an estimate)'''),
('''  push_n = MP.spring_torque(0) / 50.0 + ft_most * math.tan(phi + math.atan(RUB_DRY))   # roller press (about 29 N) plus separating push''',
'''  push_n = MP.spring_torque(0) / 50.0 + ft_most * math.tan(phi + math.atan(RUB_DRY))   # roller press (29 N) and separating push'''),
])
print("wrapped")
EOF
cd /home/claude/deliver/hardware/cad && grep -n "zt0" columnparts.py | head; /home/claude/bin/ruff check --output-format concise --line-length 140 --select E,F,W . ; echo "E/F/W exit $?"
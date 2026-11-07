python3 - <<'EOF'
p='accord_lka_parts.py'
s=open(p).read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)

rep('''def back_part_list(t, pieces: dict, tests: dict) -> dict:
  """The back-teeth mount's printed parts: name -> (part, how it turns onto the bed, how it prints, supports)."""
  import faceparts as FP        # noqa: E402
  front_down = "front face (the side towards you) down"
  bparts = {
    "back-teeth-upper": (pieces["upper"], (180, 0, 0), front_down, "none"),
    "back-teeth-lower": (pieces["lower"], (180, 0, 0), front_down, "none"),
    "back-teeth-one-piece": (pieces["one-piece"], (180, 0, 0), front_down + " (for print beds 330 mm across)", "none"),''',
'''def back_part_list(t, pieces: dict, tests: dict, short_piece) -> dict:
  """The back-teeth mount's printed parts: name -> (part, how it turns onto the bed, how it prints, supports). pieces:
  the long back teeth's (45 degrees each way); short_piece: the short back teeth (15 degrees each way), one piece."""
  import faceparts as FP        # noqa: E402
  front_down = "front face (the side towards you) down"
  bparts = {
    "back-teeth-15": (short_piece, (180, 0, 0), front_down, "none"),
    "back-teeth-45-upper": (pieces["upper"], (180, 0, 0), front_down, "none"),
    "back-teeth-45-lower": (pieces["lower"], (180, 0, 0), front_down, "none"),
    "back-teeth-45-one-piece": (pieces["one-piece"], (180, 0, 0), front_down + " (for print beds 330 mm across)", "none"),''')

rep('''  whole = FP.face_solid(t)
  pieces = FP.face_pieces(t, whole)
  tests = FP.face_fit_tests(t, whole)
  fit = FA.solve_face(t, P.COVER_BOTTOM)
  bparts = back_part_list(t, pieces, tests)''',
'''  whole = FP.face_solid(t)
  pieces = FP.face_pieces(t, whole)
  tests = FP.face_fit_tests(t, whole)
  t15 = FP.FaceTeeth(args.wheel_od, args.grip, P.RIGHT_SPOKE_DEG, n_teeth=FP.N_TEETH_SHORT)
  short_piece = FP.face_pieces(t15)["one-piece"]
  fit = FA.solve_face(t, P.COVER_BOTTOM)
  bparts = back_part_list(t, pieces, tests, short_piece)''')

rep('''  rep["parts"] = rows
  rep["teeth"] = {"teeth": FP.N_TEETH, "teeth_on_a_full_circle": FP.FACE_TEETH, "motor_gear_teeth": FP.FACE_MOTOR_TEETH,
                  "gear_ratio": round(FP.FACE_RATIO, 4), "pitch_radius_mm": FP.R_F, "teeth_from_to_radius_mm": list(FP.FACE_BAND),
                  "rolling_band_radius_mm": list(FP.ROLL_BAND), "steering_wheel_turn_with_teeth_deg": round(t.teeth_arc_deg, 1),
                  "steering_wheel_turn_tracked_deg": round(t.tracked_arc_deg, 2), "full_push_reach_deg": round(t.teeth_half, 1),
                  "piece_spans_deg": round(t.span_deg, 1), "joint_deg_above_3_oclock": round(t.joint_deg, 2),
                  "zip_tie_slots_deg": [round(a, 2) for a in FP.tie_angles(t)],
                  "notch_for_the_right_spoke_deg": [round(a, 1) for a in t.spoke], "notch_radius_mm": FP.NOTCH_R,
                  "teeth_behind_grip_middle_mm": [round(-t.z_root, 1), round(-t.z_tip, 1)],
                  "motor_face_from_column_axis_mm": FP.R_FACE, "motor_shaft_behind_grip_middle_mm": round(-t.z_axis, 1)}''',
'''  rep["parts"] = rows

  def teeth_info(tt):
    return {"teeth": tt.n_teeth, "teeth_on_a_full_circle": FP.FACE_TEETH, "motor_gear_teeth": FP.FACE_MOTOR_TEETH,
            "gear_ratio": round(FP.FACE_RATIO, 4), "pitch_radius_mm": FP.R_F, "teeth_from_to_radius_mm": list(FP.FACE_BAND),
            "rolling_band_radius_mm": list(FP.ROLL_BAND), "steering_wheel_turn_with_teeth_deg": round(tt.teeth_arc_deg, 1),
            "steering_wheel_turn_tracked_deg": round(tt.tracked_arc_deg, 2), "full_push_reach_deg": round(tt.teeth_half, 1),
            "piece_spans_deg": round(tt.span_deg, 1),
            "joint_deg_above_3_oclock": round(tt.joint_deg, 2) if tt.joint_deg is not None else None,
            "zip_tie_slots_deg": [round(a, 2) for a in FP.tie_angles(tt)],
            "notch_for_the_right_spoke_deg": [round(a, 1) for a in tt.spoke], "notch_radius_mm": FP.NOTCH_R,
            "teeth_behind_grip_middle_mm": [round(-tt.z_root, 1), round(-tt.z_tip, 1)],
            "motor_face_from_column_axis_mm": FP.R_FACE, "motor_shaft_behind_grip_middle_mm": round(-tt.z_axis, 1)}
  rep["teeth"] = teeth_info(t)
  rep["teeth_short"] = teeth_info(t15)''')

rep('''    checks = FA.check_all(A)
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
    for k in bad:
      problems.append(f"back-teeth mount, parts touch: {k} ({checks[k]:.2f} mm3)")''',
'''    checks = FA.check_all(A)
    # the short back teeth: the same mount, the teeth piece ending sooner (the carrier drops at their ends)
    A15 = FA.FaceAssembly(t15, fit, dict(fparts, teeth=short_piece), args.cover_width, args.cover_height, args.cover_front_width)
    mesh15 = FA.mesh_sweep(A15, step=1.0)
    rep["mesh_short"] = mesh15
    if mesh15["worst_overlap_mm3"] > 1e-3:
      problems.append(f"back-teeth mount: the motor gear and the short back teeth overlap by {mesh15['worst_overlap_mm3']} mm3 at "
                      f"{mesh15['worst_at_deg']} degrees")
    for k, v in FA.check_all(A15, lever_step=8.0).items():
      checks["short back teeth: " + k] = v
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
    for k in bad:
      problems.append(f"back-teeth mount, parts touch: {k} ({checks[k]:.2f} mm3)")''')
open(p,'w').write(s)
EOF
/home/claude/bin/ruff check --isolated --select E,F --line-length 140 --output-format concise . ; echo "exit $?"
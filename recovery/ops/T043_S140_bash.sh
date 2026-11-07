python3 - <<'EOF'
s = open('accord_lka_parts.py').read()

s = s.replace('''  steering wheel teeth  - zip-tied around the top of the steering wheel (one piece, or two halves for smaller printers)''',
'''  steering wheel teeth  - zip-tied around the top of the steering wheel (one piece, or two halves for smaller printers);
                          two sets: 15 (reach 15 degrees each way, for getting used to it) and 29 (29 degrees each way)''')

old = '''  # ----- parts -----
  t = WP.Teeth(args.wheel_od, args.grip)
  whole = WP.teeth_solid(t)
  parts = {}       # file name -> (solid in its own frame, rotation for the bed, how to print, supports)
  front_down = "front face (the side towards you) down"
  parts["steering-wheel-teeth-one-piece"] = (WP.teeth_one_piece(t, whole), (180, 0, 0), front_down, "none")
  parts["steering-wheel-teeth-left-half"] = (WP.teeth_half(t, "left", whole), (180, 0, 0), front_down, "none")
  parts["steering-wheel-teeth-right-half"] = (WP.teeth_half(t, "right", whole), (180, 0, 0), front_down, "none")'''
new = '''  # ----- parts -----
  teeth_sets = {reach: WP.Teeth(args.wheel_od, args.grip, reach) for reach in sorted(P.TEETH_SETS)}
  t = teeth_sets[29]
  parts = {}       # file name -> (solid in its own frame, rotation for the bed, how to print, supports)
  front_down = "front face (the side towards you) down"
  for reach, ts in teeth_sets.items():
    whole = WP.teeth_solid(ts)
    parts[f"steering-wheel-teeth-{reach}-one-piece"] = (WP.teeth_one_piece(ts, whole), (180, 0, 0), front_down, "none")
    parts[f"steering-wheel-teeth-{reach}-left-half"] = (WP.teeth_half(ts, "left", whole), (180, 0, 0), front_down, "none")
    parts[f"steering-wheel-teeth-{reach}-right-half"] = (WP.teeth_half(ts, "right", whole), (180, 0, 0), front_down, "none")'''
assert old in s
s = s.replace(old, new)

old = '''  # ----- gears mesh through the whole range of the teeth -----
  ring = WP.teeth_outline(t)
  motor = GR.gear_outline(P.MOTOR_TEETH, P.BACKLASH)
  cd = WP.centre_distance()
  phase = WP.MOTOR_GEAR_PHASE
  sweep = np.linspace(-t.teeth_half, t.teeth_half, 601)
  over = GR.mesh_sweep(ring, P.RING_TEETH, motor, P.MOTOR_TEETH, cd, sweep, phase)
  plays = []
  for w in np.linspace(-t.teeth_half + 3 * t.pitch_deg, t.teeth_half - 3 * t.pitch_deg, 7):
    ratio = P.RING_TEETH / P.MOTOR_TEETH
    ccw, cw = GR.free_play(ring.rotate(float(w)), motor, cd, phase - float(w) * ratio, P.MOTOR_TEETH)
    plays.append((ccw + cw) / ratio)      # free play in steering wheel degrees
  report["gears"] = {"teeth_on_steering_wheel": P.TEETH_ON_WHEEL, "steering_wheel_turn_with_teeth_deg": round(t.teeth_arc_deg, 1),
                     "steering_wheel_turn_tracked_deg": round(t.tracked_arc_deg, 1),
                     "gear_ratio": round(P.RING_TEETH / P.MOTOR_TEETH, 4), "most_overlap_mm2": round(max(over), 4),
                     "free_play_steering_wheel_deg": [round(min(plays), 3), round(max(plays), 3)]}
  if max(over) > 1e-3:
    problems.append(f"the gears overlap by {max(over):.3f} mm2 somewhere in the range of the teeth")'''
new = '''  # ----- gears mesh through the whole range of each set of teeth -----
  motor = GR.gear_outline(P.MOTOR_TEETH, P.BACKLASH)
  cd = WP.centre_distance()
  phase = WP.MOTOR_GEAR_PHASE
  ratio = P.RING_TEETH / P.MOTOR_TEETH
  report["gears"] = {"gear_ratio": round(ratio, 4), "sets": {}}
  for reach, ts in teeth_sets.items():
    ring = WP.teeth_outline(ts)
    sweep = np.linspace(-ts.teeth_half, ts.teeth_half, 601)
    over = GR.mesh_sweep(ring, P.RING_TEETH, motor, P.MOTOR_TEETH, cd, sweep, phase)
    plays = []
    for w in np.linspace(-ts.teeth_half + 3 * ts.pitch_deg, ts.teeth_half - 3 * ts.pitch_deg, 7):
      ccw, cw = GR.free_play(ring.rotate(float(w)), motor, cd, phase - float(w) * ratio, P.MOTOR_TEETH)
      plays.append((ccw + cw) / ratio)      # free play in steering wheel degrees
    report["gears"]["sets"][str(reach)] = {
      "teeth_on_steering_wheel": ts.n_teeth, "steering_wheel_turn_with_teeth_deg": round(ts.teeth_arc_deg, 1),
      "steering_wheel_turn_tracked_deg": round(ts.tracked_arc_deg, 1), "piece_spans_deg": round(2 * ts.half, 1),
      "zip_ties_deg": list(ts.tie_angles), "most_overlap_mm2": round(max(over), 4),
      "free_play_steering_wheel_deg": [round(min(plays), 3), round(max(plays), 3)]}
    if max(over) > 1e-3:
      problems.append(f"the gears overlap by {max(over):.3f} mm2 somewhere in the range of the {reach} teeth")'''
assert old in s
s = s.replace(old, new)

s = s.replace('''  base = {"teeth": parts["steering-wheel-teeth-one-piece"][0], "gear": parts["motor-gear"][0],''',
              '''  base = {"teeth": parts["steering-wheel-teeth-29-one-piece"][0], "gear": parts["motor-gear"][0],''')

old = '''    checks = AS.check_all(A)
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]'''
new = '''    checks = AS.check_all(A)
    # the short teeth: the same checks, with the steering wheel turned past their end
    short = teeth_sets[15]
    assy15 = dict(assy, teeth=parts["steering-wheel-teeth-15-one-piece"][0])
    A15 = AS.Assembly(short, fit, assy15, your_tilt)
    for k, v in AS.check_all(A15, wheel_turn=short.half + 17.0).items():
      if "wheel turned" in k or "teeth" in k:
        checks["15 teeth, " + k] = v
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]'''
assert old in s
s = s.replace(old, new)

old = '''  names = ["steering-wheel-teeth-left-half", "steering-wheel-teeth-right-half", "motor-gear", "motor-carrier", "hinge-block",
           "lever-bracket", "lift-lever", "dash-clamp", "clamp-pad", "setup-gauge", "fit-test-steering-wheel", "fit-test-teeth"]'''
new = '''  names = ["steering-wheel-teeth-29-left-half", "steering-wheel-teeth-29-right-half", "steering-wheel-teeth-15-one-piece",
           "motor-gear", "motor-carrier", "hinge-block", "lever-bracket", "lift-lever", "dash-clamp", "clamp-pad", "setup-gauge",
           "fit-test-steering-wheel", "fit-test-teeth"]'''
assert old in s
s = s.replace(old, new)

old = '''  g = r["gears"]
  L.append("")
  L.append(f"GEARS: ratio {g['gear_ratio']} (motor turns {g['gear_ratio']:.2f} times per steering wheel turn). Teeth cover "
           f"{g['steering_wheel_turn_with_teeth_deg']} degrees of steering wheel turn; the motor gear follows over "
           f"{g['steering_wheel_turn_tracked_deg']} degrees. Most overlap anywhere in the range: {g['most_overlap_mm2']} mm2 "
           f"(should be 0). Free play at the steering wheel: {g['free_play_steering_wheel_deg'][0]} to "
           f"{g['free_play_steering_wheel_deg'][1]} degrees.")'''
new = '''  g = r["gears"]
  L.append("")
  L.append(f"GEARS: ratio {g['gear_ratio']} (motor turns {g['gear_ratio']:.2f} times per steering wheel turn).")
  for reach, gs in g["sets"].items():
    L.append(f"  {reach} teeth: {gs['teeth_on_steering_wheel']} teeth cover {gs['steering_wheel_turn_with_teeth_deg']} degrees "
             f"of steering wheel turn; the motor gear follows over {gs['steering_wheel_turn_tracked_deg']}; the piece spans "
             f"{gs['piece_spans_deg']} degrees, zip ties at {', '.join(str(a) for a in gs['zip_ties_deg'])} degrees each side. "
             f"Most overlap anywhere in the range: {gs['most_overlap_mm2']} mm2 (should be 0). Free play at the steering "
             f"wheel: {gs['free_play_steering_wheel_deg'][0]} to {gs['free_play_steering_wheel_deg'][1]} degrees.")'''
assert old in s
s = s.replace(old, new)
open('accord_lka_parts.py', 'w').write(s)
EOF
grep -n '"no:\|one-piece' accord_lka_parts.py | head
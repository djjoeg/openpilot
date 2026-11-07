python3 - <<'EOF'
s = open('accord_lka_parts.py').read()

s = s.replace('''  motor carrier         - the motor bolts to it; finger guard around the motor gear; turns on the hinge block's hinge
  hinge block           - holds the carrier's hinge, the spring, the lift lever and the power switch; the arm bolts to it
  lift lever            - down: motor gear on the teeth, motor powered. Up: motor gear lifted off, motor's power cut''',
'''  motor carrier         - the motor bolts to it; finger guard around the motor gear; turns on the hinge block's hinge
  lever bracket         - screws onto the carrier; holds the lift lever, the power switch and the lever's click
  hinge block           - holds the carrier's hinge and the spring; the lift lever presses on it; the arm bolts to it
  lift lever            - on the driver's side. Down: motor gear on the teeth, motor powered. Flipped up: motor's power
                          cut, motor gear lifted off''')

s = s.replace('''  parts["hinge-block"] = (MP.hinge_block(), (180, 0, 0), "front end (the end towards you) down",
                          "tree supports, everywhere (small areas under the switch cage, the lever's walls and the hinge)")
  parts["lift-lever"] = (MP.lift_lever(), (0, 90, 0), "on its side", "none")''',
'''  parts["hinge-block"] = (MP.hinge_block(), (180, 0, 0), "front end (the end towards you) down",
                          "tree supports, everywhere (small areas under the hinge, the spring's pocket and the ears)")
  parts["lever-bracket"] = (MP.lever_bracket(), (90, 0, 0), "base plate down", "none")
  parts["lift-lever"] = (MP.lift_lever(), (0, 90, 0), "on its side, the side with the thin tab under the handle down", "none")''')

old = s[s.index('  # ----- lift lever, spring, power switch -----'):s.index('  # ----- fit in the car -----')]
new = '''  # ----- lift lever, spring, power switch -----
  rows = MP.lever_lift_table(1.0)
  lift_up = MP.cam_lift(MP.A_OFF)
  up_rows = [r for r in rows if r[0] <= MP.A_OFF + 1e-9]
  most = max(r[1] for r in up_rows)
  first_lift = next(r[0] for r in rows if r[1] > 0.05)
  # the handle's underside over the switch's roller rises SW_PRESS + SW_MD before the switch is sure to let go
  switch_release = math.degrees(math.asin((MP.SW_PRESS + MP.SW_MD) / MP.SW_D))
  # carrier lift at which the motor gear's teeth come clear of the steering wheel teeth
  overlap_mm = (GR.pitch_radius(P.MOTOR_TEETH) + GR.MODULE) + (GR.pitch_radius(P.RING_TEETH) + GR.MODULE) - WP.centre_distance()
  gz = (P.Z_GEAR_TEETH[0] + P.Z_GEAR_TEETH[1]) / 2 - P.Z_MOTOR_FACE - MP.HINGE[1]
  gy = -MP.HINGE[0]
  clear_deg = next(th / 10 for th in range(1, 300) if gy * math.cos(math.radians(th / 10)) + gz * math.sin(math.radians(th / 10)) - gy >= overlap_mm)
  clear_alpha = next(r[0] for r in rows if r[1] >= clear_deg)
  at_up = next(r for r in rows if abs(r[0] - MP.A_OFF) < 1e-9)
  past_up = next(r for r in rows if r[0] > MP.A_OFF + 1e-9)
  click = MP.finger_force()
  report["lift_lever"] = {
    "turns_deg": MP.A_OFF, "carrier_lift_up_deg": round(lift_up, 2), "most_lift_deg": round(most, 2),
    "starts_lifting_at_deg": first_lift, "switch_releases_by_deg": round(switch_release, 1),
    "motor_gear_out_of_mesh_at_deg": clear_alpha, "carrier_lift_out_of_mesh_deg": round(clear_deg, 1),
    "most_push_at_handle_end_N": round(max(r[2] for r in up_rows), 1),
    "most_push_with_rubbing_N": round(max(r[2] + r[3] for r in up_rows), 1),
    "push_to_bring_it_back_down_N": round(-at_up[2], 1), "push_to_bring_it_back_down_with_rubbing_N": round(-at_up[2] + at_up[3], 1),
    "push_to_go_past_up_N": round(past_up[2], 1), "rubbing_estimate": MP.RUB,
    "drop_gap_mm": round(MP.DROP_GAP, 2), "click": click,
    "table_deg_liftdeg_N_rubN": [[r[0], round(r[1], 2), round(r[2], 2), round(r[3], 2)] for r in rows[::2]]}
  report["spring"] = {"part": "Lee Spring LCM100E03S (9 mm outside, 1 mm wire, 28.5 mm long, 1.98 N/mm)",
                      "length_gear_on_teeth_mm": MP.SPRING_LEN, "force_gear_on_teeth_N": round(MP.spring_force(0), 1),
                      "length_lever_up_mm": round(MP.SPRING_LEN - MP.SPRING_ARM * math.sin(math.radians(most)), 1),
                      "force_lever_up_N": round(MP.spring_force(most), 1), "most_load_N": MP.SPRING_MAX_N,
                      "fully_squashed_mm": MP.SPRING_SOLID}
  if MP.spring_force(most) > MP.SPRING_MAX_N:
    problems.append("the spring is pushed past its most load when the lever is up")
  if switch_release >= first_lift:
    problems.append("the power switch may still be on when the motor gear starts to lift")
  if switch_release >= clear_alpha - 3.0:
    problems.append("the power switch lets go too late (the motor gear is nearly out of mesh by then)")
  if abs(lift_up - MP.LIFT_DEG) > 0.05:
    problems.append(f"lever up holds the carrier at {lift_up:.2f} degrees, not {MP.LIFT_DEG}")
  if not (at_up[2] < 0 < past_up[2]):
    problems.append("the lift lever doesn't stay up by itself")

'''
s = s.replace(old, new)

s = s.replace('''  base = {"teeth": parts["steering-wheel-teeth-one-piece"][0], "gear": parts["motor-gear"][0],
          "gear_teeth_only": WP.motor_gear_teeth_only(), "carrier": parts["motor-carrier"][0],
          "hinge_block": parts["hinge-block"][0], "lever": parts["lift-lever"][0], "clamp": parts["dash-clamp"][0]}''',
'''  base = {"teeth": parts["steering-wheel-teeth-one-piece"][0], "gear": parts["motor-gear"][0],
          "gear_teeth_only": WP.motor_gear_teeth_only(), "carrier": parts["motor-carrier"][0],
          "hinge_block": parts["hinge-block"][0], "bracket": parts["lever-bracket"][0], "lever": parts["lift-lever"][0],
          "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "clamp": parts["dash-clamp"][0]}''')
open('accord_lka_parts.py', 'w').write(s)
EOF
grep -n "A_HARD_STOP\|lever_in_block\|LEVER_ON\|scene(\|A.lever(\|A.switch(" accord_lka_parts.py
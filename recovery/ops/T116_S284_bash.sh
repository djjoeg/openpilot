python3 - <<'EOF'
p='accord_lka_parts.py'
s=open(p).read()
i0 = s.index('''  tt = c["teeth"]
  L.append("")
  L.append(f"BACK TEETH: {tt['teeth']} teeth''')
i1 = s.index('''  f = c["fit"]
  L.append("")
  L.append("FIT IN THE CAR")''', i0)
new = '''  tt = c["teeth"]
  L.append("")
  L.append(f"BACK TEETH: a face gear, {tt['teeth_on_a_full_circle']} teeth on a full circle (2 mm teeth, {tt['pitch_radius_mm']:.0f} mm "
           f"from the column's axis), the motor gear {tt['motor_gear_teeth']} teeth: ratio {tt['gear_ratio']}. The teeth stand "
           f"{tt['teeth_behind_grip_middle_mm'][0]} to {tt['teeth_behind_grip_middle_mm'][1]} mm behind the middle of the grip; the "
           f"motor's front face {tt['motor_face_from_column_axis_mm']:.0f} mm from the column's axis, its shaft "
           f"{tt['motor_shaft_behind_grip_middle_mm']} mm behind the middle of the grip. No inner wall inside "
           f"{tt['notch_radius_mm']:.0f} mm from {tt['notch_for_the_right_spoke_deg'][0]} to {tt['notch_for_the_right_spoke_deg'][1]} "
           "degrees, over the right spoke's junction. Two sets:")
  for key, mkey, label in (("teeth_short", "mesh_short", "back-teeth-15, the short set (for the highway)"),
                           ("teeth", "mesh", "back-teeth-45, the long set (off the highway)")):
    s_ = c.get(key)
    if not s_:
      continue
    joint = (f"in two pieces meeting {s_['joint_deg_above_3_oclock']} degrees above 3 o'clock"
             if s_["joint_deg_above_3_oclock"] is not None else "one piece")
    L.append(f"  {label}: {s_['teeth']} teeth reaching {s_['full_push_reach_deg']} degrees each way; with the rolling band past "
             f"them the motor gear turns with the wheel over {s_['steering_wheel_turn_tracked_deg']} degrees. It spans "
             f"{s_['piece_spans_deg']} degrees, {joint}; zip tie slots at {s_['zip_tie_slots_deg']} degrees.")
    if mkey in c:
      m = c[mkey]
      L.append(f"    gear mesh through its whole arc (every 1 degree): worst overlap {m['worst_overlap_mm3']} mm3; free play "
               f"{m['free_play_steering_wheel_deg']} degrees of steering wheel (the motor gear turns {m['free_play_motor_gear_deg'][0][0]} "
               "degrees each way before its teeth touch).")
'''
s = s[:i0] + new + s[i1:]
old = '''  touching = [k for k, v in c["touching_checks_mm3"].items() if ("should touch" not in k and v > 1e-3)]
  L.append(f"  {len(c['touching_checks_mm3'])} clearance checks, {len(touching)} touching")
  h = c["cover_heights"]'''
assert s.count(old) == 1
s = s.replace(old, '''  touching = [k for k, v in c["touching_checks_mm3"].items() if ("should touch" not in k and v > 1e-3)]
  n_short = len([k for k in c["touching_checks_mm3"] if k.startswith("short back teeth: ")])
  L.append(f"  {len(c['touching_checks_mm3'])} clearance checks ({len(c['touching_checks_mm3']) - n_short} with the long back teeth, "
           f"{n_short} with the short), {len(touching)} touching")
  h = c["cover_heights"]''')
open(p,'w').write(s)

p='faceparts.py'
s=open(p).read()
old = '''  back teeth        - the channel with the teeth and the rolling band on its back, in two pieces glued end to end (or
                      one piece for print beds 330 mm across), zip-tied round the grip. Over the right spoke's junction
                      with the grip it wraps only the grip's back and outside.'''
assert s.count(old) == 1
s = s.replace(old, '''  back teeth        - the channel with the teeth and the rolling band on its back, zip-tied round the grip, in two sets
                      like the other mounts' teeth: the short set (14 teeth, 15 degrees each way, from about 2 to 4
                      o'clock, one piece) for the highway, and the long set (42 teeth, 45 degrees each way, from 1 to 5
                      o'clock, two pieces glued end to end, or one piece for print beds 330 mm across). Over the right
                      spoke's junction with the grip the channel wraps only the grip's back and outside.''')
old = '''grip, its shaft pointing at the steering column, and its 16-tooth gear meshes the teeth from behind. 166 / 16 is
10.375, within 0.1% of the other mounts' 197 / 19, so the torque and angle the software works with are unchanged.'''
assert s.count(old) == 1
s = s.replace(old, '''grip, its shaft pointing at the steering column, and its 16-tooth gear meshes the teeth from behind. 166 / 16 is
10.375, within 0.1% of the other mounts' 197 / 19; the car setup saves the back teeth's own gearing for the long set
(its answer 45) and takes the short set as the other mounts' short teeth (15).''')
open(p,'w').write(s)
print("ok")
EOF
/home/claude/bin/ruff check --isolated --select E,F --line-length 140 --output-format concise . ; echo "exit $?"
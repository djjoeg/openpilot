python3 - << 'EOF'
p = "accord_lka_parts.py"
s = open(p).read()
a = """  most = max(r[1] for r in rows)
  first_lift = next(r[0] for r in rows if r[1] > 0.05)
  switch_release = math.degrees(math.asin((MP.SW_PRESS + 1.0) / (MP.SW_D - MP.SW_LEN / 2)))"""
b = """  most = max(r[1] for r in rows)
  first_lift = next(r[0] for r in rows if r[1] > 0.05)
  # the switch's roller sits somewhere along the switch's length; nearest the pivot it lets go last
  switch_release = math.degrees(math.asin((MP.SW_PRESS + 1.0) / (MP.SW_D - MP.SW_LEN / 2)))
  # carrier lift at which the motor gear's teeth come clear of the steering wheel teeth
  overlap_mm = WP.pitch_radius_tip_overlap() if hasattr(WP, "pitch_radius_tip_overlap") else \\
    (GR.pitch_radius(P.MOTOR_TEETH) + GR.MODULE) + (GR.pitch_radius(P.RING_TEETH) + GR.MODULE) - WP.centre_distance()
  gz = (P.Z_GEAR_TEETH[0] + P.Z_GEAR_TEETH[1]) / 2 - P.Z_MOTOR_FACE - MP.HINGE[1]
  gy = -MP.HINGE[0]
  clear_deg = next(th / 10 for th in range(1, 300) if gy * math.cos(math.radians(th / 10)) + gz * math.sin(math.radians(th / 10)) - gy >= overlap_mm)
  clear_alpha = next(r[0] for r in rows if r[1] >= clear_deg)"""
assert a in s; s = s.replace(a, b)
a = """    "starts_lifting_at_deg": first_lift, "switch_releases_by_deg": round(switch_release, 1),"""
b = """    "starts_lifting_at_deg": first_lift, "switch_releases_by_deg": round(switch_release, 1),
    "motor_gear_out_of_mesh_at_deg": clear_alpha, "carrier_lift_out_of_mesh_deg": round(clear_deg, 1),"""
assert a in s; s = s.replace(a, b)
a = """  if switch_release >= first_lift:
    problems.append("the power switch lets go after the motor gear starts to lift")"""
b = """  if switch_release >= clear_alpha - 3.0:
    problems.append("the power switch lets go too late (the motor gear is nearly out of mesh by then)")"""
assert a in s; s = s.replace(a, b)
a = """  L.append(f"LIFT LEVER: turns {lv['turns_deg']:.0f} degrees from down to up. The power switch lets go within "
           f"{lv['switch_releases_by_deg']} degrees; the motor gear starts to lift at {lv['starts_lifting_at_deg']:.0f} degrees. \""""
b = """  L.append(f"LIFT LEVER: turns {lv['turns_deg']:.0f} degrees from down to up. The power switch lets go within "
           f"{lv['switch_releases_by_deg']} degrees; the motor gear starts to lift at {lv['starts_lifting_at_deg']:.0f} degrees "
           f"and is out of mesh by {lv['motor_gear_out_of_mesh_at_deg']:.0f} degrees. \""""
assert a in s; s = s.replace(a, b)
open(p, "w").write(s)
EOF
grep -n "pitch_radius_tip_overlap" accord_lka_parts.py
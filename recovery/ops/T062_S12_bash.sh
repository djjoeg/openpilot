python3 - <<'EOF'
p='margins.py'
s=open(p).read()
old_c = '''# rubbing between the teeth: greased plastic gears, and dry printed PETG (about 0.27 measured against steel in
# Tribology in Industry, 2024; PETG on PETG taken a little higher). Both estimates.
RUB_GREASED, RUB_DRY = 0.1, 0.3
'''
new_c = '''# rubbing between the teeth, dry (the build uses no grease): printed PETG measured about 0.27 against steel in
# Tribology in Industry, 2024 (static, from its friction forces at 30 and 70 N); PETG on PETG is taken a little higher.
# An estimate: the car setup's grip test proves the real teeth.
RUB_DRY = 0.3
'''
assert old_c in s; s=s.replace(old_c,new_c,1)
i=s.index('  hold_spring = spring["holds_teeth_in_mesh_up_to_N"]')
j=s.index('  # Lewis bending at the motor gear')
new_rows = '''  hold_spring = spring["holds_teeth_in_mesh_up_to_N"]
  hold = hold_spring + weight_hold_n
  ft = P.LANE_KEEPING_MOST_NM / ring_r
  sep_dry = ft * math.tan(phi + math.atan(RUB_DRY))
  # the weakest spring Lee Spring may ship: the shortest free length within its tolerance
  hold_short = MP.SPRING_RATE * (MP.SPRING_FREE - MP.SPRING_FREE_TOL - MP.SPRING_LEN) * MP.SPRING_ARM / mesh_from_hinge_mm
  grip_x = motor_most_nm / P.LANE_KEEPING_MOST_NM
  rows.append(row(g, "The motor gear stays in the steering wheel teeth at the most push lane keeping uses, teeth dry",
                  f"{sep_dry:.1f} N pushing the teeth apart at {P.LANE_KEEPING_MOST_NM} Nm, with dry teeth rubbing",
                  f"{hold:.1f} N: the spring ({hold_spring:.1f}) and the motor's own weight ({weight_hold_n:.1f})",
                  hold / sep_dry, "calculated; rubbing estimated",
                  check=f"the grip test in the car setup pushes with the most the motor can ({motor_most_nm:.2f} Nm, "
                        f"{grip_x:.2f} times the most lane keeping uses) while you hold the wheel: nothing may slip",
                  note=f"{(hold_short + weight_hold_n) / sep_dry:.2f} with the shortest spring within Lee Spring's tolerance"))

  sp_up, sp_most = spring["force_lever_up_N"], spring["most_load_N"]
  free_long = MP.SPRING_FREE + MP.SPRING_FREE_TOL
  len_up = spring["length_lever_up_mm"]
  worst = sp_most / (MP.SPRING_RATE * (free_long - len_up))
  rows.append(row(g, "The spring isn't squashed past what it can take (lever up)",
                  f"{sp_up:.1f} N at {len_up} mm long", f"{sp_most} N: fully squashed ({MP.SPRING_SOLID} mm), the most "
                  "Lee Spring sizes it for", sp_most / sp_up, "spring data sheet; calculated",
                  note=f"{worst:.2f} for the longest spring within Lee Spring's tolerance"))

'''
s=s[:i]+new_rows+s[j:]
s=s.replace("up = spring[\"presses_roller_on_rolling_band_N\"] + ft_most * math.tan(phi + math.atan(RUB_GREASED))",
            "up = spring[\"presses_roller_on_rolling_band_N\"] + ft_most * math.tan(phi + math.atan(RUB_DRY))",1)
assert 'RUB_GREASED' not in s, [l for l in s.splitlines() if 'GREASED' in l]
open(p,'w').write(s)
EOF
grep -n "grease\|Grease" *.py | head -20
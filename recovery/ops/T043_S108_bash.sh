python3 - <<'EOF'
s = open('accord_lka_parts.py').read()
s = s.replace('''  col = {"teeth": (.72, .72, .72), "grip": (.3, .3, .3), "gear": (.95, .6, .25), "carrier": (.35, .55, .85), "motor": (.25, .25, .25),
         "hinge": (.45, .75, .45), "lever": (.85, .3, .3), "switch": (.9, .85, .2), "arm": (.6, .5, .4), "clamp": (.5, .7, .7),
         "hood": (.85, .85, .75)}

  def scene(lift_deg=0.0, alpha=0.0, wheel=0.0, crop=None, cut_x=None):
    items = [(A.teeth(wheel), col["teeth"]), (A.wheel_grip(), col["grip"]), (A.gear(lift_deg), col["gear"]),
             (A.carrier(lift_deg), col["carrier"]), (A.motor(lift_deg), col["motor"]), (A.hinge_block(), col["hinge"]),
             (A.lever(alpha), col["lever"]), (A.switch(), col["switch"]), (A.arm(), col["arm"]), (A.clamp(), col["clamp"]),
             (A.hood(), col["hood"])]''',
'''  col = {"teeth": (.72, .72, .72), "grip": (.3, .3, .3), "gear": (.95, .6, .25), "carrier": (.35, .55, .85), "motor": (.25, .25, .25),
         "hinge": (.45, .75, .45), "bracket": (.6, .45, .8), "lever": (.85, .3, .3), "switch": (.9, .85, .2),
         "arm": (.6, .5, .4), "clamp": (.5, .7, .7), "hood": (.85, .85, .75)}

  def scene(lift_deg=0.0, alpha=0.0, wheel=0.0, crop=None, cut_x=None):
    items = [(A.teeth(wheel), col["teeth"]), (A.wheel_grip(), col["grip"]), (A.gear(lift_deg), col["gear"]),
             (A.carrier(lift_deg), col["carrier"]), (A.motor(lift_deg), col["motor"]), (A.hinge_block(), col["hinge"]),
             (A.bracket(lift_deg), col["bracket"]), (A.lever(alpha, lift_deg), col["lever"]),
             (A.switch(lift_deg), col["switch"]), (A.arm(), col["arm"]), (A.clamp(), col["clamp"]), (A.hood(), col["hood"])]''')
s = s.replace('''         ["lever down (cut through the middle)", "lever up: its rounded end presses the motor carrier's tab, lifting the motor gear"], size=(900, 760))''',
'''         ["lever down (cut through the middle)", "lever up: its rounded end presses on the hinge block, lifting the motor gear"],
         size=(900, 760))''')
s = s.replace('''  names = ["steering-wheel-teeth-left-half", "steering-wheel-teeth-right-half", "motor-gear", "motor-carrier", "hinge-block",
           "lift-lever", "dash-clamp", "clamp-pad", "setup-gauge", "fit-test-steering-wheel", "fit-test-teeth", "arms/arm-130"]''',
'''  names = ["steering-wheel-teeth-left-half", "steering-wheel-teeth-right-half", "motor-gear", "motor-carrier", "hinge-block",
           "lever-bracket", "lift-lever", "dash-clamp", "clamp-pad", "setup-gauge", "fit-test-steering-wheel", "fit-test-teeth"]''')

old = s[s.index('  lv = r["lift_lever"]'):s.index('  f = r["fit"]')]
new = '''  lv = r["lift_lever"]
  sp = r["spring"]
  ck = lv["click"]
  L.append("")
  L.append(f"LIFT LEVER: turns {lv['turns_deg']:.0f} degrees from down to up. The power switch lets go within "
           f"{lv['switch_releases_by_deg']} degrees; the motor gear starts to lift at {lv['starts_lifting_at_deg']:.0f} degrees "
           f"and is out of mesh by {lv['motor_gear_out_of_mesh_at_deg']:.0f} degrees. "
           f"Up, the carrier is turned {lv['carrier_lift_up_deg']} degrees (most {lv['most_lift_deg']} on the way). "
           f"Pushes at the end of the handle: up to {lv['most_push_at_handle_end_N']} N to lift against the spring "
           f"({lv['most_push_with_rubbing_N']} N counting rubbing at the rounded end, an estimate with dry printed parts; "
           f"grease brings it down), {lv['push_to_bring_it_back_down_N']} N to start it back down "
           f"({lv['push_to_bring_it_back_down_with_rubbing_N']} N with rubbing), and {lv['push_to_go_past_up_N']} N or more to "
           f"push it past up. Lever down, its rounded end is {lv['drop_gap_mm']} mm above the hinge block.")
  L.append(f"CLICK (estimates for ASA): the tab bends {ck['bend_mm']} mm ({ck['tab_strain_percent']}% stretch at its root) "
           f"with {ck['tab_force_N']} N; about {ck['to_click_at_handle_end_N']} N at the end of the handle to click it down "
           f"and {ck['to_unclick_at_handle_end_N']} N to unclick it.")
  L.append(f"SPRING: {sp['part']}. {sp['length_gear_on_teeth_mm']} mm long and {sp['force_gear_on_teeth_N']} N with the motor gear "
           f"on the teeth; {sp['length_lever_up_mm']} mm and {sp['force_lever_up_N']} N with the lever up (its most is "
           f"{sp['most_load_N']} N at {sp['fully_squashed_mm']} mm).")
'''
s = s.replace(old, new)
open('accord_lka_parts.py', 'w').write(s)
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib timeout 900 python3 accord_lka_parts.py --out /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2/stl --report /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2/report --no-pictures 2>&1 | tail -60
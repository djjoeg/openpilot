sed -n 739p accord_lka_parts.py && sed -n 764p accord_lka_parts.py && python3 - <<'EOF'
src=open('accord_lka_parts.py').read()
src=src.replace('''           f"towards you from the middle of the grip), the right spoke meeting the grip {est['right_spoke_meets_grip_deg_below_3_oclock'][0]} "
           f"to {est['right_spoke_meets_grip_deg_below_3_oclock'][1]} degrees below 3 o'clock.")''',
'''           f"towards you from the middle of the grip), the right spoke meeting the grip "
           f"{est['right_spoke_meets_grip_deg_below_3_oclock'][0]} to {est['right_spoke_meets_grip_deg_below_3_oclock'][1]} degrees "
           "below 3 o'clock.")''')
src=src.replace('''             "of the rim (at the screw's depth), its middle {:.0f} mm behind the middle of the grip.".format(f['bracket_middle_behind_grip_mm']))''',
'''             f"of the rim (at the screw's depth), its middle {f['bracket_middle_behind_grip_mm']:.0f} mm behind the middle of the grip.")''')
open('accord_lka_parts.py','w').write(src)
a=open('columnassembly.py').read()
a=a.replace('''from params import (ARM_LENGTHS, ARM_SLIDE, CLAMP_Z, COVER_FRONT_W, COVER_FRONT_Z, COVER_H, COVER_TAPER_Z, COVER_W, DASH_Z, GRIP, HUB_BACK_Z, HUB_R,
                    KEY_FROM, KEY_R, KEY_TO, ROLLER_R, SCREW_BEHIND, SCREW_DOWN, SCREW_RIGHT, SPOKE_BACK_Z, STALK_FROM,
                    STALK_R, STALK_TO, WHEEL_OD, WINDOW_DEG, Z_GEAR_ROLLER, Z_MOTOR_FACE, Z_MOTOR_FACE_C)''',
'''from params import (ARM_LENGTHS, ARM_SLIDE, CLAMP_Z, COVER_FRONT_W, COVER_FRONT_Z, COVER_H, COVER_TAPER_Z, COVER_W, DASH_Z,
                    GRIP, HUB_BACK_Z, HUB_R, KEY_FROM, KEY_R, KEY_TO, ROLLER_R, SCREW_BEHIND, SCREW_DOWN, SCREW_RIGHT,
                    SPOKE_BACK_Z, STALK_FROM, STALK_R, STALK_TO, WHEEL_OD, WINDOW_DEG, Z_GEAR_ROLLER, Z_MOTOR_FACE,
                    Z_MOTOR_FACE_C)''')
open('columnassembly.py','w').write(a)
EOF
ruff check --select E,F,W --line-length 140 accord_lka_parts.py columnparts.py columnassembly.py margins.py params.py 2>&1 | tail -2
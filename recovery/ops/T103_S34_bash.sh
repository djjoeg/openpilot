python3 - <<'EOF'
src=open('params.py').read()
add = '''
# ----- the right-side mount (the side bracket and screw tab, columnparts.py): estimates from photos, steering wheel frame -----
SCREW_RIGHT = 45.0         # the dash's screw at the driver's right: this far right of the steering wheel's outer edge at 3
                           # o'clock (estimate; measure yours: the build takes --screw-right)
SCREW_DOWN = 60.0          # below that point (estimate; --screw-down)
SCREW_BEHIND = 265.0       # behind the front face of the steering wheel's rim (estimate; --screw-behind)
STALK_FROM = (50.0, 35.0, -65.0)    # the wiper stalk: from the covers' upper right front corner ...
STALK_TO = (125.0, 78.0, -58.0)     # ... out to about 2 o'clock, 150 mm from the column (estimate)
STALK_R = 11.0
KEY_FROM = (45.0, -35.0, -72.0)     # the key cylinder's bezel on the covers' right-hand side near their front, pointing
KEY_TO = (85.0, -62.0, -55.0)       # right, down and towards you (estimate)
KEY_R = 16.0
'''
if 'SCREW_RIGHT' not in src:
    open('params.py','w').write(src.rstrip('\n') + '\n' + add)
print('ok')
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
import time, numpy as np
t0=time.time()
import columnassembly as CA, columnparts as CP, mountparts as MP, wheelparts as WP, params as P
import accord_lka_parts as BLD
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP, shallow=True)
fit = CA.solve_side()
print('fit', fit.ok, 'arm', round(fit.arm_deg,1), 'reach', round(fit.reach,1), 'arm_len', fit.arm_len, 'slide', round(fit.slide,1),
      'z_b', fit.bracket_z, 'screw', fit.screw_w, 'tab', fit.tab_len, 'x0', round(fit.tab_x0,1), 'plate_y', fit.plate_y, fit.notes)
EOF
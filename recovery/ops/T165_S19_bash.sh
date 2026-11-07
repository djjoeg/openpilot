python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()

def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)

sub('''The side-slide mount: the motor at about 5:20 behind the steering wheel, its shaft pointing out at the steering wheel
and its gear on the back teeth, slides along its own shaft in towards the middle of the steering wheel to come off the
teeth. A spring pulls it in; you pull it back out until the latch clicks, and pull the latch's knob to let it go.

  mounting plate  - fixed. Carries the rail, the latch (a bought spring plunger with a knob), the power switch and
                    the spring's spool. How it fixes to the car is not drawn yet (see the report's questions).
  motor bracket   - the motor bolts to its face (finger guard round the gear, as before); a flange along the motor's
                    4 o'clock side bolts to the rail's block; beside it the latch's ear, with the hole the plunger's
                    pin drops into, and the end that presses the switch; on the motor's dash side the tab the spring's
                    strip is clamped to''',
'''The side-slide mount: the motor at about 5:20 behind the steering wheel, its shaft pointing out at the steering wheel
and its gear on the back teeth, slides along its own shaft in towards the middle of the steering wheel to come off the
teeth. A lever on the motor's bracket sticks out through an L-shaped slot in the mounting plate (where the latch's knob
was). Pull the lever out along the slot and the motor slides out onto the teeth; swing it into the notch at the slot's
outer end, towards the dash, and it is latched. Swing it out of the notch and the spring pulls the motor in; if the
spring doesn't, push the lever in along the slot. A second notch at the slot's inner end parks it there.

  mounting plate  - fixed. Carries the rail, the lever's slot and its two notches, the power switch and the spring's
                    spool. How it fixes to the car is not drawn yet (see the report's questions).
  motor bracket   - the motor bolts to its face (finger guard round the gear, as before); a flange along the motor's
                    4 o'clock side bolts to the rail's block; beside it the ear, a fork round the lever's hub, whose
                    outer end presses the switch; on the motor's dash side the tab the spring's strip is clamped to
  lever           - turns on a steel pin across the ear's fork; its arm runs out through the plate's slot to a knob''')
sub('''Bought: an MGN12H block on a 100 mm MGN12 rail; a KIPP K0338.11105 spring plunger (M10 x 1, 5 mm pin) and an
M10 x 1 thin nut; a Lee Spring LCF 040 08 050S constant force spring; the Omron SS-5GL2 power switch (as before).''',
'''Bought: an MGN12H block on a 100 mm MGN12 rail; a 4 mm x 24 steel dowel pin (the lever's pivot); a Lee Spring LCF 040
08 050S constant force spring; the Omron SS-5GL2 power switch (as before).''')

a = s.index("# ***** the latch: KIPP K0338.11105 spring plunger")
b = s.index("# ***** the power switch: Omron SS-5GL2")
s = s[:a] + '''# ***** the lever: on a pin across the bracket's ear, out through an L-shaped slot in the plate *****
# Its arm leaves the ear towards 4 o'clock, through the slot to a knob outside the plate. Pulled out against the stop it
# swings LATCH_DEG towards the dash into the notch at the slot's outer end; the spring then pulls its arm down onto the
# notch's floor, which sets where the motor sits on the teeth. Swung out of the notch, it runs in the straight slot with
# the motor. The notch at the inner end takes it the same way, slid in, so the motor stays in without the spring.
X_EAR = (-36.0, -22.5)            # the ear, across: a fork round the lever's hub, on the flange's dash end
EAR_Y = (FL_Y[1], 30.0)
EAR_Z = (-25.0, 0.0)              # its outer end (+z) presses the switch and meets the stop
LEVER_Z = (-17.0, -5.0)           # the lever's thickness, along the shaft (motor out)
LUG_GAP = 0.2                     # each side of its hub, between the fork's two lugs
PIVOT = (-29.25, 20.0)            # the pin's axis (x, y), along the shaft
HUB_R = 6.0
PIN_D, PIN_LEN = 4.0, 24.0        # a steel dowel pin (ISO 8734), tapped in from the inner end
PIN_Z = (EAR_Z[0] + 0.2, EAR_Z[0] + 0.2 + PIN_LEN)                # its ends: 0.8 short of the ear's outer face
PIN_PRESS_D, PIN_SLIP_D, LEVER_BORE_D = 3.9, 4.1, 4.3             # holes: press in the inner lug, slip in the outer
SHANK_W = 9.0                     # the lever's arm, across (y)
KNOB_D, KNOB_R = 50.0, 12.0       # the knob's middle from the pivot, its radius
LATCH_DEG = 42.0                  # swung this far into a notch
SLOT_CLEAR = 0.4                  # round the arm in the slot and the notches, but on the notches' load faces
BRIDGE = ((-30.0, X_EAR[1]), (HUB_R + 0.6 + PIVOT[1], EAR_Y[1]))   # joins the lugs past the hub, on the motor's side
STOP_GAP = 0.2                    # pulled out against the stop, the ear is this far past where the notch holds it
LEVER_USE_N = 20.0                # pulling the lever out or pushing it in, every time: about 2 kg (more than it needs)
LEVER_YANK_N = 100.0              # a hard yank on the knob: about 10 kg (an estimate on the high side)

''' + s[b:]

# the switch's stop used the plunger's ramp
sub('''HOLDER_Z = (EAR_Z[1] + STOP_GAP, SW_HOLES_Z + MP.SW_H / 2 + 2.0)''', '''HOLDER_Z = (EAR_Z[1] + STOP_GAP, SW_HOLES_Z + MP.SW_H / 2 + 2.0)
STOP_X = (SW_X[0], -24.5)                  # the stop beside the switch that the ear's end meets, pulled out''')
open(p, "w").write(s)
EOF
grep -n "PIN_Y\|PIN_Z\b\|BEVEL\|KIPP\|X_COLLAR\|X_PIN_TIP\|PIN_HOLE_D\|EAR_FLAT\|NUT_M10\|PIN_IN\b" sideparts.py
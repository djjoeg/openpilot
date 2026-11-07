"""
Measurements and design choices for the printed parts. Millimetres and degrees.

Steering wheel frame: the steering column is the Z axis, pointing at the driver; +Y is 12 o'clock on the steering
wheel's face; +X is the driver's right. The part of the steering wheel you hold is centred on z = 0.
"""

# ***** your car: measure these *****

# Steering wheel. Steering wheel cover makers list the 2008-12 Accord's: Wheelskins 14 1/2 x 4 1/8 in (368 mm across,
# 105 mm around the part you hold), AutoPadre 14 3/8 x 4 1/8 in (365 mm). 105 mm around is 33 mm thick if it is round.
# The fit test checks it on your car; to make the parts for yours, measure it (see the guide).
WHEEL_OD = 367.0      # across the steering wheel, outside edge to outside edge, through the centre
GRIP = 33.0           # thickness of the part you hold at the top (the distance around it divided by 3.14)

# Steering column angle from level, degrees: the column rises towards the driver, so the top of the steering wheel is
# further forward than the bottom. Measured by NHTSA in its frontal crash tests, with the steering wheel in the middle
# of its tilt range: 22.1 on a 2008 Accord LX sedan (test 6229), 22.4 on a 2011 Accord LX sedan (test 7078). The same
# reports measure the tilt's whole range (about 3.5 degrees either way) and the reach range (34-35 mm).
COLUMN_TILT = 22.1
COLUMN_TILT_RANGE = (18.5, 25.9)   # lowest and highest tilt settings, from both reports; the build checks both

# Where the dash clamp's bolt (the one the arm turns on) ends up relative to the motor gear's centre, in the car (not
# the steering wheel frame): up (towards the roof) and forward (towards the windshield). Estimates: nothing published
# gives where the cover over the gauges sits relative to the steering wheel, and the answer changes with how you set
# the steering wheel's tilt and reach (the ranges above). They only pick which arm length to print and check that the
# parts reach; the build script also checks a range of positions around them (see the report).
ARM_PIVOT_UP = 105.0
ARM_PIVOT_FORWARD = 175.0

# ***** steering wheel teeth *****

PAD = 1.0             # room for one wrap of rubber tape between the steering wheel teeth and the steering wheel
WALL = 3.5            # plastic around the part you hold

RING_TEETH = 197      # tooth count of the full circle the steering wheel teeth are cut from (197 mm pitch radius)
MOTOR_TEETH = 19      # motor gear: 38 mm pitch circle
# Two sets of steering wheel teeth, named by how far they reach each way from straight ahead (degrees of steering wheel
# turn): the teeth printed, centred on 12 o'clock, and the zip tie positions each side of 12 o'clock. The motor pushes
# with its full strength only as far as the teeth reach, so the short set is for getting used to lane keeping. Past
# the last tooth the motor gear's roller still rides on the rolling band for a few degrees, and its grip there can push
# the steering wheel weakly (the report gives how far and how hard).
TEETH_SETS = {
  15: {"teeth": 16, "ties": (9.5, 16.5, 23.5)},   # 29.2 degrees of steering wheel turn
  29: {"teeth": 32, "ties": (9.5, 20.5, 31.0)},   # 58.5 degrees
}
TEETH_ON_WHEEL = TEETH_SETS[29]["teeth"]
# Torque at the steering wheel, from the car port (opendbc/car/hondastepper/values.py and the safety chip's
# honda_stepper.h): lane keeping's own most (STEER_MAX, 43 units) and the safety chip's hard limit (47 units), in
# firmware units of 0.125 Nm turned into steering wheel torque for this motor and these gears.
LANE_KEEPING_MOST_NM = 3.85  # lane keeping's most: the grip test (the board's most) is 1.41 times this
MOST_TORQUE_NM = 4.41  # the most torque lane keeping may use at the steering wheel (the safety chip's limit)
BACKLASH = 0.175      # each gear's teeth are this much thinner than nominal (mm at the pitch circle)
CD_EXTRA = 0.3        # gear centres this much further apart than the pitch circles touching (a little free play)
# Motor gear's roller and the rolling band it rides on: the spring presses the roller onto the band, which sets how
# deep the teeth mesh. Both sit on the gears' pitch circles (scaled out by CD_EXTRA), so the roller turns at exactly
# the gear ratio and rolls without scrubbing while the teeth mesh.
ROLLER_R = MOTOR_TEETH * (RING_TEETH + MOTOR_TEETH + CD_EXTRA) / (RING_TEETH + MOTOR_TEETH)

ROLL_PAST_TEETH = 6.5   # degrees of rolling band past the last tooth, each side (the roller spins up before the teeth meet)
END_LEAD_IN = 6.0       # degrees over which the rolling band slopes down at each end
END_CHAMFER = 3.5       # mm: the very end slopes from the outer band down to the steering wheel
SPLIT_LAP = 3           # the two halves overlap this many teeth at 12 o'clock (glued)
TIE_W, TIE_T = 5.8, 2.4          # zip tie slot, for ties 4.8 mm wide

# Along the steering column (z), the bands the two gears share. The roller is centred on the part you hold.
Z_ROLL = (-3.5, 4.5)          # rolling band on the steering wheel teeth (flat for the first 5.2 mm, then sloping down)
Z_TEETH = (5.5, 17.5)         # teeth on the steering wheel teeth
Z_MOTOR_FACE = -9.5           # front face of the motor (where the shaft comes out)
MOTOR_PLATE_T = 5.0           # motor bracket plate, between the motor and the motor gear
Z_GEAR_ROLLER = (-4.0, 5.3)   # motor gear: roller (runs up to the teeth)
Z_GEAR_TEETH = (5.3, 17.0)    # motor gear: teeth

# ***** motor: STEPPERONLINE 17HS16-2004S1 (NEMA 17, 45 Ncm, 2 A, 1.3 ohm, 40 mm, 310 g) *****
# Chosen weaker than it could be on purpose: at the most current its controller board can give (3.3 A), it can't
# push the steering wheel harder than a driver is expected to overpower easily (see margins.py).

NEMA = 42.3             # square body
NEMA_LEN = 40.0
NEMA_HOLES = 31.0       # M3 holes, square pattern
NEMA_BOSS = 22.0        # round boss around the shaft, about 2 mm high
SHAFT_D = 5.0
SHAFT_ACROSS_FLAT = 4.5
SHAFT_LEN = 23.0
SHAFT_FLAT_LEN = 21.0   # the D flat runs this far back from the shaft's tip
MOTOR_HOLD_NCM, MOTOR_RATED_A, MOTOR_OHM, MOTOR_KG = 45.0, 2.0, 1.3, 0.31   # STEPPERONLINE's data
BOARD_MAX_A = 3.3       # the most current the StepperServoCAN board's motor driver gives (its firmware: I_MAX_A4950)

# ***** screws and nuts (hole sizes as printed) *****

M3_CLEAR, M3_PILOT = 3.4, 2.6        # M3 through hole / hole an M3 screw cuts its own thread into
M4_CLEAR, M4_PILOT = 4.5, 3.4
M5_CLEAR, M5_NUT_AF, M5_NUT_T = 5.5, 8.3, 5.2    # M5 hole / nyloc nut across flats / nyloc nut thickness
M5_PILOT = 4.3
M6_CLEAR, M6_NUT_AF, M6_NUT_T = 6.6, 10.3, 5.4

# ***** arm and dash clamp *****

ARM_W, ARM_T = 36.0, 18.0     # arm bar: width (across, along the bolts) and thickness
ARM_LENGTHS = (70, 90, 110, 130, 150, 170, 190, 210, 230)   # arms to print: dash clamp bolt to hinge block bolt, mm
ARM_SLIDE = 15.0              # each arm slides +- this much at the dash clamp: neighbouring lengths overlap by about
                              # 10 mm, which covers the steering wheel's tilt range and some measuring error
HOOD_EDGE_MIN, HOOD_EDGE_MAX = 3.0, 26.0   # thickness range of the cover edge the dash clamp grips
CLAMP_DEPTH = 75.0            # how far the dash clamp's top plate reaches back over the cover

BED = (220.0, 220.0, 250.0)   # print bed the parts must fit (most printers are this size or bigger)

# ***** column mount: the motor under the steering wheel, behind it, on a clamp round the steering column covers *****
# The same motor gear, carrier, hinge block, lever bracket, lift lever, spring, arm and setup gauge as the dash mount.
# What changes: the steering wheel teeth become a ring of teeth facing the hub, on a skirt that stands back from the
# bottom of the steering wheel (5 to 7 o'clock); the motor gear runs inside that ring, behind the wheel; the arm goes
# up to a two-piece clamp round the steering column covers instead of the dash. The clamp moves with the steering
# wheel when it is tilted or pulled out, so the mesh never changes with the wheel's setting. Only the short teeth fit
# between the steering wheel's two lower spokes.
COVER_W = 120.0            # steering column covers, side to side, where the clamp sits: an estimate from photos; the
COVER_W_RANGE = (95.0, 140.0)   # clamp's slots take this range
COVER_H = 95.0             # top to bottom: an estimate; the threaded rods take this range
COVER_H_RANGE = (70.0, 125.0)
COVER_FRONT_Z = -50.0      # the covers' front edge, behind the middle of the part of the wheel you hold (estimate)
COVER_FRONT_W = 100.0      # the covers' width at their front edge: they widen from there back to COVER_W at COVER_TAPER_Z
COVER_TAPER_Z = -200.0     # (estimates from photos; the right-side mount's lift lever, flipped up, swings in beside them)
CLAMP_Z = -200.0           # the middle of the clamp along the column, behind the middle of the grip: you choose where
                           # (behind the stalks and the key); the report says which places work
HUB_R = 85.0               # the steering wheel's hub (the airbag cover), its radius at the bottom (estimate from photos)
HUB_BACK_Z = -40.0         # how far behind the middle of the grip the hub reaches (estimate)
SPOKE_BACK_Z = -30.0       # the lower spokes' back face where the lift lever's handle is (13 cm from the centre; estimate).
                           # The handle stays behind it, so the spokes can sweep past when the wheel is turned far
DASH_Z = -300.0            # the dash panel below the column, behind the middle of the grip (estimate; the report says
                           # how far back the parts reach)
WINDOW_DEG = 70.0          # the open arc at the bottom of the steering wheel between its two lower spokes (estimate
                           # from photos: the spokes meet the grip about 40 and 50 degrees either side of 6 o'clock)
Z_MOTOR_FACE_C = -84.0     # the motor's front face, behind the middle of the grip: the lift lever's handle (47 mm
                           # long, from the motor's face towards you) then ends 7 mm behind SPOKE_BACK_Z
SKIRT_T = 7.0              # the skirt that carries the ring of teeth, radial thickness
FRONT_RING_T = 6.0         # the ring at the front face that joins the skirt to the band round the grip

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

# ----- the back-teeth mount (faceparts.py): estimates from photos, steering wheel frame -----
RIGHT_SPOKE_DEG = (-55.0, -15.0)    # the right spoke meets the grip between these angles from 3 o'clock (+ up, - down),
                                    # read off a straight-on photo of the wheel; the channel leaves room 2 degrees past each
COVER_BOTTOM = -50.0                # the lower column cover's underside, this far below the column's axis where the column
                                    # plate sits (estimate; --cover-bottom)
PLATE_FRONT_Z = -76.0               # the column plate's front end, behind the middle of the grip; its slots take the cover's
                                    # screws from 29 to 139 mm behind that

"""
Measurements and design choices for the printed parts. Millimetres and degrees.

Steering wheel frame: the steering column is the Z axis, pointing at the driver; +Y is 12 o'clock on the steering
wheel's face; +X is the driver's right. The part of the steering wheel you hold is centred on z = 0.
"""

# ***** your car: measure these *****

# Steering wheel. Published cover sizing lists the 2008-12 Accord at 14 3/8 - 14 1/2 in across (365-368 mm) and
# 4 1/8 in (105 mm) around the part you hold, which is 33 mm thick if it is round. Measure yours.
WHEEL_OD = 367.0      # across the steering wheel, outside edge to outside edge, through the centre
GRIP = 33.0           # thickness of the part you hold at the top (the distance around it divided by 3.14)

# Where the dash clamp's hinge ends up relative to the motor gear's centre, in the car (not the steering wheel frame):
# up (towards the roof) and forward (towards the windshield). Only used to check the parts reach; the arm slider and
# the angle joint adjust over a wide range.
HINGE_UP = 105.0
HINGE_FORWARD = 175.0
COLUMN_TILT = 22.0    # steering column angle from level, degrees (the steering wheel's face leans back by this much)

# ***** steering wheel teeth *****

PAD = 1.0             # room for one wrap of rubber tape between the steering wheel teeth and the steering wheel
WALL = 3.5            # plastic around the part you hold

RING_TEETH = 197      # tooth count of the full circle the steering wheel teeth are cut from (197 mm pitch radius)
MOTOR_TEETH = 19      # motor gear: 38 mm pitch circle
TEETH_ON_WHEEL = 32   # teeth actually printed, centred on 12 o'clock: 58.5 degrees of steering wheel turn
BACKLASH = 0.175      # each gear's teeth are this much thinner than nominal (mm at the pitch circle)
ROLL_GROW = 0.15      # the rolling band and the motor gear's roller are this much bigger than the pitch circles

ROLL_PAST_TEETH = 6.5   # degrees of rolling band past the last tooth, each side (the roller spins up before the teeth meet)
END_LEAD_IN = 2.5       # degrees over which the rolling band slopes down at each end
SPLIT_LAP = 3           # the two halves overlap this many teeth at 12 o'clock (glued)
TIE_ANGLES = (9.5, 20.5, 31.0)   # zip tie positions each side of 12 o'clock
TIE_W, TIE_T = 5.8, 2.4          # zip tie slot, for ties 4.8 mm wide

# Along the steering column (z), the bands the two gears share
Z_ROLL = (-7.0, -1.65)        # rolling band on the steering wheel teeth
Z_TEETH = (1.0, 13.0)         # teeth on the steering wheel teeth
Z_MOTOR_FACE = -13.5          # front face of the motor (where the shaft comes out)
MOTOR_PLATE_T = 5.0           # motor bracket plate, between the motor and the motor gear
Z_GEAR_ROLLER = (-8.0, 0.5)   # motor gear: roller
Z_GEAR_TEETH = (1.25, 12.5)   # motor gear: teeth

# ***** motor: STEPPERONLINE 17HS19-2004S1 (NEMA 17) *****

NEMA = 42.3             # square body
NEMA_LEN = 48.0
NEMA_HOLES = 31.0       # M3 holes, square pattern
NEMA_BOSS = 22.0        # round boss around the shaft, about 2 mm high
SHAFT_D = 5.0
SHAFT_ACROSS_FLAT = 4.5
SHAFT_LEN = 24.0
SHAFT_FLAT_LEN = 15.0   # the D flat runs this far back from the shaft's tip

# ***** screws and nuts (hole sizes as printed) *****

M3_CLEAR, M3_PILOT = 3.4, 2.6        # M3 through hole / hole an M3 screw cuts its own thread into
M4_CLEAR, M4_PILOT = 4.5, 3.4
M5_CLEAR, M5_NUT_AF, M5_NUT_T = 5.5, 8.3, 5.2    # M5 hole / nyloc nut across flats / nyloc nut thickness
M5_PILOT = 4.3
M6_CLEAR, M6_NUT_AF, M6_NUT_T = 6.6, 10.3, 5.4

# ***** arm, dash clamp, lift lever *****

ARM_W, ARM_T = 36.0, 10.0     # arm bar width and thickness
ARM_LEN = 190.0               # hinge to the end of the arm
ARM_SLOT = (55.0, 175.0)      # slot for the arm slider's bolts, measured from the hinge
TAIL = 32.0                   # arm tail behind the hinge (the lift lever pushes its screw down)
HINGE_R = 9.0                 # hinge knuckles around the M5 hinge bolt
HINGE_HALF_SPAN = 30.0        # outside faces of the dash clamp's knuckles from the middle
CLAMP_KNUCKLE = 8.0           # thickness of each dash clamp knuckle
KNUCKLE_GAP = 0.4
HOOD_EDGE_MIN, HOOD_EDGE_MAX = 3.0, 26.0   # thickness range of the cover edge the dash clamp grips
CLAMP_DEPTH = 75.0            # how far the dash clamp's top plate reaches back over the cover

BED = (220.0, 220.0, 250.0)   # print bed the parts must fit (most printers are this size or bigger)

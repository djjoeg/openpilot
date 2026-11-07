python3 - << 'EOF'
p = "params.py"
s = open(p).read()
a = """# Where the arm's pivot bolt on the dash clamp ends up relative to the motor gear's centre, in the car (not the
# steering wheel frame): up (towards the roof) and forward (towards the windshield). Only used to check that the parts
# reach; the dash clamp's angle, the arm slider and the hinge block's angle adjust over a wide range.
ARM_PIVOT_UP = 105.0
ARM_PIVOT_FORWARD = 175.0
COLUMN_TILT = 22.0    # steering column angle from level, degrees (the steering wheel's face leans back by this much)"""
b = """# Where the dash clamp's bolt (the one the arm turns on) ends up relative to the motor gear's centre, in the car (not
# the steering wheel frame): up (towards the roof) and forward (towards the windshield). These are estimates, not
# measurements of a 2010 Accord. They only pick which arm length to print and check that the parts reach; the build
# script also checks a range of positions around them (see the report).
ARM_PIVOT_UP = 105.0
ARM_PIVOT_FORWARD = 175.0
COLUMN_TILT = 22.0    # steering column angle from level, degrees: the column rises towards the driver, so the top of
                      # the steering wheel is further forward than the bottom. Estimate."""
assert a in s; s = s.replace(a, b); open(p, "w").write(s)
EOF
grep -n "COLUMN_TILT\|ARM_PIVOT" params.py
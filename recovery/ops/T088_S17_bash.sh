cat >> params.py <<'EOF'

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
CLAMP_Z = -170.0           # the middle of the clamp along the column, behind the middle of the grip: you choose where
                           # (behind the stalks and the key); the report says which places work
HUB_R = 85.0               # the steering wheel's hub (the airbag cover), its radius at the bottom (estimate from photos)
HUB_BACK_Z = -40.0         # how far behind the middle of the grip the hub reaches (estimate)
SPOKE_BACK_Z = -30.0       # the lower spokes' back face where the lift lever's handle is (13 cm from the centre; estimate).
                           # The handle stays behind it, so the spokes can sweep past when the wheel is turned far
DASH_Z = -220.0            # the dash panel below the column, behind the middle of the grip (estimate; the motor needs 150)
WINDOW_DEG = 70.0          # the open arc at the bottom of the steering wheel between its two lower spokes (estimate
                           # from photos: the spokes meet the grip about 40 and 50 degrees either side of 6 o'clock)
Z_MOTOR_FACE_C = -82.0     # the motor's front face, behind the middle of the grip: the lift lever's handle (47 mm
                           # long, from the motor's face towards you) then ends 5 mm behind SPOKE_BACK_Z
SKIRT_T = 7.0              # the skirt that carries the ring of teeth, radial thickness
FRONT_RING_T = 6.0         # the ring at the front face that joins the skirt to the band round the grip
EOF
python3 -c "import ast,sys; ast.parse(open('params.py').read()); print('ok')"
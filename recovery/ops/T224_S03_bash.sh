python3 - <<'EOF'
p='armmount.py'; s=open(p).read()
old=s[:s.index('import math')]
new='''"""
The arm mount, v2 (1 Nov 2026): the simple, adjustable apparatus that hangs on the frame plate under the column.
The frame plate stays on the car; the apparatus slides into it and one wing bolt holds it.

  frame plate v3  - the frame plate (v1, frameplate.py, with your marks) with a receiver under the block on the key
                    side of the cup: a square tube along the column, open at both ends, the arm's size inside
  arm             - a flat bar, 10 x 30, along the column: its front end slides into the receiver from the wheel end
                    (the tube carries the load); one M5 wing bolt through the receiver's outer wall, into a nut trapped
                    in the wall, pinches it so it can't slide. Push it in or pull it out to set how deep the gear sits
                    in the teeth. Its back end has two upright slots
  bracket         - the motor bolts to its face plate (four M3, the boss through a hole); from the face plate's
                    4 o'clock end an upright ear rises, bolted to the arm's upright slots by two wing bolts into nuts
                    trapped in the ear: slide it up or down to set the gear's reach along the teeth. A step on the ear
                    sits against the arm's end face, so the ear stays upright
  gear            - the side-slide gear (you have it)

The motor is at 5:20 behind the wheel, its shaft pointing out at the grip, the gear on the teeth: the side-slide
mount's place (sideparts.py), with its face at R_FACE from the column's axis, on the plane Z_AXIS.

Steering wheel frame (mm): z along the column towards you, 0 at the middle of the grip; y up; x to your right.
The frame plate: its top (the cover's underside) at COVER_Y, the cup screw at (CUP_X, CUP_Z); its own frame
(frameplate.py: x towards the driver's door, y towards the dash) maps as X = CUP_X - x, Z = CUP_Z - y.

Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, and the cover's front edge. The arm slides +-17 mm in
the receiver (more, if it must), the bracket +-9 mm up and down.

  python3 armmount.py   # writes ../stl/arm-mount/*.stl, ../plates/plate-5-frame-plate-v3.3mf, plate-6-arm-mount.3mf
                        # and ../report/arm-mount.png, column-frame-plate-v3.png
"""
'''
s=s.replace(old,new)
s=s.replace('''ARM_HOLES_Z = -153.0             # the two holes to the fin (at FIN_SLOT_Y), nominal: the middle of the fin's slots
''','')
s=s.replace('''def bolt_xz():
  """The four bolts in the steering wheel frame (x, z)."""
  return [(CUP_X - x, CUP_Z - y) for x, y in BOLTS_P]


''','')
s=s.replace('''# ----- the shoe, the arm and the bracket (steering wheel frame) -----

def arm() -> Manifold:
  m = box(ARM_X[0], ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1])
  for y in FIN_SLOT_Y:
    m = m - cyl_x(M5_HOLE / 2, ARM_X[0] - 1.0, ARM_X[1] + 1.0, y=y, z=ARM_HOLES_Z, segments=32)
  for z in ARM_SLOT_Z:''','''# ----- the arm and the bracket (steering wheel frame) -----

def arm() -> Manifold:
  m = box(ARM_X[0], ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1])
  for z in ARM_SLOT_Z:''')
s=s.replace('''  """Each part turned the way it prints: the plate labels up; the shoe on its top (the fin up); the arm on its side;''','''  """Each part turned the way it prints: the plate labels up (the receiver standing on it); the arm on its side;''')
s=s.replace('# ----- the frame plate v2 (printed frame, as frameplate.py: key side +x, labels up) -----','# ----- the frame plate v3 (printed frame, as frameplate.py: key side +x, labels up) -----')
open(p,'w').write(s)
EOF
ruff check --fix armmount.py 2>&1 | tail -3; PYTHONPATH=/home/claude/pylib timeout 900 python3 armmount.py 2>&1 | tail -6
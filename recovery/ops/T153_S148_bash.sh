cd /home/claude/deliver/hardware/cad && cat >> slideparts.py <<'EOF'


# ***** the board cap *****
# A printed cover over the controller board's parts side (the board lies flat on the motor's back, its parts and plugs
# facing the column). Its open end sits against the motor's back; four tongues run up the motor's sides and a zip tie
# round the motor holds them. Openings let the two plugs out; its edge towards the dash and the column is cut back (the
# column cover's lower front edge is there with the motor slid off).
CAP_WALL, CAP_GAP = 2.0, 1.0
CAP_DEPTH = 10.5                            # from the motor's back face to the cap's outside
CAP_TONGUE = (10.0, 8.0, 1.6)               # each tongue: width, how far up the motor, thickness
TIE_SLOT = (4.0, 1.2)                       # the zip tie's groove across each tongue (width along the motor, depth)


def _board_cs() -> CrossSection:
  core = CrossSection.square((40.1, 40.8)).translate((-20.05, -20.4))
  tab = CrossSection.square((15.9, 2.6)).translate((-8.3, -22.94))
  return (core + tab).mirror((0, 1)).rotate(90.0)


def board_cap() -> Manifold:
  """Carrier frame, as fitted."""
  from cadlib import prism_x
  z_back = -NEMA_LEN
  cs = _board_cs()
  outer = cs.offset(CAP_GAP + CAP_WALL, manifold3d.JoinType.Round, circular_segments=32)
  inner = cs.offset(CAP_GAP, manifold3d.JoinType.Round, circular_segments=32)
  shell = outer.extrude(CAP_DEPTH).translate((0, 0, z_back - CAP_DEPTH)) - \
    inner.extrude(CAP_DEPTH - CAP_WALL + 0.01).translate((0, 0, z_back - CAP_DEPTH + CAP_WALL))
  # the tongues up the motor's four sides, each with a groove for the tie
  w, up, th = CAP_TONGUE
  tongues = []
  for ang in (0.0, 90.0, 180.0, 270.0):
    tg = box(H, H + th, -w / 2, w / 2, z_back - 0.01, z_back + up)
    tg = tg - box(H + th - TIE_SLOT[1], H + th + 1.0, -w / 2 - 1, w / 2 + 1, z_back + up - 2.0 - TIE_SLOT[0], z_back + up - 2.0)
    tongues.append(tg.rotate((0, 0, ang)))
  part = union([shell] + tongues)
  # the plugs' openings: the car plug towards the dash, the motor plug towards 4 o'clock
  part = part - box(-2.7, 14.3, 18.0, 30.0, -48.6, z_back + 0.01)
  part = part - box(-30.0, -20.0, -9.7, 7.3, -48.6, z_back + 0.01)
  part = part - prism_x([(CAP_CHAMFER_Y0, -51.0), (30.0, -51.0), (30.0, -51.0 + 30.0 - CAP_CHAMFER_Y0)], -30.0, 30.0)
  return clean(part)
EOF
PYTHONPATH=/home/claude/pylib timeout 300 python3 -c "
import slideparts as S
m=S.board_cap(); print(round(m.volume()), len(m.decompose()), [round(v,1) for v in m.bounding_box()])
mb=S.motor_board(); c=mb['board+cap']; print('model cap bbox', [round(v,1) for v in c.bounding_box()])
print('cap outside model?', round((m - c).volume(),1))
"
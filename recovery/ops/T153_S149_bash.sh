python3 - <<'EOF'
p='/home/claude/deliver/hardware/cad/slideparts.py'
s=open(p).read()
old='''  # the tongues up the motor's four sides, each with a groove for the tie
  w, up, th = CAP_TONGUE
  tongues = []
  for ang in (0.0, 90.0, 180.0, 270.0):
    tg = box(H, H + th, -w / 2, w / 2, z_back - 0.01, z_back + up)
    tg = tg - box(H + th - TIE_SLOT[1], H + th + 1.0, -w / 2 - 1, w / 2 + 1, z_back + up - 2.0 - TIE_SLOT[0], z_back + up - 2.0)
    tongues.append(tg.rotate((0, 0, ang)))
  part = union([shell] + tongues)'''
new='''  # the tongues up the motor's four sides (clear of the plugs' openings), each with a groove for the tie
  w, up, th = CAP_TONGUE
  x0, y0, x1, y1 = outer.bounds()
  z_in = z_back - CAP_DEPTH + CAP_WALL
  tongues = []
  for side, along in (("+x", 0.0), ("-x", 15.0), ("+y", -14.0), ("-y", 0.0)):
    if side == "+x":
      tg = box(H, H + th, along - w / 2, along + w / 2, z_back, z_back + up) + box(H - 0.5, x1, along - w / 2, along + w / 2, z_in, z_back)
      tg = tg - box(H + th - TIE_SLOT[1], x1 + 1, along - w / 2 - 1, along + w / 2 + 1, z_back + up - 2 - TIE_SLOT[0], z_back + up - 2)
    elif side == "-x":
      tg = box(-H - th, -H, along - w / 2, along + w / 2, z_back, z_back + up) + box(x0, -H + 0.5, along - w / 2, along + w / 2, z_in, z_back)
      tg = tg - box(x0 - 1, -H - th + TIE_SLOT[1], along - w / 2 - 1, along + w / 2 + 1, z_back + up - 2 - TIE_SLOT[0], z_back + up - 2)
    elif side == "+y":
      tg = box(along - w / 2, along + w / 2, H, H + th, z_back, z_back + up) + box(along - w / 2, along + w / 2, H - 0.5, y1, z_in, z_back)
      tg = tg - box(along - w / 2 - 1, along + w / 2 + 1, H + th - TIE_SLOT[1], y1 + 1, z_back + up - 2 - TIE_SLOT[0], z_back + up - 2)
    else:
      tg = box(along - w / 2, along + w / 2, -H - th, -H, z_back, z_back + up) + box(along - w / 2, along + w / 2, y0, -H + 0.5, z_in, z_back)
      tg = tg - box(along - w / 2 - 1, along + w / 2 + 1, y0 - 1, -H - th + TIE_SLOT[1], z_back + up - 2 - TIE_SLOT[0], z_back + up - 2)
    tongues.append(tg)
  part = union([shell] + tongues)'''
assert old in s
s=s.replace(old,new)
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 300 python3 -c "
import slideparts as S
m=S.board_cap(); print(round(m.volume()), len(m.decompose()), [round(v,1) for v in m.bounding_box()])
mb=S.motor_board()
print('cap vs board+plugs? overlap with the board outline region', round((m ^ (mb['car plug']+mb['motor plug'])).volume(),1))
"
python3 - <<'EOF'
p = "mountparts.py"
s = open(p).read()
start = s.index("def motor_bracket() -> Manifold:")
end = s.index("  # block over the motor and walls beside its upper half")
new = '''def motor_bracket() -> Manifold:
  t = MOTOR_PLATE_T
  outline = CrossSection.square((2 * PLATE_HALF, 2 * PLATE_HALF), center=True) + CrossSection.circle(GUARD_OUT, 180)
  # nothing below the square's bottom edge: that keeps clear of the steering wheel teeth's outer band
  outline = outline ^ CrossSection.square((200, 200)).translate((-100, -PLATE_HALF))
  plate = outline.extrude(t) - cyl(NEMA_BOSS / 2 + 0.4, -1, t + 1, segments=128)
  for sx in (-1, 1):
    for sy in (-1, 1):
      x, y = sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2
      plate = plate - cyl(M3_CLEAR / 2, -1, t + 1, x, y, 32) - cyl(3.4, t - 2.6, t + 1, x, y, 32)

  # finger guard: a shell around the motor gear, open below where it meets the steering wheel teeth
  shell = cyl(GUARD_OUT, t, GUARD_FRONT, segments=180) - cyl(GUARD_IN, t - 1, GUARD_FRONT + 1, segments=180)
  lip = cyl(GUARD_OUT, GUARD_FRONT - 1.6, GUARD_FRONT, segments=180) - cyl(GUARD_LIP_IN, GUARD_FRONT - 3, GUARD_FRONT + 1, segments=180)
  window = sector(GUARD_OUT + 6, 270.0 - GUARD_WINDOW, 270.0 + GUARD_WINDOW).extrude(GUARD_FRONT + 4).translate((0, 0, t - 2))
  guard = (shell + lip) - window
  # rounded lower ends: a hand that meets the guard pushes the arm up instead of catching an edge
  for sgn in (-1, 1):
    a = math.radians(270.0 + sgn * GUARD_WINDOW)
    rm = (GUARD_IN + GUARD_OUT) / 2
    guard = guard + cyl((GUARD_OUT - GUARD_IN) / 2 + 0.6, t, GUARD_FRONT, rm * math.cos(a), rm * math.sin(a), 24)

'''
s = s[:start] + new + s[end:]
s = s.replace("GUARD_WINDOW = 55.0 ", "GUARD_WINDOW = 60.0 ")
open(p, "w").write(s)
EOF
grep -n "GUARD_WINDOW = " mountparts.py; export PYTHONPATH=/home/claude/pylib:. && timeout 900 python3 -c "
import time
import mountparts as M, render as R
out='/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/prev/'
parts = {}
for name, fn in (('bracket', M.motor_bracket), ('slider', M.arm_slider), ('arm', M.arm), ('clamp', M.dash_clamp), ('lever', M.lift_lever), ('pad', M.clamp_pad)):
  t0 = time.time()
  try:
    m = fn()
  except Exception as e:
    print(name, 'FAILED', repr(e)); continue
  parts[name] = m
  print(name, m.status(), round(m.volume()/1000,2), 'genus', m.genus(), 'parts', len(m.decompose()), [round(v,1) for v in m.bounding_box()], round(time.time()-t0,2))
K=(0.6,0.6,0.65)
for name, m in parts.items():
  R.save(out+f'm_{name}.png', [([(m,K)], R.view_matrix(35, 25)), ([(m,K)], R.view_matrix(215, 20)), ([(m,K)], R.view_matrix(0, 0.5)), ([(m,K)], R.view_matrix(90,0.5))], titles=['iso','iso back','from +x (side)','from +y'], size=(560,520))
"
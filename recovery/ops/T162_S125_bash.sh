python3 --version; cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "sidebuild.py"
s = open(p).read()
old = '''  st = res["stops"]
  L.append(f"  stops: pulled out, the latch's ear meets the stop {S.STOP_GAP} mm past the latch; slid in, the bracket meets the")
  L.append(f"  bumper with the block {st['block\\'s end to the bumper, slid in 40']} mm short of it; the block stays "
           f"{st['block\\'s ends to the rail\\'s ends (in, out)'][0]} and {st['block\\'s ends to the rail\\'s ends (in, out)'][1]} mm from the rail's ends")'''
new = '''  st = res["stops"]
  block_gap = st["block's end to the bumper, slid in 40"]
  rail_ends = st["block's ends to the rail's ends (in, out)"]
  L.append(f"  stops: pulled out, the latch's ear meets the stop {S.STOP_GAP} mm past the latch; slid in, the bracket meets the")
  L.append(f"  bumper with the block {block_gap} mm short of it; the block stays {rail_ends[0]} and {rail_ends[1]} mm from the "
           "rail's ends")'''
assert old in s, "stops block"
s = s.replace(old, new)

# questions from the CAD's own numbers
old = s[s.index("QUESTIONS = ["):s.index("def support_area(")]
new = '''def envelope() -> dict:
  """Where the mount reaches, from the CAD: how far in from the steering wheel's inside edge, how far forward of the
  back of the round part you hold, and how wide across (mm)."""
  parts = {"bracket": S.side_bracket(), "plate": S.side_plate()}
  r_in = PP.WHEEL_OD_P / 2 - PP.GRIP_P
  back = -PP.GRIP_P / 2
  cap = S.side_board_cap().bounding_box()
  mot_z0 = cap[2] - S.STROKE                        # the board cover's back, slid in (carrier z)
  fwd = lambda y: round(back - (PP.Z_AXIS_P - y))   # carrier y -> mm forward of the back of the round part
  b = parts["bracket"].bounding_box()
  p = parts["plate"].bounding_box()
  sp = S.spring_parts(0.0)
  y_spring = max(sp["axle"].bounding_box()[4], b[4])
  return {"motor_in_now": round(r_in - (PP.R_FACE_P + cap[2])), "motor_in_slid": round(r_in - (PP.R_FACE_P + mot_z0)),
          "motor_forward": (fwd(cap[1]), fwd(cap[4])), "moving_across": round(max(b[3], cap[3]) - b[0]),
          "plate_in": round(r_in - (PP.R_FACE_P + p[2])), "dash_side_forward": fwd(y_spring),
          "knob_from_middle": round(math.hypot(PP.R_FACE_P + S.PIN_Z, S.X_COLLAR - 15.0)),
          "knob_forward": (fwd(S.PIN_Y - S.KIPP["knob_d"] / 2), fwd(S.PIN_Y + S.KIPP["knob_d"] / 2))}


def questions() -> list:
  e = envelope()
  return [
    f"Room inside the steering wheel. Slid in, the motor's back end is {e['motor_in_slid']} mm in from the steering wheel's "
    f"inside edge at 5:20 (it is {e['motor_in_now']} mm in now). It sits {e['motor_forward'][0]} to {e['motor_forward'][1]} mm "
    f"forward of the back of the round part you hold, and with its bracket it is {e['moving_across']} mm across. Is that "
    "space clear, and does it stay clear as the steering wheel turns? Anything on the back of the steering wheel turns "
    f"with it. Beside it, towards 4 o'clock, the mounting plate reaches {e['plate_in']} mm in; on the motor's dash side the "
    f"spring and the bracket's tab reach {e['dash_side_forward']} mm forward. My photo model says the cover on the back of "
    "the steering wheel and the column cover are in the way. You said there is room, so measure it at the car.",
    "Fixing the mounting plate. The plate isn't fixed to the car yet. What is under and beside the steering column at "
    "4 to 5 o'clock, 50 to 100 mm in from the steering wheel, that it can bolt to? A photo from below and one from "
    "the right side would do.",
    f"The latch knob. It points towards 4 o'clock behind the steering wheel, about {e['knob_from_middle']} mm from the "
    f"middle of the steering wheel and {e['knob_forward'][0]} to {e['knob_forward'][1]} mm forward of the back of the round "
    "part. Can you reach it there with the steering wheel straight?",
    "Wobble. With the motor out on the teeth, how deep the teeth mesh is set by the plate; nothing springs. Turn the "
    "steering wheel slowly through its whole turn and watch the back of it at 5 o'clock against something fixed. Does "
    "it move towards or away from the dash, and by how much? Up to about 0.5 mm is fine.",
  ]


'''
s = s.replace(old, new)
s = s.replace('''  for i, q in enumerate(QUESTIONS, 1):''', '''  for i, q in enumerate(questions(), 1):''')
s = s.replace('''"bought": BOUGHT, "questions": QUESTIONS, "problems": problems}''', '''"bought": BOUGHT, "questions": questions(), "envelope": envelope(),
               "problems": problems}''')
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import sidebuild as B
print(B.envelope())
for q in B.questions(): print('-', q)
"
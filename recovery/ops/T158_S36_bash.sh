cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slidemock && python3 - <<'EOF'
import pathlib
p = pathlib.Path("slide_export.py")
s = p.read_text()
a = """  s = sc.summary()
  cars[tag] = {"D": D, "key": [float(v) for v in sc.key], "stalk_mid": [float(v) for v in (sc.p["SH"] + sc.p["ST"]) / 2.0],"""
b = """  s = sc.summary()
  # the closest the motor, its board cover and plugs come to the column cover slid off, to the cover on the back of the
  # steering wheel anywhere it goes, and the slid-off parts to the room your fingers take round the grip
  mot = union([mb["motor"], SP.board_cap(), mb["car plug"], mb["motor plug"], mb["motor's own plug"]])
  cover, bcov = sc.column_cover(), sc.back_cover()
  g_cover = SA.min_gap(A.place(mot, SP.STROKE), cover)
  g_back = min(SA.min_gap(A.place(mot, o), bcov) for o in (-SA.drop_most(), 0.0, SP.STROKE))
  fing = A.fingers()
  g_fing = min(SA.min_gap(A.place(m, SP.STROKE), fing) for m in (mot, SP.slide_carrier(), PP.pop_motor_gear()))
  fmt = lambda g: "touches" if g <= 0.05 else f"{g:.1f} mm"
  gaps[tag] = {"plug_cover": fmt(g_cover), "back_cover": fmt(g_back), "fingers": fmt(g_fing)}
  print("gaps", tag, gaps[tag], flush=True)
  cars[tag] = {"D": D, "key": [float(v) for v in sc.key], "stalk_mid": [float(v) for v in (sc.p["SH"] + sc.p["ST"]) / 2.0],"""
assert s.count(a) == 1
s = s.replace(a, b)
a2 = "cars = {}\n"
assert s.count(a2) == 1
s = s.replace(a2, "cars = {}\ngaps = {}\n")
a3 = """  # from the checks (dsweep.py, mount at 5:20): the board's plug to the column cover slid back, the motor to the back cover
  "gaps": {"107": {"plug_cover": "touches", "back_cover": "7.1 mm"}, "113": {"plug_cover": "2.2 mm", "back_cover": "6.2 mm"},
           "120": {"plug_cover": "6.6 mm", "back_cover": "4.8 mm"}},
}"""
b3 = """  "gaps": gaps,
}"""
assert s.count(a3) == 1
s = s.replace(a3, b3)
a4 = '"springs": [-31.0, 76.0, 15.0]'
assert s.count(a4) == 1
s = s.replace(a4, '"springs": [-31.0, (SP.BLOCK_Y[1] + SP.COLLAR_Y) / 2.0, 15.0]')
p.write_text(s)
print("ok")
EOF
grep -n "^DS\|union" slide_export.py | head -5
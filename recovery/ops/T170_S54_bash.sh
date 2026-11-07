python3 - <<'EOF'
import pathlib, re
p = pathlib.Path("sideassembly.py")
s = p.read_text()
s = s.replace("""  sep = ft_most * math.tan(math.radians(GR.PRESSURE_ANGLE) + math.atan(MG.RUB_DRY))
  # where things are, steering wheel frame""", """  # where things are, steering wheel frame""")
s = s.replace("""  bw, bl, bt = S.BAR
  contact_r = 15.0""", """  _bw, bl, bt = S.BAR
  contact_r = 15.0""")
s = s.replace("""  import gears as GR
  import margins as MG
  g = "Side-slide mount"
  k = MG.motor_k()
  ft_most = P.BOARD_MAX_A * k / (FP.R_P / 1000.0)
  # where things are""", """  import margins as MG
  g = "Side-slide mount"
  k = MG.motor_k()
  ft_most = P.BOARD_MAX_A * k / (FP.R_P / 1000.0)
  # where things are""")
p.write_text(s)
p = pathlib.Path("sidebuild.py")
s = p.read_text()
s = s.replace("""  # the foot's level (the cover's underside) and the cover's screw, for the middle of the range of cover positions
  ff = SA.foot_fit(sum(S.D_FOOT) / 2)
  ax.text(226, 21""", """  ax.text(226, 21""")
s = s.replace("""  ("M3 x 10 socket head screw", 6, "4: rail to mounting plate, with M3 nuts (the nuts sink into the plate's outer face); "
   "2: the spring's strip, through the bracket's tab from the 6 o'clock side into the strip clamp"),""",
 """  ("M3 x 10 socket head screw", 6, ("4: rail to mounting plate, with M3 nuts (the nuts sink into the plate's outer face); "
                                    "2: the spring's strip, through the bracket's tab from the 6 o'clock side into the strip clamp")),""")
s = s.replace("""  ("M4 x 20 socket head screw", 2, "the spool's axle (through a washer, cuts its own thread into the post), and the lever's "
   "pivot (in from the ear's inner end, into the nut in the outer lug)"),""",
 """  ("M4 x 20 socket head screw", 2, ("the spool's axle (through a washer, cuts its own thread into the post), and the lever's "
                                    "pivot (in from the ear's inner end, into the nut in the outer lug)")),""")
s = s.replace("""  ("silicone self-fusing tape (the roll already in the parts list)", 1, "one layer on the foot's top (or the top shim), "
   "where it meets the column cover"),""",
 """  ("silicone self-fusing tape (the roll already in the parts list)", 1, ("one layer on the foot's top (or the top shim), "
                                                                         "where it meets the column cover")),""")
p.write_text(s)
EOF
/home/claude/bin/ruff check --output-format concise sideparts.py sideassembly.py sidebuild.py 2>&1 | tail -3 && cd /home/claude/deliver/hardware/cad && (time PYTHONPATH=/home/claude/pylib python3 sidebuild.py --out /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/out7 --report /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/rep7 > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/build7.log 2>&1; echo "exit $?" >> /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/build7.log) 2>> /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/build7.log &
echo started
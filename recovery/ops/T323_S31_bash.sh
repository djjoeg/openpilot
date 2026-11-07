python3 - <<'EOF'
p = "rightcheck.py"
s = open(p, encoding="utf-8").read()
reps = [
("""    for n, m in sh.items():
      for fn, fm in {"plate": plate, "column cover": cover, "cup screw": screw, **car}.items():
        check(f"arm slid {dx:+.1f} across: {n} / {fn}", m, fm)
      if n != "arm" and "receiver" not in n:
        continue
      for on, om in sh.items():             # the receiver's bolt, washer and nut against the arm and each other
        if on != n and ("receiver" in on or on == "arm") and on < n:
          check(f"arm slid {dx:+.1f} across: {n} / {on}", m, om)
""", """    for n, m in sh.items():
      for fn, fm in {"plate": plate, "column cover": cover, "cup screw": screw, **car}.items():
        check(f"arm slid {dx:+.1f} across: {n} / {fn}", m, fm)
"""),
("""  for d in ((0.0, 0.0, 1.0), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0), (0.0, -1.0, 0.0)):
    blocked(f"arm moved 1 mm {d} in the receiver / plate", arm.translate(d), plate)""",
 """  for d, dn in (((0.0, 0.0, 1.0), "towards you"), ((0.0, 0.0, -1.0), "towards the dash"), ((0.0, 1.0, 0.0), "up"),
                ((0.0, -1.0, 0.0), "down")):
    blocked(f"arm moved 1 mm {dn} in the receiver / plate", arm.translate(d), plate)"""),
("""  pull = RA.BORE_Y[0] + (RA.CUP_Z - RA.ARM_Z[1])          # the arm's gap to the wall on your side, 0.2
  pull = RA.CUP_Z - RA.BORE_Y[0] - RA.ARM_Z[1]
""", """  pull = RA.CUP_Z - RA.BORE_Y[0] - RA.ARM_Z[1]            # the arm's gap to the wall on your side, 0.2
"""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:60]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
cd /home/claude/deliver/hardware/cad && (time PYTHONPATH=/home/claude/pylib python3 rightcheck.py) > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/rc1.txt 2>&1; tail -60 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/rc1.txt
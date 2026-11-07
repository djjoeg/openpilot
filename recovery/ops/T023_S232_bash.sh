python3 - << 'EOF'
import re
p = "params.py"
s = open(p).read()
s = s.replace("ARM_LENGTHS = (70, 90, 110, 130, 150, 170, 190)   # arms to print: dash clamp bolt to hinge block bolt, mm",
              "ARM_LENGTHS = (70, 90, 110, 130, 150, 170, 190, 210, 230)   # arms to print: dash clamp bolt to hinge block bolt, mm")
s = s.replace("ARM_SLIDE = 10.0              # each arm slides +- this much at the dash clamp, so the lengths overlap",
              "ARM_SLIDE = 11.0              # each arm slides +- this much at the dash clamp, so the lengths overlap")
open(p, "w").write(s)
p = "mountparts.py"
s = open(p).read()
rep = [("PIVOT = (HB_TOP + ARM_T / 2 + 1.5, -24.0)        # the arm's bolt (y, z)",
        "PIVOT = (HB_TOP + ARM_T / 2 + 1.5, -16.0)        # the arm's bolt (y, z)"),
       ("LOCK_RANGE = 35.0                                # the joint adjusts +- this many degrees ...",
        "LOCK_RANGE = 37.5                                # the joint adjusts +- this many degrees ..."),
       ("ARM_NOMINAL = 60.0                               # ... around the arm at this angle to the steering column",
        "ARM_NOMINAL = 62.5                               # ... around the arm at this angle to the steering column"),
       ("ARM_ANGLES = (0.0, 75.0)       # the arm can point from level to 75 degrees below level",
        "ARM_ANGLES = (0.0, 80.0)       # the arm can point from level to 80 degrees below level"),
       ("  ear_cs = CrossSection.batch_hull([circle_yz(10.0, py, pz), rect_yz(HB_BOTTOM, HB_TOP, pz - 14.0, pz + 12.0)] +",
        "  ear_cs = CrossSection.batch_hull([circle_yz(10.0, py, pz), rect_yz(HB_BOTTOM, HB_TOP, pz - 14.0, min(pz + 12.0, HB_FRONT))] +"),
       ]
for a, b in rep:
  assert a in s, a
  s = s.replace(a, b)
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/grid.py
cd /home/claude/deliver/hardware/cad && cp slideparts.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide/slideparts_stroke55_backup.py && cp slideassembly.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide/slideassembly_stroke55_backup.py && python3 - <<'EOF'
import pathlib
p = pathlib.Path("slideparts.py")
s = p.read_text()
reps = [
("""STROKE = 5.5                 # slid off: the carrier this far back towards the dash (the gear then clears the teeth by 2)
""",
"""STROKE = 8.25               # slid off: the carrier this far forward (towards the nose), which takes the motor, the gear
                             # and the carrier 1.5 mm out of the room your fingers need round the grip (popassembly.FINGERS)
"""),
("""ROD_D, ROD_LEN = 6.0, 100.0
RODS = ((-31.0, -15.0), (-31.0, 15.0))     # (x, z) of each rod
ROD_FRONT = -12.0                          # the rods' front ends (in the carrier)
ROD_HOLE = 5.95                            # pressed into the carrier, and a grub screw each
""",
"""ROD_D, ROD_LEN = 6.0, 100.0
RODS = ((-31.0, -15.0), (-31.0, 15.0))     # (x, z) of each rod
ROD_HOLE = 5.95                            # pressed into the carrier, and a grub screw each (the rods' front ends: below)
"""),
("""CAM_RATE = 6.5                             # mm per radian at most: where the cam touches the pusher's nose stays within
                                           # this of the nose's middle (its flat face reaches 7.5)
""",
"""CAM_RATE = 7.5                             # mm per radian at most: where the cam touches the pusher's nose stays within
                                           # this of the nose's middle (its flat face reaches 8.5)
"""),
("""NOSE_HALF = (3.3, 8.0)                     # the pusher's square nose that the cam pushes: +- across (x), +- up/down (z)
""",
"""NOSE_HALF = (3.3, 9.0)                     # the pusher's square nose that the cam pushes: +- across (x), +- up/down (z)
"""),
("""# Lee Spring LC 022D 05 S: stainless, 7.62 mm outside, 6.50 inside (on a rod up to 6.10), 0.56 mm wire, 19.05 mm long,
# 0.578 N/mm, 9.27 N at its solid height of 3.38 mm.
RSPRING = {"part": "Lee Spring LC 022D 05 S", "od": 7.62, "wire": 0.56, "free": 19.05, "rate": 0.578, "solid": 3.38,
           "max": 9.27}
END_HOLE_D = 6.8                           # the rods' holes in the block's end walls: the springs bear on the wall round them
COLLAR = (12.0, 7.0)                       # 6 mm bore shaft collar: 12 across, 7 wide (set screw)
COLLAR_Y = ROD_FRONT + ROD_LEN - COLLAR[1]  # the collars' front faces, with the carrier on
""",
"""# Lee Spring LC 022D 08 S: stainless, 7.62 mm outside, 6.50 inside (on a rod up to 6.10), 0.56 mm wire, 25.4 mm long,
# 0.403 N/mm, 9.27 N at its solid height of 4.6 mm (leespring.com). RSPRING_ON: each spring's length with the carrier on.
RSPRING = {"part": "Lee Spring LC 022D 08 S", "od": 7.62, "wire": 0.56, "free": 25.4, "rate": 0.403, "solid": 4.6,
           "max": 9.27}
RSPRING_ON = 10.5
END_HOLE_D = 6.8                           # the rods' holes in the block's end walls: the springs bear on the wall round them
COLLAR = (12.0, 7.0)                       # 6 mm bore shaft collar: 12 across, 7 wide (set screw)
COLLAR_Y = BLOCK_Y[1] + RSPRING_ON          # the collars' front faces, with the carrier on
ROD_FRONT = COLLAR_Y + COLLAR[1] - ROD_LEN  # the rods' front ends (in the carrier's wall), with the collars at their back ends
"""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:70]
  s = s.replace(a, b)
p.write_text(s)
print("ok")
EOF
grep -n "ROD_FRONT\|RSPRING\[\|release_force\|COLLAR_Y" slideparts.py slideassembly.py | head -30
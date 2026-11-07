python3 - << 'EOF'
p = "params.py"
s = open(p).read()
a = """Z_GEAR_ROLLER = (-4.0, 4.0)   # motor gear: roller
Z_GEAR_TEETH = (5.75, 17.0)   # motor gear: teeth"""
b = """Z_GEAR_ROLLER = (-4.0, 3.5)   # motor gear: roller (a 45 degree cone joins it to the teeth, so the gear prints roller
Z_GEAR_TEETH = (5.3, 17.0)    # down without supports); motor gear: teeth"""
assert a in s; s = s.replace(a, b); open(p, "w").write(s)

p = "wheelparts.py"
s = open(p).read()
a = """  roller = cyl(ROLLER_R, zr0, zr1, segments=360)
  core = cyl(rf, zr1 - 0.01, zt0 + 0.01, segments=180)"""
b = """  roller = cyl(ROLLER_R, zr0, zr1, segments=360)
  # 45 degree cone from the roller's edge up to the teeth, so the teeth sit on it when printing roller down; it stays
  # clear of the step between the steering wheel teeth's rolling band and their teeth
  core = Manifold.cylinder(zt0 - zr1 + 0.01, ROLLER_R, ROLLER_R - (zt0 - zr1), 360).translate((0, 0, zr1 - 0.005))"""
assert a in s; s = s.replace(a, b); open(p, "w").write(s)

p = "mountparts.py"
s = open(p).read()
rep = [
("""SPRING_POST_R = 3.1                   # post on the carrier's top, inside the spring
SPRING_POST_H = 7.0
SPRING_POCKET_R = 5.5                 # pocket in the hinge block's underside
SPRING_POCKET_D = 6.5
SETUP_GAP = 12.0                      # carrier top to hinge block underside with the motor gear on the teeth
SPRING_LEN = SETUP_GAP + SPRING_POCKET_D   # spring's length with the motor gear on the teeth""",
"""SPRING_SEAT_R = 5.2                   # shallow seat in the carrier's top for the spring's lower end
SPRING_SEAT_D = 2.0
SPRING_POCKET_R = 5.5                 # pocket in the hinge block's underside for its upper end
SPRING_POCKET_D = 4.5
SETUP_GAP = 12.0                      # carrier top to hinge block underside with the motor gear on the teeth
SPRING_LEN = SETUP_GAP + SPRING_POCKET_D + SPRING_SEAT_D   # spring's length with the motor gear on the teeth"""),
("""  # block over the motor, walls beside its upper half, the hinge knuckle, the tail with the fin, and the spring post""",
 """  # block over the motor, walls beside its upper half, the hinge knuckle, the tail with the fin. The knuckle and the
  # fin have 45 degree slopes in front so the carrier prints finger guard down"""),
("""  knuckle = cyl_x(HINGE_R, -CARRIER_KNUCKLE, CARRIER_KNUCKLE, y=hy, z=hz) + \\
    box(-CARRIER_KNUCKLE, CARRIER_KNUCKLE, TOP_Y[1] - 1.0, hy, hz - HINGE_R, hz + HINGE_R)""",
 """  knuckle = cyl_x(HINGE_R, -CARRIER_KNUCKLE, CARRIER_KNUCKLE, y=hy, z=hz) + \\
    box(-CARRIER_KNUCKLE, CARRIER_KNUCKLE, TOP_Y[1] - 1.0, hy, hz - HINGE_R, hz + HINGE_R)
  rise = hy - TOP_Y[1] + 0.5
  knuckle = knuckle + prism_x([(TOP_Y[1] - 0.5, hz + HINGE_R - 0.01), (hy, hz + HINGE_R - 0.01),
                               (TOP_Y[1] - 0.5, hz + HINGE_R + rise)], -CARRIER_KNUCKLE, CARRIER_KNUCKLE)"""),
("""  fin = box(-FIN_HALF, FIN_HALF, TOP_Y[0], FIN_TOP, vz - FIN_LEN / 2, vz + FIN_LEN / 2)
  post = cyl_y(SPRING_POST_R, TOP_Y[1] - 0.5, TOP_Y[1] + SPRING_POST_H, z=SPRING_Z, segments=40)
  part = plate + guard + block + walls + knuckle + tail + fin + post""",
 """  zf = vz + FIN_LEN / 2
  fin = prism_x([(TOP_Y[0], vz - FIN_LEN / 2), (FIN_TOP, vz - FIN_LEN / 2), (FIN_TOP, zf),
                 (TOP_Y[1] - 0.5, zf + FIN_TOP - TOP_Y[1] + 0.5), (TOP_Y[0], zf + FIN_TOP - TOP_Y[1] + 0.5)], -FIN_HALF, FIN_HALF)
  part = plate + guard + block + walls + knuckle + tail + fin
  part = part - cyl_y(SPRING_SEAT_R, TOP_Y[1] - SPRING_SEAT_D, TOP_Y[1] + 1.0, z=SPRING_Z, segments=64)"""),
# hinge block: wider channel clearance, ears to the front face, chins under the knuckles
("""    kn.append(cyl_x(HINGE_R, x0, x1, y=hy, z=hz) + box(x0, x1, hy, HB_BOTTOM + 0.5, hz - HINGE_R, hz + HINGE_R))

  # ears either side""",
 """    chin = prism_x([(KNUCKLE_CHIN_Y, hz + HINGE_R - 0.01), (HB_BOTTOM + 0.5, hz + HINGE_R - 0.01),
                    (HB_BOTTOM + 0.5, hz + HINGE_R + HB_BOTTOM + 0.5 - KNUCKLE_CHIN_Y)], x0, x1)
    kn.append(cyl_x(HINGE_R, x0, x1, y=hy, z=hz) + box(x0, x1, hy, HB_BOTTOM + 0.5, hz - HINGE_R, hz + HINGE_R) + chin)

  # ears either side"""),
("""  ear_cs = CrossSection.batch_hull([circle_yz(10.0, py, pz), rect_yz(HB_BOTTOM, HB_TOP, pz - 14.0, min(pz + 12.0, HB_FRONT))] +""",
 """  ear_cs = CrossSection.batch_hull([circle_yz(10.0, py, pz), rect_yz(HB_BOTTOM, py + 10.0, pz - 14.0, HB_FRONT)] +"""),
("""  part = part - (cyl_x(HINGE_R + GAP, -CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, y=hy, z=hz, segments=96) +
                 box(-CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, hy - 20.0, hy, hz - HINGE_R - GAP, hz + HINGE_R + GAP))""",
 """  rc = HINGE_R + CHANNEL_GAP
  part = part - (cyl_x(rc, -CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, y=hy, z=hz, segments=96) +
                 box(-CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, hy - 20.0, hy, hz - rc, hz + rc))"""),
("""HB_BODY_BACK = HINGE[1] - HINGE_R - 3.0          # back end of the main body (just behind the hinge)""",
 """HB_BODY_BACK = HINGE[1] - HINGE_R - 3.0          # back end of the main body (just behind the hinge)
CHANNEL_GAP = 0.6                     # the carrier's knuckle turns in a channel this much bigger than it
KNUCKLE_CHIN_Y = HINGE[0] - 5.35      # the hinge block's knuckles have 45 degree slopes in front from here up"""),
]
for a, b in rep:
  assert a in s, a[:80]
  s = s.replace(a, b)
open(p, "w").write(s)
EOF
grep -n "SPRING_POST" mountparts.py assembly.py; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  " ; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/overhang.py
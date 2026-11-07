cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
s = open('popparts.py').read()
rep = [
("""BETA_C = 100.0                # the carrier's bolt, degrees round the hinge (from +y towards +z): above the motor's front""",
 """BETA_C = 117.0                # the carrier's bolt, degrees round the hinge (from +y towards +z): through the block over
                              # the motor; both bolts sit behind the wiper stalk and the key"""),
("""BETA_B = BETA_C + 180.0 - DEAD_DEG     # the hinge block's bolt: behind the board""",
 """BETA_B = BETA_C + 180.0 - DEAD_DEG     # the hinge block's bolt: towards the column from the hinge"""),
("""    self.z_flat = z_axis - MP.PLATE_BOTTOM + FP.FLAT_CLEAR     # inside the teeth: clear of the carrier plate's edge""",
 """    self.z_flat = z_axis - MP.PLATE_BOTTOM + FLAT_CLEAR_P      # inside the teeth: clear of the carrier plate's edge"""),
("""PLUG_SLOT = (-9.5, 9.5, -NEMA_LEN - 1.0, -NEMA_LEN + 21.0)   # x and z: room for the motor's own cable plug""",
 """PLUG_SLOT = (-9.5, 9.5, -NEMA_LEN - 1.0, -NEMA_LEN + 20.0)   # x and z: room for the motor's own cable plug"""),
("""SW_HOLES_R = LOBE_R + MP.SW_OP - MP.SW_PRESS   # the switch's holes' line, this far from the hinge along SW_BETA""",
 """SW_PRESS_P = 0.9                               # on, the lobe holds the roller this far past where the switch clicks
SW_HOLES_R = LOBE_R + MP.SW_OP - SW_PRESS_P    # the switch's holes' line, this far from the hinge along SW_BETA"""),
]
for a, b in rep:
  assert a in s, a[:60]
  s = s.replace(a, b)
# flat clearance constant
s = s.replace("""SPOKE_CLEAR = 5.0             # the motor's side towards you stays this far behind the spokes' back face""",
"""SPOKE_CLEAR = 5.0             # the motor's side towards you stays this far behind the spokes' back face
FLAT_CLEAR_P = 5.0            # inside the teeth the channel's back stands this far clear of the carrier plate's edge (the
                              # motor's side clears it by 3.85 too, and by 1 dropped past the teeth's ends)""")
# carrier: replace the bar with a boss round the springs' front bolt in the block over the motor
old = """  # the springs' front bolt: a bar across above the motor's front half
  cy, cz = C_BOLT
  bar = Manifold.batch_hull([cyl_x(6.0, -SIDE_X[1], SIDE_X[1], y=cy, z=cz),
                             box(-SIDE_X[1], SIDE_X[1], TOP_Y[1] - 1.0, TOP_Y[1], cz - 8.0, cz + 8.0)])"""
new = """  # the springs' front bolt goes across through the block over the motor, thickened round it
  cy, cz = C_BOLT
  bar = Manifold.batch_hull([cyl_x(6.0, -SIDE_X[1], SIDE_X[1], y=cy, z=cz),
                             box(-SIDE_X[1], SIDE_X[1], TOP_Y[0], TOP_Y[1], cz - 6.0, cz + 6.0)]) ^ \\
    box(-SIDE_X[1], SIDE_X[1], TOP_Y[0], 60.0, -60.0, 10.0)"""
assert old in s
s = s.replace(old, new)
open('popparts.py', 'w').write(s)

a = open('popassembly.py').read()
old = '''    c = cyl_x(2.5, -44.0, 44.0, y=cy, z=cz, segments=16) + cyl_x(4.6, -48.0, -44.0, y=cy, z=cz, segments=16) + \\
      cyl_x(4.6, 39.5, 45.0, y=cy, z=cz, segments=6)
    b = cyl_x(2.5, -44.0, 44.0, y=by, z=bz, segments=16) + cyl_x(4.6, -48.0, -44.0, y=by, z=bz, segments=16) + \\
      cyl_x(4.6, 39.5, 45.0, y=by, z=bz, segments=6)'''
new = '''    def through(y, z):
      # M5 x 80: head and washer outside one spring's loop, washer and lock nut outside the other's
      x_out = PP.SPRING_X + PP.SPRING_WIRE_P / 2 + 1.0
      return (cyl_x(2.5, -x_out, x_out + 6.2, y=y, z=z, segments=16) + cyl_x(4.6, -x_out - 3.5, -x_out, y=y, z=z, segments=16) +
              cyl_x(4.6, x_out, x_out + 5.2, y=y, z=z, segments=6))
    c = through(cy, cz)
    b = through(by, bz)'''
assert old in a
a = a.replace(old, new)
open('popassembly.py', 'w').write(a)
EOF
grep -n "PLATE_FRONT_Z" popparts.py | head -5
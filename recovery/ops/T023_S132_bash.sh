python3 - <<'EOF'
p = "wheelparts.py"
s = open(p).read()
start = s.index("  teeth = gear_outline(MOTOR_TEETH, BACKLASH).extrude(zt1 - zt0).translate((0, 0, zt0))")
end = s.index("MOTOR_GEAR_PHASE = ")
new = '''  teeth = gear_outline(MOTOR_TEETH, BACKLASH).extrude(zt1 - zt0).translate((0, 0, zt0))
  roller = cyl(rp + ROLL_GROW, zr0, zr1, segments=360)
  core = cyl(rf, zr1 - 0.01, zt0 + 0.01, segments=180)
  # turn the gear so a tooth gap faces +y, where the set screw goes in and the shaft's flat faces
  part = (teeth + roller + core).rotate((0, 0, MOTOR_GEAR_PHASE))
  # bore: round where the shaft is round, D shaped where it has its flat (flat facing +y)
  flat_from = SHAFT_LEN - SHAFT_FLAT_LEN
  r = SHAFT_D / 2 + 0.12
  flat_y = SHAFT_ACROSS_FLAT - SHAFT_D / 2 + 0.12
  d_shape = CrossSection.circle(r, 96) - CrossSection.square((2 * r + 2, 2 * r)).translate((-r - 1, flat_y))
  part = part - cyl(r, zr0 - 1, flat_from + 0.01, segments=96)
  part = part - d_shape.extrude(zt1 + 1 - flat_from).translate((0, 0, flat_from))
  # chamfer the bore's entry so the gear starts onto the shaft easily
  part = part - Manifold.cylinder(1.0, r + 0.8, r, 48).translate((0, 0, zr0))
  # set screw: radial along +y onto the flat, through the middle of the tooth gap facing +y
  z_set = (zt0 + min(zt1, SHAFT_LEN)) / 2.0
  hole = cyl_y(M3_PILOT / 2, 0.0, rp + 4, z=z_set, segments=32)
  return clean(part - hole)


'''
s = s[:start] + new + s[end:]
# phase constant must be defined before use: move it above motor_gear
s = s.replace("MOTOR_GEAR_PHASE = 90.0 - 180.0 / MOTOR_TEETH   # motor_gear() is turned this much from \"tooth 0 on +x\"\n", "")
s = s.replace("# ***** motor gear *****\n", "# ***** motor gear *****\n\nMOTOR_GEAR_PHASE = 90.0 - 180.0 / MOTOR_TEETH   # motor_gear() is turned this much from \"tooth 0 on +x\"\n")
open(p, "w").write(s)
EOF
grep -n "MOTOR_GEAR_PHASE\|gap_angle" wheelparts.py; export PYTHONPATH=/home/claude/pylib:. && timeout 600 python3 -c "
import time
import wheelparts as W
t = W.Teeth()
t0=time.time()
s = W.teeth_solid(t)
r = W.teeth_half(t,'right',s); l = W.teeth_half(t,'left',s); o = W.teeth_one_piece(t,s)
g = W.motor_gear(); f1 = W.grip_fit_test(t); f2 = W.tooth_fit_test(t)
for n,m in (('right',r),('left',l),('one',o),('gear',g),('gripfit',f1),('toothfit',f2)):
  print(n, m.status(), round(m.volume()/1000,2), 'genus', m.genus(), 'parts', len(m.decompose()))
print(round(time.time()-t0,2),'s')
"
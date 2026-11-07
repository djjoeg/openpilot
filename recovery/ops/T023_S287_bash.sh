python3 - << 'EOF'
p = "params.py"
s = open(p).read()
rep = [("""ROLLER_R = 22.5       # motor gear's roller: bigger than its teeth (21 mm), so with the steering wheel turned past
                      # the teeth the roller, not the teeth, rests on the steering wheel""",
"""# Motor gear's roller and the rolling band it rides on: the spring presses the roller onto the band, which sets how
# deep the teeth mesh. Both sit on the gears' pitch circles (scaled out by CD_EXTRA), so the roller turns at exactly
# the gear ratio and rolls without scrubbing while the teeth mesh.
ROLLER_R = MOTOR_TEETH * (RING_TEETH + MOTOR_TEETH + CD_EXTRA) / (RING_TEETH + MOTOR_TEETH)"""),
("END_LEAD_IN = 4.0       # degrees over which the rolling band slopes down at each end",
 "END_LEAD_IN = 6.0       # degrees over which the rolling band slopes down at each end"),
("""Z_GEAR_ROLLER = (-4.0, 3.5)   # motor gear: roller (a 45 degree cone joins it to the teeth, so the gear prints roller
Z_GEAR_TEETH = (5.3, 17.0)    # down without supports); motor gear: teeth""",
"""Z_GEAR_ROLLER = (-4.0, 5.3)   # motor gear: roller (runs up to the teeth)
Z_GEAR_TEETH = (5.3, 17.0)    # motor gear: teeth"""),
]
for a, b in rep:
  assert a in s, a[:50]
  s = s.replace(a, b)
open(p, "w").write(s)

p = "wheelparts.py"
s = open(p).read()
a = """  roller = cyl(ROLLER_R, zr0, zr1, segments=360)
  # 45 degree cone from the roller's edge up to the teeth, so the teeth sit on it when printing roller down; it stays
  # clear of the step between the steering wheel teeth's rolling band and their teeth
  core = Manifold.cylinder(zt0 - zr1 + 0.01, ROLLER_R, ROLLER_R - (zt0 - zr1), 360).translate((0, 0, zr1 - 0.005))"""
b = """  roller = cyl(ROLLER_R, zr0, zr1 + 0.01, segments=360)
  core = roller"""
assert a in s; s = s.replace(a, b)
open(p, "w").write(s)

p = "accord_lka_parts.py"
s = open(p).read()
a = """  parts["motor-gear"] = (WP.motor_gear(), (0, 0, 0), "roller down", "none")"""
b = """  parts["motor-gear"] = (WP.motor_gear(), (180, 0, 0), "teeth down", "none")"""
assert a in s; s = s.replace(a, b)
open(p, "w").write(s)
EOF
sed -n 186,216p wheelparts.py; PYTHONPATH=/home/claude/pylib python3 -c "
import params as P, wheelparts as WP
t = WP.Teeth()
print('roller', P.ROLLER_R, 'band', t.r_roll, 'ratio check', t.r_roll / P.ROLLER_R, P.RING_TEETH / P.MOTOR_TEETH, 'half arc', t.half)
"
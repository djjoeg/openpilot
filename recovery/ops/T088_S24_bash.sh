python3 - <<'EOF'
p='columnparts.py'; s=open(p).read()
old="Z_TEETH_C = (Z_GEAR_TEETH_C[0] - 0.5, Z_GEAR_TEETH_C[1] + 0.5)      # the ring's teeth cover the motor gear's teeth\n"
new="Z_TEETH_C = (Z_GEAR_TEETH_C[0] + 0.2, Z_GEAR_TEETH_C[1] + 0.5)      # the ring's teeth: clear of the roller, past the gear's tips\n"
assert old in s; s=s.replace(old,new); open(p,'w').write(s); print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import columnparts as CP, params as P, wheelparts as WP
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP)
ring = CP.ring_teeth(t)
cd = CP.centre_distance()
g = WP.motor_gear().translate((0, -cd, P.Z_MOTOR_FACE_C))
print("whole overlap:", (ring ^ g).volume(), "Z teeth", CP.Z_TEETH_C, "roll", CP.Z_ROLL_C)
EOF
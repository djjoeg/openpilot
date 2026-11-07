python3 - <<'EOF'
p = 'incar.py'
s = open(p).read()
old = "         np.array([150.0, -147.0, -178.0]), np.array([95.0, -147.0, -178.0]), np.array([60.0, -150.0, -190.0]),"
new = "         np.array([150.0, -148.0, -180.0]), np.array([125.0, -156.0, -182.0]), np.array([60.0, -157.0, -192.0]),"
assert old in s
s = s.replace(old, new)
open(p, 'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 600 python3 -c "
import incar as IC, rightarm as RA, rightcheck as RC, carphoto as CP
c = IC.cable()[0][0]
solid = [RA.arm(), RA.carrier(0.0), RA.plate_to_wheel(RA.frame_plate_v4())] + list(RC.hardware(0.0, RA.STOP_P).values()) + [m for m, _ in CP.motor_parts(0.0)]
bad = [(i, round((c ^ m).volume(), 1)) for i, m in enumerate(solid) if (c ^ m).volume() > 0.5]
print('overlaps', bad)
pb = RA.plate_to_wheel(RA.frame_plate_v4()).bounding_box(); print('frame plate bbox', [round(v,1) for v in pb])
"
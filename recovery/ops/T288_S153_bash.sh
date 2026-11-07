python3 - <<'EOF'
p = 'incar.py'
s = open(p).read()
old = "  pts = [p0, p0 + 9.0 * out, uv(240.0, -36.0, -90.0), uv(238.0, -40.0, -168.0), uv(222.0, -50.0, -178.0),"
new = "  pts = [p0, p0 + 9.0 * out, uv(240.0, -36.0, -84.0), uv(238.0, -51.0, -100.0), uv(236.0, -51.0, -170.0), uv(222.0, -52.0, -179.0),"
assert old in s
s = s.replace(old, new)
open(p, 'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 600 python3 -c "
import incar as IC, rightarm as RA, rightcheck as RC
from manifold3d import Manifold
c = IC.cable()[0][0]
solid = [RA.arm(), RA.carrier(0.0), RA.plate_to_wheel(RA.frame_plate_v4())] + list(RC.hardware(0.0, RA.STOP_P).values())
import carphoto as CP
for m, mat in CP.motor_parts(0.0): solid.append(m)
for i, m in enumerate(solid):
    v = (c ^ m).volume()
    if v > 0.5: print('cable overlaps part', i, round(v, 1), 'mm3')
print('checked', len(solid))
"
python3 - <<'EOF'
p = 'rightarm.py'
s = open(p, encoding='utf-8').read()
a = """  pocket = pocket.translate((SLIDE_NUT_U[1], 0.0, SLIDE_Z0))"""
b = """  pocket = pocket.translate((SLIDE_NUT_U[0], 0.0, SLIDE_Z0))"""
assert s.count(a) == 1
open(p, 'w', encoding='utf-8').write(s.replace(a, b))
EOF
PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import rightarm as RA, rightcheck as RC
car = RA.carrier(0.0)
print("seated nut / carrier", round((RC.slide_nut(0.0) ^ car).volume(), 3), "mm3")
print("smallest nut turned / carrier", round((RC.slide_nut(0.0, small_turned=True) ^ car).volume(), 3), "mm3")
print("carrier genus", car.genus(), "grams", round(car.volume() / 1000 * 1.28))
EOF
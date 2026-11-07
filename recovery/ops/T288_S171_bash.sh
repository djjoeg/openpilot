python3 - <<'EOF'
p = 'incar.py'
s = open(p).read()
old = '''  return {"sky": dict(up=back / np.linalg.norm(back), sky=(0.60, 0.61, 0.63), ground=(0.10, 0.10, 0.10), power=1.0),
          "wheel_shade": dict(k=0.4, r0=150.0, r1=215.0, z=-12.0)}'''
new = '''  return {"sky": dict(up=back / np.linalg.norm(back), sky=(0.60, 0.61, 0.63), ground=(0.40, 0.40, 0.40), power=1.0),
          "wheel_shade": dict(k=0.55, r0=150.0, r1=215.0, z=-12.0)}'''
assert old in s
s = s.replace(old, new)
open(p, 'w').write(s)
EOF
(time PYTHONPATH=/home/claude/pylib timeout 2400 python3 incar.py 00) 2>&1 | tail -3
sed -n 1,12p render.py && python3 - <<'EOF'
p = 'rightarm.py'
s = open(p, encoding='utf-8').read()
a = """  bu, bv = BAR_UV
  m = m - teardrop_x(M5_HOLE / 2, SLIDE_NUT_U[0] - 2.0"""
b = """  bv = BAR_UV[1]
  m = m - teardrop_x(M5_HOLE / 2, SLIDE_NUT_U[0] - 2.0"""
assert s.count(a) == 1
open(p, 'w', encoding='utf-8').write(s.replace(a, b))
print('ok')
EOF
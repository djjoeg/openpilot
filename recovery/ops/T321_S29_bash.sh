python3 - <<'EOF'
p = 'incar.py'
s = open(p, encoding='utf-8').read()
a = """v3 and its tower, the motor carrier with the motor (slid up to its stop, the gear in the teeth), the gear, the teeth"""
b = """v5 and its tower, the motor carrier with the motor (slid up the groove, the gear in the teeth), the gear, the teeth"""
assert s.count(a) == 1
open(p, 'w', encoding='utf-8').write(s.replace(a, b))
print('ok')
EOF
sed -n 40,70p viewer3d.py
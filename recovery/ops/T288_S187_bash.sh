python3 - <<'EOF'
p = 'incar.py'
s = open(p).read()
old = '''  "33": {"file": "818fd797", "cam": 33, "wheel": 0.0, "light": "flash", "ss": 1,'''
assert old in s, 'pattern'
s = s.replace(old, '''  "33": {"file": "818fd797", "cam": 33, "wheel": 0.0, "light": "flash", "ss": 1, "pair": (0, 0, 1932, 2576),''')
s = s.replace('''                                    # and in-the-car-photo-33.jpg''', '''                                    # and in-the-car-photo-33.jpg (+ -before-after.jpg)''')
open(p, 'w').write(s)
print('ok')
EOF
(time PYTHONPATH=/home/claude/pylib timeout 2400 python3 incar.py 33) 2>&1 | tail -3; ruff check incar.py --output-format concise | tail -1; ls -la ../report | grep in-the-car
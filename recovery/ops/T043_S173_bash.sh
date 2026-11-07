cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
s = open('accord_lka_parts.py').read()
old = '''  names = ["steering-wheel-teeth-29-left-half", "steering-wheel-teeth-29-right-half", "steering-wheel-teeth-15-one-piece",
           "motor-gear", "motor-carrier", "hinge-block", "lever-bracket", "lift-lever", "dash-clamp", "clamp-pad", "setup-gauge",
           "fit-test-steering-wheel", "fit-test-teeth"]'''
new = '''  names = ["steering-wheel-teeth-29-left-half", "steering-wheel-teeth-15-one-piece", "motor-gear", "motor-carrier",
           "hinge-block", "lever-bracket", "lift-lever", "dash-clamp", "clamp-pad", "setup-gauge", "fit-test-steering-wheel",
           "fit-test-teeth"]'''
assert old in s
s = s.replace(old, new)
open('accord_lka_parts.py', 'w').write(s)
EOF
rm -f ../report/parts-*.png && PYTHONPATH=/home/claude/pylib timeout 2400 python3 accord_lka_parts.py 2>&1 | tail -2; rm -rf __pycache__; ls ../report/; md5sum ../stl/*.stl | head -3
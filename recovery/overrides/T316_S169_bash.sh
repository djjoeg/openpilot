cd /home/claude/deliver && python3 - <<'EOF'
p = 'hardware/cad/rightarm.py'
s = open(p, encoding='utf-8').read()
a = "WASHER_OD, WASHER_T = 24.0, 1.6  # a #8 or M4 fender washer; anything over 17 mm across lands on the tower"
b = ("WASHER_OD, WASHER_T = 24.0, 1.6  # a fender washer 19 to 25 mm across, #8 or M4 hole: over 18.2 it sits on the\n"
     "                                 # tower's bottom face clear of the tube's chamfer (DIN 9021 M4, 12 mm, is too small)")
assert s.count(a) == 1
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
EOF
python3 - <<'EOF'
p = "visuals.py"
s = open(p, encoding="utf-8").read()
a = """                 "as drawn, from your seat, low: the wing bolt in the receiver's groove, on your side",
                 "PUTTING IT ON: the arm, with the motor on it and the nut in the slot in its top, slides into the "
                 "receiver from the key side; then the wing bolt and washer in through the groove"],"""
b = """                 "as drawn, from your seat, low: the wing bolt in the groove, on your side",
                 "PUTTING IT ON: the arm, its nut in the slot in its top, slides in\\nfrom the key side; "
                 "then the wing bolt and washer in through the groove"],"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
grep -n "def receiver_picture" -A12 visuals.py | head -5; grep -n "def save" -A30 render.py | grep -n "title" | head
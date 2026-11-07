python3 - <<'EOF'
p = "visuals.py"
s = open(p, encoding="utf-8").read()
a = """                 "PUTTING IT ON: the arm, its nut in the slot in its top, slides in\\nfrom the key side; "
                 "then the wing bolt and washer in through the groove"],"""
b = """                 ("PUTTING IT ON: the arm, its nut in the slot in its top, slides in\\nfrom the key side; "
                  "then the wing bolt and washer in through the groove")],"""
assert s.count(a) == 1
s = s.replace(a, b)
a = """  def parts(dx, receiver_in=True, away=0.0):
    ps = assembly_parts(with_grip=False, dz=RA.DZ_OUT, arm_dx=dx + away, receiver_in=receiver_in)
    return ps"""
b = """  def parts(dx, receiver_in=True, away=0.0):
    return assembly_parts(with_grip=False, dz=RA.DZ_OUT, arm_dx=dx + away, receiver_in=receiver_in)"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
ruff check rightarm.py rightcheck.py stiffness.py visuals.py viewer3d.py incar.py carphoto.py allinone.py 2>&1 | tail -3; grep -rn "frame_plate_v4\|column-frame-plate-v4\|ARM_MID_Y\|PINCH_X\|NUT_TRAP" --include=*.py . | grep -v "^./armmount.py" | head
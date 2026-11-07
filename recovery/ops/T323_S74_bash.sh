cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "viewer3d.py"
s = open(p, encoding="utf-8").read()
a = """    ("rbolt", "Arm wing bolt", n["rbolt"], "bolts", True, [(hw["receiver bolt"], STEEL, 1.0)],
     M_ARM + [mv(8, 0.0, 1.0, (0.0, 0.0, 25.0))]),
    ("rwasher", "Arm washer (fender washer)", n["rwasher"], "bolts", True, [(hw["receiver washer"], STEEL, 1.0)],
     M_ARM + [mv(8, 0.0, 1.0, (0.0, 0.0, 25.0))]),"""
b = """    ("rbolt", "Arm wing bolt", n["rbolt"], "bolts", True, [(hw["receiver bolt"], STEEL, 1.0)],
     M_PLATE + [mv(8, 0.0, 1.0, (0.0, 0.0, 25.0))]),             # waits by the groove, then in along the column
    ("rwasher", "Arm washer (fender washer)", n["rwasher"], "bolts", True, [(hw["receiver washer"], STEEL, 1.0)],
     M_PLATE + [mv(8, 0.0, 1.0, (0.0, 0.0, 25.0))]),"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 viewer3d.py 2>&1 | tail -2; cat /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/stiff2.txt | tail -8
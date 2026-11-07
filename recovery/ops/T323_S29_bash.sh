cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "rightarm.py"
s = open(p, encoding="utf-8").read()
a = """BLOCK = (-60.0, 28.0, -14.0, 50.0)       # v1's block, out to the receiver's far end on the key side"""
b = """BLOCK = (-60.0, 28.0, -14.0, 45.4)       # v1's block (v5: ending level with the receiver's dash-side face, 4.6 short of
                                         # v4's, so it stays 3 mm clear of the dash in the photo estimates)"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
grep -n "BLOCK\[3\]\|BLOCK\b" rightarm.py | head
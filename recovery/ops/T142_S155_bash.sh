python3 - <<'EOF'
import pathlib
p = pathlib.Path("popassembly.py")
s = p.read_text()
old = '''    cy, cz = PP.turn(PP.C_BOLT, lift)
    by, bz = PP.B_BOLT'''
assert s.count(old) == 1
s = s.replace(old, '''    cy, cz = PP.C_BOLT                     # built with the motor on, then swung with the carrier
    by, bz = PP.B_BOLT''')
p.write_text(s)
print("ok")
EOF
grep -n "def bolts" -A 20 popassembly.py | head -24
sed -i 's/^  tw, tt = NUT_TRAP\n  slot = uvz(PUSH/X/' rightarm.py && python3 - <<'EOF'
p = "rightarm.py"
s = open(p).read()
old = "  tw, tt = NUT_TRAP\n  slot = uvz(PUSH_NUT_U[0]"
assert s.count(old) == 1
s = s.replace(old, "  tw = NUT_TRAP[0]\n  slot = uvz(PUSH_NUT_U[0]")
open(p, "w").write(s)
p = "rightcheck.py"
s = open(p).read()
s = s.replace("from cadlib import box, cyl, cyl_y, hex_prism_z, revolve", "from cadlib import box, cyl, hex_prism_z, revolve")
open(p, "w").write(s)
p = "visuals.py"
s = open(p).read()
old = """                 f"OUT: push bolt loosened, motor slid down until the carrier sits on the tower ({-RA.DZ_OUT:.0f} mm; "
                 "6 is enough), tightened","""
assert s.count(old) == 1
s = s.replace(old, """                 (f"OUT: push bolt loosened, motor slid down until the carrier sits on the tower ({-RA.DZ_OUT:.0f} mm; "
                  "6 is enough), tightened"),""")
open(p, "w").write(s)
EOF
/home/claude/bin/ruff check rightarm.py rightcheck.py visuals.py && cat /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fork/push_fork.sh | head -80
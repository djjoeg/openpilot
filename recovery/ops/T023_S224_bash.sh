python3 - << 'EOF'
p = "mountparts.py"
s = open(p).read()
s = s.replace("  stop_bar = extrude_x(bar, -lx1, lx1)\n", "  bar_part = extrude_x(bar, -lx1, lx1)\n")
s = s.replace("  part = part + stop_bar\n", "  part = part + bar_part\n")
open(p, "w").write(s)
EOF
grep -n "bar_part\|stop_bar" mountparts.py; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  "
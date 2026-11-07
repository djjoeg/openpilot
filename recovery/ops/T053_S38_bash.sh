python3 - <<'EOF'
p = "accord_lka_parts.py"
s = open(p).read()
old = '''It checks that every part is one closed solid that fits the print bed; that the gears mesh without touching through
the whole range of the teeth; that nothing touches anything it shouldn't with the lift lever down, up and at every
angle between, and with the steering wheel turned past the teeth; and which dash clamp positions the parts can reach.
It exits with an error if any check fails.'''
new = '''It checks that every part is one closed solid that fits the print bed; that the gears mesh without touching through
the whole range of the teeth; that nothing touches anything it shouldn't (the dash cover, the dash clamp and the bought
screws and bolts included) with the lift lever down, up and at every angle between, with the steering wheel turned
past the teeth either way, and with the setup gauge in place; that every bolt and screw is the right length; and which
dash clamp positions the parts can reach. It exits with an error if any check fails.'''
assert s.count(old) == 1, "docstring"
s = s.replace(old, new)
open(p, "w").write(s)
EOF
md5sum ../stl/*.stl ../stl/arms/*.stl > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/stl_md5_before2.txt; time PYTHONPATH=/home/claude/pylib python3 accord_lka_parts.py > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fitaudit/build.log 2>&1; echo "exit $?"; tail -3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fitaudit/build.log; cd .. && md5sum -c --quiet /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/stl_md5_before2.txt && echo "STL files unchanged"; sed -n '/^BOLTS AND SCREWS/,/^$/p;/clearance checks/p' report/parts_report.txt
cd /home/claude/deliver/hardware/cad && sed -n 42,45p mountparts.py && python3 - <<'EOF'
p = "mountparts.py"
s = open(p).read()
old = "from params import (ARM_SLIDE, ARM_T, ARM_W, CLAMP_DEPTH, HOOD_EDGE_MAX, M3_CLEAR, M3_PILOT, M4_CLEAR,"
assert s.count(old) == 1
s = s.replace(old, "from params import (ARM_SLIDE, ARM_T, ARM_W, CLAMP_DEPTH, HOOD_EDGE_MAX, HOOD_EDGE_MIN, M3_CLEAR, M3_PILOT, M4_CLEAR,")
open(p, "w").write(s)
EOF
md5sum -c --quiet /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/stl_md5_before2.txt && echo "STLs intact before rebuild"; time PYTHONPATH=/home/claude/pylib python3 accord_lka_parts.py > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fitaudit/build.log 2>&1; echo "exit $?"; tail -3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fitaudit/build.log; md5sum -c --quiet /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/stl_md5_before2.txt && echo "STL files unchanged"; sed -n '/^BOLTS AND SCREWS/,/^$/p;/clearance checks/p' ../report/parts_report.txt
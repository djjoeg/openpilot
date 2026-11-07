R=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/regress; cp $R/report/parts_report.txt /home/claude/deliver/hardware/report/parts_report.txt && cd /home/claude/deliver && python3 - <<'EOF'
p = "CHANGELOG.md"
s = open(p).read()
old = "| the other mounts, rebuilt from the CAD files | REGRESSION_RESULT |"
new = ("| the other mounts, rebuilt from the CAD files | all their checks pass; their 50 STL files the same byte for byte; "
       "their report the same but one wording (the right-side mount's screw \"behind the front face of the grip\"), "
       "updated in `parts_report.txt` |")
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w").write(s)
EOF
grep -n "the other mounts, rebuilt" CHANGELOG.md
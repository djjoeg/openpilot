python3 - <<'EOF'
p = "rightarm.py"
s = open(p, encoding="utf-8").read()
a = """20 wide, the arm's groove in the wall on your side (v4's pinch bolt was on the dash side, which the photo estimates
put within a few millimetres of the dash). Once the car shows where they sit, a later print can have shorter
slides."""
b = """20 wide, the arm's groove in the wall on your side (v4's pinch bolt was on the dash side, where the photo estimates
put its wings in the dash), its labels cut in. Once the car shows where they sit, a later print can have shorter
slides."""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
ruff check rightarm.py | tail -1; tail -3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/stiff3.txt
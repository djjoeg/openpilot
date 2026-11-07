python3 - <<'EOF'
p = "sidebuild.py"
s = open(p).read()
a = s.index("def questions() -> list:")
b = s.index("def support_area(")
block = s[a:b]
lines = block.split("\n")
out = []
# each list item starts at an indented line beginning with f" or " at 4 spaces and ends with a line ending in '",'
in_item = False
for ln in lines:
  st = ln.strip()
  if ln.startswith("    ") and not ln.startswith("     ") and (st.startswith('f"') or st.startswith('"')):
    if not in_item:
      ln = "    (" + ln[4:]
      in_item = True
    else:
      ln = "     " + ln[4:]
    if st.endswith('",'):
      ln = ln[:-1] + "),"
      in_item = False
  out.append(ln)
s = s[:a] + "\n".join(out) + s[b:]
open(p, "w").write(s)
EOF
sed -n 63,85p sidebuild.py; /home/claude/bin/ruff check --output-format concise --line-length 140 --fix --select I001 sidebuild.py; /home/claude/bin/ruff check --output-format concise --line-length 140 sideparts.py sideassembly.py sidebuild.py; echo "exit $?"
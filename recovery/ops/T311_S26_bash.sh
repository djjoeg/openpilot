python3 - <<'EOF'
import re
p='viewer3d.py'; s=open(p).read()
# STEPS: wrap each multi-line string in parentheses
start = s.index("STEPS = [\n") + len("STEPS = [\n"); end = s.index("]\n", start)
body = s[start:end]
items = [b for b in body.split('",\n') if b.strip()]
new = []
for b in items:
  b = b.rstrip()
  if not b.endswith('"'): b += '"'
  lines = b.split("\n")
  lines = [l.strip() for l in lines]
  new.append("  (" + ("\n   ".join(lines)) + "),")
s = s[:start] + "\n".join(new) + "\n" + s[end:]
open(p,'w').write(s)
EOF
sed -n 50,75p viewer3d.py
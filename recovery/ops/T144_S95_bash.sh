cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && python3 - <<'EOF'
s = open('sfm.py').read()
old = """groups = {}
for x in list(parent.keys()):
    groups.setdefault(find(x), []).append(x)"""
new = """nodes = set()
for (a, b), (mm, Fm, n) in pairs.items():
    nodes.update((a, int(q)) for q in mm[:, 0])
    nodes.update((b, int(t)) for t in mm[:, 1])
groups = {}
for x in nodes:
    groups.setdefault(find(x), []).append(x)"""
assert old in s
s = s.replace(old, new)
open('sfm.py', 'w').write(s)
EOF
timeout 2400 python3 sfm.py 2>&1 | tail -80
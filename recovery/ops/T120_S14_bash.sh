cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/mockup && python3 - <<'EOF'
p='export.py'
s=open(p).read()
n = s.count("if cs.area() < 0:")
s = s.replace("if cs.area() < 0:", "if cs.area() < 1e-9:")
print(n)
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 1500 python3 export.py . 2>&1 | tail -40; ls -la
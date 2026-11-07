python3 - <<'EOF'
p = 'plates.py'
s = open(p, encoding='utf-8').read()
old = '  ax2 = fig.add_axes([0.48, 0.03, 0.51, 0.90])\n'
new = '  ax2 = fig.add_axes([0.48, 0.03, 0.51, 0.85])           # its title clear of the plate\'s title\n'
assert s.count(old) == 1
open(p, 'w', encoding='utf-8').write(s.replace(old, new))
EOF
sha() { sha256sum ../stl/right-arm/*.stl ../stl/mid-teeth/*.stl | sort -k2; }
sha > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/stl-before.sha
echo saved
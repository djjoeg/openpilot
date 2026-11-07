cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fea && python3 - <<'EOF'
s = open('armfea_full.py').read()
old = "    screws = ((RA.CUP_X, RA.CUP_Z), (RA.CUP_X - 85.0, RA.CUP_Z + 40.0))"
new = "    screws = ((RA.CUP_X, RA.CUP_Z), (RA.CUP_X - 97.0, RA.CUP_Z + 40.0))     # the cup slot; slot 1's wheel end"
assert s.count(old) == 1
open('armfea_full.py', 'w').write(s.replace(old, new))
print('ok')
EOF
cat /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fea/aligned125.log
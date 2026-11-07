cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fea && python3 - <<'EOF'
s = open('armfea_v.py').read()
s2 = open('armfea_diag.py').read()
# carry the variant code into the diagnostic script
start = s.index('VARIANT = ')
end = s.index('def voxelize')
d0 = s2.index('def solid_model')
d1 = s2.index('def voxelize')
s2 = s2[:d0] + s[start:end] + s2[d1:]
open('armfea_diag.py', 'w').write(s2)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 armfea_diag.py 2.0 1800 deep50 2>&1 | grep -E "turned|left|right"
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fea && python3 - <<'EOF'
s = open('armfea.py').read()
old = '''    m = m + web
  return m
'''
new = '''    m = m + web
  if "flange" in variant:
    # a 3 mm flange under the motor, from the carrier's plate back to the bar's outer face
    m = m + RA.uvz(RA.PLATE_U[0], RA.BAR_U[1], RA.BAR_V[0], RA.PLATE_V[1], RA.WEB_Z0, RA.PLATE_Z[0])
  return m
'''
assert s.count(old) == 1
s = s.replace(old, new)
open('armfea.py', 'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 armfea.py 2.0 1800 deep50flange 2>&1 | grep -E "voxels|left|right"; echo ---; PYTHONPATH=/home/claude/pylib timeout 1500 python3 armfea.py 1.5 1800 v4 2>&1 | grep -E "voxels|dof|left|right|factorized"
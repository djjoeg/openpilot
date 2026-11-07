cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fea && python3 - <<'EOF'
s = open('armfea.py').read()
old = '''  bb = m.bounding_box()
  lo = np.array(bb[:3]) - h
  hi = np.array(bb[3:]) + h'''
new = '''  bb = m.bounding_box()
  lo = np.array(bb[:3]) - h
  hi = np.array(bb[3:]) + h
  # grid planes on the arm bar's faces (x 120 the receiver's mouth, y -143, z -175.2), so its 10 x 30 section is exact
  ref = np.array([120.0, -143.0, RA.ARM_Z[0]])
  lo = ref - np.ceil((ref - lo) / h) * h'''
assert s.count(old) == 1
s = s.replace(old, new)
open('armfea.py', 'w').write(s)
EOF
(for v in v4 deep50flange; do echo "== $v"; PYTHONPATH=/home/claude/pylib timeout 3000 python3 armfea.py 1.25 1800 $v cg 2>&1 | grep -E "voxels|^left|^right"; done) > aligned125.log 2>&1; cat aligned125.log
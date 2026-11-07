cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "faceparts.py"
s = open(p).read()
old = """  c = 1.0
  outer = revolve([(FACE_BAND[1] - c, t.z_tip - 0.5), (FACE_BAND[1] + 0.5, t.z_tip - 0.5), (FACE_BAND[1] + 0.5, t.z_tip + c + 0.5)],
                  a0, a1)
  inner = revolve([(FACE_BAND[0] + c, t.z_tip - 0.5), (FACE_BAND[0] - 0.5, t.z_tip - 0.5), (FACE_BAND[0] - 0.5, t.z_tip + c + 0.5)],
                  a0, a1)"""
new = """  c = 1.5
  outer = revolve([(FACE_BAND[1] - c - 0.5, t.z_tip - 0.5), (FACE_BAND[1] + 0.5, t.z_tip - 0.5), (FACE_BAND[1] + 0.5, t.z_tip + c + 0.5)],
                  a0, a1)
  inner = revolve([(FACE_BAND[0] + c + 0.5, t.z_tip - 0.5), (FACE_BAND[0] - 0.5, t.z_tip - 0.5), (FACE_BAND[0] - 0.5, t.z_tip + c + 0.5)],
                  a0, a1)"""
assert old in s
s = s.replace(old, new)
s = s.replace('"""The teeth\'s tips cut back 45 degrees at their inner and outer ends, 1 mm: lifting', '"""The teeth\'s tips cut back 45 degrees at their inner and outer ends, 1.5 mm: lifting')
old2 = "  r_split = ROLL_BAND[0] + 1.5\n"
new2 = "  r_split = ROLL_BAND[0] + 2.2      # dropped, the gear's teeth reach out to 175.8 mm; the roller rides outside that\n"
assert old2 in s
s = s.replace(old2, new2)
open(p, "w").write(s)
print("ok")
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && PYTHONPATH=/home/claude/pylib timeout 3000 python3 assy_test.py 2>&1 | tail -8
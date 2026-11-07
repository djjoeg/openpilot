cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = 'incar.py'
s = open(p).read()
old = "  out += CP.motor_parts(0.0)\n"
new = "  out += motor_parts()\n"
assert old in s
s = s.replace(old, new)
anchor = "def cable() -> list:"
add = '''MOTOR = PR.Mat((0.018, 0.018, 0.020), spec=0.12, shine=40)                     # the motor: black caps, black body
STAINLESS = PR.Mat((0.50, 0.50, 0.52), spec=0.6, shine=80)


def motor_parts() -> list:
  """The NEMA 17 (17HS15-1504S-X1, as in its listing: black end caps and body, the front face bare aluminium against
  the carrier), the four stainless M3 button heads on the carrier's pads, and the board on its back (a generic
  board: its parts are placeholders)."""
  out = []
  for m, mat in CP.motor_parts(0.0):
    if mat is CP.ALU or mat is CP.MOTOR_BLACK:
      out.append((m, MOTOR))
    elif mat is CP.STEEL:
      out.append((m, STAINLESS))
    else:
      out.append((m, mat))
  return out


'''
s = s.replace(anchor, add + anchor)
open(p, 'w').write(s)
print('ok')
EOF
grep -n "ALU\|MOTOR_BLACK\|STEEL" carphoto.py | head
cd /home/claude/deliver/hardware/cad && python3 - << 'EOF'
p = "assembly.py"
s = open(p).read()
a = """  def motor(self, lift=0.0):
    body = box(-NEMA / 2, NEMA / 2, -NEMA / 2, NEMA / 2, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
    board = box(-NEMA / 2, NEMA / 2, -NEMA / 2, NEMA / 2, -NEMA_LEN - 10.0, -NEMA_LEN)   # StepperServoCAN board + cover
    return self._carried(body + board, lift)"""
b = """  def motor(self, lift=0.0):
    \"\"\"The motor, the StepperServoCAN board on its back (side wings broken off: 42 mm square, parts up to 12 mm tall
    on its back), the board's plugs (car plug below, motor and debug plugs at the sides: the board's edge without a
    plug faces up), and the motor's own cable plug facing down.\"\"\"
    h = NEMA / 2
    body = box(-h, h, -h, h, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
    board = box(-h, h, -h, h, -NEMA_LEN - 14.0, -NEMA_LEN)
    plugs = box(-6, 6, -h - 14, -h, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0) + \\
      box(h, h + 14, -6, 6, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0) + box(-h - 14, -h, -6, 6, -NEMA_LEN - 12.0, -NEMA_LEN - 3.0)
    motor_plug = box(-8, 8, -h - 12, -h, -NEMA_LEN + 2.0, -NEMA_LEN + 18.0)
    return self._carried(body + board + plugs + motor_plug, lift)"""
assert a in s; s = s.replace(a, b); open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  " | tail -6
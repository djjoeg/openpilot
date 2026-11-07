cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "margins.py"
s = open(p).read()
old = """WIRE_20AWG_A = 7.5       # 20 AWG copper in a bundle, a common rating
MOTOR_FUSE_A, COMMA_FUSE_A = 5.0, 3.0
COMMA_MOST_A = 1.3       # the comma device's most draw at 12 V: an estimate, comma doesn't publish it
"""
new = """WIRE_20AWG_A = 7.5       # 20 AWG copper in a bundle, a common rating
MOTOR_FUSE_A = 5.0       # the fuse in the 12 V socket plug that feeds the relay and the motor
SOCKET_A = 10.0          # the car's accessory power sockets: 120 W (10 A) each, 2008-12 Accord owner's manual
"""
assert old in s; s = s.replace(old, new)
old = """  board_a = (P.BOARD_MAX_A ** 2 * P.MOTOR_OHM + 1.0) / 12.0
  rows.append(row(g, "The motor's 5 A fuse doesn't blow in use", f"{board_a:.1f} A: the motor board at the most current it "
                  "gives", f"{MOTOR_FUSE_A:.0f} A", MOTOR_FUSE_A / board_a, "calculated"))
  rows.append(row(g, "The fuses protect the wires", f"{MOTOR_FUSE_A:.0f} A: the larger fuse", f"{WIRE_20AWG_A} A: 20 AWG wire",
                  WIRE_20AWG_A / MOTOR_FUSE_A, "wire rating"))
  rows.append(row(g, "The comma device's 3 A fuse doesn't blow in use", f"{COMMA_MOST_A} A: the comma device's most draw",
                  f"{COMMA_FUSE_A:.0f} A", COMMA_FUSE_A / COMMA_MOST_A, "estimated (comma doesn't publish it)"))
"""
new = """  board_a = (P.BOARD_MAX_A ** 2 * P.MOTOR_OHM + 1.0) / 12.0
  rows.append(row(g, "The socket plug's 5 A fuse doesn't blow in use", f"{board_a:.1f} A: the motor board at the most current "
                  "it gives", f"{MOTOR_FUSE_A:.0f} A", MOTOR_FUSE_A / board_a, "calculated"))
  rows.append(row(g, "The fuse protects the wires", f"{MOTOR_FUSE_A:.0f} A: the socket plug's fuse", f"{WIRE_20AWG_A} A: 20 AWG "
                  "wire, the thinnest in the build", WIRE_20AWG_A / MOTOR_FUSE_A, "wire rating"))
  rows.append(row(g, "The car's accessory power socket carries the motor", f"{board_a:.1f} A (as above)",
                  f"{SOCKET_A:.0f} A: the socket's rating in the owner's manual", SOCKET_A / board_a, "owner's manual; calculated",
                  note="the comma device is powered from the OBD port through comma power, with its own fuse"))
"""
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
print("ok")
EOF
grep -n "COMMA_FUSE\|COMMA_MOST" *.py
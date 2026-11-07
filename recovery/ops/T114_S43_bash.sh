cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='margins.py'
s=open(p).read()
old='''SOCKET_A = 10.0          # the car's accessory power sockets: 120 W (10 A) each, 2008-12 Accord owner's manual'''
new='''SOCKET_A = 10.0          # the car's accessory power sockets: 120 W (10 A) each, 2008-12 Accord owner's manual
DEVICE_A = 1.5           # the comma device at 12 V, stand-alone fed through the socket plug too: an estimate on the high
                         # side (comma doesn't publish its draw)'''
assert old in s; s=s.replace(old,new)
old='''  board_a = (P.BOARD_MAX_A ** 2 * P.MOTOR_OHM + 1.0) / 12.0
  rows.append(row(g, "The socket plug's 5 A fuse doesn't blow in use", f"{board_a:.1f} A: the motor board at the most current "
                  "it gives", f"{MOTOR_FUSE_A:.0f} A", MOTOR_FUSE_A / board_a, "calculated"))
  rows.append(row(g, "The fuse protects the wires", f"{MOTOR_FUSE_A:.0f} A: the socket plug's fuse", f"{WIRE_20AWG_A} A: 20 AWG "
                  "wire, the thinnest in the build", WIRE_20AWG_A / MOTOR_FUSE_A, "wire rating"))
  rows.append(row(g, "The car's accessory power socket carries the motor", f"{board_a:.1f} A (as above)",
                  f"{SOCKET_A:.0f} A: the socket's rating in the owner's manual", SOCKET_A / board_a, "owner's manual; calculated",
                  note="the comma device is powered from the OBD port through comma power, with its own fuse"))'''
new='''  board_a = (P.BOARD_MAX_A ** 2 * P.MOTOR_OHM + 1.0) / 12.0
  total_a = board_a + DEVICE_A      # stand-alone (the default): the socket plug feeds the comma device too
  rows.append(row(g, "The socket plug's 5 A fuse doesn't blow in use", f"{total_a:.1f} A: the motor board at the most current "
                  f"it gives ({board_a:.1f} A) and the comma device ({DEVICE_A:.1f} A, an estimate on the high side)",
                  f"{MOTOR_FUSE_A:.0f} A", MOTOR_FUSE_A / total_a, "calculated; the comma device's draw estimated",
                  note="connected to the car (car_network) the comma device is fed from the OBD port instead: "
                       f"{MOTOR_FUSE_A / board_a:.2f}"))
  rows.append(row(g, "The fuse protects the wires", f"{MOTOR_FUSE_A:.0f} A: the socket plug's fuse", f"{WIRE_20AWG_A} A: 20 AWG "
                  "wire, the thinnest in the build", WIRE_20AWG_A / MOTOR_FUSE_A, "wire rating"))
  rows.append(row(g, "The car's accessory power socket carries the motor and the comma device", f"{total_a:.1f} A (as above)",
                  f"{SOCKET_A:.0f} A: the socket's rating in the owner's manual", SOCKET_A / total_a, "owner's manual; calculated"))'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s)
EOF
ruff check --select E,F,W --line-length 140 margins.py | tail -1
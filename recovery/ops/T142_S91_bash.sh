cp popparts.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/popparts_before_u.py && cp popassembly.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/popassembly_before_u.py && python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('''MOUNT_DEG = -7.5          # the motor at about 3:15: the most room between the wiper stalk pushed down and the key''',
'''MOUNT_DEG = -10.0         # the motor at about 3:20: between the wiper stalk pushed all the way down (3 notches, taken as
                          # 36 degrees until measured) and the key
MOUNT_ADJ = 6.0           # the whole mount (back teeth, motor and hinge block) can be set this many degrees either way
                          # when fitting it (about 3:08 to 3:32): the hinge block's slots and the back teeth's notch over
                          # the spoke allow it, so the stalk and the key can be cleared in the car''')
rep('''SPOKE_CLEAR = 5.0             # the motor's side towards you stays this far behind the spokes' back face''',
'''SPOKE_CLEAR = 8.0             # the motor's side towards you stays this far behind the spokes' back face (5, plus 3 because
                              # the spokes' depth is read off photos)''')
rep('''Z_AXIS_P = math.floor((SPOKE_BACK_Z - NEMA / 2 - SPOKE_CLEAR) * 2.0) / 2.0     # -56.5: the motor's axis''',
'''Z_AXIS_P = math.floor((SPOKE_BACK_Z - NEMA / 2 - SPOKE_CLEAR) * 2.0) / 2.0     # -59.5: the motor's axis''')
# the notch over the spoke allows the mount's adjustment
rep('''    self.spoke = (spoke_deg[0] - mount_deg - FP.SPOKE_ROOM_DEG, spoke_deg[1] - mount_deg + FP.SPOKE_ROOM_DEG)''',
'''    self.spoke = (spoke_deg[0] - mount_deg - FP.SPOKE_ROOM_DEG - MOUNT_ADJ,
                  spoke_deg[1] - mount_deg + FP.SPOKE_ROOM_DEG + MOUNT_ADJ)''')
p.write_text(s)
print("ok")
EOF
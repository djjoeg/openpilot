python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)
rep('''MOUNT_ADJ = 6.0           # the whole mount (back teeth, motor and hinge block) can be set this many degrees either way
                          # when fitting it (about 3:08 to 3:32): the hinge block's slots and the back teeth's notch over
                          # the spoke allow it, so the stalk and the key can be cleared in the car''',
'''MOUNT_ADJ = (3.0, 6.0)    # the whole mount (back teeth, motor and hinge block) can be turned this many degrees down
                          # (towards the key) and up (towards the stalk) when fitting it: about 3:26 to 3:08. The hinge
                          # block's slots and the back teeth's notch over the spoke allow it, so the stalk and the key
                          # can be cleared in the car. (Further down the key is in the way.)''')
rep('''    self.spoke = (spoke_deg[0] - mount_deg - FP.SPOKE_ROOM_DEG - MOUNT_ADJ,
                  spoke_deg[1] - mount_deg + FP.SPOKE_ROOM_DEG + MOUNT_ADJ)''',
'''    self.spoke = (spoke_deg[0] - mount_deg - FP.SPOKE_ROOM_DEG - MOUNT_ADJ[1],
                  spoke_deg[1] - mount_deg + FP.SPOKE_ROOM_DEG + MOUNT_ADJ[0])''')
p.write_text(s)
for f in ["/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/run_u.py",
          "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/popmock/pop_export.py"]:
    q = pathlib.Path(f)
    t = q.read_text()
    t = t.replace('_adj{PP.MOUNT_ADJ:.0f}', '_adj{PP.MOUNT_ADJ[0]:.0f}{PP.MOUNT_ADJ[1]:.0f}')
    t = t.replace('  for m in (PP.MOUNT_DEG - PP.MOUNT_ADJ, PP.MOUNT_DEG, PP.MOUNT_DEG + PP.MOUNT_ADJ):',
                  '  for m in (PP.MOUNT_DEG - PP.MOUNT_ADJ[0], PP.MOUNT_DEG, PP.MOUNT_DEG + PP.MOUNT_ADJ[1]):')
    t = t.replace('  for adj in (-PP.MOUNT_ADJ, PP.MOUNT_ADJ):', '  for adj in (-PP.MOUNT_ADJ[0], PP.MOUNT_ADJ[1]):')
    t = t.replace('"mount_adj": PP.MOUNT_ADJ,', '"mount_adj": list(PP.MOUNT_ADJ),')
    q.write_text(t)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 3000 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/run_u.py --quick 2>&1 | grep -v "^   {\|switch:" | tail -30
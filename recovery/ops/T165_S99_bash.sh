python3 - <<'EOF'
import pathlib
p = pathlib.Path("sidebuild.py")
s = p.read_text()

def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)

rep('''       "push the lever in along the slot, and pull it into the notch at the inner end to park it. The power switch is on",
       "only with the motor all the way out on the teeth.", ""]''',
    '''       "push the lever in along the slot. The power switch is on only with the motor all the way out on the teeth.",
       "The notch at the slot's inner end is for a broken spring: without the spring, the motor's own weight slides it back",
       "out onto the teeth; with the lever in that notch, the weight holds it in instead.", ""]''')
rep('''f"inside edge at 5:20 (it is {e['motor_in_now']} mm in now).''',
    '''f"inside edge at 5:20 ({e['motor_in_now']} mm with the motor out on the teeth).''')
p.write_text(s)
print("ok")
EOF
cd /home/claude/deliver/hardware/cad && (time PYTHONPATH=/home/claude/pylib python3 sidebuild.py > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/build6.log 2>&1; echo "exit $?" >> /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/build6.log) 2>> /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/build6.log &
echo started
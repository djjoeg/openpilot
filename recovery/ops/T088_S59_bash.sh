python3 - <<'EOF'
p='margins.py'; s=open(p).read()
old='''                  check="with the lift lever up, push the motor sideways by hand as hard as you can (about 10 kg, 1.8 times the "
                        "motor's most push): the clamp must not move on the covers. On an oval cover the V's shape helps too",'''
new='''                  check="proof pull: with the lift lever up, pull the motor sideways with a luggage scale to 5 kg (1.8 times the "
                        "motor's most push), each way: the clamp must not move on the covers. On an oval cover the V's shape helps too",'''
assert old in s; s=s.replace(old,new); open(p,'w').write(s); print("ok")
EOF
cd /home/claude/deliver/hardware/cad && (PYTHONPATH=/home/claude/pylib python3 accord_lka_parts.py > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/rebuild_col3.log 2>&1; echo "exit $?" >> /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/rebuild_col3.log) &
echo started
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && python3 - <<'EOF'
p='study90.py'
s=open(p).read()
s=s.replace('''         "wiper stalk": sc.stalk()}''','''         "wiper stalk": sc.stalk(), "adjustment tab, its swing, fingers": sc.moved(PA.tab_lever_sweep())}''')
open(p,'w').write(s)
EOF
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache
for m in -70 -73 -76 -79 -82 -85; do (timeout 1500 python3 study90.py radial:car $m 97,103,106,110,115,120 0 6 > rc_0_$m.txt 2>&1 &); (timeout 1500 python3 study90.py radial:car $m 97,103,106,110,115,120 20 6.4 > rc_20_$m.txt 2>&1 &); done; sleep 3; ps aux | grep -c "[s]tudy90"
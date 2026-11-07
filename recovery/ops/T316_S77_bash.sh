python3 - <<'EOF'
p='rightarm.py'; s=open(p).read()
a='''                 plate_list=[("plate-12-right-arm", "12 right arm v3", list(parts),
                              "Plate 12: the right arm mount v3: the arm (with its tower) and the motor carrier")])'''
assert a in s
s=s.replace(a,'''                 plate_list=[("plate-12-right-arm", "12 right arm v4", list(parts),
                              "Plate 12: the right arm mount v4: the arm (its tower a closed tube) and the motor carrier")])''')
open(p,'w').write(s)
EOF
grep -n "Right arm mount v3\|right arm mount v3\|v3 on the frame plate" rightarm.py | head; export PYTHONPATH=/home/claude/pylib && time timeout 900 python3 rightarm.py 2>&1 | tail -8 && time timeout 600 python3 allinone.py 2>&1 | tail -12
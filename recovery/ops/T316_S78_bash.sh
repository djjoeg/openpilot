python3 - <<'EOF'
p='rightarm.py'; s=open(p).read()
a='''         suptitle="Right arm mount v3 on the frame plate v4: the motor outside the rim at 4 o'clock, shaft pointing in. "'''
assert a in s
s=s.replace(a,'''         suptitle="Right arm mount v4 on the frame plate v4: the motor outside the rim just above 4 o'clock, shaft pointing in. "''')
open(p,'w').write(s)
EOF
export PYTHONPATH=/home/claude/pylib && timeout 600 python3 -c "
import rightarm as RA, os
RA.picture(os.path.join(RA.REPORT_DIR, 'right-arm.png'))
" && time timeout 1500 python3 visuals.py 2>&1 | tail -5
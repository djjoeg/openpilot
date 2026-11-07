python3 - <<'EOF'
p='rightcheck.py'; s=open(p).read()
a='''  out["stop bolt"] = hex_prism_z(7.0, under - 2.8, under + 0.01, x=sx, y=sy, rot=RA.THETA) + \\
    cyl(1.95, under, under + 30.0, x=sx, y=sy, segments=20)'''
assert a in s
s=s.replace(a,'''  out["stop bolt"] = hex_prism_z(7.0, under - 2.8, under, x=sx, y=sy, rot=RA.THETA) + \\
    cyl(1.95, under - 0.5, under + 30.0, x=sx, y=sy, segments=20)''')
open(p,'w').write(s)
EOF
export PYTHONPATH=/home/claude/pylib && (time timeout 3000 python3 rightcheck.py > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v3d/rightcheck.log 2>&1; echo "exit $?" >> /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v3d/rightcheck.log)
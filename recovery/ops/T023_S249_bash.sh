python3 - << 'EOF'
p = "mountparts.py"
s = open(p).read()
a = """  rise = tip[0] - TOP_Y[1] + 0.5
  knuckle = knuckle + prism_x([(TOP_Y[1] - 0.5, tip[1] - 0.01), (tip[0], tip[1] - 0.01),
                               (TOP_Y[1] - 0.5, tip[1] + 1.2 * rise)], -CARRIER_KNUCKLE, CARRIER_KNUCKLE)"""
b = """  rise = tip[0] - TOP_Y[1] + 0.5
  knuckle = knuckle + prism_x([(TOP_Y[1] - 0.5, hz + kr - 0.01), (tip[0], hz + kr - 0.01), tip,
                               (TOP_Y[1] - 0.5, tip[1] + 1.2 * rise)], -CARRIER_KNUCKLE, CARRIER_KNUCKLE)"""
assert a in s; s = s.replace(a, b); open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  " | tail -3; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/overhang_where.py 2>&1 | sed -n '/carrier/,/clamp/p' | awk '$NF+0 > 0 || /total/' | grep -v "z     6" | head
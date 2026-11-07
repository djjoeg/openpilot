python3 - << 'EOF'
p = "wheelparts.py"
s = open(p).read()
a = """  roller = cyl(ROLLER_R, zr0, zr1 + 0.01, segments=360)
  core = roller
  # turn the gear so a tooth gap faces +y, where the set screw goes in and the shaft's flat faces
  part = (teeth + roller + core).rotate((0, 0, MOTOR_GEAR_PHASE))"""
b = """  roller = cyl(ROLLER_R, zr0, zr1 + 0.01, segments=360)
  # turn the gear so a tooth gap faces +y, where the set screw goes in and the shaft's flat faces
  part = (teeth + roller).rotate((0, 0, MOTOR_GEAR_PHASE))"""
assert a in s; s = s.replace(a, b); open(p, "w").write(s)
EOF
grep -n "rf = rp" wheelparts.py; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  " | tail -5; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/margin.py; PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork')
exec(open('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/overhang.py').read().split('t = WP.Teeth()')[0])
import wheelparts as WP
t = WP.Teeth()
for name, m in {'gear': WP.motor_gear(), 'teeth one piece': WP.teeth_one_piece(t), 'left half': WP.teeth_half(t, 'left')}.items():
  for r in [(0,0,0), (180,0,0)]:
    s, b, size = support_area(m, r); print(name, r, round(s), [round(x) for x in size])
"
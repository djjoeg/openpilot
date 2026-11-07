python3 - << 'EOF'
p = "wheelparts.py"
s = open(p).read()
a = """      (self.r_roll, zr0),                           # rolling band (the motor gear's roller rides here)
      (self.r_roll, zr1),
      (self.r_root, zr1),                           # step up to the teeth's root"""
b = """      (self.r_roll, zr0),                           # rolling band (the motor gear's roller rides here)
      (self.r_roll, zr1 - max(0.0, self.r_roll - self.r_root)),
      (self.r_root, zr1),                           # 45 degree slope down to the teeth's root (prints without supports)"""
assert a in s; s = s.replace(a, b); open(p, "w").write(s)
p = "params.py"
s = open(p).read()
a = "Z_ROLL = (-3.5, 4.5)          # rolling band on the steering wheel teeth"
b = "Z_ROLL = (-3.5, 4.5)          # rolling band on the steering wheel teeth (flat for the first 5.2 mm, then sloping down)"
assert a in s; s = s.replace(a, b); open(p, "w").write(s)
p = "mountparts.py"
s = open(p).read()
a = "LIFT_DEG = 10.0         # lift lever up: the motor gear clears the steering wheel teeth by about 4 mm"
b = "LIFT_DEG = 8.0          # lift lever up: the motor gear clears the steering wheel teeth by about 5 mm"
assert a in s; s = s.replace(a, b); open(p, "w").write(s)
EOF
grep -n "def tooth_fit_test" -A 12 wheelparts.py | grep "pts ="; PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork')
exec(open('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/overhang.py').read().split('t = WP.Teeth()')[0])
import wheelparts as WP
t = WP.Teeth()
for name, m in {'teeth one piece': WP.teeth_one_piece(t), 'left half': WP.teeth_half(t, 'left'), 'right half': WP.teeth_half(t, 'right'), 'tooth test': WP.tooth_fit_test(t), 'grip test': WP.grip_fit_test(t)}.items():
  s, b, size = support_area(m, (180,0,0)); print(name, round(s), [round(x) for x in size])
"
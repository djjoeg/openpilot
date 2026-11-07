python3 - <<'EOF'
p = "mountparts.py"
s = open(p).read()
old = '''    a0, a1 = ARM_ANGLES
    pts = [(py, pz)]
    for a in np.linspace(-a1, -a0, 41):        # angle above level; z points towards the driver'''
new = '''    a0, a1 = ARM_ANGLES[0] - 15.0, ARM_ANGLES[1] + 15.0    # past the slot's ends so the plate stays in one piece
    pts = [(py, pz)]
    for a in np.linspace(-a1, -a0, 41):        # angle above level; z points towards the driver'''
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
EOF
export PYTHONPATH=/home/claude/pylib:. && timeout 900 python3 -c "
import mountparts as MP, render as R, numpy as np
c = MP.dash_clamp(); print('clamp', c.status(), round(c.volume()/1000,2), c.genus(), len(c.decompose()))
out='/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/prev/'
K=(0.6,0.6,0.65)
side = R.look([1,0,0],[0,1,0]); iso = R.look([1,0.8,1.2],[0,1,0]); iso2 = R.look([-1,0.6,-1.0],[0,1,0])
for name, fn in (('carrier', MP.motor_carrier), ('hinge_block', MP.hinge_block), ('lever', MP.lift_lever), ('slider', MP.arm_slider), ('arm', MP.arm), ('clamp', MP.dash_clamp)):
  m = fn()
  R.save(out+f'n_{name}.png', [([(m,K)], side), ([(m,K)], iso), ([(m,K)], iso2)], titles=['side (+x)','iso front','iso back'], size=(600,520))
print('ok')
"

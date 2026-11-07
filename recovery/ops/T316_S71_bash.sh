grep -n "foot = Manifold.batch_hull" -A 3 rightarm.py && python3 - <<'EOF'
p='rightarm.py'; s=open(p).read()
a='''  foot = Manifold.batch_hull([box(ARM_X[1] - 5.0, ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1]),
                              uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], ARM_Z[0], ARM_Z[1])])'''
assert a in s
s=s.replace(a,'''  foot = Manifold.batch_hull([box(ARM_X[1] - 5.0, ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1]),
                              uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], ARM_Z[0], ARM_Z[1])])
  foot = foot ^ box(ARM_X[0], 400.0, -400.0, ARM_Y[1], ARM_Z[0] - 1.0, ARM_Z[1] + 1.0)   # no higher than the arm (v4: the
                                                 # tower's top corner now stands above it; slid in, it would meet the plate)''')
open(p,'w').write(s)
EOF
export PYTHONPATH=/home/claude/pylib && timeout 300 python3 -c "
import rightarm as RA
plate = RA.plate_to_wheel(RA.frame_plate_v4()); a = RA.arm()
print('arm genus', a.genus(), 'g', round(a.volume()/1000*1.28,1))
for dx in (-25,-24,-22,-20,-10,0,10,20,25): print(dx, round((a.translate((dx,0,0)) ^ plate).volume(),2))
"
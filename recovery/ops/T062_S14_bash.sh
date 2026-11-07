grep -n "LEG_SLOT_Z = " mountparts.py && python3 - <<'EOF'
p='mountparts.py'
s=open(p).read()
old='LEG_SLOT_Z = (BR_LEG_Z[0] - 2.6, BR_LEG_Z[1] + 1.5)\n'
new=('_LEG_REACH = HB_TOP + 1.0 - HINGE[0]   # the highest point of a leg inside the hinge block, above the hinge axis\n'
     'LEG_SLOT_Z = (BR_LEG_Z[0] - _LEG_REACH * math.sin(math.radians(10.0)) - 0.35,   # lifted 10 degrees (the most is 9)\n'
     '              BR_LEG_Z[1] + _LEG_REACH * math.sin(math.radians(4.0)) + 0.55)    # dropped 4 degrees (the most is 3)\n')
assert old in s; s=s.replace(old,new,1)
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import mountparts as MP
print('LEG_SLOT_Z', [round(v,2) for v in MP.LEG_SLOT_Z], 'HB_TOP', MP.HB_TOP, 'LEVER_PIVOT', MP.LEVER_PIVOT, 'SPRING_LEN', MP.SPRING_LEN, 'F0', round(MP.spring_force(0),1))"
cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='slideparts.py'
s=open(p).read()
s=s.replace("STROKE = 6.0                 # slid off: the carrier this far back towards the dash (the gear then clears the teeth by 2.5)",
            "STROKE = 5.5                 # slid off: the carrier this far back towards the dash (the gear then clears the teeth by 2)")
old='''  cap = cs.offset(3.0, manifold3d.JoinType.Round, circular_segments=32).extrude(10.5).translate((0, 0, -50.5)) ^ \\
    box(-30, 30, -30, 30, -50.5, -40.0)'''
new='''  cap = cs.offset(3.0, manifold3d.JoinType.Round, circular_segments=32).extrude(10.5).translate((0, 0, -50.5)) ^ \\
    box(-30, 30, -30, 30, -50.5, -40.0)
  # its edge towards the dash and the column cut back 45 degrees (the column cover's lower front edge is there, slid off)
  from cadlib import prism_x
  cap = cap - prism_x([(CAP_CHAMFER_Y0, -51.0), (30.0, -51.0), (30.0, -51.0 + 30.0 - CAP_CHAMFER_Y0)], -30.0, 30.0)'''
assert old in s
s=s.replace(old,new)
s=s.replace("# ***** bought parts (for the checks and the pictures) *****",
"""CAP_CHAMFER_Y0 = 19.0                      # the board cap's 45 degree cut starts here on its column side (y)


# ***** bought parts (for the checks and the pictures) *****""")
open(p,'w').write(s)
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache && python3 -c "
import sys; sys.path.insert(0,'/home/claude/deliver/hardware/cad')
import slideparts as S
mb=S.motor_board(); print('cap', round(mb['board+cap'].volume()), [round(v,1) for v in mb['board+cap'].bounding_box()])
print('CAM_FLAT', round(S.CAM_FLAT,2), 'block', S.BLOCK_Y)
" && timeout 1700 python3 chk.py -70 103,106,108,110 2>&1 | sed 's/; /\n      /g' | grep -v "fingers on the grip\|adjustment tab"
cd /home/claude/deliver/hardware/cad && python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/patch_ra6b.py && PYTHONPATH=/home/claude/pylib python3 -c "
import rightarm as RA
print('ARM_Z', RA.ARM_Z, 'BAR_Z', RA.BAR_Z, 'RGROOVE_X', RA.RGROOVE_X, 'RG_STOP', RA.RG_STOP, 'DEEP_X0', RA.DEEP_X0, 'ARM_NUT_Z', RA.ARM_NUT_Z, 'HOLE_END', RA.ARM_HOLE_END)
a = RA.arm(); c = RA.carrier(); f = RA.frame_plate_v5()
for n, m in (('arm', a), ('carrier', c), ('plate', f)):
    bb = m.bounding_box(); print(n, round(m.volume()/1000*1.28), 'g', [round(bb[i+3]-bb[i],1) for i in range(3)], 'genus', m.genus())
"
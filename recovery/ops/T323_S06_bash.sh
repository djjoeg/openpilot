cp rightarm.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/rightarm.v5.py && cp rightcheck.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/rightcheck.v5.py && python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/patch_ra6.py && grep -n "frame_plate_v4\|PINCH_X\|NUT_TRAP" rightarm.py | head; PYTHONPATH=/home/claude/pylib python3 -c "
import rightarm as RA
print('ARM_Z', RA.ARM_Z, 'TOWER_Z', RA.TOWER_Z, 'DZ_OUT', RA.DZ_OUT, 'GROOVE_Z', RA.GROOVE_Z, 'BAR_Z', RA.BAR_Z, 'DEEP_X0', RA.DEEP_X0, 'RGROOVE_X', RA.RGROOVE_X)
a = RA.arm(); c = RA.carrier(); f = RA.frame_plate_v5()
for n, m in (('arm', a), ('carrier', c), ('plate', f)):
    bb = m.bounding_box(); print(n, round(m.volume()/1000*1.28), 'g', [round(bb[i+3]-bb[i],1) for i in range(3)], 'genus', m.genus())
import frameplate as FR
print('KEY label width', FR.text_width('< KEY', 1.0))
"
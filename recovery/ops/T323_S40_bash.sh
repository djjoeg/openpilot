sed -i 's/  return clean(body - union(labels).translate((0.0, 0.0, -SL.LABEL_H - 0.01)))/  return clean(body - union(labels).translate((0.0, 0.0, -SL.LABEL_H + 0.01)))/' rightarm.py && grep -n "LABEL_H + 0.01" rightarm.py && PYTHONPATH=/home/claude/pylib python3 -c "
import rightarm as RA
f = RA.frame_plate_v5(); a = RA.arm()
print('plate', round(f.volume()/1000*1.28,1), 'g', [round(v,1) for v in f.bounding_box()], f.genus())
print('arm', round(a.volume()/1000*1.28,1), 'g', a.genus(), 'ARM_BOLT_Y', RA.ARM_BOLT_Y, 'RG_Z', RA.RG_Z)
" && (time PYTHONPATH=/home/claude/pylib python3 rightcheck.py) > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/rc2.txt 2>&1; tail -30 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/rc2.txt
cp slideparts.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide/slideparts_dup_backup.py && python3 - <<'EOF'
p='/home/claude/deliver/hardware/cad/slideparts.py'
s=open(p).read()
first_carrier_end = s.index('# ***** the block *****\nBLOCK_Y', s.index('def slide_carrier()'))
tail_start = s.index('# ***** the block *****\n\ndef slide_block()')
new = s[:first_carrier_end] + s[tail_start:]
open(p,'w').write(new)
import re
print(len(s.splitlines()), '->', len(new.splitlines()))
for name in ['def slide_carrier','def slide_block','TONGUE_X =','LAND_H =','BLOCK_Y =','def cam_support','def _motor_plate']:
    print(name, new.count(name))
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 600 python3 -c "
import slideparts as S, slideassembly as SA
print('SW_HOLES_X', S.SW_HOLES_X, 'TONGUE', S.TONGUE_X, 'LAND_H', S.LAND_H, 'BLOCK', S.BLOCK_Y)
for n,f in [('carrier',S.slide_carrier),('block',S.slide_block),('lever',S.slide_lever),('pusher',S.pusher)]:
    m=f(); print(n, round(m.volume()), len(m.decompose()))
print(SA.switch_states())
"
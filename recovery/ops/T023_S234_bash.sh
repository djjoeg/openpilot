sed -i 's/^LIFT_DEG = 7.5          # lift lever up: motor gear about 7 mm off the teeth/LIFT_DEG = 10.0         # lift lever up: the motor gear clears the steering wheel teeth by about 4 mm/' mountparts.py && grep -n "^LIFT_DEG\|^STOP_DEG" mountparts.py && PYTHONPATH=/home/claude/pylib python3 -c "
import mountparts as MP
rows = MP.lever_lift_table(4.0, MP.A_HARD_STOP + 2)
print(' '.join('%d:%.2f/%.1fN' % (a, th, f) for a, th, f in rows))
print('max force %.1f N; spring at dead centre %.1f N, length %.1f' % (max(r[2] for r in rows), MP.spring_force(MP.cam_lift(MP.A_DEAD)), MP.SPRING_LEN - MP.SPRING_ARM*__import__('math').sin(__import__('math').radians(MP.cam_lift(MP.A_DEAD)))))
" && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/margin.py && PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  " | tail -4